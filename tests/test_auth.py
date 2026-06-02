import time

import pytest
from authlib.jose import JsonWebKey
from authlib.jose import jwt as authlib_jwt

from EventCoord.auth import (
    AudienceOrgResolver,
    HostedDomainOrgResolver,
    Identity,
    StaticOrgResolver,
    TokenIssuer,
    TokenVerifier,
)
from EventCoord.auth.providers import AuthProviderRegistry
from EventCoord.auth.providers.base import AuthError
from EventCoord.auth.providers.google import GoogleAuthProvider


@pytest.fixture(scope="module")
def rsa_keys():
    key = JsonWebKey.generate_key("RSA", 2048, is_private=True)
    private_pem = key.as_pem(is_private=True).decode("utf-8")
    public_jwk = JsonWebKey.import_key(
        key.as_pem(is_private=False), {"kty": "RSA"}
    ).as_dict()
    return private_pem, public_jwk


# --------------------------------------------------------------------------- #
# Identity
# --------------------------------------------------------------------------- #
def test_identity_to_claims_preserves_wire_spellings():
    identity = Identity(
        subject="abc",
        provider="google",
        email="a@b.com",
        name="A B",
        given_name="A",
        family_name="B",
        org_id="org-1",
        org_name="Org One",
    )
    claims = identity.to_claims()
    assert claims["sub"] == "abc"
    assert claims["givenName"] == "A"
    assert claims["familyName"] == "B"
    assert claims["org_id"] == "org-1"
    assert "given_name" not in claims


def test_identity_public_user_hides_internal_fields():
    identity = Identity(subject="abc", provider="google", email="a@b.com")
    user = identity.to_public_user()
    assert "sub" not in user
    assert "provider" not in user
    assert user["email"] == "a@b.com"


def test_identity_from_claims_roundtrip_and_extra():
    identity = Identity(subject="abc", provider="google", given_name="A")
    rebuilt = Identity.from_claims({**identity.to_claims(), "role": "admin"})
    assert rebuilt.subject == "abc"
    assert rebuilt.given_name == "A"
    assert rebuilt.extra == {"role": "admin"}


def test_identity_from_claims_accepts_snake_case():
    rebuilt = Identity.from_claims({"sub": "x", "given_name": "G", "family_name": "F"})
    assert rebuilt.given_name == "G"
    assert rebuilt.family_name == "F"


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
class _StubProvider:
    name = "stub"

    def authenticate(self, credential):
        return Identity(subject=credential, provider="stub"), None


def test_registry_register_get_and_names():
    reg = AuthProviderRegistry()
    reg.register(_StubProvider())
    assert "stub" in reg
    assert reg.get("STUB") is not None  # case-insensitive
    assert reg.names() == ["stub"]
    assert reg.get("missing") is None


def test_registry_rejects_nameless_provider():
    reg = AuthProviderRegistry()
    with pytest.raises(ValueError):
        reg.register(object())


# --------------------------------------------------------------------------- #
# Org resolvers
# --------------------------------------------------------------------------- #
class _FakeOrgModel:
    def __init__(self):
        self.by_aud = {"client-123": {"org_id": "org-1", "name": "Org One"}}
        self.by_domain = {"example.com": {"org_id": "org-2", "name": "Org Two"}}

    def get_by_aud(self, aud):
        return self.by_aud.get(aud)

    def get_by_domain(self, domain):
        return self.by_domain.get(domain)


def test_audience_resolver():
    resolver = AudienceOrgResolver(_FakeOrgModel())
    assert resolver.resolve({"aud": "client-123"})["org_id"] == "org-1"
    assert resolver.resolve({"aud": "nope"}) is None
    assert resolver.resolve({}) is None


def test_hosted_domain_resolver_uses_hd_then_email():
    resolver = HostedDomainOrgResolver(_FakeOrgModel())
    assert resolver.resolve({"hd": "example.com"})["org_id"] == "org-2"
    assert resolver.resolve({"email": "joe@example.com"})["org_id"] == "org-2"
    assert resolver.resolve({"email": "joe@unknown.com"}) is None


def test_static_resolver():
    org = {"org_id": "fixed", "name": "Fixed"}
    assert StaticOrgResolver(org).resolve({}) is org


# --------------------------------------------------------------------------- #
# Token issue / verify round trip
# --------------------------------------------------------------------------- #
def test_token_issue_and_verify_roundtrip(rsa_keys):
    private_pem, public_jwk = rsa_keys
    issuer = TokenIssuer("https://api.example.com", lambda: private_pem, ttl_seconds=60)
    verifier = TokenVerifier(
        "https://api.example.com",
        jwks_fetcher=lambda url: [public_jwk],
    )
    identity = Identity(
        subject="user-1", provider="google", email="u@example.com", org_id="org-1"
    )
    token = issuer.issue(identity)
    verified = verifier.verify_identity(token)
    assert verified is not None
    assert verified.subject == "user-1"
    assert verified.org_id == "org-1"


def test_token_verify_rejects_wrong_issuer(rsa_keys):
    private_pem, public_jwk = rsa_keys
    issuer = TokenIssuer("https://evil.example.com", lambda: private_pem)
    verifier = TokenVerifier(
        "https://api.example.com",
        jwks_fetcher=lambda url: [public_jwk],
        max_retries=1,
    )
    token = issuer.issue(Identity(subject="x", provider="google"))
    assert verifier.verify(token) is None


def test_token_verify_rejects_expired(rsa_keys):
    private_pem, public_jwk = rsa_keys
    issuer = TokenIssuer("https://api.example.com", lambda: private_pem, ttl_seconds=10)
    verifier = TokenVerifier(
        "https://api.example.com",
        jwks_fetcher=lambda url: [public_jwk],
        max_retries=1,
    )
    token = issuer.issue(Identity(subject="x", provider="google"), now=int(time.time()) - 100)
    assert verifier.verify(token) is None


# --------------------------------------------------------------------------- #
# Google provider (with injected JWKS + org resolver)
# --------------------------------------------------------------------------- #
def _google_token(private_pem, public_jwk, **overrides):
    payload = {
        "iss": "https://accounts.google.com",
        "aud": "client-123",
        "sub": "google-sub-1",
        "email": "user@example.com",
        "name": "User Example",
        "given_name": "User",
        "family_name": "Example",
        "exp": int(time.time()) + 300,
        "iat": int(time.time()),
    }
    payload.update(overrides)
    header = {"alg": "RS256", "kid": public_jwk.get("kid")}
    return authlib_jwt.encode(header, payload, private_pem).decode("utf-8")


def test_google_provider_authenticates_and_resolves_org(rsa_keys):
    private_pem, public_jwk = rsa_keys
    provider = GoogleAuthProvider(
        AudienceOrgResolver(_FakeOrgModel()),
        jwks_fetcher=lambda url: [public_jwk],
    )
    token = _google_token(private_pem, public_jwk)
    identity, error = provider.authenticate(token)
    assert error is None
    assert identity is not None
    assert identity.provider == "google"
    assert identity.org_id == "org-1"
    assert identity.org_name == "Org One"
    assert identity.email == "user@example.com"
    assert identity.given_name == "User"


def test_google_provider_rejects_unknown_audience(rsa_keys):
    private_pem, public_jwk = rsa_keys
    provider = GoogleAuthProvider(
        AudienceOrgResolver(_FakeOrgModel()),
        jwks_fetcher=lambda url: [public_jwk],
    )
    token = _google_token(private_pem, public_jwk, aud="unknown-client")
    identity, error = provider.authenticate(token)
    assert identity is None
    assert isinstance(error, AuthError)


def test_google_provider_rejects_bad_token(rsa_keys):
    private_pem, public_jwk = rsa_keys
    provider = GoogleAuthProvider(
        AudienceOrgResolver(_FakeOrgModel()),
        jwks_fetcher=lambda url: [public_jwk],
        max_retries=1,
    )
    identity, error = provider.authenticate("not-a-jwt")
    assert identity is None
    assert isinstance(error, AuthError)

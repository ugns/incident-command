"""Canonical, provider-agnostic representation of an authenticated principal.

Every :class:`~EventCoord.auth.providers.base.AuthProvider` normalises its
provider-specific payload (a Google ID token, a GitHub user, an API key
record, ...) into a single :class:`Identity`. Downstream code -- token
issuing, the API Gateway authorizer context, feature-flag evaluation, and the
resource handlers -- only ever depends on this shape, never on the originating
provider.

Wire compatibility note: the API has historically emitted the name parts as
``givenName`` / ``familyName`` (camelCase) in both the login response and the
JWT claims. To avoid breaking already-issued tokens and the existing frontend,
:meth:`Identity.to_claims` keeps those exact spellings. The internal attribute
names use snake_case for Pythonic clarity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Claims that are part of the canonical identity and therefore promoted to
# top-level attributes rather than being stashed in ``extra``. Both the wire
# spellings (camelCase) and the internal snake_case spellings are listed so
# neither leaks into ``extra`` when rebuilding from claims.
_CORE_CLAIM_KEYS = (
    "sub",
    "iss",
    "iat",
    "exp",
    "email",
    "name",
    "givenName",
    "familyName",
    "given_name",
    "family_name",
    "picture",
    "org_id",
    "org_name",
    "hd",
    "provider",
)


@dataclass
class Identity:
    """A normalised, authenticated principal.

    Attributes:
        subject: Stable unique id for the principal *within its provider*.
        provider: Name of the provider that authenticated this identity.
        email: Primary email address, if known.
        name: Human readable display name.
        given_name / family_name: Optional name parts.
        picture: Optional avatar URL.
        org_id: The EventCoord organisation this principal belongs to. This is
            the single most important multi-tenant claim and is resolved by an
            :class:`~EventCoord.auth.org_resolver.OrgResolver`, *not* by the
            provider itself.
        org_name: Human readable organisation name.
        hd: Optional hosted-domain hint (e.g. Google Workspace domain).
        extra: Any additional provider-specific claims worth carrying through.
    """

    subject: str
    provider: str
    email: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    org_id: Optional[str] = None
    org_name: Optional[str] = None
    hd: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_claims(self) -> Dict[str, Any]:
        """Return the identity as a flat JWT claim dictionary.

        The historical camelCase spellings (``givenName`` / ``familyName``)
        are preserved for backwards compatibility. ``None`` values are omitted.
        Provider-specific extras never override core claims.
        """
        claims: Dict[str, Any] = {
            "sub": self.subject,
            "provider": self.provider,
            "email": self.email,
            "name": self.name,
            "givenName": self.given_name,
            "familyName": self.family_name,
            "picture": self.picture,
            "org_id": self.org_id,
            "org_name": self.org_name,
            "hd": self.hd,
        }
        claims = {k: v for k, v in claims.items() if v is not None}
        for key, value in self.extra.items():
            claims.setdefault(key, value)
        return claims

    def to_public_user(self) -> Dict[str, Any]:
        """Return the user info safe to return to the client on login.

        Internal/security fields (the provider subject and provider name) are
        intentionally excluded, matching the original login response.
        """
        user = self.to_claims()
        for hidden in ("sub", "provider"):
            user.pop(hidden, None)
        return user

    @classmethod
    def from_claims(cls, claims: Dict[str, Any]) -> "Identity":
        """Rebuild an :class:`Identity` from a (verified) claim dictionary.

        Accepts both the camelCase spellings emitted by this API and the
        snake_case registered-claim spellings, so verification works regardless
        of which producer minted the token.
        """
        extra = {k: v for k, v in claims.items() if k not in _CORE_CLAIM_KEYS}
        return cls(
            subject=claims.get("sub", ""),
            provider=claims.get("provider", "unknown"),
            email=claims.get("email"),
            name=claims.get("name"),
            given_name=claims.get("givenName") or claims.get("given_name"),
            family_name=claims.get("familyName") or claims.get("family_name"),
            picture=claims.get("picture"),
            org_id=claims.get("org_id"),
            org_name=claims.get("org_name"),
            hd=claims.get("hd"),
            extra=extra,
        )

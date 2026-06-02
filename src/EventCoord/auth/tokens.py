"""Issue and verify the API's own RS256 session tokens.

These two classes replace three near-duplicate implementations that previously
lived in ``lambda/login`` (minting), ``lambda/authorizer`` (verification, with
JWKS caching) and ``src/EventCoord/client/auth.py`` (verification, with retry).
Consolidating them removes drift between the signer and verifier and makes the
token format reusable by any component.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Dict, List, Optional, Sequence

import requests
from authlib.jose import JsonWebKey, JsonWebToken, JWTClaims
from authlib.jose import jwt as authlib_jwt

from EventCoord.auth.identity import Identity
from EventCoord.utils.handler import get_logger

logger = get_logger(__name__)

# A provider for the signing/verifying key material (PEM strings). Injectable so
# the AWS Secrets Manager dependency stays out of the core logic.
KeyProvider = Callable[[], str]
PublicKeysProvider = Callable[[], List[str]]
JwksFetcher = Callable[[str], List[Dict[str, Any]]]


def _jwks_path(issuer: str) -> str:
    return f"{issuer.rstrip('/')}/.well-known/jwks.json"


class TokenIssuer:
    """Mint signed RS256 JWTs from an :class:`Identity`."""

    def __init__(
        self,
        issuer: str,
        private_key_provider: KeyProvider,
        *,
        ttl_seconds: int = 3600,
    ) -> None:
        self._issuer = issuer
        self._get_private_key = private_key_provider
        self._ttl = ttl_seconds

    def issue(
        self,
        identity: Identity,
        *,
        extra_claims: Optional[Dict[str, Any]] = None,
        now: Optional[int] = None,
    ) -> str:
        now = int(time.time()) if now is None else now
        payload: Dict[str, Any] = identity.to_claims()
        if extra_claims:
            payload.update(extra_claims)
        payload["iss"] = str(self._issuer)
        payload["iat"] = now
        payload["exp"] = now + self._ttl

        private_key = self._get_private_key()
        jwk = JsonWebKey.import_key(private_key, {"kty": "RSA"})
        jwk_dict = jwk.as_dict() if hasattr(jwk, "as_dict") else None
        key_id = jwk_dict.get("kid") if jwk_dict else None

        header: Dict[str, Any] = {
            "alg": "RS256",
            "typ": "JWT",
            "jku": _jwks_path(self._issuer),
        }
        if key_id:
            header["kid"] = key_id

        return authlib_jwt.encode(header, payload, private_key).decode("utf-8")


class TokenVerifier:
    """Verify the API's RS256 JWTs against a JWKS endpoint.

    JWKS responses are cached for ``cache_ttl_seconds`` to avoid a network call
    on every request (matching the previous authorizer behaviour), and fetches
    are retried with backoff (matching the previous client behaviour).
    """

    def __init__(
        self,
        issuer: str,
        *,
        jwks_url: Optional[str] = None,
        jwks_fetcher: Optional[JwksFetcher] = None,
        algorithms: Sequence[str] = ("RS256",),
        cache_ttl_seconds: int = 300,
        max_retries: int = 3,
        leeway: int = 3,
    ) -> None:
        self._issuer = issuer
        self._jwks_url = jwks_url or _jwks_path(issuer)
        self._fetch_jwks = jwks_fetcher or self._default_fetch
        self._algorithms = list(algorithms)
        self._cache_ttl = cache_ttl_seconds
        self._max_retries = max_retries
        self._leeway = leeway
        self._cache: List[Dict[str, Any]] = []
        self._cache_at = 0.0
        self._lock = threading.Lock()

    @staticmethod
    def _default_fetch(url: str) -> List[Dict[str, Any]]:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()["keys"]

    def _get_jwks(self) -> List[Dict[str, Any]]:
        now = time.time()
        with self._lock:
            if not self._cache or (now - self._cache_at) > self._cache_ttl:
                self._cache = self._fetch_jwks(self._jwks_url)
                self._cache_at = now
            return self._cache

    def verify(self, token: str) -> Optional[JWTClaims]:
        for attempt in range(1, self._max_retries + 1):
            try:
                jwks = self._get_jwks()
                jwt_obj = JsonWebToken(self._algorithms)
                claims = jwt_obj.decode(
                    token,
                    jwks,
                    claims_options={
                        "iss": {"essential": True, "value": self._issuer},
                    },
                )
                claims.validate(now=int(time.time()), leeway=self._leeway)
                return claims
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    f"JWT verification error (attempt {attempt}): {e}"
                )
                # Force a JWKS refresh in case the signing key rotated.
                with self._lock:
                    self._cache = []
                if attempt == self._max_retries:
                    return None
                time.sleep(0.5 * attempt)
        return None

    def verify_identity(self, token: str) -> Optional[Identity]:
        claims = self.verify(token)
        if claims is None:
            return None
        return Identity.from_claims(dict(claims))

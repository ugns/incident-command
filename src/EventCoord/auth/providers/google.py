"""Google ID-token authentication provider.

This is a faithful port of the original ``lambda/login/googleAuthProvider.py``
with two important decoupling changes:

1. The organisation lookup is delegated to an injected
   :class:`~EventCoord.auth.org_resolver.OrgResolver` instead of being
   hard-coded against the ``Organization`` model.
2. The set of valid audiences is resolved lazily, per request, rather than
   scanning DynamoDB once at module-import time (which made newly created orgs
   invisible until the Lambda recycled and made the module impossible to import
   without AWS access).
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

import requests
from authlib.jose import JsonWebToken, JWTClaims

from EventCoord.auth.identity import Identity
from EventCoord.auth.org_resolver import OrgResolver
from EventCoord.auth.providers.base import AuthError, AuthResult
from EventCoord.utils.handler import get_logger

logger = get_logger(__name__)

GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ("accounts.google.com", "https://accounts.google.com")

# Type of an optional JWKS fetcher dependency (kept injectable for tests).
JwksFetcher = Callable[[str], List[Dict[str, Any]]]


def _default_jwks_fetcher(url: str) -> List[Dict[str, Any]]:
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.json()["keys"]


class GoogleAuthProvider:
    name = "google"

    def __init__(
        self,
        org_resolver: OrgResolver,
        *,
        jwks_url: str = GOOGLE_JWKS_URL,
        jwks_fetcher: Optional[JwksFetcher] = None,
        allowed_issuers: tuple = GOOGLE_ISSUERS,
        max_retries: int = 3,
    ) -> None:
        self._org_resolver = org_resolver
        self._jwks_url = jwks_url
        self._fetch_jwks = jwks_fetcher or _default_jwks_fetcher
        self._allowed_issuers = list(allowed_issuers)
        self._max_retries = max_retries

    def _validate_id_token(self, token: str) -> Optional[JWTClaims]:
        for attempt in range(1, self._max_retries + 1):
            try:
                jwks = self._fetch_jwks(self._jwks_url)
                jwt_obj = JsonWebToken(["RS256"])
                claims = jwt_obj.decode(
                    token,
                    jwks,
                    claims_options={
                        "iss": {
                            "essential": True,
                            "values": self._allowed_issuers,
                        },
                        # ``aud`` must be present; that it maps to a known org
                        # is enforced by the org resolver below.
                        "aud": {"essential": True},
                    },
                )
                claims.validate(now=int(time.time()), leeway=3)
                return claims
            except Exception as e:  # noqa: BLE001 - we deliberately retry/log
                logger.warning(
                    f"Google ID token validation failed (attempt {attempt}): {e}"
                )
                if attempt == self._max_retries:
                    return None
                time.sleep(0.5 * attempt)
        return None

    def authenticate(self, credential: str) -> AuthResult:
        try:
            claims = self._validate_id_token(credential)
            if not claims:
                return None, AuthError("Invalid Google token")

            aud = claims.get("aud")
            if not isinstance(aud, str) or not aud:
                return None, AuthError("Missing or invalid audience (aud) in token")

            org = self._org_resolver.resolve(dict(claims))
            if not org:
                return None, AuthError(
                    "No organization found for this audience (aud)"
                )

            identity = Identity(
                subject=str(claims.get("sub")),
                provider=self.name,
                email=claims.get("email"),
                name=claims.get("name"),
                given_name=claims.get("given_name"),
                family_name=claims.get("family_name"),
                picture=claims.get("picture"),
                org_id=org.get("org_id"),
                org_name=org.get("name"),
                hd=claims.get("hd") or None,
            )
            return identity, None
        except Exception as e:  # noqa: BLE001
            logger.error(f"Google token validation failed: {e}")
            return None, AuthError("Token validation failed")

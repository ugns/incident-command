import logging
import time
from typing import Optional

from authlib.jose import JsonWebToken, JWTClaims

from EventCoord.auth.jwks import JwksClient
from EventCoord.auth.provider import AuthResult
from EventCoord.models.organizations import Organization

logger = logging.getLogger(__name__)

_GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
_VALID_ISSUERS = ("accounts.google.com", "https://accounts.google.com")

# Module-level client so the key cache is shared across Lambda warm invocations.
_jwks_client = JwksClient(_GOOGLE_JWKS_URL)


class GoogleAuthProvider:
    """
    Google Sign-In (OIDC) authentication provider.

    Validates a Google ID token against Google's public JWKS, then maps the
    token's ``aud`` claim to an organisation record in DynamoDB.

    The ``aud`` value (Google OAuth Client ID) must be stored in the
    ``organizations`` table's ``aud`` attribute so that
    :meth:`~EventCoord.models.organizations.Organization.get_by_aud` can
    resolve the owning organisation.
    """

    @property
    def provider_name(self) -> str:
        return "google"

    def _validate_token(self, token: str) -> Optional[JWTClaims]:
        """
        Verify the Google ID token's RS256 signature and standard claims.

        Acceptable audiences are fetched fresh on each call from DynamoDB so
        that newly registered organisations are immediately honoured without a
        Lambda cold start.
        """
        valid_auds = [
            org["aud"] for org in Organization.list_all() if "aud" in org
        ]
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                jwks = _jwks_client.get_keys()
                jwt_obj = JsonWebToken(["RS256"])
                claims = jwt_obj.decode(
                    token,
                    jwks,
                    claims_options={
                        "iss": {
                            "essential": True,
                            "values": list(_VALID_ISSUERS),
                        },
                        "aud": {
                            "essential": True,
                            "values": valid_auds,
                        },
                    },
                )
                claims.validate(now=int(time.time()), leeway=3)
                return claims
            except Exception as exc:
                logger.error(
                    "Google token validation failed (attempt %d/%d): %s",
                    attempt,
                    max_retries,
                    exc,
                )
                if attempt == max_retries:
                    return None
                time.sleep(0.5 * attempt)
        return None

    def authenticate(self, token: str) -> AuthResult:
        try:
            token_info = self._validate_token(token)
        except Exception as exc:
            logger.error("Unexpected error validating Google token: %s", exc)
            return AuthResult.failure("Token validation failed")

        if not token_info:
            return AuthResult.failure("Invalid Google token")

        aud = token_info.get("aud")
        if not isinstance(aud, str) or not aud:
            return AuthResult.failure("Missing or invalid audience (aud) in token")

        org = Organization.get_by_aud(aud)
        if not org:
            return AuthResult.failure("No organization found for this audience (aud)")

        user_info = {
            "sub": token_info.get("sub"),
            "email": token_info.get("email"),
            "name": token_info.get("name"),
            "givenName": token_info.get("given_name"),
            "familyName": token_info.get("family_name"),
            "picture": token_info.get("picture"),
            "org_id": org.get("org_id"),
            "org_name": org.get("name"),
            "hd": token_info.get("hd") or None,
        }
        return AuthResult.success(user_info)

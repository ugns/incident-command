import logging
import os
import time
from typing import Optional

from authlib.jose import JsonWebToken, JWTClaims

from EventCoord.auth.jwks import JwksClient
from EventCoord.auth.provider import AuthResult
from EventCoord.models.organizations import Organization

logger = logging.getLogger(__name__)

# Microsoft publishes tenant-independent JWKS.  Single-tenant apps can
# override this with a tenant-specific URL via the environment variable.
_DEFAULT_JWKS_URL = (
    "https://login.microsoftonline.com/common/discovery/v2.0/keys"
)
_VALID_ISSUER_PREFIX = "https://login.microsoftonline.com/"

_jwks_client = JwksClient(
    os.environ.get("MICROSOFT_JWKS_URL", _DEFAULT_JWKS_URL)
)


class MicrosoftAuthProvider:
    """
    Microsoft Azure AD / Entra ID (OIDC) authentication provider.

    Validates a Microsoft ID token against Microsoft's public JWKS, then maps
    the token's ``aud`` claim (Application Client ID) to an organisation record
    in DynamoDB.

    Configuration (environment variables)
    --------------------------------------
    ``MICROSOFT_JWKS_URL`` *(optional)*:
        Override the JWKS endpoint URL, e.g. for a single-tenant application::

            https://login.microsoftonline.com/<tenant-id>/discovery/v2.0/keys

        Defaults to the tenant-independent common endpoint.

    ``MICROSOFT_CLIENT_ID`` *(optional)*:
        Expected ``aud`` value for strict app-specific validation.  When set,
        tokens whose ``aud`` does not match this value are rejected before the
        DynamoDB look-up.

    Organisation mapping
    --------------------
    The Application (Client) ID must be stored in the ``organizations`` table
    as the ``aud`` attribute so that
    :meth:`~EventCoord.models.organizations.Organization.get_by_aud` can
    resolve the owning organisation – the same convention used by the Google
    provider.
    """

    @property
    def provider_name(self) -> str:
        return "microsoft"

    def _validate_token(self, token: str) -> Optional[JWTClaims]:
        """Verify the Microsoft ID token's RS256 signature and standard claims."""
        client_id = os.environ.get("MICROSOFT_CLIENT_ID")
        aud_option: dict = (
            {"essential": True, "value": client_id}
            if client_id
            else {"essential": True}
        )
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                jwks = _jwks_client.get_keys()
                jwt_obj = JsonWebToken(["RS256"])
                claims = jwt_obj.decode(
                    token,
                    jwks,
                    claims_options={
                        "iss": {"essential": True},
                        "aud": aud_option,
                    },
                )
                claims.validate(now=int(time.time()), leeway=3)
                # Verify issuer is a Microsoft tenant endpoint.
                iss = claims.get("iss", "")
                if not iss.startswith(_VALID_ISSUER_PREFIX):
                    logger.warning("Unrecognised Microsoft token issuer: %s", iss)
                    return None
                return claims
            except Exception as exc:
                logger.error(
                    "Microsoft token validation failed (attempt %d/%d): %s",
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
            logger.error("Unexpected error validating Microsoft token: %s", exc)
            return AuthResult.failure("Token validation failed")

        if not token_info:
            return AuthResult.failure("Invalid Microsoft token")

        # For Microsoft tokens the audience is the Application Client ID,
        # which maps to the ``aud`` column in the organisations table.
        aud = token_info.get("aud")
        if not isinstance(aud, str) or not aud:
            return AuthResult.failure("Missing or invalid audience (aud) in token")

        org = Organization.get_by_aud(aud)
        if not org:
            return AuthResult.failure("No organization found for this audience (aud)")

        user_info = {
            # Microsoft uses ``oid`` (object ID) as the stable subject
            # identifier; fall back to ``sub`` for compatibility.
            "sub": token_info.get("oid") or token_info.get("sub"),
            "email": (
                token_info.get("email") or token_info.get("preferred_username")
            ),
            "name": token_info.get("name") or "",
            "givenName": token_info.get("given_name"),
            "familyName": token_info.get("family_name"),
            "org_id": org.get("org_id"),
            "org_name": org.get("name"),
            # Tenant ID is the Microsoft equivalent of a hosted domain.
            "hd": token_info.get("tid") or None,
        }
        return AuthResult.success(user_info)

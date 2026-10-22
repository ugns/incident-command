import logging
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from authlib.jose import JsonWebToken, JWTClaims
from aws_lambda_typing.events import APIGatewayProxyEventV2

from EventCoord.auth.jwks import JwksClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Module-level client; shared across warm Lambda invocations.
# The JWKS_URL must point to the application's own JWKS endpoint, e.g.
# https://api.example.com/.well-known/jwks.json
_JWKS_URL = os.environ.get("JWKS_URL", "https://your-api-domain/.well-known/jwks.json")
_jwks_client = JwksClient(_JWKS_URL)


def verify_jwt_token(token: str) -> Optional[JWTClaims]:
    """
    Verify *token* against the application's own JWKS endpoint.

    This performs full cryptographic verification (RS256) and claim validation.
    It is intended for use outside of API Gateway (e.g. background workers,
    CLI tools).  Lambda handlers that sit behind the API Gateway authorizer do
    not need to call this – the authorizer already verifies the token, and
    :func:`EventCoord.utils.handler.get_claims` extracts the already-trusted
    claims from the request context.

    Returns the decoded :class:`JWTClaims` on success, or ``None`` on failure.
    """
    parsed = urlparse(_JWKS_URL)
    issuer = f"{parsed.scheme}://{parsed.hostname}"
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                "Verifying JWT token: %s… (attempt %d)", token[:10], attempt
            )
            jwks = _jwks_client.get_keys()
            jwt_obj = JsonWebToken(["RS256"])
            claims = jwt_obj.decode(
                token,
                jwks,
                claims_options={
                    "iss": {
                        "essential": True,
                        "value": issuer,
                    },
                },
            )
            claims.validate(now=int(time.time()), leeway=3)
            logger.debug("Decoded JWT payload: %s", claims)
            return claims
        except Exception as exc:
            logger.warning(
                "JWT verification error (attempt %d): %s", attempt, exc, exc_info=True
            )
            if attempt == max_retries:
                logger.error("Max retries reached; token verification failed")
                return None
            time.sleep(0.5 * attempt)
    return None


def require_auth(event: APIGatewayProxyEventV2) -> Optional[JWTClaims]:
    """
    Extract and verify the Bearer token from an API Gateway V2 event.

    Returns the decoded :class:`JWTClaims` on success, or ``None`` if the
    Authorization header is absent or the token is invalid.
    """
    headers = event.get("headers", {}) or {}
    auth_header = headers.get("Authorization") or headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header")
        return None
    token = auth_header.split(" ", 1)[1]
    logger.info("Extracted Bearer token: %s… (truncated)", token[:10])
    return verify_jwt_token(token)


def check_auth(event: APIGatewayProxyEventV2) -> Dict[str, Any] | JWTClaims:
    """
    Verify the Bearer token and return claims, or a 401 error response dict.

    This is a convenience wrapper for non-Lambda-authorizer contexts.  In
    production Lambda handlers backed by API Gateway, prefer
    :func:`EventCoord.utils.handler.get_claims` instead.
    """
    user = require_auth(event)
    if not user:
        logger.warning("Unauthorized access attempt")
        return {"statusCode": 401, "body": "Unauthorized"}
    logger.info("Authenticated user: %s", user)
    return user

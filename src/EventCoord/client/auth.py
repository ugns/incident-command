"""Backwards-compatible auth helpers for protected handlers.

This module historically carried its own JWT verification implementation. It
now delegates to the shared :class:`EventCoord.auth.TokenVerifier` so there is
a single source of truth for how the API's tokens are verified. The public
``require_auth`` / ``check_auth`` API is unchanged.
"""

import logging
import os
from urllib.parse import urlparse
from typing import Any, Dict, Optional

from authlib.jose import JWTClaims
from aws_lambda_typing.events import APIGatewayProxyEventV2

from EventCoord.auth import TokenVerifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _build_verifier() -> TokenVerifier:
    jwks_url = os.environ.get(
        "JWKS_URL", "https://your-api-domain/auth/.well-known/jwks.json"
    )
    parsed = urlparse(jwks_url)
    issuer = f"{parsed.scheme}://{parsed.hostname}"
    return TokenVerifier(issuer, jwks_url=jwks_url)


def verify_jwt_token(token: str) -> Optional[JWTClaims]:
    return _build_verifier().verify(token)


def require_auth(event: APIGatewayProxyEventV2) -> Optional[JWTClaims]:
    headers = event.get("headers", {})
    auth_header = headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header.")
        return None
    token = auth_header.split(" ", 1)[1]
    logger.info(f"Extracted Bearer token: {token[:10]}... (truncated)")
    return verify_jwt_token(token)


def check_auth(event: APIGatewayProxyEventV2) -> Dict[str, Any] | JWTClaims:
    user = require_auth(event)
    if not user:
        logger.warning("Unauthorized access attempt.")
        return {
            "statusCode": 401,
            "body": "Unauthorized",
        }
    logger.info(f"Authenticated user: {user}")
    return user

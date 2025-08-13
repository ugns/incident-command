import os
import logging
import time
import requests
from urllib.parse import urlparse
from authlib.jose import JsonWebToken, JWTClaims
from typing import Optional, Dict, Any
from aws_lambda_typing.events import APIGatewayProxyEventV2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def verify_jwt_token(token: str) -> Optional[JWTClaims]:
    JWKS_URL = os.environ.get(
        'JWKS_URL', 'https://your-api-domain/auth/.well-known/jwks.json')
    parsed = urlparse(JWKS_URL)
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"Verifying JWT token: {token[:10]}... (truncated) [attempt {attempt}]")
            resp = requests.get(JWKS_URL, timeout=5)
            logger.debug("JWKS endpoint responded")
            resp.raise_for_status()
            logger.debug("JWKS response status OK")
            jwks = resp.json()['keys']
            logger.debug(f"JWKS keys: {jwks}")
            jwt_obj = JsonWebToken(['RS256'])
            logger.debug("About to decode JWT")
            claims = jwt_obj.decode(
                token,
                jwks,
                claims_options={
                    "iss": {
                        "essential": True,
                        "value": f"{parsed.scheme}://{parsed.hostname}"
                    },
                }
            )
            logger.debug("Decoded JWT, about to validate")
            claims.validate(now=int(time.time()), leeway=3)
            logger.debug(f"Decoded JWT payload: {claims}")
            return claims
        except Exception as e:
            logger.warning(
                f"JWT verification error (attempt {attempt}): {e}", exc_info=True)
            if attempt == max_retries:
                logger.error("Max retries reached")
                return None
            time.sleep(0.5 * attempt)  # Exponential backoff


def require_auth(event: APIGatewayProxyEventV2) -> Optional[JWTClaims]:
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.warning("Missing or invalid Authorization header.")
        return None
    token = auth_header.split(' ', 1)[1]
    logger.info(f"Extracted Bearer token: {token[:10]}... (truncated)")
    logger.debug(f"Full token: {token}")
    payload = verify_jwt_token(token)
    return payload


def check_auth(event: APIGatewayProxyEventV2) -> Dict[str, Any] | JWTClaims:
    user = require_auth(event)
    if not user:
        logger.warning("Unauthorized access attempt.")
        return {
            "statusCode": 401,
            "body": "Unauthorized"
        }
    logger.info(f"Authenticated user: {user}")
    return user

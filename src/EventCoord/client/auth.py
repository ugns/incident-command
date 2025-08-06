import os
import logging
from authlib.jose import JsonWebToken

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def verify_jwt_token(token):
    import time
    import requests
    JWKS_URL = os.environ.get(
        'JWKS_URL', 'https://your-api-domain/auth/.well-known/jwks.json')
    try:
        logger.info(f"Verifying JWT token: {token[:10]}... (truncated)")
        resp = requests.get(JWKS_URL, timeout=3)
        resp.raise_for_status()
        jwks = resp.json()['keys']
        jwt_obj = JsonWebToken(['RS256'])
        # Try each key in JWKS
        for jwk_dict in jwks:
            try:
                claims = jwt_obj.decode(token, jwk_dict)
                claims.validate_exp(now=int(time.time()), leeway=30)
                logger.debug(f"Decoded JWT payload: {claims}")
                return dict(claims)
            except Exception as e:
                logger.debug(
                    f"JWT verification failed for key: {jwk_dict.get('kid')}, error: {e}")
                continue
        logger.warning("JWT verification failed for all keys in JWKS.")
        return None
    except Exception as e:
        logger.warning(f"JWT verification general error: {e}")
        return None


def require_auth(event):
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


def check_auth(event):
    user = require_auth(event)
    if not user:
        logger.warning("Unauthorized access attempt.")
        return {
            "statusCode": 401,
            "body": "Unauthorized"
        }
    logger.info(f"Authenticated user: {user}")
    return user

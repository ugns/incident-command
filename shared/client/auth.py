import os
import logging
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_jwt_secret():
    secret = os.environ.get('JWT_SECRET', 'changeme')
    logger.debug(f"Using JWT secret: {'*' * len(secret) if secret != 'changeme' else 'changeme'}")
    return secret


def verify_jwt_token(token):
    import time
    secret = get_jwt_secret()
    try:
        logger.info(f"Verifying JWT token: {token[:10]}... (truncated)")
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        logger.debug(f"Decoded JWT payload: {payload}")
        # Manual expiration check for tokens missing 'exp' or with expired 'exp'
        if 'exp' not in payload or payload['exp'] < int(time.time()):
            logger.warning("JWT token missing or expired 'exp' claim.")
            return None
        return payload
    except ExpiredSignatureError:
        logger.warning("JWT token expired.")
        return None
    except JWTError as e:
        logger.warning(f"JWT verification error: {e}")
        return None


def require_auth(event):
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.warning("Missing or invalid Authorization header.")
        return None
    token = auth_header.split(' ', 1)[1]
    logger.info(f"Extracted Bearer token: {token[:10]}... (truncated)")
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

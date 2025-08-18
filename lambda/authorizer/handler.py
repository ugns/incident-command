import os
import time
import logging
import requests
import threading
from urllib.parse import urlparse
from authlib.jose import JsonWebToken, JWTClaims
from typing import Optional
from aws_lambda_typing.events import APIGatewayRequestAuthorizerEvent
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses.api_gateway_authorizer import APIGatewayAuthorizerResponse
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()  # Automatically patches boto3, requests, etc.

xray_recorder.configure(service='incident-cmd')

# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logging.getLogger().setLevel(LOG_LEVEL)

_JWKS_CACHE = []
_JWKS_CACHE_LOCK = threading.Lock()
_JWKS_CACHE_EXPIRY = 300  # seconds
_JWKS_CACHE_LAST_FETCH = 0


def get_jwks(jwks_url: str):
    global _JWKS_CACHE, _JWKS_CACHE_LAST_FETCH
    now = time.time()
    with _JWKS_CACHE_LOCK:
        if not _JWKS_CACHE or (now - _JWKS_CACHE_LAST_FETCH) > _JWKS_CACHE_EXPIRY:
            resp = requests.get(jwks_url, timeout=5)
            resp.raise_for_status()
            _JWKS_CACHE = resp.json()['keys']
            _JWKS_CACHE_LAST_FETCH = now
    return _JWKS_CACHE


def verify_jwt_token(token: str) -> Optional[JWTClaims]:
    JWKS_URL = os.environ.get(
        'JWKS_URL', 'https://your-api-domain/auth/.well-known/jwks.json')
    parsed = urlparse(JWKS_URL)
    try:
        logger.info(
            f"Verifying JWT token: {token[:10]}... (truncated)")
        jwks = get_jwks(JWKS_URL)
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
        logger.warning(f"JWT verification error: {e}", exc_info=True)
        return None


def lambda_handler(
    event: APIGatewayRequestAuthorizerEvent,
    context: LambdaContext
) -> APIGatewayAuthorizerResponse:
    logger.debug(f"Authorizer event: {event}")
    method_arn = event['methodArn']
    token = None
    # REST API: Authorization header
    if 'headers' in event and event['headers'].get('Authorization'):
        token = event['headers']['Authorization'].replace(
            "Bearer ", "").strip()
    # WebSocket API: token query param
    elif 'queryStringParameters' in event and event['queryStringParameters'] and event['queryStringParameters'].get('token'):
        token = event['queryStringParameters']['token']
    if not token:
        logger.error(
            f"Missing authorization header in request to {method_arn}")
        return {
            "principalId": "unauthorized",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": method_arn
                }]
            },
            "context": {}
        }

    try:
        claims = verify_jwt_token(token)
        if claims is None:
            logger.error("JWT verification failed: claims is None")
            return {
                "principalId": "unauthorized",
                "policyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Action": "execute-api:Invoke",
                        "Effect": "Deny",
                        "Resource": method_arn
                    }]
                },
                "context": {}
            }
        logger.info(f"Authenticated claims: {claims}")
        return {
            "principalId": claims['sub'],
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": method_arn
                }]
            },
            "context": {
                "email": claims.get("email"),
                "sub": claims.get("sub"),
                "name": claims.get("name"),
                "hd": claims.get("hd", None),
                "org_id": claims.get("org_id"),
                "org_name": claims.get("org_name"),
            }
        }
    except Exception as e:
        logger.error(f"Exception in lambda_handler: {e}")
        return {
            "principalId": "unauthorized",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": method_arn
                }]
            },
            "context": {}
        }

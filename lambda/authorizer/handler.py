import os
import time
import requests
import threading
from authlib.jose import JsonWebToken, JWTClaims
from typing import Optional, Literal, Any
from aws_lambda_typing.events import APIGatewayRequestAuthorizerEvent
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses.api_gateway_authorizer import APIGatewayAuthorizerResponse
from aws_lambda_typing.common import PolicyDocument
from EventCoord.utils.handler import get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)

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
    JWT_ISSUER = os.environ.get('JWT_ISSUER', 'https://your-api-domain')
    try:
        logger.info(
            f"Verifying JWT token: {token[:10]}... (truncated)")
        jwks = get_jwks(f"{JWT_ISSUER}/.well-known/jwks.json")
        logger.debug(f"JWKS keys: {jwks}")
        jwt_obj = JsonWebToken(['RS256'])
        logger.debug("About to decode JWT")
        claims = jwt_obj.decode(
            token,
            jwks,
            claims_options={
                "iss": {
                    "essential": True,
                    "value": JWT_ISSUER
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


def get_policy_document(
    effect: Literal["Allow", "Deny"],
    method_arn: str
) -> PolicyDocument:
    return {
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "execute-api:Invoke",
            "Effect": effect,
            "Resource": method_arn
        }]
    }


def build_response(
    principal_id: str,
    policy_document: PolicyDocument,
    context: Optional[Any] = None
) -> APIGatewayAuthorizerResponse:
    return {
        "principalId": principal_id,
        "policyDocument": policy_document,
        "context": context if context else {}
    }


def lambda_handler(
    event: APIGatewayRequestAuthorizerEvent,
    context: LambdaContext
) -> APIGatewayAuthorizerResponse:
    logger.debug(f"Authorizer event: {event}")
    logger.debug(f"Authorizer context: {context}")
    method_arn = event['methodArn']
    token = None
    # REST API: Authorization header
    if 'headers' in event and (event['headers'].get('authorization') or event['headers'].get('Authorization')):
        token = event['headers'].get(
            'authorization') or event['headers'].get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.replace("Bearer ", "").strip()
    # WebSocket API: token query param
    elif 'queryStringParameters' in event and event['queryStringParameters'] and event['queryStringParameters'].get('token'):
        token = event['queryStringParameters']['token']
    if not token:
        logger.error(
            f"Missing authorization header in request to {method_arn}")
        return build_response("unauthorized", get_policy_document('Deny', method_arn))
    logger.debug(f"Authorizer token: {token}")
    try:
        claims = verify_jwt_token(token)
        if claims is None:
            logger.error("JWT verification failed: claims is None")
            return build_response("unauthorized", get_policy_document('Deny', method_arn))
        logger.info(f"Authenticated claims: {claims}")
        return build_response(
            claims['sub'],
            get_policy_document('Allow', method_arn), {
                "email": claims.get("email"),
                "sub": claims.get("sub"),
                "name": claims.get("name"),
                "hd": claims.get("hd", None),
                "org_id": claims.get("org_id"),
                "org_name": claims.get("org_name"),
            }
        )
    except Exception as e:
        logger.error(f"Exception in lambda_handler: {e}")
        return build_response("unauthorized", get_policy_document('Deny', method_arn))

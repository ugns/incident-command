import os
import time
from typing import Any, Literal, Optional

from authlib.jose import JsonWebToken, JWTClaims
from aws_lambda_typing.common import PolicyDocument
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.events import APIGatewayRequestAuthorizerEvent
from aws_lambda_typing.responses.api_gateway_authorizer import APIGatewayAuthorizerResponse

from EventCoord.auth.jwks import JwksClient
from EventCoord.utils.handler import get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)

# One JwksClient instance per Lambda execution environment; the cache is
# shared across warm invocations (5-minute TTL matches the previous behaviour).
_jwks_client: Optional[JwksClient] = None


def _get_jwks_client() -> JwksClient:
    """Return (or lazily create) the module-level JwksClient."""
    global _jwks_client
    if _jwks_client is None:
        jwt_issuer = os.environ.get("JWT_ISSUER", "https://your-api-domain")
        jwks_url = f"{jwt_issuer}/.well-known/jwks.json"
        _jwks_client = JwksClient(jwks_url, cache_expiry=300)
    return _jwks_client


def verify_jwt_token(token: str) -> Optional[JWTClaims]:
    jwt_issuer = os.environ.get("JWT_ISSUER", "https://your-api-domain")
    try:
        logger.info("Verifying JWT token: %s… (truncated)", token[:10])
        jwks = _get_jwks_client().get_keys()
        jwt_obj = JsonWebToken(["RS256"])
        claims = jwt_obj.decode(
            token,
            jwks,
            claims_options={
                "iss": {
                    "essential": True,
                    "value": jwt_issuer,
                },
            },
        )
        claims.validate(now=int(time.time()), leeway=3)
        logger.debug("JWT payload: %s", claims)
        return claims
    except Exception as exc:
        logger.warning("JWT verification error: %s", exc, exc_info=True)
        return None


def get_policy_document(
    effect: Literal["Allow", "Deny"],
    method_arn: str,
) -> PolicyDocument:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": method_arn,
            }
        ],
    }


def build_response(
    principal_id: str,
    policy_document: PolicyDocument,
    context: Optional[Any] = None,
) -> APIGatewayAuthorizerResponse:
    return {
        "principalId": principal_id,
        "policyDocument": policy_document,
        "context": context if context else {},
    }


def lambda_handler(
    event: APIGatewayRequestAuthorizerEvent,
    context: LambdaContext,
) -> APIGatewayAuthorizerResponse:
    logger.debug("Authorizer event: %s", event)
    method_arn = event["methodArn"]
    token = None

    # REST API: Bearer token in Authorization header
    if "headers" in event and event["headers"]:
        auth_header = event["headers"].get("authorization") or event["headers"].get(
            "Authorization"
        )
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "", 1).strip()

    # WebSocket API: token query-string parameter
    if not token:
        qs = event.get("queryStringParameters") or {}
        token = qs.get("token")

    if not token:
        logger.error("Missing authorization token for %s", method_arn)
        return build_response("unauthorized", get_policy_document("Deny", method_arn))

    try:
        claims = verify_jwt_token(token)
        if claims is None:
            logger.error("JWT verification failed: claims is None")
            return build_response(
                "unauthorized", get_policy_document("Deny", method_arn)
            )
        logger.info("Authenticated claims: %s", claims)
        return build_response(
            claims["sub"],
            get_policy_document("Allow", method_arn),
            {
                "email": claims.get("email"),
                "sub": claims.get("sub"),
                "name": claims.get("name"),
                "hd": claims.get("hd", None),
                "org_id": claims.get("org_id"),
                "org_name": claims.get("org_name"),
            },
        )
    except Exception as exc:
        logger.error("Exception in authorizer lambda_handler: %s", exc)
        return build_response(
            "unauthorized", get_policy_document("Deny", method_arn)
        )

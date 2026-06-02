import os
from typing import Any, Literal, Optional

from aws_lambda_typing.common import PolicyDocument
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.events import APIGatewayRequestAuthorizerEvent
from aws_lambda_typing.responses.api_gateway_authorizer import (
    APIGatewayAuthorizerResponse,
)

from EventCoord.auth import TokenVerifier
from EventCoord.utils.handler import get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)

JWT_ISSUER = os.environ.get("JWT_ISSUER", "https://your-api-domain")

# One verifier per container: it caches JWKS internally (5 min) and refreshes on
# verification failure to handle key rotation.
VERIFIER = TokenVerifier(JWT_ISSUER)


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


def extract_token(event: APIGatewayRequestAuthorizerEvent) -> Optional[str]:
    """Pull the bearer token from a REST header or a WebSocket query param."""
    headers = event.get("headers") or {}
    auth_header = headers.get("authorization") or headers.get("Authorization")
    if auth_header:
        token = auth_header
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "").strip()
        return token
    query = event.get("queryStringParameters") or {}
    if query and query.get("token"):
        return query["token"]
    return None


def lambda_handler(
    event: APIGatewayRequestAuthorizerEvent,
    context: LambdaContext,
) -> APIGatewayAuthorizerResponse:
    method_arn = event["methodArn"]
    token = extract_token(event)
    if not token:
        logger.error(f"Missing authorization in request to {method_arn}")
        return build_response("unauthorized", get_policy_document("Deny", method_arn))

    try:
        identity = VERIFIER.verify_identity(token)
        if identity is None:
            logger.error("JWT verification failed")
            return build_response(
                "unauthorized", get_policy_document("Deny", method_arn)
            )
        logger.info(f"Authenticated principal: {identity.subject}")
        return build_response(
            identity.subject,
            get_policy_document("Allow", method_arn),
            {
                "email": identity.email,
                "sub": identity.subject,
                "name": identity.name,
                "hd": identity.hd,
                "org_id": identity.org_id,
                "org_name": identity.org_name,
            },
        )
    except Exception as e:
        logger.error(f"Exception in lambda_handler: {e}")
        return build_response("unauthorized", get_policy_document("Deny", method_arn))

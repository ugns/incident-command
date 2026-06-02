import json
import os

import boto3

from aws_lambda_typing.context import Context as LambdaContext

from EventCoord.auth import AudienceOrgResolver, TokenIssuer
from EventCoord.auth.providers import AuthProviderRegistry
from EventCoord.auth.providers.google import GoogleAuthProvider
from EventCoord.models.organizations import Organization
from EventCoord.utils.handler import get_logger, init_tracing
from EventCoord.utils.response import build_response
from EventCoord.utils.types import APIGatewayProxyEvent, APIGatewayProxyResponse

init_tracing()
logger = get_logger(__name__)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
}

PRIVATE_KEY_SECRET_ARN = os.environ.get("JWT_PRIVATE_KEY_SECRET_ARN")
JWT_ISSUER = os.environ.get("JWT_ISSUER", "event-coordinator-backend")
TOKEN_TTL = int(os.environ.get("TOKEN_TTL", "3600"))


def get_private_key() -> str:
    if not PRIVATE_KEY_SECRET_ARN:
        logger.error("JWT_PRIVATE_KEY_SECRET_ARN not set in environment")
        raise Exception("JWT_PRIVATE_KEY_SECRET_ARN not set")
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=PRIVATE_KEY_SECRET_ARN)
    return response["SecretString"]


def build_registry() -> AuthProviderRegistry:
    """Wire up the supported auth providers.

    Adding a new authentication method is as simple as implementing an
    ``AuthProvider`` and registering it here -- the rest of the handler is
    provider agnostic.
    """
    org_resolver = AudienceOrgResolver(Organization)
    reg = AuthProviderRegistry()
    reg.register(GoogleAuthProvider(org_resolver))
    # Future: reg.register(GithubAuthProvider(...)), reg.register(ApiKeyProvider(...)), etc.
    return reg


# Built once per Lambda container; providers themselves resolve their
# dependencies (org lookups, JWKS) lazily per request.
PROVIDERS = build_registry()
TOKEN_ISSUER = TokenIssuer(
    str(JWT_ISSUER), get_private_key, ttl_seconds=TOKEN_TTL
)


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext,
) -> APIGatewayProxyResponse:
    try:
        logger.info(f"Received event: {json.dumps(event)[:500]}... (truncated)")
        body = json.loads(event.get("body") or "{}")
        provider_name = body.get("provider", "google")
        token = body.get("token")
        logger.info(f"Provider: {provider_name}")

        if not token:
            logger.warning("Missing token in request body")
            return build_response(400, {"error": "Missing token"}, headers=cors_headers)

        provider = PROVIDERS.get(provider_name)
        if not provider:
            logger.warning(f"Unsupported provider: {provider_name}")
            return build_response(
                400,
                {"error": f"Unsupported provider: {provider_name}"},
                headers=cors_headers,
            )

        identity, error = provider.authenticate(token)
        if error or identity is None:
            message = error.to_body() if error else {"error": "Authentication failed"}
            status = error.status_code if error else 401
            logger.warning(f"Authentication error: {message}")
            return build_response(status, message, headers=cors_headers)

        jwt_token = TOKEN_ISSUER.issue(identity)
        user_response = identity.to_public_user()

        logger.info(f"Authentication successful for user: {user_response}")
        return build_response(
            200,
            {"token": jwt_token, "user": user_response},
            headers=cors_headers,
        )
    except Exception as e:
        logger.error(f"Exception in lambda_handler: {e}")
        return build_response(
            400,
            {"error": "Invalid request body", "details": str(e)},
            headers=cors_headers,
        )

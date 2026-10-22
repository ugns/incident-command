import copy
import json
import os
import time

import boto3
from authlib.jose import JsonWebKey, jwt
from aws_lambda_typing.context import Context as LambdaContext

from EventCoord.auth import AuthProviderRegistry
from EventCoord.auth.api_key import ApiKeyAuthProvider
from EventCoord.auth.google import GoogleAuthProvider
from EventCoord.auth.microsoft import MicrosoftAuthProvider
from EventCoord.utils.handler import CORS_HEADERS, get_logger, init_tracing
from EventCoord.utils.response import build_response
from EventCoord.utils.types import APIGatewayProxyEvent, APIGatewayProxyResponse

init_tracing()
logger = get_logger(__name__)

PRIVATE_KEY_SECRET_ARN = os.environ.get("JWT_PRIVATE_KEY_SECRET_ARN")
JWT_ISSUER = os.environ.get("JWT_ISSUER", "event-coordinator-backend")
TOKEN_TTL = int(os.environ.get("TOKEN_TTL", "3600"))

# Registry is built once per Lambda execution environment (cold start).
# Add or remove providers here; the handler requires no further changes.
PROVIDER_REGISTRY: AuthProviderRegistry = (
    AuthProviderRegistry()
    .register(GoogleAuthProvider())
    .register(MicrosoftAuthProvider())
    .register(ApiKeyAuthProvider())
)


def _get_private_key() -> str:
    if not PRIVATE_KEY_SECRET_ARN:
        raise RuntimeError("JWT_PRIVATE_KEY_SECRET_ARN is not set in environment")
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=PRIVATE_KEY_SECRET_ARN)
    return response["SecretString"]


def _issue_jwt(payload: dict) -> str:
    """Sign *payload* with the RS256 private key and return a JWT string."""
    private_key = _get_private_key()
    jwk = JsonWebKey.import_key(private_key, {"kty": "RSA"})
    jwk_dict = jwk.as_dict() if hasattr(jwk, "as_dict") else {}
    header: dict = {
        "alg": "RS256",
        "typ": "JWT",
        "jku": f"{JWT_ISSUER}/.well-known/jwks.json",
    }
    kid = jwk_dict.get("kid") if jwk_dict else None
    if kid:
        header["kid"] = kid
    return jwt.encode(header, payload, private_key).decode("utf-8")


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext,
) -> APIGatewayProxyResponse:
    try:
        logger.debug("Login event: %s", json.dumps(event)[:500])
        body = json.loads(event.get("body") or "{}")
        provider_name = body.get("provider", "google")
        token = body.get("token")

        if not token:
            logger.warning("Missing token in request body")
            return build_response(
                400, {"error": "Missing token"}, headers=CORS_HEADERS
            )

        logger.info("Authentication attempt via provider: %s", provider_name)
        result = PROVIDER_REGISTRY.authenticate(provider_name, token)

        if result.error:
            logger.warning("Authentication error: %s", result.error)
            return build_response(401, result.error, headers=CORS_HEADERS)

        user_info = result.user_info  # guaranteed non-None when error is None
        if not user_info:
            logger.error("user_info is None after successful authenticate() call")
            return build_response(
                401, {"error": "Authentication failed"}, headers=CORS_HEADERS
            )

        payload = copy.deepcopy(user_info)
        payload["iss"] = str(JWT_ISSUER)
        payload["exp"] = int(time.time()) + TOKEN_TTL

        jwt_token = _issue_jwt(payload)

        user_response = {
            k: v
            for k, v in user_info.items()
            if k not in ("sub", "provider", "raw")
        }
        logger.info("Authentication successful for user: %s", user_response)

        # TODO: Create or update volunteer record on first login
        # Volunteer.get_or_create_by_email(
        #     org_id=user_response.get("org_id"),
        #     email=user_response.get("email"),
        #     defaults=user_response,
        # )

        return build_response(
            200,
            {"token": jwt_token, "user": user_response},
            headers=CORS_HEADERS,
        )
    except Exception as exc:
        logger.error("Exception in login lambda_handler: %s", exc)
        return build_response(
            400,
            {"error": "Invalid request body", "details": str(exc)},
            headers=CORS_HEADERS,
        )

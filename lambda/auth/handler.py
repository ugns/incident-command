import os
import json
import time
import copy
import logging
import boto3
from authlib.jose import jwt, JsonWebKey
from typing import Protocol, Tuple, Optional, Dict, Any
from googleAuthProvider import GoogleAuthProvider
from EventCoord.models.volunteers import Volunteer
from EventCoord.utils.response import build_response

# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS"
}

# Use RSA private key from AWS Secrets Manager
PRIVATE_KEY_SECRET_ARN = os.environ.get('JWT_PRIVATE_KEY_SECRET_ARN')
JWT_ISSUER = os.environ.get('JWT_ISSUER', 'event-coordinator-backend')
TOKEN_TTL = int(os.environ.get('TOKEN_TTL', '3600'))


def get_private_key():
    if not PRIVATE_KEY_SECRET_ARN:
        logger.error("JWT_PRIVATE_KEY_SECRET_ARN not set in environment")
        raise Exception("JWT_PRIVATE_KEY_SECRET_ARN not set")
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=PRIVATE_KEY_SECRET_ARN)
    return response['SecretString']


class AuthProvider(Protocol):
    def authenticate(self, token: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        ...


PROVIDERS: Dict[str, AuthProvider] = {
    "google": GoogleAuthProvider(),
    # Future: "github": GithubAuthProvider(), etc.
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        logger.info(
            f"Received event: {json.dumps(event)[:500]}... (truncated)")
        logger.debug(f"Event details: {json.dumps(event)}")
        body = json.loads(event.get('body', '{}'))
        provider_name = body.get('provider', 'google')
        token = body.get('token')
        logger.info(f"Provider: {provider_name}")
        if not token:
            logger.warning("Missing token in request body")
            return build_response(400, {"error": "Missing token"}, headers=cors_headers)
        provider: Optional[AuthProvider] = PROVIDERS.get(provider_name)
        if not provider:
            logger.warning(f"Unsupported provider: {provider_name}")
            return build_response(400, {"error": f"Unsupported provider: {provider_name}"}, headers=cors_headers)
        user_info, error = provider.authenticate(token)
        if error:
            logger.warning(f"Authentication error: {error}")
            return build_response(401, error, headers=cors_headers)
        # Copy user_info and add JWT claims
        payload = copy.deepcopy(user_info) if user_info else {}
        payload['iss'] = str(JWT_ISSUER)
        payload['exp'] = int(time.time()) + TOKEN_TTL
        private_key = get_private_key()
        # Generate kid from the private key so it matches the JWKS
        jwk = JsonWebKey.import_key(private_key, {"kty": "RSA"})
        jwk_dict = jwk.as_dict() if hasattr(jwk, "as_dict") else None
        key_id = jwk_dict.get("kid") if jwk_dict else None
        header = {"alg": "RS256", "typ": "JWT"}
        header["jku"] = f"{JWT_ISSUER}/.well-known/jwks.json"
        if key_id:
            header["kid"] = key_id
        jwt_token = jwt.encode(header, payload, private_key).decode("utf-8")
        # Return user info (excluding sub, iss, provider, raw)
        user_response = {k: v for k, v in user_info.items() if k not in (
            'sub', 'provider', 'raw')} if user_info else {}
        logger.info(f"Authentication successful for user: {user_response}")
        volunteer = Volunteer.get_or_create_by_email(
            org_id=user_response.get("org_id"),
            email=user_response.get("email"),
            defaults=user_response
        )
        return build_response(200, {"token": jwt_token, "user": user_response}, headers=cors_headers)
    except Exception as e:
        logger.error(f"Exception in lambda_handler: {e}")
        return build_response(400, {"error": "Invalid request body", "details": str(e)}, headers=cors_headers)

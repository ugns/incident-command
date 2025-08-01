import os
import json
import time
import copy
import logging
from jose import jwt
from typing import Protocol, Tuple, Optional, Dict, Any
from googleAuthProvider import GoogleAuthProvider
from models.volunteers import Volunteer
from utils.response import build_response

# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS"
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

JWT_SECRET = os.environ.get('JWT_SECRET', 'changeme')
TOKEN_TTL = int(os.environ.get('TOKEN_TTL', '3600'))


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
        payload['iss'] = 'incident-cmd-backend'
        payload['exp'] = int(time.time()) + TOKEN_TTL
        jwt_token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
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

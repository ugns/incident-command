import os
import json
import requests
import time
import copy
from jose import jwt
from typing import Protocol, Tuple, Optional, Dict, Any
from organizations.model import Organization
from typing import Any, Dict

JWT_SECRET = os.environ.get('JWT_SECRET', 'changeme')
TOKEN_TTL = int(os.environ.get('TOKEN_TTL', '3600'))

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS"
}


def build_response(status_code: int, body: Any) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(body)
    }


class AuthProvider(Protocol):
    def authenticate(self, token: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        ...


class GoogleAuthProvider:
    def authenticate(self, token: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        try:
            resp = requests.get(
                f'https://oauth2.googleapis.com/tokeninfo?id_token={token}')
            if resp.status_code != 200:
                return None, {"error": "Invalid Google token"}
            token_info = resp.json()
            # Lookup organization by aud
            org = Organization.get_by_aud(token_info.get('aud'))
            if not org:
                return None, {"error": "No organization found for this audience (aud)"}
            # Standardize user info
            user_info = {
                'email': token_info.get('email'),
                'name': token_info.get('name'),
                'org_id': org.get('org_id'),
                'org_name': org.get('name'),
                'sub': token_info.get('sub'),
                'provider': 'google',
                'raw': token_info
            }
            return user_info, None
        except Exception:
            return None, {"error": "Token validation failed"}


PROVIDERS: Dict[str, AuthProvider] = {
    "google": GoogleAuthProvider(),
    # Future: "github": GithubAuthProvider(), etc.
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        body = json.loads(event.get('body', '{}'))
        provider_name = body.get('provider', 'google')
        token = body.get('token')
        if not token:
            return build_response(400, {"error": "Missing token"})
        provider: Optional[AuthProvider] = PROVIDERS.get(provider_name)
        if not provider:
            return build_response(400, {"error": f"Unsupported provider: {provider_name}"})
        user_info, error = provider.authenticate(token)
        if error:
            return build_response(401, error)
        # Copy user_info and add JWT claims
        payload = copy.deepcopy(user_info) if user_info else {}
        payload['iss'] = 'incident-cmd-backend'
        payload['exp'] = int(time.time()) + TOKEN_TTL
        jwt_token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        # Return user info (excluding sub, iss, provider, raw)
        user_response = {k: v for k, v in user_info.items() if k not in (
            'sub', 'provider', 'raw')} if user_info else {}
        return build_response(200, {"token": jwt_token, "user": user_response})
    except Exception as e:
        return build_response(400, {"error": "Invalid request body", "details": str(e)})

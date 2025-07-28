import os
import json
import requests
import ldclient
from ldclient.context import Context
from ldclient.config import Config
from jose import jwt
from typing import Protocol, Tuple, Optional, Dict, Any

ldclient.set_config(Config(os.environ.get(
    'LAUNCHDARKLY_SDK_KEY', '')))  # SDK key from env
ld_client = ldclient.get()


def has_admin_access(user):
    if not ld_client or not ld_client.is_initialized():
        return False

    user_ctx = Context.builder(user.get("email") or user.get("sub")) \
        .kind('user') \
        .set('email', user.get("email")) \
        .build()
    org_ctx = Context.builder(user.get("org_id")) \
        .kind('organization') \
        .set('org_id', user.get("org_id")) \
        .build()
    multi_ctx = Context.builder('multi') \
        .kind('multi') \
        .set('user', user_ctx) \
        .set('organization', org_ctx) \
        .build()
    ld_client.track('auth.callback', multi_ctx)
    return ld_client.variation("admin-access", multi_ctx, False)


cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS"
}


ALLOWED_CLIENT_IDS = set(os.environ.get('GOOGLE_CLIENT_IDS', '').split(','))
JWT_SECRET = os.environ.get('JWT_SECRET', 'changeme')
TOKEN_TTL = int(os.environ.get('TOKEN_TTL', '3600'))


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
            if token_info.get('aud') not in ALLOWED_CLIENT_IDS:
                return None, {"error": "Token audience not allowed"}
            # Standardize user info
            user_info = {
                'email': token_info.get('email'),
                'name': token_info.get('name'),
                'org_id': token_info.get('hd'),
                'hd': token_info.get('hd'),
                'sub': token_info.get('sub'),
                'provider': 'google',
                'raw': token_info
            }
            user_info['is_admin'] = has_admin_access(user_info)
            return user_info, None
        except Exception:
            return None, {"error": "Token validation failed"}


PROVIDERS: Dict[str, AuthProvider] = {
    "google": GoogleAuthProvider(),
    # Future: "github": GithubAuthProvider(), etc.
}


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        provider_name = body.get('provider', 'google')
        token = body.get('token')
        if not token:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({"error": "Missing token"})
            }
        provider: Optional[AuthProvider] = PROVIDERS.get(provider_name)
        if not provider:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({"error": f"Unsupported provider: {provider_name}"})
            }
        user_info, error = provider.authenticate(token)
        if error:
            return {
                "statusCode": 401,
                "headers": cors_headers,
                "body": json.dumps(error)
            }
        # Issue our own JWT for session
        import time
        payload = {
            'email': user_info['email'],
            'name': user_info['name'],
            'sub': user_info['sub'],
            'iss': 'incident-cmd-backend',
            'org_id': user_info.get('org_id'),
            'hd': user_info.get('hd'),
            'is_admin': user_info['is_admin'],
            # expires in TOKEN_TTL seconds
            'exp': int(time.time()) + TOKEN_TTL,
        } if user_info else {}
        jwt_token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        # Return user info (excluding sub, iss, provider, raw)
        user_response = {k: v for k, v in user_info.items(
        ) if k not in ('sub', 'provider', 'raw')} if user_info else {}
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({
                "token": jwt_token,
                "user": user_response
            })
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": cors_headers,
            "body": json.dumps({"error": "Invalid request body", "details": str(e)})
        }

import os
import ldclient
from ldclient.context import Context
from ldclient.config import Config
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError

ldclient.set_config(Config(os.environ.get(
    'LAUNCHDARKLY_SDK_KEY', '')))  # SDK key from env
ld_client = ldclient.get()


def has_admin_access(user):
    if not ld_client.is_initialized():
        return False

    # user should have at least 'key' (email or sub)
    user_context = (
        Context.builder(user.get("email") or user.get("sub"))
        .kind('user')
        .set('email', user.get("email"))
        .set('org_id', user.get("org_id"))
        .build()
    )
    org_context = (
        Context.builder(user.get("org_id") or user.get("hd"))
        .kind('organization')
        .set('org_id', user.get("org_id"))
        .build()
    )
    ld_client.track('client.auth', user_context)
    ld_client.track('client.auth', org_context)
    return ld_client.variation("admin-access", user_context, False)


def get_jwt_secret():
    return os.environ.get('JWT_SECRET', 'changeme')


def verify_jwt_token(token):
    import time
    secret = get_jwt_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        # Manual expiration check for tokens missing 'exp' or with expired 'exp'
        if 'exp' not in payload or payload['exp'] < int(time.time()):
            return None
        return payload
    except ExpiredSignatureError:
        # Token expired, treat as logged out
        return None
    except JWTError:
        return None


def require_auth(event):
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ', 1)[1]
    payload = verify_jwt_token(token)
    return payload


def check_auth(event):
    user = require_auth(event)
    if not user:
        return {
            "statusCode": 401,
            "body": "Unauthorized"
        }
    user['is_admin'] = has_admin_access(user)
    return user

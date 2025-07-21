import os
import json
from jose import jwt, JWTError
import requests


def get_jwt_secret():
    return os.environ.get('JWT_SECRET', 'changeme')


def verify_jwt_token(token):
    secret = get_jwt_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
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
    return user

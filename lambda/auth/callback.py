import os
import json
import requests
from jose import jwt
from urllib.parse import parse_qs


cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS"
}

# RBAC: Comma-separated admin emails from environment variable
ADMIN_EMAILS = set(email.strip() for email in os.environ.get('ADMIN_EMAILS', '').split(',') if email.strip())
ALLOWED_CLIENT_IDS = set(os.environ.get('GOOGLE_CLIENT_IDS', '').split(','))


def lambda_handler(event, context):
    # Get Google token from request (assume POST with JSON body)
    try:
        body = json.loads(event.get('body', '{}'))
        google_token = body.get('token')
        if not google_token:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({"error": "Missing token"})
            }
    except Exception:
        return {
            "statusCode": 400,
            "headers": cors_headers,
            "body": json.dumps({"error": "Invalid request body"})
        }

    # Validate Google token
    try:
        resp = requests.get(
            f'https://oauth2.googleapis.com/tokeninfo?id_token={google_token}')
        if resp.status_code != 200:
            return {
                "statusCode": 401,
                "headers": cors_headers,
                "body": json.dumps({"error": "Invalid Google token"})
            }
        token_info = resp.json()
        if token_info.get('aud') not in ALLOWED_CLIENT_IDS:
            return {
                "statusCode": 401,
                "headers": cors_headers,
                "body": json.dumps({"error": "Token audience not allowed"})
            }
    except Exception:
        return {
            "statusCode": 401,
            "headers": cors_headers,
            "body": json.dumps({"error": "Token validation failed"})
        }

    # Issue our own JWT for session
    user_email = token_info.get('email')
    user_name = token_info.get('name')
    org_id = token_info.get('hd')
    is_admin = user_email in ADMIN_EMAILS
    payload = {
        'email': user_email,
        'name': user_name,
        'sub': token_info.get('sub'),
        'iss': 'incident-cmd-backend',
        'hd': org_id,
        'is_admin': is_admin,
    }
    secret = os.environ.get('JWT_SECRET', 'changeme')
    jwt_token = jwt.encode(payload, secret, algorithm='HS256')

    return {
        "statusCode": 200,
        "headers": cors_headers,
        "body": json.dumps({
            "token": jwt_token,
            "user": {
                "email": user_email,
                "name": user_name,
                "org_id": org_id,
                "is_admin": is_admin
            }
        })
    }

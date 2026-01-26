import json
from authlib.jose import JWTClaims
from jose import jwt
from aws_lambda_typing.responses import APIGatewayProxyResponse
from aws_lambda_typing.events import APIGatewayProxyEvent
from typing import Dict, Any, Optional

def build_response(
    status_code: int,
    body,
    headers=None
) -> APIGatewayProxyResponse:
    return {
        'statusCode': status_code,
        'headers': headers or {},
        'body': json.dumps(body)
    }

def decode_claims(
    event: APIGatewayProxyEvent
) -> Optional[JWTClaims | Dict[str, Any]]:
    """
    Decode API Gateway Proxy Event to collect JWT and return claims
    """
    token = None
    if 'headers' in event and (event['headers'].get('authorization') or event['headers'].get('Authorization')):
        token = event['headers'].get(
            'authorization') or event['headers'].get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.replace("Bearer ", "").strip()
    if token:
        # Use empty string as key for unsigned JWTs and pass claims_cls and claims_options
        payload = jwt.get_unverified_claims(token)
        return payload
    return None

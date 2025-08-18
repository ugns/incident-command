import json
from authlib.jose import jwt, JWTClaims
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from aws_lambda_typing.events import APIGatewayProxyEventV2
from typing import Optional

def build_response(
    status_code: int,
    body,
    headers=None
) -> APIGatewayProxyResponseV2:
    return {
        'statusCode': status_code,
        'headers': headers or {},
        'body': json.dumps(body)
    }

def decode_claims(
    event: APIGatewayProxyEventV2
) -> Optional[JWTClaims]:
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
        payload = jwt.decode(token, '', claims_cls=JWTClaims, claims_options={"verify_signature": False})
        return payload
    return None

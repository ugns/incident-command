import json
from aws_lambda_typing.responses import APIGatewayProxyResponseV2


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

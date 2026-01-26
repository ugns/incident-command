from typing import Any, Dict

try:
    from aws_lambda_typing.events import APIGatewayProxyEventV1  # type: ignore
    from aws_lambda_typing.responses import APIGatewayProxyResponseV1  # type: ignore

    APIGatewayProxyEvent = APIGatewayProxyEventV1
    APIGatewayProxyResponse = APIGatewayProxyResponseV1
except Exception:
    APIGatewayProxyEvent = Dict[str, Any]
    APIGatewayProxyResponse = Dict[str, Any]

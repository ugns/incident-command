from typing import Any, Dict, TypeAlias

try:
    from aws_lambda_typing.events import APIGatewayProxyEventV1  # type: ignore
    from aws_lambda_typing.responses import APIGatewayProxyResponseV1  # type: ignore

    APIGatewayProxyEvent: TypeAlias = APIGatewayProxyEventV1
    APIGatewayProxyResponse: TypeAlias = APIGatewayProxyResponseV1
except Exception:
    APIGatewayProxyEvent: TypeAlias = Dict[str, Any]
    APIGatewayProxyResponse: TypeAlias = Dict[str, Any]

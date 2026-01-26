import os
import boto3
import json
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.utils.response import build_response
from EventCoord.utils.handler import get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,OPTIONS"
}


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext
) -> APIGatewayProxyResponse:
    requestContext = event.get('requestContext', {})
    rest_api_id = requestContext.get('apiId')
    stage_name = requestContext.get('stage')
    client = boto3.client('apigateway')
    try:
        response = client.get_export(
            restApiId=rest_api_id,
            stageName=stage_name,
            exportType='oas30',
            parameters={'extensions': 'apigateway'},
            accepts='application/json'
        )
        spec = response['body'].read()
        spec_json = json.loads(spec.decode('utf-8'))
        return build_response(
            200,
            spec_json,
            {
                **cors_headers,
                'Content-Type': 'application/json'
            }
        )
    except Exception as e:
        logger.exception("Failed to export OpenAPI spec")
        return build_response(
            500,
            str(e),
            {
                **cors_headers,
                'Content-Type': 'text/plain'
            }
        )

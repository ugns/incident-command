import os
import boto3
import json
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from EventCoord.utils.response import build_response
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()  # Automatically patches boto3, requests, etc.

xray_recorder.configure(service='incident-cmd')

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,OPTIONS"
}


def lambda_handler(
    event: APIGatewayProxyEventV2,
    context: LambdaContext
) -> APIGatewayProxyResponseV2:
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
        return build_response(
            500,
            str(e),
            {
                **cors_headers,
                'Content-Type': 'text/plain'
            }
        )

import os
import boto3
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from EventCoord.utils.response import build_response


def lambda_handler(
    event: APIGatewayProxyEventV2,
    context: LambdaContext
) -> APIGatewayProxyResponseV2:
    rest_api_id = os.environ['REST_API_ID']
    stage_name = os.environ['STAGE_NAME']
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
        return build_response(
            200,
            spec.decode('utf-8'),
            {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except Exception as e:
        return build_response(
            500,
            str(e),
            {
                'Content-Type': 'text/plain',
                'Access-Control-Allow-Origin': '*'
            }
        )

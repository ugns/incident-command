import os
import boto3

def lambda_handler(event, context):
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
        return {
            'statusCode': 200,
            'body': spec.decode('utf-8'),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e),
            'headers': {
                'Content-Type': 'text/plain',
                'Access-Control-Allow-Origin': '*'
            }
        }

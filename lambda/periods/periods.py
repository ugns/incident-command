import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from client.auth import check_auth
from typing import Any, Dict

dynamodb = boto3.resource('dynamodb')
table: Any = dynamodb.Table(os.environ.get(  # type: ignore
    'ICS_PERIODS_TABLE', 'periods'))
cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    claims = check_auth(event)
    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    period_id = path_params.get('periodId') if path_params else None

    if method == 'GET':
        if period_id:
            # Get period metadata
            resp = table.get_item(
                Key={'org_id': claims.get('hd'), 'periodId': period_id})
            period = resp.get('Item')
            if not period:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'Period not found'})
                }
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps(period)
            }
        else:
            # List all ICS-214 periods
            resp = table.query(KeyConditionExpression=Key(
                'org_id').eq(claims.get('hd')))
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps(resp.get('Items', []))
            }

    elif method == 'POST':
        # Create a new ICS-214 period
        import uuid
        from datetime import datetime, timezone
        body = json.loads(event.get('body', '{}'))
        if 'periodId' not in body:
            body['periodId'] = str(uuid.uuid4())
        if 'startTime' not in body or not body['startTime']:
            # Set startTime in UTC ISO 8601 format with 'Z' suffix
            body['startTime'] = datetime.now(
                timezone.utc).isoformat().replace('+00:00', 'Z')
        body['org_id'] = claims.get('hd')
        table.put_item(Item=body)
        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps({'message': 'ICS-214 period created', 'id': body['periodId']})
        }

    elif method == 'PUT':
        # Update an existing ICS-214 period
        if not period_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing ICS-214 period id in path'})
            }
        from datetime import datetime
        body = json.loads(event.get('body', '{}'))
        body['periodId'] = period_id
        if 'startTime' not in body or not body['startTime']:
            body['startTime'] = datetime.now().isoformat()
        body['org_id'] = claims.get('hd')
        table.put_item(Item=body)
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'ICS-214 period updated', 'id': period_id})
        }

    elif method == 'DELETE':
        # RBAC: Only allow admin users to delete
        if not period_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing ICS-214 period id in path'})
            }
        if not claims.get('is_admin'):
            return {
                'statusCode': 403,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Admin privileges required for delete'})
            }
        table.delete_item(
            Key={'org_id': claims.get('hd'), 'periodId': period_id})
        return {
            'statusCode': 204,
            'headers': cors_headers,
            'body': ''
        }

    else:
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }

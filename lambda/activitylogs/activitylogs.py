import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from client.auth import check_auth
from typing import Any, Dict

dynamodb = boto3.resource('dynamodb')
table: Any = dynamodb.Table(os.environ.get('ACTIVITY_LOGS_TABLE', 'activity_logs'))  # type: ignore
cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    claims = check_auth(event)
    org_id = claims.get('hd')
    if not org_id:
        return {
            'statusCode': 403,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Missing organization (hd claim) in token'})
        }
    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    log_id = path_params.get('logId') if path_params else None
    volunteer_id = path_params.get('volunteerId') if path_params else None

    if method == 'GET':
        if log_id:
            # Get a single activity log
            resp = table.get_item(Key={'org_id': org_id, 'logId': log_id})
            item = resp.get('Item')
            if not item:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'Activity log not found'})
                }
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps(item)
            }
        elif volunteer_id:
            # List all activity logs for a volunteer in this org (GSI)
            resp = table.query(
                IndexName='VolunteerIdIndex',
                KeyConditionExpression=Key('org_id').eq(
                    org_id) & Key('volunteerId').eq(volunteer_id)
            )
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps(resp.get('Items', []))
            }
        else:
            # List all activity logs for this org
            resp = table.query(KeyConditionExpression=Key('org_id').eq(org_id))
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps(resp.get('Items', []))
            }

    elif method == 'POST':
        # Create a new activity log
        import uuid
        from datetime import datetime, timezone
        body = json.loads(event.get('body', '{}'))
        if 'logId' not in body:
            body['logId'] = str(uuid.uuid4())
        if 'periodId' not in body or not body['periodId']:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing required field: periodId'})
            }
        if 'timestamp' not in body or not body['timestamp']:
            body['timestamp'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        body['org_id'] = org_id
        table.put_item(Item=body)
        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Activity log created', 'id': body['logId']})
        }

    elif method == 'PUT':
        # Update an existing activity log
        if not log_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing activity log id in path'})
            }
        from datetime import datetime, timezone
        body = json.loads(event.get('body', '{}'))
        body['logId'] = log_id
        if 'periodId' not in body or not body['periodId']:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing required field: periodId'})
            }
        if 'timestamp' not in body or not body['timestamp']:
            body['timestamp'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        body['org_id'] = org_id
        table.put_item(Item=body)
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Activity log updated', 'id': log_id})
        }

    elif method == 'DELETE':
        # RBAC: Only allow admin users to delete
        if not log_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing activity log id in path'})
            }
        if not claims.get('is_admin'):
            return {
                'statusCode': 403,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Admin privileges required for delete'})
            }
        table.delete_item(Key={'org_id': org_id, 'logId': log_id})
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

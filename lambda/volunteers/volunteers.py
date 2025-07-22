import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from client.auth import check_auth
from typing import Any, Dict

dynamodb = boto3.resource('dynamodb')
table: Any = dynamodb.Table(os.environ.get('VOLUNTEERS_TABLE', 'volunteers'))  # type: ignore
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
    volunteer_id = path_params.get('volunteerId') if path_params else None

    if method == 'GET':
        if volunteer_id:
            # Get a single volunteer
            resp = table.get_item(
                Key={'org_id': org_id, 'volunteerId': volunteer_id})
            item = resp.get('Item')
            if not item:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'Volunteer not found'})
                }
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps(item)
            }
        else:
            # List all volunteers for this org
            resp = table.query(KeyConditionExpression=Key('org_id').eq(org_id))
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps(resp.get('Items', []))
            }

    elif method == 'POST':
        # Only allow POST to /volunteers (no volunteerId in path)
        if volunteer_id:
            return {
                'statusCode': 405,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Method not allowed: use PUT to update volunteer'})
            }
        import uuid
        body = json.loads(event.get('body', '{}'))
        if 'volunteerId' not in body:
            body['volunteerId'] = str(uuid.uuid4())
        body['org_id'] = org_id
        table.put_item(Item=body)
        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Volunteer created', 'id': body['volunteerId']})
        }

    elif method == 'PUT':
        # Update an existing volunteer
        if not volunteer_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing volunteer id in path'})
            }
        body = json.loads(event.get('body', '{}'))
        body['volunteerId'] = volunteer_id
        body['org_id'] = org_id
        table.put_item(Item=body)
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Volunteer updated', 'id': volunteer_id})
        }

    elif method == 'DELETE':
        # RBAC: Only allow admin users to delete
        if not volunteer_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing volunteer id in path'})
            }
        if not claims.get('is_admin'):
            return {
                'statusCode': 403,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Admin privileges required for delete'})
            }
        table.delete_item(Key={'org_id': org_id, 'volunteerId': volunteer_id})
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

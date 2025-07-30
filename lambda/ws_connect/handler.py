import os
import boto3
from client.auth import require_auth
from typing import Any

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('WS_CONNECTIONS_TABLE', 'WebSocketConnections')
table: Any = dynamodb.Table(TABLE_NAME)  # type: ignore


def lambda_handler(event, context):
    # API Gateway WebSocket $connect event
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization')
    if not auth_header:
        return {"statusCode": 401, "body": "Missing Authorization header"}
    user = require_auth(event)
    if not user:
        return {"statusCode": 401, "body": "Unauthorized"}
    connection_id = event['requestContext']['connectionId']
    org_id = user.get('org_id')
    user_id = user.get('user_id')
    # Store connection info
    item = {
        'connectionId': connection_id,
        'orgId': org_id,
        'userId': user_id,
        'subscriptions': [],
    }
    table.put_item(Item=item)
    return {"statusCode": 200, "body": "Connected"}

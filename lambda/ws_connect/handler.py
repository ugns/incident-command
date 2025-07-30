import os
import boto3
from client.auth import require_auth
from typing import Any

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('WS_CONNECTIONS_TABLE', 'WebSocketConnections')
table: Any = dynamodb.Table(TABLE_NAME)  # type: ignore


def lambda_handler(event, context):
    # API Gateway WebSocket $connect event
    params = event.get('queryStringParameters') or {}
    token = params.get('token')
    if not token:
        return {"statusCode": 401, "body": "Missing token in query string"}
    # Use shared require_auth, passing the token as if it were an Authorization header
    fake_event = {'headers': {'Authorization': f'Bearer {token}'}}
    user = require_auth(fake_event)
    if not user:
        return {"statusCode": 401, "body": "Unauthorized"}
    connection_id = event['requestContext']['connectionId']
    org_id = user.get('org_id')
    # Use sub or email as user identifier
    user_identifier = user.get('sub') or user.get('email')
    if not user_identifier:
        return {"statusCode": 400, "body": "Token missing sub or email"}
    # Store connection info
    item = {
        'connectionId': connection_id,
        'orgId': org_id,
        'user': user_identifier,
        'subscriptions': [],
    }
    table.put_item(Item=item)
    return {"statusCode": 200, "body": "Connected"}

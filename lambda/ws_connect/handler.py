import os
import boto3
import logging
from client.auth import require_auth
from typing import Any


# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('WS_CONNECTIONS_TABLE', 'WebSocketConnections')
table: Any = dynamodb.Table(TABLE_NAME)  # type: ignore


def lambda_handler(event, context):
    logger.info(f"Received $connect event: {event}")
    params = event.get('queryStringParameters') or {}
    token = params.get('token')
    if not token:
        logger.warning("Missing token in query string")
        return {"statusCode": 401, "body": "Missing token in query string"}
    fake_event = {'headers': {'Authorization': f'Bearer {token}'}}
    user = require_auth(fake_event)
    if not user:
        logger.warning("Unauthorized: token did not resolve to user")
        return {"statusCode": 401, "body": "Unauthorized"}
    connection_id = event['requestContext']['connectionId']
    org_id = user.get('org_id')
    user_identifier = user.get('sub') or user.get('email')
    if not user_identifier:
        logger.error("Token missing sub or email")
        return {"statusCode": 400, "body": "Token missing sub or email"}
    item = {
        'connectionId': connection_id,
        'orgId': org_id,
        'user': user_identifier,
        'subscriptions': [],
    }
    try:
        table.put_item(Item=item)
        logger.info(f"Stored connection: {item}")
    except Exception as e:
        logger.error(f"Error storing connection: {e}")
        return {"statusCode": 500, "body": "Failed to store connection"}
    return {"statusCode": 200, "body": "Connected"}

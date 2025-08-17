import os
import boto3
import logging
from aws_lambda_typing.events import WebSocketConnectEvent, APIGatewayProxyEventV2
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.client.auth import require_auth
from typing import Any
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()  # Automatically patches boto3, requests, etc.

xray_recorder.configure(service='incident-cmd')

# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logging.getLogger().setLevel(LOG_LEVEL)
logging.getLogger("EventCoord.client.auth").setLevel(LOG_LEVEL)

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('WS_CONNECTIONS_TABLE', 'WebSocketConnections')
table: Any = dynamodb.Table(TABLE_NAME)  # type: ignore


def lambda_handler(
    event: WebSocketConnectEvent,
    context: LambdaContext
) -> dict[str, str | int]:
    logger.info(f"Received $connect event: {event}")
    claims = event.get('requestContext', {}).get('authorizer', {})
    org_id = claims.get('org_id')
    user_id = claims.get('sub') or claims.get('email')
    if not org_id or not user_id:
        logger.error("Missing org_id or user_id in authorizer context")
        return {"statusCode": 401, "body": "Unauthorized"}
    connection_id = event['requestContext']['connectionId']
    item = {
        'connectionId': connection_id,
        'orgId': org_id,
        'user': user_id,
        'subscriptions': [],
    }
    try:
        table.put_item(Item=item)
        logger.info(f"Stored connection: {item}")
    except Exception as e:
        logger.error(f"Error storing connection: {e}")
        return {"statusCode": 500, "body": "Failed to store connection"}
    return {"statusCode": 200, "body": "Connected"}

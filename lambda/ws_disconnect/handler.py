import os
import boto3
import logging
from aws_lambda_typing.events import WebSocketConnectEvent
from aws_lambda_typing.context import Context as LambdaContext
from boto3.dynamodb.conditions import Key
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

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('WS_CONNECTIONS_TABLE', 'WebSocketConnections')
table: Any = dynamodb.Table(TABLE_NAME)  # type: ignore


def lambda_handler(
    event: WebSocketConnectEvent,
    context: LambdaContext
) -> dict[str, str | int]:
    logger.info(f"Received $disconnect event: {event}")
    connection_id = event['requestContext']['connectionId']
    try:
        resp = table.query(
            IndexName="ConnectionIdIndex",
            KeyConditionExpression=Key('connectionId').eq(connection_id)
        )
        items = resp.get('Items', [])
        if not items:
            logger.warning(f"No connection found for connectionId={connection_id}")
            return {"statusCode": 404, "body": "Connection not found"}
        org_id = items[0]['orgId']
        table.delete_item(Key={'orgId': org_id, 'connectionId': connection_id})
        logger.info(f"Deleted connection: orgId={org_id}, connectionId={connection_id}")
        return {"statusCode": 200, "body": "Disconnected"}
    except Exception as e:
        logger.error(f"Error disconnecting connectionId={connection_id}: {e}")
        return {"statusCode": 500, "body": "Failed to disconnect"}

import os
import boto3
import logging
from aws_lambda_typing.events import WebSocketConnectEvent
from aws_lambda_typing.context import Context as LambdaContext
from typing import Any


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
    org_id = event['requestContext'].get('authorizer', {}).get('org_id')
    if not org_id:
        logger.warning(
            "org_id not found in authorizer, attempting fallback lookup")
        resp = table.get_item(
            Key={'orgId': org_id, 'connectionId': connection_id})
        item = resp.get('Item')
        if not item:
            logger.error(
                f"Connection {connection_id} not found for disconnect")
            return {"statusCode": 404, "body": "Connection not found"}
        org_id = item['orgId']
    try:
        table.delete_item(Key={'orgId': org_id, 'connectionId': connection_id})
        logger.info(
            f"Deleted connection: orgId={org_id}, connectionId={connection_id}")
    except Exception as e:
        logger.error(f"Error deleting connection: {e}")
        return {"statusCode": 500, "body": "Failed to disconnect"}
    return {"statusCode": 200, "body": "Disconnected"}

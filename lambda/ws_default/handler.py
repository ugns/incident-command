import json
import os
import logging
from aws_lambda_typing.events import WebSocketRouteEvent
from aws_lambda_typing.context import Context as LambdaContext
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


def lambda_handler(
    event: WebSocketRouteEvent,
    context: LambdaContext
) -> dict[str, str | int]:
    logger.info(f"Received ws_default event: {event}")
    body = event.get('body')
    try:
        message = json.loads(body) if body else {}
        logger.debug(f"Parsed message: {message}")
    except Exception as e:
        logger.error(f"Error parsing message body: {e}")
        message = {}
    action = message.get('action')
    if action == 'ping':
        logger.info("Received ping, responding with pong")
        return {"statusCode": 200, "body": json.dumps({"type": "pong"})}
    logger.info("No ping detected, responding with ack")
    return {"statusCode": 200, "body": json.dumps({"type": "ack"})}

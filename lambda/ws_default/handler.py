import json
import os
from aws_lambda_typing.events import WebSocketRouteEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.handler import get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)


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

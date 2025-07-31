import json
import os
import logging


# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
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

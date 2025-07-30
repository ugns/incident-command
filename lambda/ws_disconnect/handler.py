import os
import boto3
from typing import Any

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('WS_CONNECTIONS_TABLE', 'WebSocketConnections')
table: Any = dynamodb.Table(TABLE_NAME)  # type: ignore


def lambda_handler(event, context):
    # API Gateway WebSocket $disconnect event
    connection_id = event['requestContext']['connectionId']
    table.delete_item(Key={'connectionId': connection_id})
    return {"statusCode": 200, "body": "Disconnected"}

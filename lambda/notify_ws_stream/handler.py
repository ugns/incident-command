import os
import json
import boto3
import logging
from aws_lambda_typing.events import DynamoDBStreamEvent
from aws_lambda_typing.context import Context as LambdaContext
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.conditions import Key
from urllib.parse import urlparse
from typing import Any


# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logging.getLogger().setLevel(LOG_LEVEL)

deserializer = TypeDeserializer()
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('WS_CONNECTIONS_TABLE', 'WebSocketConnections')
table: Any = dynamodb.Table(TABLE_NAME)  # type: ignore
WS_API_ENDPOINT = os.environ['WS_API_ENDPOINT']


def get_table_from_arn(arn):
    # arn:aws:dynamodb:region:account:table/TableName/stream/timestamp
    table = arn.split(':table/')[-1].split('/')[0]
    logger.debug(f"Extracted table name from ARN: {table}")
    return table


def notify_connections(org_id, message):
    logger.info(
        f"Notifying connections for org_id={org_id} with message={message}")
    try:
        resp = table.query(KeyConditionExpression=Key('orgId').eq(org_id))
    except Exception as e:
        logger.error(f"Error querying table for org_id={org_id}: {e}")
        return
    apigw = boto3.client('apigatewaymanagementapi',
                         endpoint_url=WS_API_ENDPOINT)
    for conn in resp.get('Items', []):
        try:
            logger.debug(f"Posting to connection {conn['connectionId']}")
            apigw.post_to_connection(
                ConnectionId=conn['connectionId'], Data=json.dumps(message).encode('utf-8'))
        except apigw.exceptions.GoneException:
            logger.info(
                f"Stale connection {conn['connectionId']} detected, deleting.")
            table.delete_item(
                Key={'orgId': conn['orgId'], 'connectionId': conn['connectionId']})
        except Exception as e:
            logger.error(
                f"Error posting to connection {conn['connectionId']}: {e}")


def lambda_handler(
    event: DynamoDBStreamEvent,
    context: LambdaContext
) -> None:
    logger.info(f"Received event: {json.dumps(event)[:1000]}")
    logger.debug(f"Received event (full): {json.dumps(event)}")
    for record in event['Records']:
        event_name = record.get('eventName')
        table_arn = record.get('eventSourceArn')
        if not table_arn:
            logger.warning(f"Missing eventSourceArn in record: {record}")
            continue
        table_name = get_table_from_arn(table_arn)
        new_image = record.get('dynamodb', {}).get('NewImage')
        old_image = record.get('dynamodb', {}).get('OldImage')
        if new_image:
            new_item = {k: deserializer.deserialize(
                v) for k, v in new_image.items()}
        else:
            new_item = None
        if old_image:
            old_item = {k: deserializer.deserialize(
                v) for k, v in old_image.items()}
        else:
            old_item = None

        # Routing logic by table and event type
        item = new_item or old_item
        if not item:
            logger.warning(f"No item found in record: {record}")
            continue  # Skip if both new_item and old_item are None

        logger.info(
            f"Processing {event_name} for table {table_name} and org_id={item.get('org_id')}")

        if table_name == 'volunteers' and event_name in ('INSERT', 'MODIFY', 'REMOVE'):
            org_id = item['org_id']
            period_id = item.get('periodId')
            notify_connections(
                org_id, {"action": "volunteersUpdated", "orgId": org_id, "periodId": period_id})
        elif table_name == 'assignments' and event_name in ('INSERT', 'MODIFY', 'REMOVE'):
            org_id = item['org_id']
            period_id = item.get('periodId')
            notify_connections(
                org_id, {"action": "assignmentsUpdated", "orgId": org_id, "periodId": period_id})
        elif table_name == 'periods' and event_name in ('INSERT', 'MODIFY', 'REMOVE'):
            org_id = item['org_id']
            notify_connections(
                org_id, {"action": "periodsUpdated", "orgId": org_id})
        elif table_name == 'units' and event_name in ('INSERT', 'MODIFY', 'REMOVE'):
            org_id = item['org_id']
            notify_connections(
                org_id, {"action": "unitsUpdated", "orgId": org_id})
        elif table_name == 'incidents' and event_name in ('INSERT', 'MODIFY', 'REMOVE'):
            org_id = item['org_id']
            notify_connections(
                org_id, {"action": "incidentsUpdated", "orgId": org_id})
        else:
            logger.debug(
                f"No routing match for table {table_name} and event {event_name}")

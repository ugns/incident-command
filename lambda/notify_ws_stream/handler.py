import os
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.conditions import Key
from urllib.parse import urlparse
from typing import Any

deserializer = TypeDeserializer()
dynamodb = boto3.resource('dynamodb')
ws_table: Any = dynamodb.Table(   # type: ignore
    os.environ['WS_CONNECTIONS_TABLE'])

# Set this to your WebSocket API endpoint, e.g., wss://<api-id>.execute-api.<region>.amazonaws.com/ws
WS_API_ENDPOINT = os.environ['WS_API_ENDPOINT']


def get_table_from_arn(arn):
    # arn:aws:dynamodb:region:account:table/TableName/stream/timestamp
    return arn.split(':table/')[-1].split('/')[0]


def notify_connections(org_id, message):
    # Query all connections for the org
    resp = ws_table.query(
        KeyConditionExpression=Key('orgId').eq(org_id))
    apigw = boto3.client('apigatewaymanagementapi',
                         endpoint_url=WS_API_ENDPOINT)
    for conn in resp.get('Items', []):
        try:
            apigw.post_to_connection(
                ConnectionId=conn['connectionId'], Data=json.dumps(message).encode('utf-8'))
        except apigw.exceptions.GoneException:
            # Clean up stale connection
            ws_table.delete_item(
                Key={'orgId': org_id, 'connectionId': conn['connectionId']})


def lambda_handler(event, context):
    for record in event['Records']:
        event_name = record['eventName']  # INSERT, MODIFY, REMOVE
        table_arn = record['eventSourceARN']
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
            continue  # Skip if both new_item and old_item are None

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
    return {"statusCode": 200}

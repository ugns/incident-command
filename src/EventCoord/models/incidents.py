import os
import uuid
import boto3
from typing import Optional, Dict, Any, List
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table: Any = dynamodb.Table(os.environ.get(  # type: ignore
    'INCIDENTS_TABLE', 'incidents'))


class Incident:
    @staticmethod
    def get(org_id: str, incident_id: str) -> Optional[Dict[str, Any]]:
        resp = table.get_item(
            Key={"org_id": org_id, "incidentId": incident_id})
        return resp.get("Item")

    @staticmethod
    def list(org_id: str) -> List[Dict[str, Any]]:
        resp = table.query(KeyConditionExpression=Key("org_id").eq(org_id))
        return resp.get("Items", [])

    @staticmethod
    def create(org_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        if "incidentId" not in item:
            item["incidentId"] = str(uuid.uuid4())
        item["org_id"] = org_id
        table.put_item(Item=item)
        return item

    @staticmethod
    def update(org_id: str, incident_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        item = {"org_id": org_id, "incidentId": incident_id, **updates}
        table.put_item(Item=item)
        return item

    @staticmethod
    def delete(org_id: str, incident_id: str) -> None:
        table.delete_item(Key={"org_id": org_id, "incidentId": incident_id})

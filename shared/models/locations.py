import os
import uuid
import boto3
from typing import Optional, Dict, Any, List
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table: Any = dynamodb.Table(os.environ.get(  # type: ignore
    'LOCATIONS_TABLE', 'locations'))


class Location:
    @staticmethod
    def get(org_id: str, location_id: str) -> Optional[Dict[str, Any]]:
        resp = table.get_item(Key={"org_id": org_id, "locationId": location_id})
        return resp.get("Item")

    @staticmethod
    def list(org_id: str) -> List[Dict[str, Any]]:
        resp = table.query(KeyConditionExpression=Key("org_id").eq(org_id))
        return resp.get("Items", [])

    @staticmethod
    def create(org_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        if "locationId" not in item:
            item["locationId"] = str(uuid.uuid4())
        item["org_id"] = org_id
        table.put_item(Item=item)
        return item

    @staticmethod
    def update(org_id: str, location_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        updates["org_id"] = org_id
        updates["locationId"] = location_id
        table.put_item(Item=updates)
        return updates

    @staticmethod
    def delete(org_id: str, location_id: str) -> None:
        table.delete_item(Key={"org_id": org_id, "locationId": location_id})

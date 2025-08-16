import os
import boto3
from boto3.dynamodb.conditions import Key
from typing import Optional, Dict, Any, List
import uuid

dynamodb = boto3.resource("dynamodb")
table: Any = dynamodb.Table(os.environ.get(  # type: ignore
    'VOLUNTEERS_TABLE', 'volunteers'))


class Volunteer:
    @staticmethod
    def get(org_id: str, volunteer_id: str) -> Optional[Dict[str, Any]]:
        resp = table.get_item(
            Key={"org_id": org_id, "volunteerId": volunteer_id})
        return resp.get("Item")

    @staticmethod
    def get_by_email(org_id: str, email: str) -> Optional[Dict[str, Any]]:
        resp = table.query(
            IndexName="email-index",
            KeyConditionExpression=Key("org_id").eq(org_id) & Key("email").eq(email)
        )
        items = resp.get("Items", [])
        return items[0] if items else None

    @staticmethod
    def get_or_create_by_email(org_id: str, email: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
        volunteer = Volunteer.get_by_email(org_id, email)
        if volunteer:
            return volunteer
        item = {"email": email, **defaults}
        return Volunteer.create(org_id, item)

    @staticmethod
    def list(org_id: str) -> List[Dict[str, Any]]:
        resp = table.query(KeyConditionExpression=Key("org_id").eq(org_id))
        return resp.get("Items", [])

    @staticmethod
    def create(org_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        if "volunteerId" not in item:
            item["volunteerId"] = str(uuid.uuid4())
        item["org_id"] = org_id
        table.put_item(Item=item)
        return item

    @staticmethod
    def update(org_id: str, volunteer_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        item = {"org_id": org_id, "volunteerId": volunteer_id, **updates}
        table.put_item(Item=item)
        return item

    @staticmethod
    def delete(org_id: str, volunteer_id: str) -> None:
        table.delete_item(Key={"org_id": org_id, "volunteerId": volunteer_id})

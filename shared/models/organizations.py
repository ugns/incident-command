import os
import boto3
from boto3.dynamodb.conditions import Key
from typing import Optional, Dict, Any
import uuid

dynamodb = boto3.resource("dynamodb")
table: Any = dynamodb.Table(os.environ.get(  # type: ignore
    'ORGANIZATIONS_TABLE', 'organizations'))


class Organization:
    # TODO: Standardize function naming across models
    @staticmethod
    def get_by_org_id(org_id: str) -> Optional[Dict[str, Any]]:
        resp = table.get_item(Key={"org_id": org_id})
        return resp.get("Item")

    @staticmethod
    def get_by_aud(aud: str) -> Optional[Dict[str, Any]]:
        resp = table.query(
            IndexName="aud-index",
            KeyConditionExpression=Key("aud").eq(aud)
        )
        items = resp.get("Items", [])
        return items[0] if items else None

    @staticmethod
    def list_all() -> list[dict[str, Any]]:
        resp = table.scan()
        return resp.get("Items", [])

    @staticmethod
    def create(aud: str, name: str) -> Dict[str, Any]:
        org_id = str(uuid.uuid4())
        item = {"org_id": org_id, "aud": aud, "name": name}
        table.put_item(Item=item)
        return item

    @staticmethod
    def update(org_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["org_id"] = org_id
        table.put_item(Item=updates)
        return updates

    @staticmethod
    def delete(org_id: str) -> bool:
        table.delete_item(Key={"org_id": org_id})
        return True

import os
import boto3
from boto3.dynamodb.conditions import Key
from typing import Optional, Dict, Any
import uuid

dynamodb = boto3.resource("dynamodb")
table: Any = dynamodb.Table(os.environ.get(  # type: ignore
    'ORGANIZATIONS_TABLE', 'organizations'))


class Organization:
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
    def create(aud: str, name: str) -> Dict[str, Any]:
        org_id = str(uuid.uuid4())
        item = {"org_id": org_id, "aud": aud, "name": name}
        table.put_item(Item=item)
        return item

    @staticmethod
    def update(org_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        expr = []
        vals = {}
        for k, v in updates.items():
            expr.append(f"{k} = :{k}")
            vals[f":{k}"] = v
        if not expr:
            return None
        update_expr = "SET " + ", ".join(expr)
        resp = table.update_item(
            Key={"org_id": org_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=vals,
            ReturnValues="ALL_NEW"
        )
        return resp.get("Attributes")

    @staticmethod
    def delete(org_id: str) -> bool:
        table.delete_item(Key={"org_id": org_id})
        return True

import os
import uuid
import boto3
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, List, Optional

dynamodb = boto3.resource("dynamodb")
table: Any = dynamodb.Table(os.environ.get(  # type: ignore
    'PERIODS_TABLE', 'periods'))


class Period:
    @staticmethod
    def get(org_id: str, period_id: str) -> Optional[Dict[str, Any]]:
        resp = table.get_item(Key={"org_id": org_id, "periodId": period_id})
        return resp.get("Item")

    @staticmethod
    def list(org_id: str) -> List[Dict[str, Any]]:
        resp = table.query(KeyConditionExpression=Key("org_id").eq(org_id))
        return resp.get("Items", [])

    @staticmethod
    def list_by_unit(org_id: str, unit_id: str) -> List[Dict[str, Any]]:
        resp = table.query(
            IndexName="unitId-index",
            KeyConditionExpression=Key("org_id").eq(
                org_id) & Key("unitId").eq(unit_id)
        )
        return resp.get("Items", [])

    @staticmethod
    def list_by_incident(org_id: str, incident_id: str) -> List[Dict[str, Any]]:
        resp = table.query(
            IndexName="incidentId-index",
            KeyConditionExpression=Key("org_id").eq(
                org_id) & Key("incidentId").eq(incident_id)
        )
        return resp.get("Items", [])

    @staticmethod
    def create(org_id: str, incident_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        item["org_id"] = org_id
        item["incidentId"] = incident_id
        if "periodId" not in item:
            item["periodId"] = str(uuid.uuid4())
        table.put_item(Item=item)
        return item

    @staticmethod
    def update(org_id: str, period_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        item = {"org_id": org_id, "periodId": period_id, **updates}
        table.put_item(Item=item)
        return item

    @staticmethod
    def delete(org_id: str, period_id: str) -> None:
        table.delete_item(Key={"org_id": org_id, "periodId": period_id})

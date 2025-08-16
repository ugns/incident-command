import os
import uuid
import boto3
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, List, Optional

dynamodb = boto3.resource("dynamodb")
table: Any = dynamodb.Table(os.environ.get(  # type: ignore
    'ACTIVITY_LOGS_TABLE', 'activity_logs'))


class ActivityLog:
    # TODO: Standardize function naming across models
    @staticmethod
    def get(org_id: str, log_id: str) -> Optional[Dict[str, Any]]:
        resp = table.get_item(
            Key={"org_id": org_id, "logId": log_id})
        return resp.get("Item")

    @staticmethod
    def list(org_id: str) -> List[Dict[str, Any]]:
        resp = table.query(KeyConditionExpression=Key("org_id").eq(org_id))
        return resp.get("Items", [])

    @staticmethod
    def list_by_volunteer(org_id: str, volunteer_id: str) -> List[Dict[str, Any]]:
        resp = table.query(
            IndexName="VolunteerIdIndex",
            KeyConditionExpression=Key("org_id").eq(
                org_id) & Key("volunteerId").eq(volunteer_id)
        )
        return resp.get("Items", [])

    @staticmethod
    def list_by_period(org_id: str, period_id: str) -> List[Dict[str, Any]]:
        resp = table.query(
            IndexName="PeriodIdIndex",
            KeyConditionExpression=Key("org_id").eq(
                org_id) & Key("periodId").eq(period_id)
        )
        return resp.get("Items", [])

    @staticmethod
    def create(org_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        if "logId" not in item:
            item["logId"] = str(uuid.uuid4())
        item["org_id"] = org_id
        table.put_item(Item=item)
        return item

    @staticmethod
    def update(org_id: str, log_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        item = {"org_id": org_id, "logId": log_id, **updates}
        table.put_item(Item=item)
        return item

    @staticmethod
    def delete(org_id: str, log_id: str) -> None:
        table.delete_item(Key={"org_id": org_id, "logId": log_id})

import os
import boto3
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, List, Optional

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get(  # type: ignore
    'ACTIVITY_LOGS_TABLE', 'activity_logs'))


class ActivityLog:
    @staticmethod
    def get_activity_log(log_id: str) -> Optional[Dict[str, Any]]:
        resp = table.get_item(Key={"log_id": log_id})
        return resp.get("Item")

    @staticmethod
    def list_activity_logs() -> List[Dict[str, Any]]:
        resp = table.scan()
        return resp.get("Items", [])

    @staticmethod
    def create_activity_log(item: Dict[str, Any]) -> Dict[str, Any]:
        table.put_item(Item=item)
        return item

    @staticmethod
    def update_activity_log(log_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        # Simple update: overwrite the item
        item = {"log_id": log_id, **updates}
        table.put_item(Item=item)
        return item

    @staticmethod
    def delete_activity_log(log_id: str) -> None:
        table.delete_item(Key={"log_id": log_id})

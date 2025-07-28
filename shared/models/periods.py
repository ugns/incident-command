import os
import boto3
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, List, Optional

dynamodb = boto3.resource("dynamodb")
table: Any = dynamodb.Table(os.environ.get(  # type: ignore
    'ICS_PERIODS_TABLE', 'ics_periods'))


class Period:
    @staticmethod
    def get_period(period_id: str) -> Optional[Dict[str, Any]]:
        resp = table.get_item(Key={"period_id": period_id})
        return resp.get("Item")

    @staticmethod
    def list_periods() -> List[Dict[str, Any]]:
        resp = table.scan()
        return resp.get("Items", [])

    @staticmethod
    def create_period(item: Dict[str, Any]) -> Dict[str, Any]:
        table.put_item(Item=item)
        return item

    @staticmethod
    def update_period(period_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        item = {"period_id": period_id, **updates}
        table.put_item(Item=item)
        return item

    @staticmethod
    def delete_period(period_id: str) -> None:
        table.delete_item(Key={"period_id": period_id})

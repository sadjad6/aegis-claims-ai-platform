import boto3
from typing import Dict, Any, Optional
from ..application.ports import ClaimRepository # Using it for state tracking as well
import time

class DynamoDBStateRepository:
    def __init__(self, table_name: str, region: str = "us-east-1"):
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(table_name)

    async def save_state(self, tenant_id: str, key: str, state: Dict[str, Any]):
        self.table.put_item(
            Item={
                "PK": f"TENANT#{tenant_id}",
                "SK": f"STATE#{key}",
                "state": state,
                "updated_at": int(time.time()),
                "tenant_id": tenant_id
            }
        )

    async def get_state(self, tenant_id: str, key: str) -> Optional[Dict[str, Any]]:
        response = self.table.get_item(
            Key={
                "PK": f"TENANT#{tenant_id}",
                "SK": f"STATE#{key}"
            }
        )
        return response.get("Item", {}).get("state")

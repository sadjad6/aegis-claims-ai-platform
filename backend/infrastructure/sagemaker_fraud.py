import boto3
import json
from typing import Dict, Any
from ..application.ports import FraudDetectionService
from ..domain.entities import Claim

class SageMakerFraudService(FraudDetectionService):
    def __init__(self, endpoint_name: str, region: str = "us-east-1"):
        self.sagemaker = boto3.client("sagemaker-runtime", region_name=region)
        self.endpoint_name = endpoint_name

    async def detect_fraud(self, claim: Claim) -> float:
        payload = {
            "claim_id": claim.claim_id,
            "amount": claim.amount.amount,
            "description": claim.description,
            "metadata": claim.metadata
        }
        
        response = self.sagemaker.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload)
        )
        
        result = json.loads(response["Body"].read().decode())
        return float(result.get("fraud_probability", 0.0))

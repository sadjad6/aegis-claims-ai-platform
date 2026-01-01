import boto3
import json
from typing import Dict, Any
from ..application.ports import LLMService
from ..domain.entities import Claim, Policy

class BedrockLLMService(LLMService):
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0", region: str = "us-east-1"):
        self.bedrock = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id

    async def reason_coverage(self, claim: Claim, policy: Policy, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._build_prompt(claim, policy, context)
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0
        })

        response = self.bedrock.invoke_model(
            body=body,
            modelId=self.model_id,
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get("body").read())
        text = response_body["content"][0]["text"]
        
        return self._parse_structured_output(text)

    def _build_prompt(self, claim: Claim, policy: Policy, context: Dict[str, Any]) -> str:
        return f"""
        Analyze the following insurance claim against the policy coverage.
        
        Policy: {json.dumps(policy.coverage_details)}
        Claim: {claim.description}
        Claim Amount: {claim.amount.amount} {claim.amount.currency}
        Additional Context: {json.dumps(context)}
        
        Provide a structured response in JSON format with:
        1. confidence: 0.0 to 1.0
        2. recommended_outcome: "APPROVED" or "DENIED"
        3. reasoning: A detailed explanation of the decision.
        """

    def _parse_structured_output(self, text: str) -> Dict[str, Any]:
        # Simple extraction logic (in production, use a more robust parser or tool use)
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except Exception:
            return {
                "confidence": 0.0,
                "recommended_outcome": "PENDING_HUMAN",
                "reasoning": "Failed to parse AI response."
            }

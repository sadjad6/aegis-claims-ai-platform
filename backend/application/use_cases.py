from typing import Dict, Any
from .ports import ClaimRepository, PolicyRepository, DecisionRepository, LLMService, FraudDetectionService
from ..domain.entities import Claim, Decision
from ..domain.value_objects import ClaimStatus, DecisionOutcome, ConfidenceScore, RiskLevel
import uuid

class ProcessClaimUseCase:
    def __init__(
        self,
        claim_repo: ClaimRepository,
        policy_repo: PolicyRepository,
        decision_repo: DecisionRepository,
        llm_service: LLMService,
        fraud_service: FraudDetectionService
    ):
        self.claim_repo = claim_repo
        self.policy_repo = policy_repo
        self.decision_repo = decision_repo
        self.llm_service = llm_service
        self.fraud_service = fraud_service

    async def execute(self, tenant_id: str, claim_data: Dict[str, Any]) -> str:
        # 1. Resolve Policy
        policy = await self.policy_repo.get_by_number(claim_data["policy_number"], tenant_id)
        if not policy:
            raise ValueError(f"Policy {claim_data['policy_number']} not found for tenant {tenant_id}")

        # 2. Create Claim Entity
        claim = Claim(
            claim_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            policy_id=policy.policy_id,
            claim_number=claim_data.get("claim_number", f"CLN-{uuid.uuid4().hex[:8].upper()}"),
            incident_date=claim_data["incident_date"],
            description=claim_data["description"],
            status=ClaimStatus.SUBMITTED,
            amount=claim_data["amount"]
        )
        await self.claim_repo.save(claim)

        # 3. Fraud Detection Agent logic (Simplified orchestration)
        fraud_score = await self.fraud_service.detect_fraud(claim)
        
        # 4. Coverage Reasoning Agent logic (LLM)
        llm_result = await self.llm_service.reason_coverage(claim, policy, context={"fraud_score": fraud_score})
        
        # 5. Decision Agent logic
        outcome = DecisionOutcome.PENDING_HUMAN
        if llm_result["confidence"] > 0.8 and fraud_score < 0.2:
            outcome = DecisionOutcome.APPROVED if llm_result["recommended_outcome"] == "APPROVED" else DecisionOutcome.DENIED

        decision = Decision(
            decision_id=str(uuid.uuid4()),
            claim_id=claim.claim_id,
            tenant_id=tenant_id,
            outcome=outcome,
            confidence=ConfidenceScore(llm_result["confidence"]),
            reasoning_trace=llm_result["reasoning"],
            risk_level=RiskLevel.HIGH if fraud_score > 0.5 else RiskLevel.LOW,
            decided_by="AI_AGENT"
        )
        
        await self.decision_repo.save(decision)
        
        # 6. Update Claim Status
        claim.status = ClaimStatus.DECIDED
        await self.claim_repo.save(claim)
        
        return claim.claim_id

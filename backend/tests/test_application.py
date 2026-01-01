import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.application.use_cases import ProcessClaimUseCase
from backend.application.agents import ClaimIntakeAgent, FraudDetectionAgent, DecisionAgent
from backend.domain.entities import Claim
from backend.domain.value_objects import Money, Currency, ClaimStatus
from datetime import datetime

@pytest.mark.asyncio
async def test_claim_intake_agent_validates_required_fields():
    agent = ClaimIntakeAgent(tenant_id="test-tenant")
    
    # Missing required field
    result = await agent.execute({"claim_data": {"policy_number": "POL-001"}})
    assert result["success"] is False
    assert "incident_date" in result["errors"]

@pytest.mark.asyncio
async def test_claim_intake_agent_success():
    agent = ClaimIntakeAgent(tenant_id="test-tenant")
    
    claim_data = {
        "policy_number": "POL-001",
        "incident_date": "2025-12-28",
        "description": "Test claim",
        "amount": {"amount": 1000, "currency": "USD"}
    }
    result = await agent.execute({"claim_data": claim_data})
    assert result["success"] is True

@pytest.mark.asyncio
async def test_fraud_detection_agent():
    mock_fraud_service = AsyncMock()
    mock_fraud_service.detect_fraud.return_value = 0.15
    
    claim = Claim(
        claim_id="1",
        tenant_id="test-tenant",
        policy_id="pol-1",
        claim_number="CLM-001",
        incident_date=datetime.now(),
        description="Minor damage",
        status=ClaimStatus.SUBMITTED,
        amount=Money(500, Currency.USD)
    )
    
    agent = FraudDetectionAgent(tenant_id="test-tenant", fraud_service=mock_fraud_service)
    result = await agent.execute({"claim": claim})
    
    assert result["fraud_score"] == 0.15
    assert result["is_suspicious"] is False

@pytest.mark.asyncio
async def test_decision_agent_auto_approve():
    claim = MagicMock()
    claim.claim_id = "1"
    
    llm_result = {
        "confidence": 0.92,
        "recommended_outcome": "APPROVED",
        "reasoning": "Coverage verified."
    }
    
    agent = DecisionAgent(tenant_id="test-tenant")
    result = await agent.execute({
        "claim": claim,
        "llm_result": llm_result,
        "fraud_score": 0.1
    })
    
    assert result["final_outcome"] == "APPROVED"
    assert result["requires_human_review"] is False

@pytest.mark.asyncio
async def test_decision_agent_escalates_low_confidence():
    claim = MagicMock()
    claim.claim_id = "1"
    
    llm_result = {
        "confidence": 0.55,
        "recommended_outcome": "APPROVED",
        "reasoning": "Uncertain."
    }
    
    agent = DecisionAgent(tenant_id="test-tenant")
    result = await agent.execute({
        "claim": claim,
        "llm_result": llm_result,
        "fraud_score": 0.1
    })
    
    assert result["final_outcome"] == "PENDING_HUMAN"
    assert result["requires_human_review"] is True

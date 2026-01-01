from fastapi import APIRouter, Depends, HTTPException, Header, Request
from typing import List, Optional
from datetime import datetime
from .dtos import (
    ClaimCreateDTO, ClaimResponseDTO, DecisionResponseDTO,
    OverrideRequestDTO, MoneyDTO, AnalyticsResponseDTO, ModelHealthDTO
)
from ..application.use_cases import ProcessClaimUseCase
from ..application.ports import (
    ClaimRepository, DecisionRepository, PolicyRepository,
    AnalyticsService, MonitoringService
)
from ..domain.value_objects import Money, DecisionOutcome, ConfidenceScore, RiskLevel
from ..domain.entities import Decision
import uuid

router = APIRouter()


# Dependency injection placeholders - configured in main.py
_claim_repo: Optional[ClaimRepository] = None
_decision_repo: Optional[DecisionRepository] = None
_policy_repo: Optional[PolicyRepository] = None
_process_claim_use_case: Optional[ProcessClaimUseCase] = None
_analytics_service: Optional[AnalyticsService] = None
_monitoring_service: Optional[MonitoringService] = None


def configure_dependencies(
    claim_repo: ClaimRepository,
    decision_repo: DecisionRepository,
    policy_repo: PolicyRepository,
    use_case: ProcessClaimUseCase,
    analytics_service: AnalyticsService = None,
    monitoring_service: MonitoringService = None
):
    """Configure dependencies for API routes. Called from main.py startup."""
    global _claim_repo, _decision_repo, _policy_repo, _process_claim_use_case
    global _analytics_service, _monitoring_service
    _claim_repo = claim_repo
    _decision_repo = decision_repo
    _policy_repo = policy_repo
    _process_claim_use_case = use_case
    _analytics_service = analytics_service
    _monitoring_service = monitoring_service


def get_claim_repo() -> ClaimRepository:
    if not _claim_repo:
        raise HTTPException(status_code=500, detail="Claim repository not configured")
    return _claim_repo


def get_decision_repo() -> DecisionRepository:
    if not _decision_repo:
        raise HTTPException(status_code=500, detail="Decision repository not configured")
    return _decision_repo


def get_process_claim_use_case() -> ProcessClaimUseCase:
    if not _process_claim_use_case:
        raise HTTPException(status_code=500, detail="Use case not configured")
    return _process_claim_use_case


async def get_tenant_id(x_tenant_id: str = Header(...)):
    """Extract and validate tenant ID from request header."""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header missing")
    return x_tenant_id


# ==================== CLAIMS ENDPOINTS ====================

@router.post("/claims", response_model=str, tags=["Claims"])
async def submit_claim(
    claim_data: ClaimCreateDTO,
    tenant_id: str = Depends(get_tenant_id),
    use_case: ProcessClaimUseCase = Depends(get_process_claim_use_case)
):
    """Submit a new claim for AI-powered processing and decisioning."""
    data = claim_data.dict()
    data["amount"] = Money(claim_data.amount.amount, claim_data.amount.currency)

    try:
        claim_id = await use_case.execute(tenant_id, data)
        return claim_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/claims", response_model=List[ClaimResponseDTO], tags=["Claims"])
async def list_claims(
    tenant_id: str = Depends(get_tenant_id),
    repo: ClaimRepository = Depends(get_claim_repo)
):
    """List all claims for the current tenant."""
    claims = await repo.list_by_tenant(tenant_id)
    return [
        ClaimResponseDTO(
            claim_id=c.claim_id,
            claim_number=c.claim_number,
            status=c.status,
            amount=MoneyDTO(amount=c.amount.amount, currency=c.amount.currency),
            created_at=c.created_at
        )
        for c in claims
    ]


@router.get("/claims/{claim_id}", response_model=ClaimResponseDTO, tags=["Claims"])
async def get_claim(
    claim_id: str,
    tenant_id: str = Depends(get_tenant_id),
    repo: ClaimRepository = Depends(get_claim_repo)
):
    """Get a specific claim by ID."""
    claim = await repo.get_by_id(claim_id, tenant_id)
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")

    return ClaimResponseDTO(
        claim_id=claim.claim_id,
        claim_number=claim.claim_number,
        status=claim.status,
        amount=MoneyDTO(amount=claim.amount.amount, currency=claim.amount.currency),
        created_at=claim.created_at
    )


@router.get("/claims/{claim_id}/decision", response_model=DecisionResponseDTO, tags=["Claims"])
async def get_claim_decision(
    claim_id: str,
    tenant_id: str = Depends(get_tenant_id),
    repo: DecisionRepository = Depends(get_decision_repo)
):
    """Get the AI decision for a specific claim."""
    decision = await repo.get_by_claim_id(claim_id, tenant_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision for claim {claim_id} not found")

    return DecisionResponseDTO(
        decision_id=decision.decision_id,
        claim_id=decision.claim_id,
        outcome=decision.outcome,
        confidence=decision.confidence.value,
        reasoning_trace=decision.reasoning_trace,
        risk_level=decision.risk_level,
        decided_at=decision.decided_at
    )


@router.post("/claims/{claim_id}/override", tags=["Claims"])
async def override_decision(
    claim_id: str,
    override_data: OverrideRequestDTO,
    tenant_id: str = Depends(get_tenant_id),
    decision_repo: DecisionRepository = Depends(get_decision_repo)
):
    """Override an AI decision with a human decision (HITL)."""
    existing = await decision_repo.get_by_claim_id(claim_id, tenant_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Decision for claim {claim_id} not found")

    # Create new decision record for the override
    override_decision = Decision(
        decision_id=str(uuid.uuid4()),
        claim_id=claim_id,
        tenant_id=tenant_id,
        outcome=DecisionOutcome(override_data.outcome),
        confidence=ConfidenceScore(1.0),  # Human decisions have full confidence
        reasoning_trace=f"Human override: {override_data.reason}",
        risk_level=existing.risk_level,
        decided_by=override_data.user_id or "HUMAN_OVERRIDE",
        metadata={"previous_decision_id": existing.decision_id, "override": True}
    )

    await decision_repo.save(override_decision)

    # Log audit event if monitoring service is available
    if _monitoring_service:
        await _monitoring_service.log_audit_event(
            tenant_id=tenant_id,
            event_type="DECISION_OVERRIDE",
            user_id=override_data.user_id or "UNKNOWN",
            data={
                "claim_id": claim_id,
                "previous_outcome": existing.outcome.value,
                "new_outcome": override_data.outcome,
                "reason": override_data.reason
            }
        )

    return {"success": True, "decision_id": override_decision.decision_id}


# ==================== ANALYTICS ENDPOINTS ====================

@router.get("/analytics/automation-rate", response_model=AnalyticsResponseDTO, tags=["Analytics"])
async def get_automation_rate(
    tenant_id: str = Depends(get_tenant_id)
):
    """Get the automation rate for the current tenant."""
    if _analytics_service:
        rate = await _analytics_service.get_automation_rate(tenant_id)
    else:
        # Fallback mock data for development
        rate = 0.924

    return AnalyticsResponseDTO(rate=rate)


@router.get("/analytics/model-health", response_model=ModelHealthDTO, tags=["Analytics"])
async def get_model_health(
    tenant_id: str = Depends(get_tenant_id)
):
    """Get model health metrics including drift and latency."""
    if _monitoring_service:
        health = await _monitoring_service.get_model_health(tenant_id)
        return ModelHealthDTO(
            drift=health.get("drift", 0.04),
            precision=health.get("precision", 0.982),
            latency=health.get("latency", 1.8)
        )
    else:
        # Fallback mock data for development
        return ModelHealthDTO(drift=0.04, precision=0.982, latency=1.8)


@router.get("/analytics/tenant-metrics", tags=["Analytics"])
async def get_tenant_metrics(
    tenant_id: str = Depends(get_tenant_id)
):
    """Get comprehensive metrics for the current tenant."""
    if _analytics_service:
        metrics = await _analytics_service.get_tenant_metrics(tenant_id)
        return metrics
    else:
        # Fallback mock data
        return {
            "total_claims": 1284,
            "automation_rate": 0.924,
            "average_confidence": 0.89,
            "pending_overrides": 12,
            "claims_today": 47,
            "decisions_today": 43
        }

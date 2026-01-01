from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..domain.value_objects import Currency, ClaimStatus, DecisionOutcome, RiskLevel


class MoneyDTO(BaseModel):
    """Data transfer object for monetary values."""
    amount: float
    currency: Currency


class ClaimCreateDTO(BaseModel):
    """DTO for creating a new claim."""
    policy_number: str = Field(..., description="Policy number to file the claim against")
    incident_date: datetime = Field(..., description="Date when the incident occurred")
    description: str = Field(..., description="Description of the claim/incident")
    amount: MoneyDTO = Field(..., description="Claimed amount")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    document_keys: Optional[List[str]] = Field(default=None, description="S3 keys of uploaded documents")


class ClaimResponseDTO(BaseModel):
    """DTO for claim responses."""
    claim_id: str
    claim_number: str
    status: ClaimStatus
    amount: MoneyDTO
    created_at: datetime
    description: Optional[str] = None
    policy_id: Optional[str] = None


class ClaimDetailDTO(BaseModel):
    """Detailed claim information including decision."""
    claim_id: str
    claim_number: str
    status: ClaimStatus
    amount: MoneyDTO
    description: str
    incident_date: datetime
    policy_id: str
    documents: List[str] = []
    created_at: datetime
    updated_at: datetime
    decision: Optional["DecisionResponseDTO"] = None


class DecisionResponseDTO(BaseModel):
    """DTO for AI decision responses."""
    decision_id: str
    claim_id: str
    outcome: DecisionOutcome
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    reasoning_trace: str = Field(..., description="Full reasoning trace for the decision")
    risk_level: RiskLevel
    decided_at: datetime
    decided_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class OverrideRequestDTO(BaseModel):
    """DTO for human-in-the-loop decision override."""
    outcome: str = Field(..., description="New outcome: APPROVED, DENIED, or PARTIAL")
    reason: str = Field(..., description="Reason for the override")
    user_id: Optional[str] = Field(default=None, description="ID of the user making the override")


class AnalyticsResponseDTO(BaseModel):
    """DTO for automation rate analytics."""
    rate: float = Field(..., ge=0.0, le=1.0, description="Automation rate as decimal")


class ModelHealthDTO(BaseModel):
    """DTO for model health metrics."""
    drift: float = Field(..., description="Drift indicator score")
    precision: float = Field(..., ge=0.0, le=1.0, description="Model precision")
    latency: float = Field(..., description="Average latency in seconds")


class TenantConfigDTO(BaseModel):
    """DTO for tenant configuration."""
    tenant_id: str
    name: str
    fraud_threshold: float = 0.5
    confidence_threshold: float = 0.8
    high_value_claim_threshold: float = 10000.0
    auto_approve_enabled: bool = True
    rag_enabled: bool = True
    human_escalation_enabled: bool = True
    coverage_prompt_version: str = "v1"
    document_prompt_version: str = "v1"
    custom_settings: Optional[Dict[str, Any]] = None


class AgentTraceDTO(BaseModel):
    """DTO for agent execution trace."""
    agent: str
    action: str
    status: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None


# Enable forward references for nested models
ClaimDetailDTO.model_rebuild()

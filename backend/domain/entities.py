from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from .value_objects import Money, ClaimStatus, DecisionOutcome, ConfidenceScore, RiskLevel

@dataclass
class Tenant:
    tenant_id: str
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Policy:
    policy_id: str
    tenant_id: str
    policy_number: str
    holder_name: str
    coverage_details: Dict[str, Any]
    limit: Money
    deductible: Money
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Claim:
    claim_id: str
    tenant_id: str
    policy_id: str
    claim_number: str
    incident_date: datetime
    description: str
    status: ClaimStatus
    amount: Money
    metadata: Dict[str, Any] = field(default_factory=dict)
    documents: List[str] = field(default_factory=list)  # S3 Keys
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Decision:
    decision_id: str
    claim_id: str
    tenant_id: str
    outcome: DecisionOutcome
    confidence: ConfidenceScore
    reasoning_trace: str
    risk_level: RiskLevel
    decided_by: str  # "AI_AGENT" or User ID
    decided_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

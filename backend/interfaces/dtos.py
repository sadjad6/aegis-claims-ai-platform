from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..domain.value_objects import Currency, ClaimStatus, DecisionOutcome, RiskLevel

class MoneyDTO(BaseModel):
    amount: float
    currency: Currency

class ClaimCreateDTO(BaseModel):
    policy_number: str
    incident_date: datetime
    description: str
    amount: MoneyDTO
    metadata: Optional[Dict[str, Any]] = None

class ClaimResponseDTO(BaseModel):
    claim_id: str
    claim_number: str
    status: ClaimStatus
    amount: MoneyDTO
    created_at: datetime

class DecisionResponseDTO(BaseModel):
    decision_id: str
    claim_id: str
    outcome: DecisionOutcome
    confidence: float
    reasoning_trace: str
    risk_level: RiskLevel
    decided_at: datetime

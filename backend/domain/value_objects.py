from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

@dataclass(frozen=True)
class Money:
    amount: float
    currency: Currency

class ClaimStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    TRIAGED = "TRIAGED"
    DECIDED = "DECIDED"
    CLOSED = "CLOSED"

class DecisionOutcome(str, Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PARTIAL = "PARTIAL"
    PENDING_HUMAN = "PENDING_HUMAN"

@dataclass(frozen=True)
class ConfidenceScore:
    value: float  # 0.0 to 1.0
    
    def __post_init__(self):
        if not (0.0 <= self.value <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

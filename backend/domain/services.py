from typing import List
from .entities import Claim, Decision
from .value_objects import ClaimStatus, DecisionOutcome

class ClaimDomainService:
    """Pure domain service for claim-related business logic."""
    
    @staticmethod
    def can_transition_to(current_status: ClaimStatus, next_status: ClaimStatus) -> bool:
        allowed_transitions = {
            ClaimStatus.DRAFT: [ClaimStatus.SUBMITTED],
            ClaimStatus.SUBMITTED: [ClaimStatus.UNDER_REVIEW],
            ClaimStatus.UNDER_REVIEW: [ClaimStatus.TRIAGED],
            ClaimStatus.TRIAGED: [ClaimStatus.DECIDED, ClaimStatus.CLOSED],
            ClaimStatus.DECIDED: [ClaimStatus.CLOSED],
            ClaimStatus.CLOSED: []
        }
        return next_status in allowed_transitions.get(current_status, [])

    @staticmethod
    def is_claim_high_value(claim: Claim, threshold: float) -> bool:
        return claim.amount.amount > threshold

import pytest
from backend.domain.entities import Claim
from backend.domain.value_objects import Money, Currency, ClaimStatus
from backend.domain.services import ClaimDomainService
from datetime import datetime

def test_claim_high_value_check():
    money = Money(amount=15000, currency=Currency.USD)
    claim = Claim(
        claim_id="1",
        tenant_id="ten-1",
        policy_id="pol-1",
        claim_number="CLM-001",
        incident_date=datetime.now(),
        description="Heavy damage",
        status=ClaimStatus.SUBMITTED,
        amount=money
    )
    
    service = ClaimDomainService()
    assert service.is_claim_high_value(claim, 10000) is True
    assert service.is_claim_high_value(claim, 20000) is False

def test_claim_status_transitions():
    service = ClaimDomainService()
    assert service.can_transition_to(ClaimStatus.DRAFT, ClaimStatus.SUBMITTED) is True
    assert service.can_transition_to(ClaimStatus.SUBMITTED, ClaimStatus.CLOSED) is False
    assert service.can_transition_to(ClaimStatus.TRIAGED, ClaimStatus.DECIDED) is True

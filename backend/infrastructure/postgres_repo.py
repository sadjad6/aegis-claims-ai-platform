from sqlalchemy import Column, String, Float, DateTime, Boolean, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future import select
from datetime import datetime
from typing import Optional, List
from ..domain.entities import Claim, Policy, Tenant, Decision
from ..domain.value_objects import Money, Currency, ClaimStatus, DecisionOutcome, ConfidenceScore, RiskLevel
from ..application.ports import ClaimRepository, PolicyRepository, DecisionRepository

Base = declarative_base()

class DBClaim(Base):
    __tablename__ = "claims"
    claim_id = Column(String, primary_key=True)
    tenant_id = Column(String, primary_key=True) # Composite key for isolation
    policy_id = Column(String, nullable=False)
    claim_number = Column(String, nullable=False)
    incident_date = Column(DateTime, nullable=False)
    description = Column(String)
    status = Column(String)
    amount = Column(Float)
    currency = Column(String)
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class PostgresClaimRepository(ClaimRepository):
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def get_by_id(self, claim_id: str, tenant_id: str) -> Optional[Claim]:
        async with self.session_factory() as session:
            stmt = select(DBClaim).where(DBClaim.claim_id == claim_id, DBClaim.tenant_id == tenant_id)
            result = await session.execute(stmt)
            db_claim = result.scalar_one_or_none()
            if not db_claim:
                return None
            return self._to_entity(db_claim)

    async def save(self, claim: Claim) -> None:
        async with self.session_factory() as session:
            db_claim = DBClaim(
                claim_id=claim.claim_id,
                tenant_id=claim.tenant_id,
                policy_id=claim.policy_id,
                claim_number=claim.claim_number,
                incident_date=claim.incident_date,
                description=claim.description,
                status=claim.status.value,
                amount=claim.amount.amount,
                currency=claim.amount.currency.value,
                metadata_json=claim.metadata
            )
            await session.merge(db_claim)
            await session.commit()

    def _to_entity(self, db_claim: DBClaim) -> Claim:
        return Claim(
            claim_id=db_claim.claim_id,
            tenant_id=db_claim.tenant_id,
            policy_id=db_claim.policy_id,
            claim_number=db_claim.claim_number,
            incident_date=db_claim.incident_date,
            description=db_claim.description,
            status=ClaimStatus(db_claim.status),
            amount=Money(db_claim.amount, Currency(db_claim.currency)),
            metadata=db_claim.metadata_json or {}
        )

    async def list_by_tenant(self, tenant_id: str) -> List[Claim]:
        async with self.session_factory() as session:
            stmt = select(DBClaim).where(DBClaim.tenant_id == tenant_id)
            result = await session.execute(stmt)
            return [self._to_entity(c) for c in result.scalars().all()]

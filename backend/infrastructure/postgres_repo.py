from sqlalchemy import Column, String, Float, DateTime, Boolean, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future import select
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..domain.entities import Claim, Policy, Tenant, Decision
from ..domain.value_objects import Money, Currency, ClaimStatus, DecisionOutcome, ConfidenceScore, RiskLevel
from ..application.ports import ClaimRepository, PolicyRepository, DecisionRepository, TenantRepository

Base = declarative_base()


class DBClaim(Base):
    __tablename__ = "claims"
    claim_id = Column(String, primary_key=True)
    tenant_id = Column(String, primary_key=True)  # Composite key for isolation
    policy_id = Column(String, nullable=False)
    claim_number = Column(String, nullable=False)
    incident_date = Column(DateTime, nullable=False)
    description = Column(String)
    status = Column(String)
    amount = Column(Float)
    currency = Column(String)
    metadata_json = Column(JSON)
    documents_json = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DBPolicy(Base):
    __tablename__ = "policies"
    policy_id = Column(String, primary_key=True)
    tenant_id = Column(String, primary_key=True)  # Composite key for isolation
    policy_number = Column(String, nullable=False, index=True)
    holder_name = Column(String, nullable=False)
    coverage_details_json = Column(JSON)
    limit_amount = Column(Float)
    limit_currency = Column(String)
    deductible_amount = Column(Float)
    deductible_currency = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DBDecision(Base):
    __tablename__ = "decisions"
    decision_id = Column(String, primary_key=True)
    claim_id = Column(String, nullable=False, index=True)
    tenant_id = Column(String, primary_key=True)  # Composite key for isolation
    outcome = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning_trace = Column(String)
    risk_level = Column(String)
    decided_by = Column(String, nullable=False)
    metadata_json = Column(JSON)
    decided_at = Column(DateTime, default=datetime.utcnow)


class DBTenant(Base):
    __tablename__ = "tenants"
    tenant_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    config_json = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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


class PostgresPolicyRepository(PolicyRepository):
    """PostgreSQL implementation of PolicyRepository with tenant isolation."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def get_by_number(self, policy_number: str, tenant_id: str) -> Optional[Policy]:
        async with self.session_factory() as session:
            stmt = select(DBPolicy).where(
                DBPolicy.policy_number == policy_number,
                DBPolicy.tenant_id == tenant_id,
                DBPolicy.is_active == True
            )
            result = await session.execute(stmt)
            db_policy = result.scalar_one_or_none()
            if not db_policy:
                return None
            return self._to_entity(db_policy)

    async def get_by_id(self, policy_id: str, tenant_id: str) -> Optional[Policy]:
        async with self.session_factory() as session:
            stmt = select(DBPolicy).where(
                DBPolicy.policy_id == policy_id,
                DBPolicy.tenant_id == tenant_id
            )
            result = await session.execute(stmt)
            db_policy = result.scalar_one_or_none()
            if not db_policy:
                return None
            return self._to_entity(db_policy)

    async def save(self, policy: Policy) -> None:
        async with self.session_factory() as session:
            db_policy = DBPolicy(
                policy_id=policy.policy_id,
                tenant_id=policy.tenant_id,
                policy_number=policy.policy_number,
                holder_name=policy.holder_name,
                coverage_details_json=policy.coverage_details,
                limit_amount=policy.limit.amount,
                limit_currency=policy.limit.currency.value,
                deductible_amount=policy.deductible.amount,
                deductible_currency=policy.deductible.currency.value,
                is_active=policy.is_active
            )
            await session.merge(db_policy)
            await session.commit()

    def _to_entity(self, db_policy: DBPolicy) -> Policy:
        return Policy(
            policy_id=db_policy.policy_id,
            tenant_id=db_policy.tenant_id,
            policy_number=db_policy.policy_number,
            holder_name=db_policy.holder_name,
            coverage_details=db_policy.coverage_details_json or {},
            limit=Money(db_policy.limit_amount, Currency(db_policy.limit_currency)),
            deductible=Money(db_policy.deductible_amount, Currency(db_policy.deductible_currency)),
            is_active=db_policy.is_active,
            created_at=db_policy.created_at
        )


class PostgresDecisionRepository(DecisionRepository):
    """PostgreSQL implementation of DecisionRepository with tenant isolation."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def save(self, decision: Decision) -> None:
        async with self.session_factory() as session:
            db_decision = DBDecision(
                decision_id=decision.decision_id,
                claim_id=decision.claim_id,
                tenant_id=decision.tenant_id,
                outcome=decision.outcome.value,
                confidence=decision.confidence.value,
                reasoning_trace=decision.reasoning_trace,
                risk_level=decision.risk_level.value,
                decided_by=decision.decided_by,
                metadata_json=decision.metadata,
                decided_at=decision.decided_at
            )
            await session.merge(db_decision)
            await session.commit()

    async def get_by_claim_id(self, claim_id: str, tenant_id: str) -> Optional[Decision]:
        async with self.session_factory() as session:
            stmt = select(DBDecision).where(
                DBDecision.claim_id == claim_id,
                DBDecision.tenant_id == tenant_id
            )
            result = await session.execute(stmt)
            db_decision = result.scalar_one_or_none()
            if not db_decision:
                return None
            return self._to_entity(db_decision)

    def _to_entity(self, db_decision: DBDecision) -> Decision:
        return Decision(
            decision_id=db_decision.decision_id,
            claim_id=db_decision.claim_id,
            tenant_id=db_decision.tenant_id,
            outcome=DecisionOutcome(db_decision.outcome),
            confidence=ConfidenceScore(db_decision.confidence),
            reasoning_trace=db_decision.reasoning_trace,
            risk_level=RiskLevel(db_decision.risk_level),
            decided_by=db_decision.decided_by,
            decided_at=db_decision.decided_at,
            metadata=db_decision.metadata_json or {}
        )


class PostgresTenantRepository(TenantRepository):
    """PostgreSQL implementation of TenantRepository."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def get_config(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        async with self.session_factory() as session:
            stmt = select(DBTenant).where(
                DBTenant.tenant_id == tenant_id,
                DBTenant.is_active == True
            )
            result = await session.execute(stmt)
            db_tenant = result.scalar_one_or_none()
            if not db_tenant:
                return None
            return db_tenant.config_json or {}

    async def save_config(self, tenant_id: str, config: Dict[str, Any]) -> None:
        async with self.session_factory() as session:
            stmt = select(DBTenant).where(DBTenant.tenant_id == tenant_id)
            result = await session.execute(stmt)
            db_tenant = result.scalar_one_or_none()
            if db_tenant:
                db_tenant.config_json = config
                db_tenant.updated_at = datetime.utcnow()
            else:
                db_tenant = DBTenant(
                    tenant_id=tenant_id,
                    name=config.get("name", tenant_id),
                    config_json=config
                )
                session.add(db_tenant)
            await session.commit()

    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        async with self.session_factory() as session:
            stmt = select(DBTenant).where(DBTenant.tenant_id == tenant_id)
            result = await session.execute(stmt)
            db_tenant = result.scalar_one_or_none()
            if not db_tenant:
                return None
            return Tenant(
                tenant_id=db_tenant.tenant_id,
                name=db_tenant.name,
                config=db_tenant.config_json or {},
                created_at=db_tenant.created_at
            )

    async def list_all(self) -> List[Tenant]:
        async with self.session_factory() as session:
            stmt = select(DBTenant).where(DBTenant.is_active == True)
            result = await session.execute(stmt)
            return [
                Tenant(
                    tenant_id=t.tenant_id,
                    name=t.name,
                    config=t.config_json or {},
                    created_at=t.created_at
                )
                for t in result.scalars().all()
            ]

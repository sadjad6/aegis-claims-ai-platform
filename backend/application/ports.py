from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..domain.entities import Claim, Policy, Decision, Tenant
from ..domain.value_objects import ConfidenceScore


class ClaimRepository(ABC):
    @abstractmethod
    async def get_by_id(self, claim_id: str, tenant_id: str) -> Optional[Claim]:
        pass

    @abstractmethod
    async def save(self, claim: Claim) -> None:
        pass

    @abstractmethod
    async def list_by_tenant(self, tenant_id: str) -> List[Claim]:
        pass


class PolicyRepository(ABC):
    @abstractmethod
    async def get_by_number(self, policy_number: str, tenant_id: str) -> Optional[Policy]:
        pass

    @abstractmethod
    async def get_by_id(self, policy_id: str, tenant_id: str) -> Optional[Policy]:
        pass

    @abstractmethod
    async def save(self, policy: Policy) -> None:
        pass


class DecisionRepository(ABC):
    @abstractmethod
    async def save(self, decision: Decision) -> None:
        pass

    @abstractmethod
    async def get_by_claim_id(self, claim_id: str, tenant_id: str) -> Optional[Decision]:
        pass


class TenantRepository(ABC):
    """Repository for tenant configuration and management."""

    @abstractmethod
    async def get_config(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve tenant configuration by tenant_id."""
        pass

    @abstractmethod
    async def save_config(self, tenant_id: str, config: Dict[str, Any]) -> None:
        """Save tenant configuration."""
        pass

    @abstractmethod
    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Retrieve tenant entity by ID."""
        pass

    @abstractmethod
    async def list_all(self) -> List[Tenant]:
        """List all tenants."""
        pass


class VectorSearchService(ABC):
    """Service for vector-based similarity search using embeddings."""

    @abstractmethod
    async def search_similar_claims(
        self, tenant_id: str, embedding: List[float], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar claims based on embedding vector."""
        pass

    @abstractmethod
    async def index_claim(
        self, tenant_id: str, claim_id: str, text: str, embedding: List[float]
    ) -> None:
        """Index a claim with its embedding for future similarity searches."""
        pass

    @abstractmethod
    async def search_policies(
        self, tenant_id: str, embedding: List[float], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for relevant policy documents based on embedding vector."""
        pass


class LLMService(ABC):
    @abstractmethod
    async def reason_coverage(
        self, claim: Claim, policy: Policy, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Returns structured reasoning with confidence score."""
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text."""
        pass


class FraudDetectionService(ABC):
    @abstractmethod
    async def detect_fraud(self, claim: Claim) -> float:
        """Returns fraud probability score."""
        pass


class DocumentProcessor(ABC):
    @abstractmethod
    async def extract_info(self, document_key: str, tenant_id: str) -> Dict[str, Any]:
        pass


class StorageService(ABC):
    @abstractmethod
    async def upload(self, file_content: bytes, filename: str, tenant_id: str) -> str:
        """Returns storage key (e.g. S3 key)."""
        pass

    @abstractmethod
    async def download(self, key: str, tenant_id: str) -> bytes:
        """Download file content by key."""
        pass

    @abstractmethod
    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Get a presigned URL for temporary access."""
        pass


class MonitoringService(ABC):
    """Service for monitoring, metrics, and drift detection."""

    @abstractmethod
    async def record_decision_metric(
        self, tenant_id: str, claim_id: str, outcome: str, confidence: float, latency_ms: float
    ) -> None:
        """Record a decision event for monitoring."""
        pass

    @abstractmethod
    async def record_model_prediction(
        self, tenant_id: str, model_name: str, prediction: float, latency_ms: float
    ) -> None:
        """Record model prediction for drift detection."""
        pass

    @abstractmethod
    async def get_automation_rate(self, tenant_id: str, days: int = 30) -> float:
        """Get the automation rate for a tenant."""
        pass

    @abstractmethod
    async def get_model_health(self, tenant_id: str) -> Dict[str, Any]:
        """Get model health metrics including drift indicators."""
        pass

    @abstractmethod
    async def log_audit_event(
        self, tenant_id: str, event_type: str, user_id: str, data: Dict[str, Any]
    ) -> None:
        """Log an audit event for compliance."""
        pass


class AnalyticsService(ABC):
    """Service for analytics and SaaS reporting via data warehouse."""

    @abstractmethod
    async def record_decision_event(
        self, tenant_id: str, claim_id: str, outcome: str, confidence: float
    ) -> None:
        """Record decision event in analytics warehouse."""
        pass

    @abstractmethod
    async def get_automation_rate(self, tenant_id: str) -> float:
        """Calculate automation rate from analytics data."""
        pass

    @abstractmethod
    async def get_tenant_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive metrics for a tenant."""
        pass

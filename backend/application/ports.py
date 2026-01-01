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

class DecisionRepository(ABC):
    @abstractmethod
    async def save(self, decision: Decision) -> None:
        pass
    
    @abstractmethod
    async def get_by_claim_id(self, claim_id: str, tenant_id: str) -> Optional[Decision]:
        pass

class LLMService(ABC):
    @abstractmethod
    async def reason_coverage(self, claim: Claim, policy: Policy, context: Dict[str, Any]) -> Dict[str, Any]:
        """Returns structured reasoning with confidence score."""
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

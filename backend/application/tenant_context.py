from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime

@dataclass
class TenantConfig:
    """Tenant-specific configuration including AI thresholds and feature flags."""
    tenant_id: str
    name: str
    
    # AI Thresholds
    fraud_threshold: float = 0.5
    confidence_threshold: float = 0.8
    high_value_claim_threshold: float = 10000.0
    
    # Feature Flags
    auto_approve_enabled: bool = True
    rag_enabled: bool = True
    human_escalation_enabled: bool = True
    
    # Prompt Template IDs
    coverage_prompt_version: str = "v1"
    document_prompt_version: str = "v1"
    
    # Custom Settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class TenantContextResolver:
    """Resolves and provides tenant context for the current request."""
    
    def __init__(self, tenant_repo):
        self.tenant_repo = tenant_repo
        self._current_tenant: TenantConfig = None
    
    async def resolve(self, tenant_id: str) -> TenantConfig:
        """Resolve tenant configuration from repository."""
        config = await self.tenant_repo.get_config(tenant_id)
        if not config:
            raise ValueError(f"Tenant {tenant_id} not found or inactive")
        self._current_tenant = config
        return config
    
    @property
    def current_tenant(self) -> TenantConfig:
        if not self._current_tenant:
            raise RuntimeError("Tenant context not resolved. Call resolve() first.")
        return self._current_tenant

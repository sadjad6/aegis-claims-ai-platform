# AegisClaims AI - Multi-Tenancy Guide

Documentation for the multi-tenant architecture and isolation mechanisms.

---

## Overview

AegisClaims AI is designed as a multi-tenant SaaS platform where multiple insurance companies share the same infrastructure while maintaining complete data isolation.

---

## Tenant Isolation Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│         X-Tenant-ID header → TenantContextResolver          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Database Layer                          │
│         All queries filtered by tenant_id (WHERE clause)    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Storage Layer                           │
│         S3 prefix: {tenant_id}/documents/...                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      IAM Layer                              │
│         Resource-based policies with tenant_id tags         │
└─────────────────────────────────────────────────────────────┘
```

---

## Application Layer Isolation

### Request Context

Every API request must include `X-Tenant-ID` header:

```python
# backend/interfaces/api.py
async def get_tenant_id(x_tenant_id: str = Header(...)):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header missing")
    return x_tenant_id
```

### Tenant Context Resolver

```python
# backend/application/tenant_context.py
class TenantContextResolver:
    async def resolve(self, tenant_id: str) -> TenantConfig:
        config = await self.tenant_repo.get_config(tenant_id)
        if not config:
            raise ValueError(f"Tenant {tenant_id} not found")
        return config
```

---

## Database Layer Isolation

### Schema Design

All tables include `tenant_id` as part of the primary key:

```sql
CREATE TABLE claims (
    claim_id UUID NOT NULL,
    tenant_id VARCHAR(255) NOT NULL,
    -- other columns
    PRIMARY KEY (claim_id, tenant_id)
);

CREATE INDEX idx_claims_tenant ON claims(tenant_id);
```

### Repository Pattern

Repositories always filter by tenant:

```python
# backend/infrastructure/postgres_repo.py
async def get_by_id(self, claim_id: str, tenant_id: str) -> Optional[Claim]:
    stmt = select(DBClaim).where(
        DBClaim.claim_id == claim_id,
        DBClaim.tenant_id == tenant_id  # Always filtered
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

### DynamoDB

Uses composite keys for isolation:

```python
PK: "TENANT#{tenant_id}"
SK: "STATE#{key}"
```

---

## Storage Layer Isolation

### S3 Structure

```
aegis-claims-bucket/
├── tenant-acme/
│   ├── documents/
│   │   ├── claim-001/
│   │   └── claim-002/
│   └── processed/
├── tenant-shield/
│   ├── documents/
│   └── processed/
```

### S3 Service

```python
# backend/infrastructure/s3_storage.py
async def upload(self, file_content: bytes, filename: str, tenant_id: str) -> str:
    key = f"{tenant_id}/{filename}"  # Tenant prefix
    self.s3.put_object(
        Bucket=self.bucket_name,
        Key=key,
        Metadata={"tenant_id": tenant_id}
    )
    return key
```

---

## Vector Database Isolation

### OpenSearch Index

All embeddings include tenant_id for filtering:

```python
async def search_similar_claims(self, tenant_id: str, embedding: List[float], limit: int = 5):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"tenant_id": tenant_id}}  # Tenant filter
                ],
                "knn": {
                    "embedding": {"vector": embedding, "k": limit}
                }
            }
        }
    }
```

---

## IAM / Access Control

### Cognito User Attributes

Users have tenant_id as a custom attribute:

```hcl
# terraform/modules/cognito/main.tf
schema {
    name                = "tenant_id"
    attribute_data_type = "String"
    mutable             = true
}
```

### Resource Tags (ABAC)

AWS resources are tagged for attribute-based access:

```hcl
tags = {
    tenant_id = var.tenant_id
}
```

---

## Tenant Configuration

### TenantConfig Entity

```python
@dataclass
class TenantConfig:
    tenant_id: str
    name: str
    
    # AI Thresholds (per-tenant)
    fraud_threshold: float = 0.5
    confidence_threshold: float = 0.8
    high_value_claim_threshold: float = 10000.0
    
    # Feature Flags
    auto_approve_enabled: bool = True
    rag_enabled: bool = True
    human_escalation_enabled: bool = True
    
    # Prompt Versions
    coverage_prompt_version: str = "v1"
    document_prompt_version: str = "v1"
```

### Usage

```python
config = await tenant_context.resolve(tenant_id)
if config.auto_approve_enabled and confidence > config.confidence_threshold:
    # Auto-approve
```

---

## Testing Isolation

### Data Leak Test

```python
@pytest.mark.asyncio
async def test_no_cross_tenant_data_access():
    # Create claim for tenant A
    claim_a = await repo.save(Claim(tenant_id="A", ...))
    
    # Try to access from tenant B - should fail
    result = await repo.get_by_id(claim_a.claim_id, tenant_id="B")
    assert result is None
```

---

## Best Practices

1. **Never trust client-provided tenant_id** - Validate against auth token
2. **Always filter queries by tenant_id** - No exceptions
3. **Use composite keys** in DynamoDB for partition isolation
4. **S3 prefixes** are not security boundaries - Use bucket policies
5. **Audit all cross-tenant access attempts**
6. **Regular penetration testing** for isolation verification

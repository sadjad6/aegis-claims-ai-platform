# AegisClaims AI - AI Agents Guide

Comprehensive documentation for the autonomous AI agent system.

---

## Overview

AegisClaims AI uses a multi-agent architecture where specialized agents handle different aspects of claim processing. Each agent is:
- **Tenant-aware**: Isolated data and configuration per tenant
- **Auditable**: Emits structured audit events
- **Testable**: Can be unit tested independently

---

## Agent Pipeline

```
┌─────────────────┐
│  Claim Intake   │ ──▶ Validates incoming claim data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Document      │ ──▶ OCR + NLP extraction from PDFs/images
│  Understanding  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fraud Detection │ ──▶ ML model scoring (SageMaker)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Coverage     │ ──▶ LLM reasoning with RAG (Bedrock)
│    Reasoning    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Decision     │ ──▶ Final outcome with HITL escalation
└─────────────────┘
```

---

## Agent Details

### 1. Claim Intake Agent

**Purpose**: Validates and normalizes incoming claim data.

**Location**: `backend/application/agents.py` → `ClaimIntakeAgent`

**Input**:
```python
{
    "claim_data": {
        "policy_number": "POL-001",
        "incident_date": "2025-12-28",
        "description": "...",
        "amount": {"amount": 2500, "currency": "USD"}
    }
}
```

**Output**:
```python
{
    "success": True,
    "normalized_claim": {...}
}
```

**Validation Rules**:
- Required fields: `policy_number`, `incident_date`, `description`, `amount`
- Date must be in past
- Amount must be positive

---

### 2. Document Understanding Agent

**Purpose**: Extracts structured data from unstructured documents.

**Location**: `backend/application/agents.py` → `DocumentUnderstandingAgent`

**Technology**: AWS Bedrock (Claude 3) with multi-modal capabilities

**Input**:
```python
{
    "document_keys": ["s3://bucket/invoice.pdf", "s3://bucket/photo.jpg"]
}
```

**Output**:
```python
{
    "success": True,
    "extracted_documents": [
        {
            "damage_type": "Collision",
            "estimated_cost": 2450.0,
            "currency": "USD",
            "incident_date": "2025-12-28",
            "confidence": 0.98
        }
    ]
}
```

**Prompt Template**: `prompts/document_extraction_v1.md`

---

### 3. Fraud Detection Agent

**Purpose**: Scores claims for fraud probability using ML.

**Location**: `backend/application/agents.py` → `FraudDetectionAgent`

**Technology**: AWS SageMaker (XGBoost model)

**Input**:
```python
{
    "claim": Claim  # Domain entity
}
```

**Output**:
```python
{
    "fraud_score": 0.15,  # 0.0 - 1.0
    "is_suspicious": False  # True if > 0.5
}
```

**Features Used**:
- Claim amount
- Time since policy inception
- Historical claim frequency
- Description sentiment
- Document consistency

---

### 4. Coverage Reasoning Agent

**Purpose**: Determines if claim is covered by policy using LLM + RAG.

**Location**: `backend/application/agents.py` → `CoverageReasoningAgent`

**Technology**: 
- AWS Bedrock (Claude 3 Sonnet)
- AWS OpenSearch (Vector embeddings)

**Input**:
```python
{
    "claim": Claim,
    "policy": Policy,
    "fraud_score": 0.15
}
```

**Output**:
```python
{
    "confidence": 0.92,
    "recommended_outcome": "APPROVED",
    "reasoning": "Coverage verified under comprehensive policy...",
    "flags": []
}
```

**RAG Flow**:
1. Generate embedding from claim description
2. Search OpenSearch for similar historical claims
3. Include similar claims in LLM context
4. LLM reasons about coverage with examples

**Prompt Template**: `prompts/coverage_reasoning_v1.md`

---

### 5. Decision Agent

**Purpose**: Makes final decision with confidence-based logic.

**Location**: `backend/application/agents.py` → `DecisionAgent`

**Decision Logic**:
```python
if confidence >= 0.8 and fraud_score < 0.3:
    outcome = recommended_outcome  # AUTO-DECIDE
else:
    outcome = "PENDING_HUMAN"  # ESCALATE
```

**Input**:
```python
{
    "claim": Claim,
    "llm_result": {...},  # From Coverage Agent
    "fraud_score": 0.15
}
```

**Output**:
```python
{
    "final_outcome": "APPROVED",
    "confidence": 0.92,
    "fraud_score": 0.15,
    "requires_human_review": False,
    "reasoning": "..."
}
```

---

## Tenant-Specific Configuration

Each tenant can configure agent thresholds:

```python
@dataclass
class TenantConfig:
    tenant_id: str
    fraud_threshold: float = 0.5      # Fraud score cutoff
    confidence_threshold: float = 0.8  # Auto-approve threshold
    high_value_claim_threshold: float = 10000.0
    auto_approve_enabled: bool = True
    rag_enabled: bool = True
```

---

## Audit Events

All agents emit structured audit events:

```python
{
    "agent": "DecisionAgent",
    "tenant_id": "tenant-acme",
    "event_type": "DECISION_COMPLETE",
    "data": {
        "claim_id": "abc-123",
        "outcome": "APPROVED",
        "requires_human": False
    }
}
```

**Event Types by Agent**:

| Agent | Events |
|-------|--------|
| Intake | `INTAKE_START`, `INTAKE_SUCCESS`, `INTAKE_FAILED` |
| Document | `DOC_PROCESSING_START`, `DOC_PROCESSING_COMPLETE` |
| Fraud | `FRAUD_CHECK_START`, `FRAUD_CHECK_COMPLETE` |
| Coverage | `COVERAGE_REASONING_START`, `COVERAGE_REASONING_COMPLETE` |
| Decision | `DECISION_START`, `DECISION_COMPLETE` |

---

## Testing Agents

```python
import pytest
from backend.application.agents import ClaimIntakeAgent

@pytest.mark.asyncio
async def test_intake_validates_required_fields():
    agent = ClaimIntakeAgent(tenant_id="test")
    result = await agent.execute({"claim_data": {}})
    assert result["success"] is False
```

See `backend/tests/test_application.py` for complete test suite.

---

## Extending Agents

To add a new agent:

1. Create class extending `BaseAgent`
2. Implement `execute(context)` method
3. Use `emit_audit_event()` for traceability
4. Add to orchestration in `use_cases.py`

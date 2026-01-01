# AegisClaims AI - System Architecture

Comprehensive technical architecture documentation for the AegisClaims AI platform.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [High-Level System Design](#high-level-system-design)
4. [Clean Architecture Layers](#clean-architecture-layers)
5. [Data Flow](#data-flow)
6. [AI Agent Architecture](#ai-agent-architecture)
7. [Data Architecture](#data-architecture)
8. [Security Architecture](#security-architecture)
9. [Scalability & Performance](#scalability--performance)

---

## Overview

AegisClaims AI is a **production-grade, multi-tenant B2B SaaS platform** for autonomous insurance claims triage and decisioning. The system processes motor and property insurance claims using a multi-agent AI architecture that combines:

- **Large Language Models (LLMs)** for coverage reasoning
- **Machine Learning models** for fraud detection
- **Retrieval-Augmented Generation (RAG)** for policy analysis
- **Human-in-the-loop (HITL)** for low-confidence decisions

---

## Architecture Principles

### Clean Architecture (SOLID)

The system strictly follows Clean Architecture with these rules:

| Principle | Implementation |
|-----------|----------------|
| **Single Responsibility** | Each agent handles one specific task |
| **Open/Closed** | Agents extend `BaseAgent` without modification |
| **Liskov Substitution** | All repository implementations are interchangeable |
| **Interface Segregation** | Ports define minimal interfaces per service |
| **Dependency Inversion** | Domain depends on nothing; Infrastructure depends on Application |

### Dependency Rule

```
┌─────────────────────────────────────────────────────────────────┐
│                          Interface Layer                        │
│              (FastAPI, DTOs, Middleware - OUTER)                │
└─────────────────────────────────────────────────────────────────┘
                              │ depends on
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Infrastructure Layer                      │
│          (AWS SDKs, Repositories, External APIs)                │
└─────────────────────────────────────────────────────────────────┘
                              │ depends on
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Application Layer                        │
│              (Use Cases, Agents, Ports/Interfaces)              │
└─────────────────────────────────────────────────────────────────┘
                              │ depends on
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Domain Layer                           │
│        (Entities, Value Objects, Domain Services - CORE)        │
└─────────────────────────────────────────────────────────────────┘
```

**Rule**: Dependencies point INWARD. Domain has zero external dependencies.

---

## High-Level System Design

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENTS                                    │
│                    (Web Browser, Mobile App, API Consumers)                  │
└──────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              AWS CloudFront                                  │
│                         (CDN + Edge Caching)                                 │
└──────────────────────────────────────────────────────────────────────────────┘
                    │                                    │
                    ▼                                    ▼
┌────────────────────────────────┐    ┌────────────────────────────────────────┐
│          S3 Bucket             │    │      Application Load Balancer         │
│    (React Static Assets)       │    │         (HTTPS Termination)            │
└────────────────────────────────┘    └────────────────────────────────────────┘
                                                         │
                                                         ▼
                                      ┌────────────────────────────────────────┐
                                      │           ECS Fargate Cluster          │
                                      │        (FastAPI Backend Services)      │
                                      │                                        │
                                      │  ┌──────────┐  ┌──────────┐           │
                                      │  │ Task 1   │  │ Task 2   │  ...      │
                                      │  └──────────┘  └──────────┘           │
                                      └────────────────────────────────────────┘
                                                         │
                    ┌────────────────────────────────────┼────────────────────────────────────┐
                    │                                    │                                    │
                    ▼                                    ▼                                    ▼
┌────────────────────────────────┐    ┌────────────────────────────────┐    ┌────────────────────────────────┐
│       AWS Cognito              │    │         AWS Bedrock            │    │       AWS SageMaker            │
│   (Authentication/RBAC)        │    │     (Claude 3 LLM API)         │    │   (Fraud Detection ML)         │
└────────────────────────────────┘    └────────────────────────────────┘    └────────────────────────────────┘
                                                         │
                    ┌────────────────────────────────────┼────────────────────────────────────┐
                    │                                    │                                    │
                    ▼                                    ▼                                    ▼
┌────────────────────────────────┐    ┌────────────────────────────────┐    ┌────────────────────────────────┐
│     RDS Aurora PostgreSQL      │    │          DynamoDB              │    │       AWS OpenSearch           │
│    (Transactional Data)        │    │    (Agent State/Idempotency)   │    │     (Vector Embeddings)        │
└────────────────────────────────┘    └────────────────────────────────┘    └────────────────────────────────┘
                                                         │
                                                         ▼
                                      ┌────────────────────────────────────────┐
                                      │              AWS S3                    │
                                      │      (Documents: PDFs, Images)         │
                                      └────────────────────────────────────────┘
```

---

## Clean Architecture Layers

### Domain Layer (`backend/domain/`)

**Purpose**: Pure business logic with zero external dependencies.

**Contents**:
| File | Purpose |
|------|---------|
| `entities.py` | Core entities: `Claim`, `Policy`, `Tenant`, `Decision` |
| `value_objects.py` | Immutable values: `Money`, `ClaimStatus`, `ConfidenceScore` |
| `services.py` | Domain logic: status transitions, thresholds |

**Rules**:
- ❌ No imports from `infrastructure/` or `interfaces/`
- ❌ No AWS SDK, no SQLAlchemy, no FastAPI
- ✅ Only Python standard library and dataclasses

```python
# Example: Pure domain entity
@dataclass
class Claim:
    claim_id: str
    tenant_id: str
    policy_id: str
    amount: Money
    status: ClaimStatus
    # No database annotations, no JSON serializers
```

---

### Application Layer (`backend/application/`)

**Purpose**: Orchestrate use cases, define ports (interfaces), coordinate agents.

**Contents**:
| File | Purpose |
|------|---------|
| `use_cases.py` | Business workflows: `ProcessClaimUseCase` |
| `agents.py` | AI agents: Intake, Document, Fraud, Coverage, Decision |
| `ports.py` | Abstract interfaces for external services |
| `tenant_context.py` | Tenant configuration resolution |

**Key Pattern - Ports (Interfaces)**:
```python
# Application defines WHAT it needs (port)
class LLMService(ABC):
    @abstractmethod
    async def reason_coverage(self, claim: Claim, policy: Policy) -> Dict:
        pass

# Infrastructure implements HOW (adapter)
class BedrockLLMService(LLMService):
    async def reason_coverage(self, claim: Claim, policy: Policy) -> Dict:
        # AWS Bedrock implementation
```

---

### Infrastructure Layer (`backend/infrastructure/`)

**Purpose**: Implement ports with concrete AWS/database technologies.

**Contents**:
| File | Purpose |
|------|---------|
| `bedrock_llm.py` | AWS Bedrock Claude 3 integration |
| `sagemaker_fraud.py` | AWS SageMaker inference endpoint |
| `postgres_repo.py` | SQLAlchemy async repository |
| `dynamodb_repo.py` | DynamoDB state management |
| `s3_storage.py` | S3 document storage |
| `opensearch_adapter.py` | Vector search for RAG |
| `redshift_adapter.py` | Analytics queries |

---

### Interface Layer (`backend/interfaces/`)

**Purpose**: HTTP API, DTOs, middleware. No business logic.

**Contents**:
| File | Purpose |
|------|---------|
| `api.py` | FastAPI routes |
| `dtos.py` | Pydantic request/response models |
| `middleware.py` | Audit logging, tenant extraction |

---

## Data Flow

### Claim Processing Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Claim     │     │  Document   │     │    Fraud    │     │  Coverage   │     │  Decision   │
│   Intake    │ ──▶ │Understanding│ ──▶ │  Detection  │ ──▶ │  Reasoning  │ ──▶ │   Agent     │
│   Agent     │     │    Agent    │     │    Agent    │     │    Agent    │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼                   ▼
   Validate           Extract OCR         Score claim        LLM + RAG          Apply rules
   + Normalize        + NLP data          (SageMaker)        (Bedrock)          + HITL check
      │                   │                   │                   │                   │
      └───────────────────┴───────────────────┴───────────────────┴───────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────────┐
                                    │   Final Decision    │
                                    │ APPROVED | DENIED   │
                                    │ PENDING_HUMAN       │
                                    └─────────────────────┘
```

### Request Flow

```
HTTP Request (X-Tenant-ID header)
         │
         ▼
┌─────────────────────┐
│  Audit Middleware   │ ──▶ Log request
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Tenant Middleware  │ ──▶ Extract & validate tenant_id
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   FastAPI Router    │ ──▶ Route to handler
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│      Use Case       │ ──▶ Orchestrate business logic
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│    Repositories     │ ──▶ Data access (filtered by tenant)
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│     Database        │
└─────────────────────┘
```

---

## AI Agent Architecture

### Agent Base Class

```python
class BaseAgent(ABC):
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id  # Always tenant-aware
    
    @abstractmethod
    async def execute(self, context: Dict) -> Dict:
        pass
    
    def emit_audit_event(self, event_type: str, data: Dict):
        # Structured logging for traceability
```

### Agent Responsibilities

| Agent | Input | Output | Technology |
|-------|-------|--------|------------|
| **Intake** | Raw claim JSON | Validated claim | Python validation |
| **Document** | S3 document keys | Extracted fields | Bedrock multi-modal |
| **Fraud** | Claim entity | Fraud score (0-1) | SageMaker XGBoost |
| **Coverage** | Claim + Policy | Reasoning + confidence | Bedrock Claude + RAG |
| **Decision** | All agent outputs | Final outcome | Deterministic rules |

### Decision Logic

```python
if confidence >= tenant.confidence_threshold and fraud_score < tenant.fraud_threshold:
    outcome = recommended_outcome  # AUTO-APPROVE/DENY
else:
    outcome = "PENDING_HUMAN"  # Escalate to human
```

---

## Data Architecture

### Database Selection

| Database | Use Case | Why |
|----------|----------|-----|
| **PostgreSQL** | Claims, Policies, Decisions | ACID transactions, complex queries |
| **DynamoDB** | Agent state, idempotency keys | Low latency, auto-scaling |
| **OpenSearch** | Vector embeddings for RAG | k-NN similarity search |
| **S3** | Documents (PDF, images) | Scalable blob storage |
| **Redshift** | Analytics, SaaS metrics | Columnar analytics at scale |

### Multi-Tenant Data Model

```sql
-- All tables include tenant_id in primary key
CREATE TABLE claims (
    claim_id    UUID NOT NULL,
    tenant_id   VARCHAR(255) NOT NULL,
    -- data columns
    PRIMARY KEY (claim_id, tenant_id)
);

-- Queries always filter by tenant
SELECT * FROM claims WHERE tenant_id = :tenant AND claim_id = :id;
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         WAF + Shield                            │
│                   (DDoS protection, Rate limiting)              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CloudFront + TLS 1.3                        │
│                    (Edge termination, HTTPS)                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Cognito Authentication                      │
│               (OAuth2/OIDC, MFA, RBAC groups)                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                           │
│          (Tenant isolation, input validation, audit)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     IAM Least Privilege                         │
│        (Resource policies, ABAC with tenant_id tags)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Encryption at Rest                          │
│            (RDS encryption, S3 SSE, DynamoDB KMS)               │
└─────────────────────────────────────────────────────────────────┘
```

### RBAC Roles

| Role | Permissions |
|------|-------------|
| **Tenant Admin** | Full tenant management, user provisioning |
| **Claims Adjuster** | View/submit/override claims |
| **Supervisor** | Approve HITL escalations |
| **AI Ops** | Monitor models, view metrics, no claim access |

---

## Scalability & Performance

### Horizontal Scaling

| Component | Strategy |
|-----------|----------|
| **Backend API** | ECS Fargate auto-scaling (CPU/memory) |
| **Database** | Aurora read replicas, DynamoDB on-demand |
| **AI Services** | Bedrock/SageMaker scale automatically |

### Performance Targets

| Metric | Target | How |
|--------|--------|-----|
| **API Latency (p95)** | < 200ms | Async I/O, connection pooling |
| **Claim Triage Time** | < 2s | Parallel agent execution |
| **Throughput** | 1000 claims/min | Horizontal scaling |
| **Availability** | 99.9% | Multi-AZ, health checks |

### Caching Strategy

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   CloudFront    │ ──▶ │   ElastiCache   │ ──▶ │    Database     │
│   (Static CDN)  │     │   (Session/API) │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Related Documentation

- [AI Agents Guide](./agents.md) - Detailed agent implementation
- [Multi-Tenancy Guide](./multi-tenancy.md) - Isolation mechanisms
- [API Reference](./api.md) - REST endpoint documentation
- [Deployment Guide](./deployment.md) - AWS production deployment

You are a Principal Software Architect, Staff Backend Engineer, Senior Frontend Engineer,
and Principal ML Engineer with deep experience in:

- B2B SaaS platforms
- Insurance systems (claims, policies, fraud, underwriting)
- Clean Architecture & SOLID design principles
- AWS-native systems (Bedrock, SageMaker, Lambda, S3, DynamoDB, OpenSearch, Redshift)
- Autonomous AI agents, RAG systems, LLM governance
- React + TypeScript enterprise frontends
- Secure, multi-tenant systems (GDPR, auditability)

Your task is to DESIGN AND IMPLEMENT a COMPLETE, PRODUCTION-READY, MULTI-TENANT SaaS
application called:

==================================================
AegisClaims AI
==================================================

AegisClaims AI is a B2B SaaS platform that provides AI-powered, autonomous insurance
claims triage and decisioning for motor and property insurance.

This is NOT a demo.
This is NOT a prototype.
This is a production-grade SaaS system.

Do NOT generate placeholders, fake logic, or superficial examples unless explicitly stated.

--------------------------------------------------
1. SAAS PRODUCT REQUIREMENTS
--------------------------------------------------

The system MUST support:

### Multi-Tenancy (MANDATORY)
- Logical tenant isolation using tenant_id
- Tenant-specific:
  - Configuration
  - AI thresholds
  - Prompt templates
  - Feature flags
- Strict data isolation enforced at:
  - Application layer
  - Database queries
  - IAM / access control

### Authentication & Authorization
- OAuth2 / OIDC (e.g. AWS Cognito)
- Role-based access control:
  - Tenant Admin
  - Claims Adjuster
  - Supervisor
  - AI Ops
- Secure API tokens for service-to-service calls

--------------------------------------------------
2. CORE BUSINESS CAPABILITIES
--------------------------------------------------

### Claims Processing
- Claim intake (JSON forms)
- Unstructured documents (PDF, email, images)
- S3-based storage with raw / processed / feature layers

### Autonomous AI Agents
Implement a full agent system:

- Claim Intake Agent
- Document Understanding Agent (OCR + NLP)
- Fraud Detection Agent (ML via SageMaker)
- Coverage Reasoning Agent (LLM via Bedrock + RAG)
- Decision Agent with confidence-based logic

Agents MUST:
- Be tenant-aware
- Be independently testable
- Emit structured logs and audit events

--------------------------------------------------
3. DECISION & GOVERNANCE FRAMEWORK
--------------------------------------------------

Implement:
- Deterministic decision logic
- Confidence scoring
- Human-in-the-loop escalation
- Full decision traceability

No opaque or unexplainable AI decisions are allowed.

--------------------------------------------------
4. CLEAN ARCHITECTURE (STRICT)
--------------------------------------------------

You MUST strictly follow Clean Architecture and SOLID principles.

### Layering (NO VIOLATIONS ALLOWED):

#### Domain Layer
- Pure business logic
- Entities:
  - Claim
  - Policy
  - Tenant
  - Decision
- Value objects
- Domain services
- NO frameworks
- NO AWS SDKs
- NO databases

#### Application Layer
- Use cases (e.g. ProcessClaim, EvaluateCoverage)
- Agent orchestration
- Interfaces (ports) for:
  - LLMs
  - Databases
  - External services
- Tenant context resolution

#### Infrastructure Layer
- AWS implementations:
  - Bedrock
  - SageMaker
  - S3
  - DynamoDB
  - OpenSearch
  - Redshift
- Repository implementations
- Auth providers
- Logging & monitoring

#### Interface Layer
- REST APIs (FastAPI or Lambda handlers)
- DTOs & validation
- Event handlers
- No business logic

--------------------------------------------------
5. FRONTEND (REACT SAAS UI)
--------------------------------------------------

Implement a production-grade React + TypeScript frontend.

### Frontend MUST:
- Be a separate layer
- Contain NO business logic
- Communicate ONLY via backend APIs
- Be tenant-aware via auth context

### Frontend Features:
- Login & tenant selection
- Claims dashboard
- Claim detail view with:
  - AI decision
  - Confidence score
  - Reasoning trace
- Human override actions
- AI Ops dashboard:
  - Automation rate
  - Drift indicators
  - Model health

Use:
- React
- TypeScript
- Clean component architecture
- Role-based routing

--------------------------------------------------
6. AI / ML STACK (MANDATORY)
--------------------------------------------------

### AWS Bedrock
- LLM-based coverage reasoning
- Prompt templates stored & versioned
- Retrieval-Augmented Generation using vector DB

### AWS SageMaker
- Fraud detection model
- Training pipelines
- Inference endpoints
- Model versioning

### Vector Database
- OpenSearch (or equivalent)
- Tenant-aware embeddings
- Policy & historical claims retrieval

--------------------------------------------------
7. DATA & STORAGE
--------------------------------------------------

Implement ALL of the following:

- PostgreSQL – core transactional data
- DynamoDB – agent state, orchestration, idempotency
- OpenSearch – vector embeddings
- Redshift – analytics & SaaS reporting

--------------------------------------------------
8. INFRASTRUCTURE AS CODE
--------------------------------------------------

ALL infrastructure must be provisioned via IaC.

Use ONE:
- Terraform (preferred)
- OR AWS CDK

Include:
- Multi-environment setup (dev / staging / prod)
- IAM least-privilege policies
- Secure secrets handling
- Reproducible deployments

--------------------------------------------------
9. MONITORING, AUDIT & COMPLIANCE
--------------------------------------------------

Implement:
- CloudWatch logs & metrics
- Per-tenant audit trails
- Model performance monitoring
- Data drift detection
- Prompt drift detection
- GDPR-compliant data handling

--------------------------------------------------
10. PROJECT STRUCTURE (MANDATORY)
--------------------------------------------------

Repository MUST be structured as:

aegis-claims-ai-platform/
│
├── backend/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── interfaces/
│   └── tests/
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── auth/
│
├── prompts/
├── evaluations/
├── terraform/
├── docs/
└── README.md

--------------------------------------------------
11. CODE QUALITY RULES
--------------------------------------------------

- Python & TypeScript only
- Full type safety
- Dependency inversion everywhere
- No framework leakage into domain
- Unit tests for domain & application layers
- Secure defaults
- Explicit error handling

--------------------------------------------------
12. OUTPUT INSTRUCTIONS
--------------------------------------------------

You MUST:

1. Create the full repository structure
2. Implement key backend & frontend components
3. Show real agent logic and decision flows
4. Provide example prompts and configs
5. Include architecture & SaaS documentation

If something is ambiguous:
- Choose the most enterprise-grade solution
- Document the reasoning

Start by:
1. Creating the repository structure
2. Implementing the Domain layer
3. Building upward incrementally until the full SaaS system is complete

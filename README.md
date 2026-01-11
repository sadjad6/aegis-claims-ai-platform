# AegisClaims AI

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org)
[![AWS](https://img.shields.io/badge/AWS-Native-FF9900.svg)](https://aws.amazon.com)
[![AWS CDK](https://img.shields.io/badge/IaC-AWS_CDK-FF9900.svg)](https://aws.amazon.com/cdk/)

AegisClaims AI is a **production-grade, multi-tenant B2B SaaS platform** that provides AI-powered, autonomous insurance claims triage and decisioning for motor and property insurance.

## 🎯 Overview

AegisClaims AI automates the insurance claims lifecycle using a multi-agent AI system. It combines LLM-based reasoning (AWS Bedrock), ML-based fraud detection (AWS SageMaker), and RAG-powered policy retrieval (OpenSearch) to deliver explainable, auditable decisions with human-in-the-loop escalation.

### Business Value
- **92%+ Automation Rate**: Reduce manual claim processing
- **Sub-2s Decision Time**: Real-time AI-powered triage
- **Full Auditability**: Every decision is traceable and explainable
- **Multi-Tenant SaaS**: Serve multiple insurance providers from one platform

---

## ✨ Key Features

### 🤖 Autonomous AI Agent System
| Agent | Purpose | Technology |
|-------|---------|------------|
| **Claim Intake Agent** | Validates and normalizes claim data | Python |
| **Document Understanding Agent** | OCR + NLP for unstructured documents | AWS Bedrock |
| **Fraud Detection Agent** | ML-based anomaly detection | AWS SageMaker |
| **Coverage Reasoning Agent** | LLM + RAG for policy analysis | AWS Bedrock + OpenSearch |
| **Decision Agent** | Confidence-based decisioning with HITL | Python |

### 🏢 Multi-Tenancy
- Logical tenant isolation via `tenant_id`
- Tenant-specific AI thresholds and configurations
- Per-tenant prompt template versioning
- Feature flags per tenant

### 🔐 Security & Compliance
- OAuth2/OIDC authentication (AWS Cognito)
- Role-based access control (Admin, Adjuster, Supervisor, AI Ops)
- Per-tenant audit trails
- GDPR-compliant data handling

### 📊 AI Ops Dashboard
- Real-time automation rate monitoring
- Model drift detection
- LLM prompt drift tracking
- Latency and performance metrics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│  (Dashboard, Claim Details, AI Ops, Login/Tenant Selection)    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Interface Layer                     │
│           (REST APIs, DTOs, Audit Middleware)                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│    (Use Cases, Agent Orchestration, Tenant Context)            │
└─────────────────────────────────────────────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Domain Layer   │  │ Infrastructure  │  │   AI Services   │
│   (Entities,    │  │  (PostgreSQL,   │  │  (Bedrock LLM,  │
│  Value Objects) │  │ DynamoDB, S3)   │  │ SageMaker ML)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Clean Architecture Layers
- **Domain**: Pure business logic (no frameworks, no AWS SDKs)
- **Application**: Use cases, agents, ports/interfaces
- **Infrastructure**: AWS implementations, repositories
- **Interface**: REST APIs, DTOs, middleware

---

## 🛠️ Technology Stack

### Backend
| Component | Technology |
|-----------|------------|
| Runtime | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy (async) |
| Validation | Pydantic |

### Frontend
| Component | Technology |
|-----------|------------|
| Framework | React 18 |
| Language | TypeScript |
| Build Tool | Vite |
| Routing | React Router 6 |

### AWS Services
| Service | Purpose |
|---------|---------|
| Bedrock | LLM for coverage reasoning |
| SageMaker | Fraud detection ML model |
| Cognito | Authentication & RBAC |
| S3 | Document storage |
| DynamoDB | Agent state & idempotency |
| OpenSearch | Vector embeddings for RAG |
| RDS PostgreSQL | Transactional data |
| Redshift | Analytics & reporting |

### Infrastructure
| Tool | Purpose |
|------|---------|
| AWS CDK (Python) | Infrastructure as Code |
| Docker | Containerization |
| CloudWatch | Logging & monitoring |

---

## 📁 Project Structure

```
aegis-claims-ai-platform/
├── backend/
│   ├── domain/           # Entities, Value Objects, Domain Services
│   ├── application/      # Use Cases, Agents, Ports
│   ├── infrastructure/   # AWS adapters, Repositories
│   ├── interfaces/       # FastAPI routes, DTOs, Middleware
│   └── tests/            # Unit & integration tests
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API service layer
│   │   ├── context/      # React contexts (Auth)
│   │   └── auth/         # Protected routes
├── prompts/              # Versioned LLM prompt templates
├── evaluations/          # Model evaluation datasets
├── cdk/                  # AWS CDK infrastructure (Python)
├── docs/                 # Architecture documentation
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS Account with configured credentials
- PostgreSQL 15+

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

See [INSTRUCTIONS.md](./INSTRUCTIONS.md) for detailed setup and configuration.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Setup Instructions](./docs/INSTRUCTIONS.md) | Complete setup and running guide |
| [API Reference](./docs/api.md) | REST API endpoints and examples |
| [Architecture Guide](./docs/architecture.md) | System design and Clean Architecture |
| [AI Agents Guide](./docs/agents.md) | Autonomous agent system documentation |
| [Multi-Tenancy Guide](./docs/multi-tenancy.md) | Tenant isolation mechanisms |
| [Deployment Guide](./docs/deployment.md) | AWS production deployment |
| [Original Requirements](./docs/prompt.md) | Full project specification |

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test
```

---

## 📄 License

Proprietary - All Rights Reserved

---

## 🤝 Contributing

This is an internal enterprise system. Contact the platform team for contribution guidelines.

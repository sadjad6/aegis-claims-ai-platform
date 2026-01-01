# AegisClaims AI

AegisClaims AI is a B2B SaaS platform that provides AI-powered, autonomous insurance claims triage and decisioning for motor and property insurance.

## Key Features
- **Multi-Tenancy**: Strict data and configuration isolation for insurance providers.
- **Autonomous AI Agents**: Specialized agents for intake, document understanding, fraud detection, coverage reasoning, and decisions.
- **Explainable AI**: Full traceability and confidence scoring for every decision.
- **Clean Architecture**: Strictly decoupled domain logic for maintainability and testability.
- **SaaS Dashboard**: Comprehensive UI for claims management and AI performance monitoring.

## Tech Stack
- **Backend**: Python (FastAPI), SQLAlchemy, Boto3.
- **Frontend**: React, TypeScript, Vite.
- **AI/ML**: AWS Bedrock (LLMs), AWS SageMaker (Fraud ML), AWS OpenSearch (RAG).
- **Storage**: PostgreSQL (Transactional), DynamoDB (State), S3 (Files), Redshift (Analytics).
- **IaC**: Terraform.

## Project Structure
- `backend/`: Fast API backend following Clean Architecture.
- `frontend/`: React SaaS frontend.
- `terraform/`: Infrastructure provisioning.
- `prompts/`: LLM prompt templates and versioning.
- `docs/`: Technical documentation.

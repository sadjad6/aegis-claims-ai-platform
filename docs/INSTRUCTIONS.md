# AegisClaims AI - Setup & Running Instructions

This guide provides step-by-step instructions to set up and run AegisClaims AI locally for development and testing.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Environment Setup](#environment-setup)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [AWS Configuration](#aws-configuration)
7. [Database Setup](#database-setup)
8. [Running the Application](#running-the-application)
9. [Testing with Real Data](#testing-with-real-data)
10. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| npm | 9+ | Package management |
| PostgreSQL | 15+ | Primary database |
| AWS CLI | 2.x | AWS service access |
| AWS CDK | 2.x | Infrastructure provisioning |
| Git | 2.x | Version control |

### AWS Account Requirements

You need an AWS account with access to the following services:
- **AWS Bedrock** - LLM access (Claude 3 Sonnet)
- **AWS SageMaker** - ML model hosting
- **AWS Cognito** - User authentication
- **AWS S3** - Document storage
- **AWS DynamoDB** - State management
- **AWS OpenSearch** - Vector search
- **AWS RDS** - PostgreSQL (production)
- **AWS Redshift** - Analytics (optional)

---

## 2. System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 8 cores |
| Disk | 20 GB | 50 GB |
| OS | Windows 10/11, macOS 12+, Ubuntu 20.04+ | - |

---

## 3. Environment Setup

### Clone the Repository

```bash
git clone https://github.com/your-org/aegis-claims-ai-platform.git
cd aegis-claims-ai-platform
```

### Create Environment Files

#### Backend (.env)
Create `backend/.env`:

```env
# ===========================================
# DATABASE CONFIGURATION
# ===========================================
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/aegis_claims

# ===========================================
# AWS CONFIGURATION
# ===========================================
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# ===========================================
# AWS BEDROCK (LLM)
# ===========================================
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# ===========================================
# AWS SAGEMAKER (FRAUD DETECTION)
# ===========================================
SAGEMAKER_FRAUD_ENDPOINT=aegis-fraud-detection-dev

# ===========================================
# AWS S3 (DOCUMENT STORAGE)
# ===========================================
S3_BUCKET_NAME=aegis-claims-data-dev

# ===========================================
# AWS DYNAMODB (STATE)
# ===========================================
DYNAMODB_TABLE_NAME=aegis-claims-state-dev

# ===========================================
# AWS OPENSEARCH (VECTOR DB)
# ===========================================
OPENSEARCH_HOST=your-opensearch-domain.us-east-1.es.amazonaws.com

# ===========================================
# AWS COGNITO (AUTH)
# ===========================================
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=your_client_id_here

# ===========================================
# APPLICATION SETTINGS
# ===========================================
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

#### Frontend (.env)
Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
VITE_COGNITO_CLIENT_ID=your_client_id_here
VITE_COGNITO_DOMAIN=aegis-claims-dev
VITE_AWS_REGION=us-east-1
```

---

## 4. Backend Setup

### Step 1: Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
```

---

## 5. Frontend Setup

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Verify Installation

```bash
npm run build
```

---

## 6. AWS Configuration

### Step 1: Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter output format (json)
```

### Step 2: Verify AWS Access

```bash
aws sts get-caller-identity
```

### Step 3: Enable Bedrock Model Access

1. Go to AWS Console → Bedrock → Model access
2. Request access to **Anthropic Claude 3 Sonnet**
3. Wait for approval (usually instant)

### Step 4: Deploy Infrastructure (Optional)

For a fully functional deployment, provision AWS resources:

```bash
cd cdk

# Install CDK dependencies
pip install -r requirements.txt

# Synthesize CloudFormation templates
cdk synth --context env=dev

# Deploy infrastructure
cdk deploy --context env=dev --all
```

> ⚠️ **Note**: This will create billable AWS resources

---

## 7. Database Setup

### Option A: Local PostgreSQL (Recommended for Development)

#### Step 1: Create Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE aegis_claims;

-- Create user (optional)
CREATE USER aegis_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE aegis_claims TO aegis_user;
```

#### Step 2: Run Migrations

```bash
cd backend
alembic upgrade head
```

### Option B: Docker PostgreSQL

```bash
docker run -d \
  --name aegis-postgres \
  -e POSTGRES_DB=aegis_claims \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15
```

---

## 8. Running the Application

### Start Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The UI will be available at: `http://localhost:3000`

---

## 9. Testing with Real Data

### Step 1: Create Test Tenant

```bash
curl -X POST http://localhost:8000/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "test-tenant",
    "name": "Test Insurance Co."
  }'
```

### Step 2: Create Test Policy

```bash
curl -X POST http://localhost:8000/api/v1/policies \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: test-tenant" \
  -d '{
    "policy_number": "POL-TEST-001",
    "holder_name": "John Doe",
    "coverage_details": {
      "type": "comprehensive",
      "collision": true,
      "liability": true
    },
    "limit": {"amount": 50000, "currency": "USD"},
    "deductible": {"amount": 500, "currency": "USD"}
  }'
```

### Step 3: Submit Test Claim

```bash
curl -X POST http://localhost:8000/api/v1/claims \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: test-tenant" \
  -d '{
    "policy_number": "POL-TEST-001",
    "incident_date": "2025-12-28T10:30:00Z",
    "description": "Minor fender bender in parking lot. Front bumper damage.",
    "amount": {"amount": 2500, "currency": "USD"}
  }'
```

### Step 4: Check Claim Status

```bash
curl http://localhost:8000/api/v1/claims \
  -H "X-Tenant-ID: test-tenant"
```

### Login to Frontend

1. Open `http://localhost:3000`
2. Select "Test Insurance Co." tenant
3. View the claims dashboard
4. Click on a claim to see AI reasoning

---

## 10. Troubleshooting

### Common Issues

#### "Cannot find module 'vite'"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### "Database connection refused"
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify port 5432 is not in use

#### "AWS credentials not found"
```bash
aws configure list
# Ensure credentials are set
```

#### "Bedrock model access denied"
- Verify model access is enabled in AWS Console
- Check IAM permissions include `bedrock:InvokeModel`

#### "CORS errors in browser"
- Backend must include CORS middleware (already configured)
- Ensure frontend `.env` has correct `VITE_API_BASE_URL`

#### "Tenant not found" errors
- Every API request requires `X-Tenant-ID` header
- Create tenant first before other operations

### Getting Help

1. Check logs: `backend/logs/` or console output
2. Enable debug mode: Set `DEBUG=true` in `.env`
3. Check AWS CloudWatch for infrastructure issues
4. Review `docs/architecture.md` for system design

---

## 📞 Support

For issues or questions, contact the platform team or create an issue in the repository.

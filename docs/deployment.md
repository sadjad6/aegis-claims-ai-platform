# AegisClaims AI - Deployment Guide

This guide covers deploying AegisClaims AI to AWS production environments.

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CloudFront CDN                         │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    S3 (Frontend)        │     │   Application Load      │
│    Static Assets        │     │   Balancer (ALB)        │
└─────────────────────────┘     └─────────────────────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              ▼                               ▼
                    ┌─────────────────┐           ┌─────────────────┐
                    │  ECS Fargate    │           │  ECS Fargate    │
                    │  (Backend API)  │           │  (Backend API)  │
                    └─────────────────┘           └─────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   RDS Aurora    │ │    DynamoDB     │ │   OpenSearch    │
│   PostgreSQL    │ │   (Serverless)  │ │   (Managed)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## Prerequisites

- AWS Account with admin access
- Terraform 1.5+ installed
- Docker installed
- AWS CLI configured
- Domain name (optional)

---

## Step 1: Configure Terraform Variables

Create `terraform/environments/prod/terraform.tfvars`:

```hcl
env                = "prod"
region             = "us-east-1"
db_username        = "aegis_admin"
db_password        = "SecurePassword123!"  # Use secrets manager in production
vpc_cidr           = "10.0.0.0/16"
fraud_model_image  = "your-ecr-repo/fraud-model:latest"
callback_urls      = ["https://app.aegisclaims.com/callback"]
logout_urls        = ["https://app.aegisclaims.com/logout"]
```

---

## Step 2: Deploy Infrastructure

```bash
cd terraform/environments/prod

# Initialize
terraform init

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan
```

### Created Resources:
- VPC with public/private subnets
- RDS Aurora PostgreSQL cluster
- DynamoDB tables
- S3 buckets (documents, frontend)
- Cognito User Pool with RBAC groups
- OpenSearch domain
- SageMaker endpoint
- IAM roles with least privilege

---

## Step 3: Build and Push Docker Image

```bash
cd backend

# Build
docker build -t aegis-claims-api:latest .

# Tag for ECR
docker tag aegis-claims-api:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/aegis-claims-api:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/aegis-claims-api:latest
```

---

## Step 4: Deploy Backend to ECS

```bash
# Update ECS service (after Terraform creates the cluster)
aws ecs update-service \
  --cluster aegis-claims-prod \
  --service aegis-api \
  --force-new-deployment
```

---

## Step 5: Build and Deploy Frontend

```bash
cd frontend

# Build for production
npm run build

# Sync to S3
aws s3 sync dist/ s3://aegis-claims-frontend-prod --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id EXXXXX \
  --paths "/*"
```

---

## Step 6: Database Migration

```bash
# Run from bastion host or ECS task
alembic upgrade head
```

---

## Environment Variables (Production)

Set these in ECS Task Definition or Secrets Manager:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@aurora-cluster.xxx.us-east-1.rds.amazonaws.com:5432/aegis_claims
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
SAGEMAKER_FRAUD_ENDPOINT=aegis-fraud-detection-prod
S3_BUCKET_NAME=aegis-claims-data-prod
DYNAMODB_TABLE_NAME=aegis-claims-state-prod
OPENSEARCH_HOST=search-aegis-xxx.us-east-1.es.amazonaws.com
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=xxxxxxxxxxxx
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

---

## Multi-Environment Strategy

| Environment | Purpose | Terraform Workspace |
|-------------|---------|---------------------|
| dev | Development | `terraform/environments/dev` |
| staging | Pre-production testing | `terraform/environments/staging` |
| prod | Production | `terraform/environments/prod` |

---

## Monitoring & Alerts

### CloudWatch Dashboards

Create dashboards for:
- API latency (p50, p95, p99)
- Error rates by endpoint
- Bedrock/SageMaker invocation metrics
- Database connections

### Alarms

```bash
# Example: High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "aegis-high-error-rate" \
  --metric-name "5XXError" \
  --namespace "AWS/ApplicationELB" \
  --statistic Average \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

---

## Rollback Procedure

```bash
# Rollback ECS to previous task definition
aws ecs update-service \
  --cluster aegis-claims-prod \
  --service aegis-api \
  --task-definition aegis-api:PREVIOUS_VERSION

# Rollback database
alembic downgrade -1
```

---

## Security Checklist

- [ ] All secrets in AWS Secrets Manager
- [ ] VPC endpoints for AWS services
- [ ] WAF rules on ALB
- [ ] TLS 1.3 enforced
- [ ] Database encryption at rest
- [ ] S3 bucket policies restrict public access
- [ ] IAM roles follow least privilege
- [ ] Cognito MFA enabled for admins

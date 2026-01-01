# AegisClaims AI - Staging Environment

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "aegis-terraform-state"
    key    = "staging/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.region
}

# Variables
variable "region" {
  type        = string
  description = "AWS region for deployment"
  default     = "us-east-1"
}

variable "db_password" {
  type        = string
  description = "Password for the PostgreSQL database"
  sensitive   = true
}

variable "opensearch_password" {
  type        = string
  description = "Password for OpenSearch admin user"
  sensitive   = true
}

variable "redshift_password" {
  type        = string
  description = "Password for Redshift admin user"
  sensitive   = true
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"
  env    = "staging"
}

# S3 for Claims Documents
module "s3_claims_data" {
  source      = "../../modules/s3"
  bucket_name = "aegis-claims-data-staging"
  env         = "staging"
}

# DynamoDB for State Management
module "dynamodb_state" {
  source     = "../../modules/dynamodb"
  table_name = "aegis-claims-state-staging"
  env        = "staging"
}

# AI/ML Services (Bedrock, SageMaker)
module "ai_ml_services" {
  source = "../../modules/ai_ml"
  env    = "staging"
}

# Cognito for Authentication
module "cognito_auth" {
  source = "../../modules/cognito"
  env    = "staging"
}

# OpenSearch for Vector Database
module "opensearch" {
  source               = "../../modules/opensearch"
  env                  = "staging"
  region               = var.region
  instance_type        = "t3.medium.search"
  instance_count       = 2
  volume_size          = 50
  master_user_password = var.opensearch_password
}

# Redshift for Analytics
module "redshift" {
  source             = "../../modules/redshift"
  env                = "staging"
  master_password    = var.redshift_password
  node_type          = "dc2.large"
  number_of_nodes    = 1
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_ids = [aws_security_group.redshift.id]
}

# PostgreSQL RDS
resource "aws_db_instance" "postgres" {
  allocated_storage      = 50
  engine                 = "postgres"
  engine_version         = "15.3"
  instance_class         = "db.t3.small"
  db_name                = "aegis_claims"
  username               = "admin"
  password               = var.db_password
  parameter_group_name   = "default.postgres15"
  skip_final_snapshot    = true
  multi_az               = false
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  tags = {
    Environment = "staging"
    Project     = "AegisClaimsAI"
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "aegis-db-subnet-staging"
  subnet_ids = module.vpc.private_subnet_ids
}

resource "aws_security_group" "rds" {
  name        = "aegis-rds-sg-staging"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr]
  }
}

resource "aws_security_group" "redshift" {
  name        = "aegis-redshift-sg-staging"
  description = "Security group for Redshift"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr]
  }
}


# AegisClaims AI - Production Environment

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "aegis-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "aegis-terraform-locks"
    encrypt        = true
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
  env    = "prod"
}

# S3 for Claims Documents
module "s3_claims_data" {
  source      = "../../modules/s3"
  bucket_name = "aegis-claims-data-prod"
  env         = "prod"
}

# DynamoDB for State Management
module "dynamodb_state" {
  source     = "../../modules/dynamodb"
  table_name = "aegis-claims-state-prod"
  env        = "prod"
}

# AI/ML Services (Bedrock, SageMaker)
module "ai_ml_services" {
  source = "../../modules/ai_ml"
  env    = "prod"
}

# Cognito for Authentication
module "cognito_auth" {
  source = "../../modules/cognito"
  env    = "prod"
}

# OpenSearch for Vector Database (Production - HA)
module "opensearch" {
  source               = "../../modules/opensearch"
  env                  = "prod"
  region               = var.region
  instance_type        = "m6g.large.search"
  instance_count       = 3
  volume_size          = 100
  master_user_password = var.opensearch_password
}

# Redshift for Analytics (Production - Multi-node)
module "redshift" {
  source             = "../../modules/redshift"
  env                = "prod"
  master_password    = var.redshift_password
  node_type          = "dc2.large"
  number_of_nodes    = 2
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_ids = [aws_security_group.redshift.id]
}

# PostgreSQL RDS (Production - Multi-AZ)
resource "aws_db_instance" "postgres" {
  allocated_storage       = 100
  max_allocated_storage   = 500
  engine                  = "postgres"
  engine_version          = "15.3"
  instance_class          = "db.r6g.large"
  db_name                 = "aegis_claims"
  username                = "admin"
  password                = var.db_password
  parameter_group_name    = "default.postgres15"
  skip_final_snapshot     = false
  final_snapshot_identifier = "aegis-claims-final-snapshot"
  multi_az                = true
  publicly_accessible     = false
  storage_encrypted       = true
  vpc_security_group_ids  = [aws_security_group.rds.id]
  db_subnet_group_name    = aws_db_subnet_group.main.name
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:05:00-sun:06:00"

  tags = {
    Environment = "prod"
    Project     = "AegisClaimsAI"
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "aegis-db-subnet-prod"
  subnet_ids = module.vpc.private_subnet_ids
}

resource "aws_security_group" "rds" {
  name        = "aegis-rds-sg-prod"
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
  name        = "aegis-redshift-sg-prod"
  description = "Security group for Redshift"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr]
  }
}


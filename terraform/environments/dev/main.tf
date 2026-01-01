provider "aws" {
  region = var.region
}

module "vpc" {
  source = "../../modules/vpc"
  env    = "dev"
}

module "s3_claims_data" {
  source      = "../../modules/s3"
  bucket_name = "aegis-claims-data-dev"
  env         = "dev"
}

module "dynamodb_state" {
  source     = "../../modules/dynamodb"
  table_name = "aegis-claims-state-dev"
  env        = "dev"
}

module "ai_ml_services" {
  source = "../../modules/ai_ml"
  env    = "dev"
}

module "cognito_auth" {
  source = "../../modules/cognito"
  env    = "dev"
}

resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro"
  db_name              = "aegis_claims"
  username             = "admin"
  password             = var.db_password
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
}

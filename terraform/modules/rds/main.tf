resource "aws_db_subnet_group" "main" {
  name       = "aegis-db-subnet-${var.env}"
  subnet_ids = var.subnet_ids
}

resource "aws_db_instance" "postgres" {
  identifier        = "aegis-claims-db-${var.env}"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = var.instance_class
  allocated_storage = var.allocated_storage

  db_name  = "aegis_claims"
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = var.security_group_ids

  multi_az               = var.env == "prod" ? true : false
  publicly_accessible    = false
  skip_final_snapshot    = var.env != "prod"
  deletion_protection    = var.env == "prod"

  backup_retention_period = var.env == "prod" ? 7 : 1

  tags = {
    Environment = var.env
    Project     = "AegisClaimsAI"
  }
}

variable "env" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_ids" {
  type = list(string)
}

variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "allocated_storage" {
  type    = number
  default = 20
}

output "endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "database_name" {
  value = aws_db_instance.postgres.db_name
}

# Redshift Cluster for Analytics & SaaS Reporting

resource "aws_redshift_cluster" "analytics" {
  cluster_identifier = "aegis-analytics-${var.env}"
  database_name      = "aegis_analytics"
  master_username    = var.master_username
  master_password    = var.master_password
  node_type          = var.node_type
  cluster_type       = var.number_of_nodes > 1 ? "multi-node" : "single-node"
  number_of_nodes    = var.number_of_nodes

  vpc_security_group_ids = var.security_group_ids
  cluster_subnet_group_name = aws_redshift_subnet_group.main.name

  encrypted        = true
  skip_final_snapshot = var.env != "prod"
  final_snapshot_identifier = var.env == "prod" ? "aegis-analytics-final-${var.env}" : null

  # Enable enhanced VPC routing for better network control
  enhanced_vpc_routing = true

  # Automated snapshots
  automated_snapshot_retention_period = var.env == "prod" ? 7 : 1

  # Maintenance window
  preferred_maintenance_window = "sun:05:00-sun:06:00"

  iam_roles = [aws_iam_role.redshift.arn]

  tags = {
    Environment = var.env
    Project     = "AegisClaimsAI"
    Purpose     = "Analytics"
  }
}

resource "aws_redshift_subnet_group" "main" {
  name       = "aegis-redshift-subnet-${var.env}"
  subnet_ids = var.subnet_ids

  tags = {
    Environment = var.env
    Project     = "AegisClaimsAI"
  }
}

# IAM Role for Redshift to access S3 and other services
resource "aws_iam_role" "redshift" {
  name = "aegis-redshift-role-${var.env}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "redshift.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "redshift_s3" {
  name = "aegis-redshift-s3-policy-${var.env}"
  role = aws_iam_role.redshift.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::aegis-claims-data-${var.env}",
          "arn:aws:s3:::aegis-claims-data-${var.env}/*"
        ]
      }
    ]
  })
}

# Variables
variable "env" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

variable "master_username" {
  type      = string
  sensitive = true
  default   = "admin"
}

variable "master_password" {
  type      = string
  sensitive = true
}

variable "node_type" {
  type    = string
  default = "dc2.large"
}

variable "number_of_nodes" {
  type    = number
  default = 1
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_ids" {
  type    = list(string)
  default = []
}

# Outputs
output "cluster_endpoint" {
  value = aws_redshift_cluster.analytics.endpoint
}

output "cluster_identifier" {
  value = aws_redshift_cluster.analytics.cluster_identifier
}

output "database_name" {
  value = aws_redshift_cluster.analytics.database_name
}

output "iam_role_arn" {
  value = aws_iam_role.redshift.arn
}


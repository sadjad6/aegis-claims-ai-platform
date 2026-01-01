# DynamoDB Table for Claims and Tenant Data

resource "aws_dynamodb_table" "this" {
  name           = var.table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PK"
  range_key      = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  # Global Secondary Index for tenant-based queries
  attribute {
    name = "tenant_id"
    type = "S"
  }

  global_secondary_index {
    name            = "TenantIndex"
    hash_key        = "tenant_id"
    range_key       = "SK"
    projection_type = "ALL"
  }

  # Enable point-in-time recovery for production
  point_in_time_recovery {
    enabled = var.env == "prod" ? true : false
  }

  # Enable server-side encryption
  server_side_encryption {
    enabled = true
  }

  tags = {
    Environment = var.env
    Project     = "AegisClaimsAI"
  }
}

# Variables
variable "table_name" {
  type        = string
  description = "Name of the DynamoDB table"
}

variable "env" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

# Outputs
output "table_name" {
  value = aws_dynamodb_table.this.name
}

output "table_arn" {
  value = aws_dynamodb_table.this.arn
}

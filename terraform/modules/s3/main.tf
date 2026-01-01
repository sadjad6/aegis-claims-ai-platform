# S3 Bucket for Claims Documents and Data

resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags = {
    Environment = var.env
    Project     = "AegisClaimsAI"
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = var.env == "prod" ? "Enabled" : "Suspended"
  }
}

# Lifecycle rules for cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    id     = "archive-old-documents"
    status = "Enabled"

    filter {
      prefix = ""
    }

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 365
      storage_class = "GLACIER"
    }
  }
}

# Variables
variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket"
}

variable "env" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

# Outputs
output "bucket_name" {
  value = aws_s3_bucket.this.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.this.arn
}

output "bucket_domain_name" {
  value = aws_s3_bucket.this.bucket_domain_name
}

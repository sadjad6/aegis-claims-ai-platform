# OpenSearch Domain for Vector Database (RAG & Similarity Search)

resource "aws_opensearch_domain" "claims_vectors" {
  domain_name    = "aegis-claims-vectors-${var.env}"
  engine_version = "OpenSearch_2.11"

  cluster_config {
    instance_type            = var.instance_type
    instance_count           = var.instance_count
    dedicated_master_enabled = var.env == "prod" ? true : false
    dedicated_master_type    = var.env == "prod" ? "m6g.large.search" : null
    dedicated_master_count   = var.env == "prod" ? 3 : null
    zone_awareness_enabled   = var.env == "prod" ? true : false

    dynamic "zone_awareness_config" {
      for_each = var.env == "prod" ? [1] : []
      content {
        availability_zone_count = 2
      }
    }
  }

  ebs_options {
    ebs_enabled = true
    volume_size = var.volume_size
    volume_type = "gp3"
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = var.master_user_name
      master_user_password = var.master_user_password
    }
  }

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action   = "es:*"
        Resource = "arn:aws:es:${var.region}:${data.aws_caller_identity.current.account_id}:domain/aegis-claims-vectors-${var.env}/*"
        Condition = {
          IpAddress = {
            "aws:SourceIp" = var.allowed_ips
          }
        }
      }
    ]
  })

  tags = {
    Environment = var.env
    Project     = "AegisClaimsAI"
    Purpose     = "VectorDatabase"
  }
}

# Create index template for claims vectors
resource "null_resource" "create_index" {
  depends_on = [aws_opensearch_domain.claims_vectors]

  provisioner "local-exec" {
    command = <<-EOF
      curl -XPUT "https://${aws_opensearch_domain.claims_vectors.endpoint}/claims-vectors" \
        -u "${var.master_user_name}:${var.master_user_password}" \
        -H "Content-Type: application/json" \
        -d '{
          "settings": {
            "index": {
              "knn": true,
              "knn.algo_param.ef_search": 100
            }
          },
          "mappings": {
            "properties": {
              "tenant_id": { "type": "keyword" },
              "claim_id": { "type": "keyword" },
              "text": { "type": "text" },
              "embedding": {
                "type": "knn_vector",
                "dimension": 768,
                "method": {
                  "name": "hnsw",
                  "space_type": "cosinesimil",
                  "engine": "nmslib"
                }
              },
              "created_at": { "type": "date" }
            }
          }
        }'
    EOF
  }
}

data "aws_caller_identity" "current" {}

# Variables
variable "env" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  type    = string
  default = "t3.small.search"
}

variable "instance_count" {
  type    = number
  default = 1
}

variable "volume_size" {
  type    = number
  default = 20
}

variable "master_user_name" {
  type      = string
  sensitive = true
  default   = "admin"
}

variable "master_user_password" {
  type      = string
  sensitive = true
}

variable "allowed_ips" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}

# Outputs
output "domain_endpoint" {
  value = aws_opensearch_domain.claims_vectors.endpoint
}

output "domain_arn" {
  value = aws_opensearch_domain.claims_vectors.arn
}


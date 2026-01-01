# AWS Bedrock Model Access
resource "aws_bedrockagent_agent" "claims_reasoning" {
  agent_name              = "aegis-claims-reasoning-${var.env}"
  agent_resource_role_arn = aws_iam_role.bedrock_agent.arn
  foundation_model        = "anthropic.claude-3-sonnet-20240229-v1:0"
  idle_session_ttl_in_seconds = 600
  instruction             = "You are an insurance claims coverage reasoning agent."
}

# SageMaker Fraud Detection Endpoint
resource "aws_sagemaker_endpoint" "fraud_detection" {
  name                 = "aegis-fraud-detection-${var.env}"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.fraud.name
}

resource "aws_sagemaker_endpoint_configuration" "fraud" {
  name = "aegis-fraud-config-${var.env}"

  production_variants {
    variant_name           = "AllTraffic"
    model_name             = aws_sagemaker_model.fraud.name
    initial_instance_count = 1
    instance_type          = "ml.t2.medium"
  }
}

resource "aws_sagemaker_model" "fraud" {
  name               = "aegis-fraud-model-${var.env}"
  execution_role_arn = aws_iam_role.sagemaker.arn

  primary_container {
    image = var.fraud_model_image
  }
}

# IAM Roles
resource "aws_iam_role" "bedrock_agent" {
  name = "aegis-bedrock-agent-role-${var.env}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "bedrock.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role" "sagemaker" {
  name = "aegis-sagemaker-role-${var.env}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "sagemaker.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker_full" {
  role       = aws_iam_role.sagemaker.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

variable "env" {
  type = string
}

variable "fraud_model_image" {
  type    = string
  default = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.5-1"
}

output "fraud_endpoint_name" {
  value = aws_sagemaker_endpoint.fraud_detection.name
}

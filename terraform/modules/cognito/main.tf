resource "aws_cognito_user_pool" "main" {
  name = "aegis-claims-users-${var.env}"

  password_policy {
    minimum_length    = 12
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  mfa_configuration = "OPTIONAL"

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  schema {
    name                = "tenant_id"
    attribute_data_type = "String"
    mutable             = true
    required            = false

    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }

  schema {
    name                = "role"
    attribute_data_type = "String"
    mutable             = true
    required            = false

    string_attribute_constraints {
      min_length = 1
      max_length = 50
    }
  }

  tags = {
    Environment = var.env
    Project     = "AegisClaimsAI"
  }
}

resource "aws_cognito_user_pool_client" "web" {
  name         = "aegis-web-client-${var.env}"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  supported_identity_providers = ["COGNITO"]

  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls

  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  allowed_oauth_flows_user_pool_client = true
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "aegis-claims-${var.env}"
  user_pool_id = aws_cognito_user_pool.main.id
}

# RBAC Groups
resource "aws_cognito_user_group" "tenant_admin" {
  name         = "TenantAdmin"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Tenant administrators with full access"
}

resource "aws_cognito_user_group" "claims_adjuster" {
  name         = "ClaimsAdjuster"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Claims adjusters who review and process claims"
}

resource "aws_cognito_user_group" "supervisor" {
  name         = "Supervisor"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Supervisors who approve escalated decisions"
}

resource "aws_cognito_user_group" "ai_ops" {
  name         = "AIOps"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "AI Operations team for model monitoring"
}

variable "env" {
  type = string
}

variable "callback_urls" {
  type    = list(string)
  default = ["http://localhost:3000/callback"]
}

variable "logout_urls" {
  type    = list(string)
  default = ["http://localhost:3000/logout"]
}

output "user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "user_pool_client_id" {
  value = aws_cognito_user_pool_client.web.id
}

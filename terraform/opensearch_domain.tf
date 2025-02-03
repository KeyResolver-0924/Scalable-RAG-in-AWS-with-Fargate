# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

# IAM Policy for OpenSearch
data "aws_iam_policy_document" "opensearch_access_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions   = ["es:*"]
    resources = ["arn:aws:es:${var.aws_region}:${data.aws_caller_identity.current.account_id}:domain/${var.name}/*"]

  }
}

# Create the OpenSearch domain
resource "aws_opensearch_domain" "rag" {
  domain_name    = var.name
  engine_version = var.engine_version

  cluster_config {
    instance_type  = var.instance_type
    dedicated_master_enabled = var.dedicated_master_enabled
    instance_count = var.instance_count
    warm_enabled = var.cluster_config_warm_enabled
  }

  ebs_options {
    ebs_enabled = var.ebs_options_ebs_enabled
    volume_type = var.ebs_options_volume_type
    volume_size = var.volume_size
  }

  encrypt_at_rest {
    enabled = var.encrypt_at_rest
  }

  node_to_node_encryption {
    enabled = var.node_to_node_encryption
  }

  domain_endpoint_options {
    enforce_https       = var.enforce_https
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }


  advanced_security_options {
    enabled                        = var.advanced_security_options_enabled
    internal_user_database_enabled = var.advanced_security_options_enabled_internal_user
    master_user_options {
      master_user_name     = var.name
      master_user_password = aws_secretsmanager_secret_version.opensearch_master_password.secret_string
    }
  }

  access_policies = data.aws_iam_policy_document.opensearch_access_policy.json

  depends_on = [
    aws_secretsmanager_secret.opensearch_master_password,
    ]
  }


# Output the endpoint and credentials
output "opensearch_endpoint" {
  value = aws_opensearch_domain.rag.endpoint
}

output "master_password_secret_name" {
  value = aws_secretsmanager_secret.opensearch_master_password.name
}

output "opensearch_dashboard" {
  value = aws_opensearch_domain.rag.dashboard_endpoint
}
resource "random_password" "master_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
  min_numeric      = 1
  min_special      = 1
  min_upper        = 1
}

resource "aws_secretsmanager_secret" "opensearch_master_password" {
  name_prefix = var.name
  description = "Master password for OpenSearch domain" 
}

resource "aws_secretsmanager_secret_version" "opensearch_master_password" {
  secret_id     = aws_secretsmanager_secret.opensearch_master_password.id
  secret_string = random_password.master_password.result
}

output "secret_name" {
  value = aws_secretsmanager_secret.opensearch_master_password.name
}
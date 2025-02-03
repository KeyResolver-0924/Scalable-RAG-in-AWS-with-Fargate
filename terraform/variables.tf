variable "aws_region" {
  description = "The AWS region to deploy the OpenSearch domain in"
  type        = string
  default     = "eu-central-1"
}

variable "name" {
  description = "The name of the OpenSearch domain"
  type        = string
  default     = "rag"
}

variable "engine_version" {
  description = "The version of OpenSearch to deploy"
  type        = string
  default     = "OpenSearch_2.15"
}

variable "instance_type" {
  description = "The instance type for the OpenSearch cluster"
  type        = string
  default     = "r6g.large.search"
}

variable "instance_count" {
  description = "The number of instances in the OpenSearch cluster"
  type        = number
  default     = 2
}

variable "node_to_node_encryption" {
  default     = true
  description = "Opensearch node to node encryption"
}

variable "encrypt_at_rest" {
  default     = true
  description = "Opensearch encryption at rest"
}

variable "enforce_https" {
  default     = true
  description = "OpenSearch domain enforce https"
}

variable "dedicated_master_enabled" {
  default = false
}

variable "cluster_config_warm_enabled" {
  default = false
}

variable "ebs_options_ebs_enabled" {
  default = true
}

variable "volume_size" {
  description = "The size of the EBS volume for each instance (in GB)"
  type        = number
  default     = 100
}

variable "ebs_options_volume_type" {
  default = "gp3"
}


variable "advanced_security_options_enabled" {
  default = true
}

variable "advanced_security_options_enabled_internal_user" {
  default = true
}
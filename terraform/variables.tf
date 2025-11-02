variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Resource name prefix"
  type        = string
  default     = "cicd-benchmark"
}

variable "instance_type" {
  description = "EC2 instance size"
  type        = string
  default     = "t3.small"
}

variable "ssh_cidr" {
  description = "CIDR allowed for SSH (use your IP/32 or 0.0.0.0/32 to disable effectively)"
  type        = string
  default     = "0.0.0.0/32"
}

variable "github_user" {
  description = "GitHub username (public repo assumed)"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "secret_key" {
  description = "Django SECRET_KEY"
  type        = string
}

variable "bench_api_key" {
  description = "API key for ingest endpoint"
  type        = string
}

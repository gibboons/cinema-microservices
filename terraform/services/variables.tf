variable "aws_region" {
  type    = string
  default = "eu-north-1"
}

variable "state_bucket" {
  description = "Nazwa bucketu S3 przechowującego stan Terraform"
  type        = string
}

variable "project_name" {
  type    = string
  default = "cinema"
}

variable "image_tag" {
  description = "Docker image tag do wdrożenia (np. latest, v1.2.0, git SHA)"
  type        = string
  default     = "latest"
}

variable "amqp_url" {
  description = "CloudAMQP connection URL (amqps://user:pass@host/vhost)"
  type        = string
  sensitive   = true
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID używany przez film_upload_service do S3"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key używany przez film_upload_service do S3"
  type        = string
  sensitive   = true
}

variable "aws_s3_bucket" {
  description = "Nazwa bucketu S3 na pliki filmowe"
  type        = string
}

variable "task_cpu" {
  description = "CPU units dla każdego zadania Fargate (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Pamięć RAM w MB dla każdego zadania Fargate"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Liczba replik każdego serwisu"
  type        = number
  default     = 1
}

# ── RDS PostgreSQL ─────────────────────────────────────────────────────────────
variable "rds_host" {
  description = "Endpoint RDS dla film_upload_service"
  type        = string
}

variable "rds_metadata_host" {
  description = "Endpoint RDS dla metadata_service"
  type        = string
}

variable "rds_rating_host" {
  description = "Endpoint RDS dla rating_service"
  type        = string
}

variable "rds_password" {
  description = "Hasło do RDS PostgreSQL"
  type        = string
  sensitive   = true
}

# ── DynamoDB ──────────────────────────────────────────────────────────────────
variable "dynamodb_reviews_table" {
  type    = string
  default = "reviews"
}

variable "dynamodb_transcoding_table" {
  type    = string
  default = "transcoding_jobs"
}

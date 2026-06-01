variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Prefix applied to all resource names"
  type        = string
  default     = "cinema"
}

variable "environment" {
  description = "Deployment environment tag"
  type        = string
  default     = "production"
}

variable "db_password" {
  description = "Hasło do RDS PostgreSQL"
  type        = string
  sensitive   = true
}

variable "s3_films_bucket" {
  description = "Nazwa bucketu S3 na pliki filmowe"
  type        = string
  default     = "cinema-serv-gibek"
}

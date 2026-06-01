output "vpc_id" {
  description = "ID of the main VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets (used by ALB and ECS)"
  value       = aws_subnet.public[*].id
}

output "alb_security_group_id" {
  description = "Security group ID for the Application Load Balancer"
  value       = aws_security_group.alb.id
}

output "ecs_security_group_id" {
  description = "Security group ID for ECS tasks"
  value       = aws_security_group.ecs_tasks.id
}

output "ecr_repository_urls" {
  description = "ECR repository URLs keyed by service name"
  value       = { for k, v in aws_ecr_repository.services : k => v.repository_url }
}

output "ecs_execution_role_arn" {
  description = "ARN of the ECS task execution IAM role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task IAM role (runtime permissions)"
  value       = aws_iam_role.ecs_task.arn
}

output "aws_account_id" {
  description = "AWS Account ID (used to build ECR image URIs)"
  value       = data.aws_caller_identity.current.account_id
}

output "rds_film_upload_endpoint" {
  description = "Endpoint RDS dla film_upload_service"
  value       = aws_db_instance.main.address
}

output "rds_metadata_endpoint" {
  description = "Endpoint RDS dla metadata_service"
  value       = aws_db_instance.metadata.address
}

output "rds_rating_endpoint" {
  description = "Endpoint RDS dla rating_service"
  value       = aws_db_instance.rating.address
}

output "dynamodb_reviews_table" {
  value = aws_dynamodb_table.reviews.name
}

output "dynamodb_transcoding_table" {
  value = aws_dynamodb_table.transcoding_jobs.name
}

output "s3_films_bucket" {
  description = "Nazwa bucketu S3 na pliki filmowe"
  value       = aws_s3_bucket.films.bucket
}

data "aws_caller_identity" "current" {}

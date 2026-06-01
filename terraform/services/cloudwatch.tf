resource "aws_cloudwatch_log_group" "services" {
  for_each = toset([
    "film_upload_service",
    "metadata_service",
    "transcoding_service",
    "review_service",
    "rating_service",
  ])

  name              = "/ecs/${var.project_name}/${each.key}"
  retention_in_days = 7
}

locals {
  common_env = [
    { name = "AMQP_URL",               value = var.amqp_url },
    { name = "AWS_ACCESS_KEY_ID",       value = var.aws_access_key_id },
    { name = "AWS_SECRET_ACCESS_KEY",   value = var.aws_secret_access_key },
    { name = "AWS_REGION",              value = var.aws_region },
    { name = "AWS_S3_BUCKET",           value = var.aws_s3_bucket },
    { name = "FILM_UPLOAD_DB_HOST",     value = var.rds_host },
    { name = "FILM_UPLOAD_DB_PORT",     value = "5432" },
    { name = "FILM_UPLOAD_DB_NAME",     value = "film_upload_db" },
    { name = "FILM_UPLOAD_DB_USER",     value = "postgres" },
    { name = "FILM_UPLOAD_DB_PASSWORD", value = var.rds_password },
    { name = "METADATA_DB_HOST",        value = var.rds_metadata_host },
    { name = "METADATA_DB_PORT",        value = "5432" },
    { name = "METADATA_DB_NAME",        value = "metadata_db" },
    { name = "METADATA_DB_USER",        value = "postgres" },
    { name = "METADATA_DB_PASSWORD",    value = var.rds_password },
    { name = "RATING_DB_HOST",          value = var.rds_rating_host },
    { name = "RATING_DB_PORT",          value = "5432" },
    { name = "RATING_DB_NAME",          value = "rating_db" },
    { name = "RATING_DB_USER",          value = "postgres" },
    { name = "RATING_DB_PASSWORD",      value = var.rds_password },
    { name = "DYNAMODB_REVIEWS_TABLE",     value = var.dynamodb_reviews_table },
    { name = "DYNAMODB_TRANSCODING_TABLE", value = var.dynamodb_transcoding_table },
  ]
}

# ── film_upload_service (port 8001) ──────────────────────────────────────────

resource "aws_ecs_task_definition" "film_upload" {
  family                   = "${var.project_name}-film-upload"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = local.infra.ecs_execution_role_arn
  task_role_arn            = local.infra.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "film_upload_service"
      image     = "${local.ecr_base}/film_upload_service:${var.image_tag}"
      essential = true

      portMappings = [{ containerPort = 8001, protocol = "tcp" }]

      command = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

      environment = local.common_env

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.services["film_upload_service"].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "film_upload" {
  name            = "${var.project_name}-film-upload"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.film_upload.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = local.infra.public_subnet_ids
    security_groups  = [local.infra.ecs_security_group_id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.film_upload.arn
    container_name   = "film_upload_service"
    container_port   = 8001
  }

  depends_on = [aws_lb_listener_rule.film_upload]
}

# ── metadata_service (port 8002, brak ALB – consumer RabbitMQ) ───────────────

resource "aws_ecs_task_definition" "metadata" {
  family                   = "${var.project_name}-metadata"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = local.infra.ecs_execution_role_arn
  task_role_arn            = local.infra.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "metadata_service"
      image     = "${local.ecr_base}/metadata_service:${var.image_tag}"
      essential = true

      portMappings = [{ containerPort = 8002, protocol = "tcp" }]

      command = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

      environment = local.common_env

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.services["metadata_service"].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "metadata" {
  name            = "${var.project_name}-metadata"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.metadata.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = local.infra.public_subnet_ids
    security_groups  = [local.infra.ecs_security_group_id]
    assign_public_ip = true
  }
}

# ── transcoding_service (port 8003, brak ALB – consumer RabbitMQ) ────────────

resource "aws_ecs_task_definition" "transcoding" {
  family                   = "${var.project_name}-transcoding"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = local.infra.ecs_execution_role_arn
  task_role_arn            = local.infra.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "transcoding_service"
      image     = "${local.ecr_base}/transcoding_service:${var.image_tag}"
      essential = true

      portMappings = [{ containerPort = 8003, protocol = "tcp" }]

      command = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]

      environment = local.common_env

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.services["transcoding_service"].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "transcoding" {
  name            = "${var.project_name}-transcoding"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.transcoding.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = local.infra.public_subnet_ids
    security_groups  = [local.infra.ecs_security_group_id]
    assign_public_ip = true
  }
}

# ── review_service (port 8004) ────────────────────────────────────────────────

resource "aws_ecs_task_definition" "review" {
  family                   = "${var.project_name}-review"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = local.infra.ecs_execution_role_arn
  task_role_arn            = local.infra.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "review_service"
      image     = "${local.ecr_base}/review_service:${var.image_tag}"
      essential = true

      portMappings = [{ containerPort = 8004, protocol = "tcp" }]

      command = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]

      environment = local.common_env

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.services["review_service"].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "review" {
  name            = "${var.project_name}-review"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.review.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = local.infra.public_subnet_ids
    security_groups  = [local.infra.ecs_security_group_id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.review.arn
    container_name   = "review_service"
    container_port   = 8004
  }

  depends_on = [aws_lb_listener_rule.review]
}

# ── rating_service (port 8005) ────────────────────────────────────────────────

resource "aws_ecs_task_definition" "rating" {
  family                   = "${var.project_name}-rating"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = local.infra.ecs_execution_role_arn
  task_role_arn            = local.infra.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "rating_service"
      image     = "${local.ecr_base}/rating_service:${var.image_tag}"
      essential = true

      portMappings = [{ containerPort = 8005, protocol = "tcp" }]

      command = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]

      environment = local.common_env

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.services["rating_service"].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "rating" {
  name            = "${var.project_name}-rating"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.rating.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = local.infra.public_subnet_ids
    security_groups  = [local.infra.ecs_security_group_id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.rating.arn
    container_name   = "rating_service"
    container_port   = 8005
  }

  depends_on = [aws_lb_listener_rule.rating]
}

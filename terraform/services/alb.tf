resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [local.infra.alb_security_group_id]
  subnets            = local.infra.public_subnet_ids

  tags = { Name = "${var.project_name}-alb" }
}


resource "aws_lb_target_group" "film_upload" {
  name        = "${var.project_name}-film-upload-tg"
  port        = 8001
  protocol    = "HTTP"
  vpc_id      = local.infra.vpc_id
  target_type = "ip"

  health_check {
    path                = "/docs"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_target_group" "review" {
  name        = "${var.project_name}-review-tg"
  port        = 8004
  protocol    = "HTTP"
  vpc_id      = local.infra.vpc_id
  target_type = "ip"

  health_check {
    path                = "/docs"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_target_group" "rating" {
  name        = "${var.project_name}-rating-tg"
  port        = 8005
  protocol    = "HTTP"
  vpc_id      = local.infra.vpc_id
  target_type = "ip"

  health_check {
    path                = "/docs"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}


resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "Cinema Microservices – invalid path"
      status_code  = "404"
    }
  }
}

resource "aws_lb_listener_rule" "film_upload" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10

  condition {
    path_pattern { values = ["/films*"] }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.film_upload.arn
  }
}

resource "aws_lb_listener_rule" "review" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 20

  condition {
    path_pattern { values = ["/reviews*"] }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.review.arn
  }
}

resource "aws_lb_listener_rule" "rating" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 30

  condition {
    path_pattern { values = ["/ratings*", "/recommendations*"] }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.rating.arn
  }
}

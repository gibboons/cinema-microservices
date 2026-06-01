resource "aws_dynamodb_table" "reviews" {
  name         = "reviews"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name        = "reviews"
    Environment = var.environment
    Service     = "review_service"
  }
}

resource "aws_dynamodb_table" "transcoding_jobs" {
  name         = "transcoding_jobs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name        = "transcoding_jobs"
    Environment = var.environment
    Service     = "transcoding_service"
  }
}

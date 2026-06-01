resource "aws_s3_bucket" "films" {
  bucket = var.s3_films_bucket

  tags = {
    Name        = var.s3_films_bucket
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "films" {
  bucket = aws_s3_bucket.films.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "films" {
  bucket = aws_s3_bucket.films.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "films" {
  bucket = aws_s3_bucket.films.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

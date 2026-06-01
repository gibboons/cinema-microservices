terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Partial backend configuration – bucket podaj przy terraform init:
  # terraform init -backend-config="bucket=TWOJ_BUCKET" -backend-config="region=eu-north-1"
  #
  # Utwórz bucket ręcznie przed pierwszym init:
  # aws s3 mb s3://TWOJ_BUCKET --region eu-north-1
  backend "s3" {
    key = "infrastructure/terraform.tfstate"
  }
}

provider "aws" {
  region = var.aws_region
}

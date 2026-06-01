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
  backend "s3" {
    key = "services/terraform.tfstate"
  }
}

provider "aws" {
  region = var.aws_region
}

data "terraform_remote_state" "infrastructure" {
  backend = "s3"
  config = {
    bucket = var.state_bucket
    key    = "infrastructure/terraform.tfstate"
    region = var.aws_region
  }
}

locals {
  infra       = data.terraform_remote_state.infrastructure.outputs
  account_id  = local.infra.aws_account_id
  ecr_base    = "${local.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/cinema"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # It is a good practice to specify the required Terraform version
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.aws_region
}
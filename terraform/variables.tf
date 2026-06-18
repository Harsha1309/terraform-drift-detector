variable "aws_region" {
  description = "The AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "The name of the S3 bucket. Must be globally unique."
  type        = string
  default     = "my-unique-starter-bucket-123452323284" # Change this to something unique
}

variable "tf_state_bucket" {
  description = "The S3 bucket name for storing Terraform state"
  type        = string
  default     = "terraform-state-bucket-unique-name" # Change this to something unique
}

variable "tf_state_key" {
  description = "The S3 key path for the Terraform state file"
  type        = string
  default     = "prod/terraform.tfstate"
}

variable "tf_lock_table" {
  description = "The DynamoDB table name for Terraform state locking"
  type        = string
  default     = "terraform-lock-table"
}
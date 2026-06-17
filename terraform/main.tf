resource "aws_s3_bucket" "my_first_bucket" {
  bucket = var.bucket_name

  tags = {
    Environment = "Dev"
    ManagedBy   = "Terraform"
  }
}

# Ensure the bucket is private by blocking public access
resource "aws_s3_bucket_public_access_block" "bucket_privacy" {
  bucket = aws_s3_bucket.my_first_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
terraform {
  backend "s3" {
    # These values will be provided via -backend-config flags in GitHub Actions
    # Or set as environment variables: AWS_BACKEND_BUCKET, AWS_BACKEND_KEY, AWS_BACKEND_DYNAMODB_TABLE
    encrypt = true
  }
}

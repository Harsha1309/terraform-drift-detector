# S3 Backend Setup Guide

This project uses AWS S3 and DynamoDB for remote Terraform state management.

## Prerequisites

### 1. Create S3 Bucket for State Storage

```bash
aws s3api create-bucket \
  --bucket terraform-state-bucket-unique-name \
  --region us-east-1
```

Enable versioning (recommended for state recovery):
```bash
aws s3api put-bucket-versioning \
  --bucket terraform-state-bucket-unique-name \
  --versioning-configuration Status=Enabled
```

Enable encryption:
```bash
aws s3api put-bucket-encryption \
  --bucket terraform-state-bucket-unique-name \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

### 2. Create DynamoDB Table for State Locking

```bash
aws dynamodb create-table \
  --table-name terraform-lock-table \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1
```

## GitHub Actions Secrets

Add the following secrets to your GitHub repository (Settings > Secrets and variables > Actions):

- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret access key
- `TF_STATE_BUCKET` - Name of your S3 bucket (e.g., `terraform-state-bucket-unique-name`)
- `TF_STATE_KEY` - Path for state file (e.g., `prod/terraform.tfstate`)
- `TF_LOCK_TABLE` - Name of your DynamoDB table (e.g., `terraform-lock-table`)

## Local Development

Create a `terraform/terraform.tfvars` file with your values (copy from `terraform.tfvars.example`):

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform/terraform.tfvars with your actual values
```

Then initialize Terraform locally:

```bash
cd terraform
terraform init \
  -backend-config="bucket=YOUR_BUCKET_NAME" \
  -backend-config="key=prod/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="dynamodb_table=terraform-lock-table"
```

## Benefits

- **Remote State**: State is stored centrally in S3, accessible by your team
- **State Locking**: DynamoDB prevents concurrent modifications to state
- **Versioning**: S3 versioning allows state recovery if needed
- **Encryption**: State is encrypted at rest in S3

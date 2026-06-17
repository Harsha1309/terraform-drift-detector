import boto3
import anyio
from typing import List, Dict, Any
from providers.base import CloudFetcher
from core.models import ResourceModel

class AWSCloudFetcher(CloudFetcher):
    """Fetches real-time infrastructure state from AWS APIs."""

    async def fetch_resources(self, config: Dict[str, Any]) -> List[ResourceModel]:
        region = config.get("region", "us-east-1")
        resource_types = config.get("resource_types", ["aws_s3_bucket"])
        
        resources: List[ResourceModel] = []
        
        # Orchestrate calls based on configured target types
        if "aws_s3_bucket" in resource_types:
            s3_resources = await anyio.to_thread.run_sync(self._fetch_s3_buckets, region)
            resources.extend(s3_resources)
            
        return resources
    
    def _fetch_s3_buckets(self, region: str) -> List[ResourceModel]:
        s3_client = boto3.client('s3', region_name=region)
        normalized_resources: List[ResourceModel] = []
        
        try:
            response = s3_client.list_buckets()
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                
                # 1. Base Attributes
                attributes = {
                    "bucket": bucket_name,
                    "arn": f"arn:aws:s3:::{bucket_name}"
                }

                # 2. Fetch Tags
                tags = {}
                try:
                    tagging_resp = s3_client.get_bucket_tagging(Bucket=bucket_name)
                    tags = {t['Key']: t['Value'] for t in tagging_resp.get('TagSet', [])}
                except s3_client.exceptions.ClientError:
                    pass 

                # ---------------------------------------------------------
                # 3. ADVANCED CONFIGURATIONS (The Drift Catchers)
                # ---------------------------------------------------------
                
                # A. Public Access Block (PAB)
                try:
                    pab_response = s3_client.get_public_access_block(Bucket=bucket_name)
                    pab_config = pab_response.get("PublicAccessBlockConfiguration", {})
                    attributes["block_public_acls"] = pab_config.get("BlockPublicAcls")
                    attributes["block_public_policy"] = pab_config.get("BlockPublicPolicy")
                    attributes["ignore_public_acls"] = pab_config.get("IgnorePublicAcls")
                    attributes["restrict_public_buckets"] = pab_config.get("RestrictPublicBuckets")
                except s3_client.exceptions.ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchPublicAccessBlockConfiguration':
                        pass

                # B. Versioning
                try:
                    versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
                    attributes["versioning"] = versioning.get("Status", "Disabled")
                except s3_client.exceptions.ClientError:
                    pass

                # C. Server-Side Encryption
                try:
                    encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
                    rules = encryption.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
                    attributes["server_side_encryption"] = rules
                except s3_client.exceptions.ClientError:
                    attributes["server_side_encryption"] = []

                # D. CORS Rules
                try:
                    cors = s3_client.get_bucket_cors(Bucket=bucket_name)
                    attributes["cors_rules"] = cors.get('CORSRules', [])
                except s3_client.exceptions.ClientError:
                    attributes["cors_rules"] = []

                # E. Lifecycle Rules
                try:
                    lifecycle = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                    attributes["lifecycle_rules"] = lifecycle.get('Rules', [])
                except s3_client.exceptions.ClientError:
                    attributes["lifecycle_rules"] = []

                # F. Server Access Logging
                try:
                    logging = s3_client.get_bucket_logging(Bucket=bucket_name)
                    attributes["logging"] = logging.get('LoggingEnabled', {})
                except s3_client.exceptions.ClientError:
                    attributes["logging"] = {}

                # G. Static Website Hosting
                try:
                    website = s3_client.get_bucket_website(Bucket=bucket_name)
                    attributes["website"] = {
                        "index_document": website.get("IndexDocument", {}),
                        "error_document": website.get("ErrorDocument", {})
                    }
                except s3_client.exceptions.ClientError:
                    attributes["website"] = {}

                # ---------------------------------------------------------
                
                normalized_resources.append(ResourceModel(
                    resource_id=bucket_name,
                    resource_type="aws_s3_bucket",
                    provider="aws",
                    region=region,
                    attributes=attributes,
                    tags=tags
                ))
                
        except Exception as e:
            print(f"Error fetching S3 buckets: {e}")
            
        return normalized_resources
    
    # def _fetch_s3_buckets(self, region: str) -> List[ResourceModel]:
    #     s3_client = boto3.client('s3', region_name=region)
    #     normalized_resources: List[ResourceModel] = []
        
    #     try:
    #         response = s3_client.list_buckets()
    #         for bucket in response.get('Buckets', []):
    #             bucket_name = bucket['Name']
                
    #             # 1. Fetch Tags
    #             tags = {}
    #             try:
    #                 tagging_resp = s3_client.get_bucket_tagging(Bucket=bucket_name)
    #                 tags = {t['Key']: t['Value'] for t in tagging_resp.get('TagSet', [])}
    #             except s3_client.exceptions.ClientError:
    #                 pass 
                
    #             # 2. Base Attributes
    #             attributes = {
    #                 "bucket": bucket_name,
    #                 "arn": f"arn:aws:s3:::{bucket_name}"
    #             }

    #             # ---------------------------------------------------------
    #             # 3. NEW: Fetch Public Access Block (PAB) Configuration
    #             # ---------------------------------------------------------
    #             try:
    #                 pab_response = s3_client.get_public_access_block(Bucket=bucket_name)
    #                 # AWS returns a dictionary of 4 boolean values
    #                 pab_config = pab_response.get("PublicAccessBlockConfiguration", {})
                    
    #                 # Add them to our normalized attributes
    #                 attributes["block_public_acls"] = pab_config.get("BlockPublicAcls")
    #                 attributes["block_public_policy"] = pab_config.get("BlockPublicPolicy")
    #                 attributes["ignore_public_acls"] = pab_config.get("IgnorePublicAcls")
    #                 attributes["restrict_public_buckets"] = pab_config.get("RestrictPublicBuckets")
                    
    #             except s3_client.exceptions.ClientError as e:
    #                 # If no PAB configuration exists at all, AWS throws a specific error
    #                 if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
    #                     attributes["public_access_block"] = "None"
    #                 else:
    #                     print(f"Permission denied reading PAB for {bucket_name}")
    #             # ---------------------------------------------------------
                
    #             normalized_resources.append(ResourceModel(
    #                 resource_id=bucket_name,
    #                 resource_type="aws_s3_bucket",
    #                 provider="aws",
    #                 region=region,
    #                 attributes=attributes,
    #                 tags=tags
    #             ))
    #     except Exception as e:
    #         print(f"Error fetching S3 buckets: {e}")
            
    #     return normalized_resources

    # def _fetch_s3_buckets(self, region: str) -> List[ResourceModel]:
    #     s3_client = boto3.client('s3', region_name=region)
    #     normalized_resources: List[ResourceModel] = []
        
    #     try:
    #         response = s3_client.list_buckets()
    #         for bucket in response.get('Buckets', []):
    #             bucket_name = bucket['Name']
                
    #             # Fetch tags for distinct classification in Phase 2
    #             tags = {}
    #             try:
    #                 tagging_resp = s3_client.get_bucket_tagging(Bucket=bucket_name)
    #                 tags = {t['Key']: t['Value'] for t in tagging_resp.get('TagSet', [])}
    #             except s3_client.exceptions.ClientError:
    #                 pass # Ignore if no tags present or access denied
                
    #             # Mock structure mirroring the essential structural configuration
    #             attributes = {
    #                 "bucket": bucket_name,
    #                 "arn": f"arn:aws:s3:::{bucket_name}"
    #             }
                
    #             normalized_resources.append(ResourceModel(
    #                 resource_id=bucket_name,
    #                 resource_type="aws_s3_bucket",
    #                 provider="aws",
    #                 region=region,
    #                 attributes=attributes,
    #                 tags=tags
    #             ))
    #     except Exception as e:
    #         # In production, route to loggers or track missing execution contexts gracefully
    #         print(f"Error fetching S3 buckets: {e}")
            
    #     return normalized_resources
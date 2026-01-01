import boto3
from typing import Dict, Any
from ..application.ports import StorageService


class S3StorageService(StorageService):
    """S3 implementation of StorageService with tenant isolation."""

    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.s3 = boto3.client("s3", region_name=region)
        self.bucket_name = bucket_name

    async def upload(self, file_content: bytes, filename: str, tenant_id: str) -> str:
        """Upload file with tenant-scoped key prefix."""
        key = f"{tenant_id}/raw/{filename}"
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_content,
            Metadata={"tenant_id": tenant_id},
            ServerSideEncryption="AES256"
        )
        return key

    async def download(self, key: str, tenant_id: str) -> bytes:
        """Download file content, ensuring tenant isolation."""
        # Verify the key belongs to the tenant
        if not key.startswith(f"{tenant_id}/"):
            raise PermissionError(f"Access denied to key {key} for tenant {tenant_id}")

        response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        return response["Body"].read()

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for temporary access."""
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expires_in
        )

    async def list_by_tenant(self, tenant_id: str, prefix: str = "") -> list:
        """List all objects for a tenant with optional prefix."""
        full_prefix = f"{tenant_id}/{prefix}"
        response = self.s3.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=full_prefix
        )
        return [obj["Key"] for obj in response.get("Contents", [])]

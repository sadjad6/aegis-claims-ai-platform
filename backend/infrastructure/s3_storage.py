import boto3
from .ports import StorageService
from typing import Dict, Any

class S3StorageService(StorageService):
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.s3 = boto3.client("s3", region_name=region)
        self.bucket_name = bucket_name

    async def upload(self, file_content: bytes, filename: str, tenant_id: str) -> str:
        key = f"{tenant_id}/{filename}"
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_content,
            Metadata={"tenant_id": tenant_id}
        )
        return key

    async def get_url(self, key: str) -> str:
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=3600
        )

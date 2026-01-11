"""
S3 Bucket Construct for AegisClaims AI Platform.

Creates an S3 bucket with encryption, versioning, public access blocking,
and lifecycle policies matching the original Terraform S3 module.
"""

from constructs import Construct
from aws_cdk import (
    aws_s3 as s3,
    Duration,
    RemovalPolicy,
    CfnOutput,
)


class S3BucketConstruct(Construct):
    """
    S3 bucket construct for claims documents and data.
    
    Features:
    - Block all public access
    - Server-side encryption (AES256)
    - Versioning (enabled for prod, suspended otherwise)
    - Lifecycle policies for cost optimization
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket_name: str,
        env_name: str,
        versioning_enabled: bool = False,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create S3 bucket
        self.bucket = s3.Bucket(
            self,
            "Bucket",
            bucket_name=bucket_name,
            encryption=s3.BucketEncryption.S3_MANAGED,  # AES256
            versioned=versioning_enabled,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN if env_name == "prod" else RemovalPolicy.DESTROY,
            auto_delete_objects=env_name != "prod",
        )
        
        # Add lifecycle rules for cost optimization
        self.bucket.add_lifecycle_rule(
            id="archive-old-documents",
            enabled=True,
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                    transition_after=Duration.days(90),
                ),
                s3.Transition(
                    storage_class=s3.StorageClass.GLACIER,
                    transition_after=Duration.days(365),
                ),
            ],
        )
        
        # Outputs
        CfnOutput(
            self,
            "BucketName",
            value=self.bucket.bucket_name,
            description="S3 Bucket Name",
        )
        
        CfnOutput(
            self,
            "BucketArn",
            value=self.bucket.bucket_arn,
            description="S3 Bucket ARN",
        )
    
    @property
    def bucket_name(self) -> str:
        """Return the bucket name."""
        return self.bucket.bucket_name
    
    @property
    def bucket_arn(self) -> str:
        """Return the bucket ARN."""
        return self.bucket.bucket_arn
    
    @property
    def bucket_domain_name(self) -> str:
        """Return the bucket domain name."""
        return self.bucket.bucket_domain_name

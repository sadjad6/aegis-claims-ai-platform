"""
Main Infrastructure Stack for AegisClaims AI Platform.

This stack creates the core infrastructure components including
VPC, S3, DynamoDB, RDS, OpenSearch, Redshift, and Cognito.
"""

from aws_cdk import Stack
from constructs import Construct

from config.environments import EnvironmentConfig
from constructs import (
    VpcConstruct,
    S3BucketConstruct,
    DynamoDbConstruct,
    RdsConstruct,
    OpenSearchConstruct,
    RedshiftConstruct,
    CognitoConstruct,
)


class AegisClaimsStack(Stack):
    """
    Main AegisClaims infrastructure stack.
    
    Creates all core infrastructure components with environment-specific
    configurations for dev, staging, and prod environments.
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: EnvironmentConfig,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        
        # VPC with public and private subnets
        self.vpc_construct = VpcConstruct(
            self,
            "Vpc",
            env_name=config.env_name,
            vpc_cidr=config.vpc_cidr,
            enable_nat_gateway=config.env_name != "dev",  # Save costs in dev
        )
        self.vpc = self.vpc_construct.vpc
        
        # S3 bucket for claims documents
        self.s3_construct = S3BucketConstruct(
            self,
            "S3",
            bucket_name=config.s3_bucket_name,
            env_name=config.env_name,
            versioning_enabled=config.s3_versioning_enabled,
        )
        
        # DynamoDB table for state management
        self.dynamodb_construct = DynamoDbConstruct(
            self,
            "DynamoDB",
            table_name=config.dynamodb_table_name,
            env_name=config.env_name,
            point_in_time_recovery=config.dynamodb_point_in_time_recovery,
        )
        
        # RDS PostgreSQL instance
        self.rds_construct = RdsConstruct(
            self,
            "RDS",
            env_name=config.env_name,
            vpc=self.vpc,
            instance_class=config.rds_instance_class,
            allocated_storage=config.rds_allocated_storage,
            max_allocated_storage=config.rds_max_allocated_storage,
            multi_az=config.rds_multi_az,
            backup_retention_days=config.rds_backup_retention_days,
            deletion_protection=config.rds_deletion_protection,
            storage_encrypted=config.rds_storage_encrypted,
            skip_final_snapshot=config.rds_skip_final_snapshot,
        )
        
        # Cognito User Pool for authentication
        self.cognito_construct = CognitoConstruct(
            self,
            "Cognito",
            env_name=config.env_name,
            callback_urls=config.cognito_callback_urls,
            logout_urls=config.cognito_logout_urls,
        )
        
        # OpenSearch domain for vector database (optional based on config)
        self.opensearch_construct = None
        if config.opensearch_enabled:
            self.opensearch_construct = OpenSearchConstruct(
                self,
                "OpenSearch",
                env_name=config.env_name,
                vpc=self.vpc,
                instance_type=config.opensearch_instance_type,
                instance_count=config.opensearch_instance_count,
                volume_size=config.opensearch_volume_size,
                dedicated_master_enabled=config.opensearch_dedicated_master_enabled,
                zone_awareness_enabled=config.opensearch_zone_awareness_enabled,
            )
        
        # Redshift cluster for analytics (optional based on config)
        self.redshift_construct = None
        if config.redshift_enabled:
            self.redshift_construct = RedshiftConstruct(
                self,
                "Redshift",
                env_name=config.env_name,
                vpc=self.vpc,
                s3_bucket_arn=self.s3_construct.bucket_arn,
                node_type=config.redshift_node_type,
                number_of_nodes=config.redshift_number_of_nodes,
                snapshot_retention_days=config.redshift_snapshot_retention_days,
            )

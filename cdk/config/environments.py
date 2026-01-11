"""
Environment-specific configurations for AegisClaims AI Platform.

This module defines configurations for dev, staging, and prod environments,
maintaining the same characteristics as the original Terraform setup.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EnvironmentConfig:
    """Configuration class for environment-specific settings."""
    
    # Environment identifiers
    env_name: str
    region: str = "us-east-1"
    
    # VPC Configuration
    vpc_cidr: str = "10.0.0.0/16"
    
    # S3 Configuration
    s3_bucket_name: str = ""
    s3_versioning_enabled: bool = False
    
    # DynamoDB Configuration
    dynamodb_table_name: str = ""
    dynamodb_point_in_time_recovery: bool = False
    
    # RDS Configuration
    rds_instance_class: str = "db.t3.micro"
    rds_allocated_storage: int = 20
    rds_max_allocated_storage: Optional[int] = None
    rds_multi_az: bool = False
    rds_backup_retention_days: int = 1
    rds_deletion_protection: bool = False
    rds_storage_encrypted: bool = False
    rds_skip_final_snapshot: bool = True
    
    # OpenSearch Configuration
    opensearch_enabled: bool = True
    opensearch_instance_type: str = "t3.small.search"
    opensearch_instance_count: int = 1
    opensearch_volume_size: int = 10
    opensearch_dedicated_master_enabled: bool = False
    opensearch_zone_awareness_enabled: bool = False
    
    # Redshift Configuration
    redshift_enabled: bool = False
    redshift_node_type: str = "dc2.large"
    redshift_number_of_nodes: int = 1
    redshift_snapshot_retention_days: int = 1
    
    # Cognito Configuration
    cognito_callback_urls: list = None
    cognito_logout_urls: list = None
    
    # AI/ML Configuration
    sagemaker_instance_type: str = "ml.t2.medium"
    
    def __post_init__(self):
        """Set default bucket and table names based on environment."""
        if not self.s3_bucket_name:
            self.s3_bucket_name = f"aegis-claims-data-{self.env_name}"
        if not self.dynamodb_table_name:
            self.dynamodb_table_name = f"aegis-claims-state-{self.env_name}"
        if self.cognito_callback_urls is None:
            self.cognito_callback_urls = ["http://localhost:3000/callback"]
        if self.cognito_logout_urls is None:
            self.cognito_logout_urls = ["http://localhost:3000/logout"]


# Development environment configuration
DEV_CONFIG = EnvironmentConfig(
    env_name="dev",
    region="us-east-1",
    
    # S3 - versioning disabled for dev
    s3_versioning_enabled=False,
    
    # DynamoDB - no PITR for dev
    dynamodb_point_in_time_recovery=False,
    
    # RDS - minimal resources
    rds_instance_class="db.t3.micro",
    rds_allocated_storage=20,
    rds_multi_az=False,
    rds_backup_retention_days=1,
    rds_deletion_protection=False,
    rds_skip_final_snapshot=True,
    
    # OpenSearch - minimal single node
    opensearch_enabled=True,
    opensearch_instance_type="t3.small.search",
    opensearch_instance_count=1,
    opensearch_volume_size=10,
    
    # Redshift - disabled for dev
    redshift_enabled=False,
)


# Staging environment configuration
STAGING_CONFIG = EnvironmentConfig(
    env_name="staging",
    region="us-east-1",
    
    # S3 - versioning disabled for staging
    s3_versioning_enabled=False,
    
    # DynamoDB - no PITR for staging
    dynamodb_point_in_time_recovery=False,
    
    # RDS - moderate resources
    rds_instance_class="db.t3.small",
    rds_allocated_storage=50,
    rds_multi_az=False,
    rds_backup_retention_days=1,
    rds_deletion_protection=False,
    rds_skip_final_snapshot=True,
    
    # OpenSearch - 2 nodes for testing HA
    opensearch_enabled=True,
    opensearch_instance_type="t3.medium.search",
    opensearch_instance_count=2,
    opensearch_volume_size=50,
    
    # Redshift - single node for analytics testing
    redshift_enabled=True,
    redshift_node_type="dc2.large",
    redshift_number_of_nodes=1,
    redshift_snapshot_retention_days=1,
)


# Production environment configuration
PROD_CONFIG = EnvironmentConfig(
    env_name="prod",
    region="us-east-1",
    
    # S3 - versioning enabled for prod
    s3_versioning_enabled=True,
    
    # DynamoDB - PITR enabled for prod
    dynamodb_point_in_time_recovery=True,
    
    # RDS - production resources with Multi-AZ
    rds_instance_class="db.r6g.large",
    rds_allocated_storage=100,
    rds_max_allocated_storage=500,
    rds_multi_az=True,
    rds_backup_retention_days=7,
    rds_deletion_protection=True,
    rds_storage_encrypted=True,
    rds_skip_final_snapshot=False,
    
    # OpenSearch - 3-node HA cluster with dedicated masters
    opensearch_enabled=True,
    opensearch_instance_type="m6g.large.search",
    opensearch_instance_count=3,
    opensearch_volume_size=100,
    opensearch_dedicated_master_enabled=True,
    opensearch_zone_awareness_enabled=True,
    
    # Redshift - multi-node for production analytics
    redshift_enabled=True,
    redshift_node_type="dc2.large",
    redshift_number_of_nodes=2,
    redshift_snapshot_retention_days=7,
)


def get_environment_config(env_name: str) -> EnvironmentConfig:
    """
    Get configuration for a specific environment.
    
    Args:
        env_name: Environment name ('dev', 'staging', or 'prod')
        
    Returns:
        EnvironmentConfig for the specified environment
        
    Raises:
        ValueError: If environment name is not recognized
    """
    configs = {
        "dev": DEV_CONFIG,
        "staging": STAGING_CONFIG,
        "prod": PROD_CONFIG,
    }
    
    if env_name not in configs:
        raise ValueError(
            f"Unknown environment: {env_name}. "
            f"Valid environments are: {', '.join(configs.keys())}"
        )
    
    return configs[env_name]

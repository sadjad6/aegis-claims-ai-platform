"""
DynamoDB Construct for AegisClaims AI Platform.

Creates a DynamoDB table with GSI for tenant-based queries,
matching the original Terraform DynamoDB module configuration.
"""

from constructs import Construct
from aws_cdk import (
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    CfnOutput,
)


class DynamoDbConstruct(Construct):
    """
    DynamoDB table construct for claims and tenant data.
    
    Features:
    - PAY_PER_REQUEST billing mode
    - Primary key: PK (hash), SK (range)
    - GSI TenantIndex for tenant-based queries
    - Point-in-time recovery (enabled for prod)
    - Server-side encryption
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        table_name: str,
        env_name: str,
        point_in_time_recovery: bool = False,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create DynamoDB table
        self.table = dynamodb.Table(
            self,
            "Table",
            table_name=table_name,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING,
            ),
            point_in_time_recovery=point_in_time_recovery,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.RETAIN if env_name == "prod" else RemovalPolicy.DESTROY,
        )
        
        # Add Global Secondary Index for tenant-based queries
        self.table.add_global_secondary_index(
            index_name="TenantIndex",
            partition_key=dynamodb.Attribute(
                name="tenant_id",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING,
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )
        
        # Outputs
        CfnOutput(
            self,
            "TableName",
            value=self.table.table_name,
            description="DynamoDB Table Name",
        )
        
        CfnOutput(
            self,
            "TableArn",
            value=self.table.table_arn,
            description="DynamoDB Table ARN",
        )
    
    @property
    def table_name(self) -> str:
        """Return the table name."""
        return self.table.table_name
    
    @property
    def table_arn(self) -> str:
        """Return the table ARN."""
        return self.table.table_arn

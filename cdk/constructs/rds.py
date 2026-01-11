"""
RDS Construct for AegisClaims AI Platform.

Creates a PostgreSQL RDS instance with environment-specific sizing,
matching the original Terraform RDS module configuration.
"""

from constructs import Construct
from aws_cdk import (
    aws_rds as rds,
    aws_ec2 as ec2,
    Duration,
    RemovalPolicy,
    SecretValue,
    CfnOutput,
)


class RdsConstruct(Construct):
    """
    RDS PostgreSQL construct for transactional data.
    
    Features:
    - PostgreSQL 15
    - Environment-specific instance sizing
    - Multi-AZ for production
    - Storage encryption for production
    - Configurable backup retention
    - Private subnet placement
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        vpc: ec2.IVpc,
        instance_class: str = "db.t3.micro",
        allocated_storage: int = 20,
        max_allocated_storage: int = None,
        multi_az: bool = False,
        backup_retention_days: int = 1,
        deletion_protection: bool = False,
        storage_encrypted: bool = False,
        skip_final_snapshot: bool = True,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create security group for RDS
        self.security_group = ec2.SecurityGroup(
            self,
            "SecurityGroup",
            security_group_name=f"aegis-rds-sg-{env_name}",
            description="Security group for RDS PostgreSQL",
            vpc=vpc,
            allow_all_outbound=True,
        )
        
        # Allow PostgreSQL access from within VPC
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(5432),
            description="PostgreSQL access from VPC",
        )
        
        # Create subnet group
        subnet_group = rds.SubnetGroup(
            self,
            "SubnetGroup",
            description=f"Subnet group for AegisClaims RDS - {env_name}",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )
        
        # Parse instance class
        instance_type = self._parse_instance_class(instance_class)
        
        # Create RDS instance
        self.instance = rds.DatabaseInstance(
            self,
            "Instance",
            instance_identifier=f"aegis-claims-db-{env_name}",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            instance_type=instance_type,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            subnet_group=subnet_group,
            security_groups=[self.security_group],
            database_name="aegis_claims",
            credentials=rds.Credentials.from_generated_secret(
                username="admin",
                secret_name=f"aegis-claims-db-credentials-{env_name}",
            ),
            allocated_storage=allocated_storage,
            max_allocated_storage=max_allocated_storage,
            multi_az=multi_az,
            publicly_accessible=False,
            storage_encrypted=storage_encrypted,
            deletion_protection=deletion_protection,
            backup_retention=Duration.days(backup_retention_days),
            preferred_backup_window="03:00-04:00",
            preferred_maintenance_window="sun:05:00-sun:06:00",
            removal_policy=RemovalPolicy.SNAPSHOT if not skip_final_snapshot else RemovalPolicy.DESTROY,
        )
        
        # Outputs
        CfnOutput(
            self,
            "Endpoint",
            value=self.instance.db_instance_endpoint_address,
            description="RDS Endpoint",
        )
        
        CfnOutput(
            self,
            "Port",
            value=self.instance.db_instance_endpoint_port,
            description="RDS Port",
        )
        
        CfnOutput(
            self,
            "SecretArn",
            value=self.instance.secret.secret_arn,
            description="RDS Credentials Secret ARN",
        )
    
    def _parse_instance_class(self, instance_class: str) -> ec2.InstanceType:
        """Parse Terraform-style instance class to CDK InstanceType."""
        # Remove 'db.' prefix if present
        if instance_class.startswith("db."):
            instance_class = instance_class[3:]
        
        # Map common instance types
        instance_mapping = {
            "t3.micro": ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            "t3.small": ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.SMALL),
            "t3.medium": ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM),
            "r6g.large": ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.LARGE),
            "r6g.xlarge": ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.XLARGE),
        }
        
        return instance_mapping.get(instance_class, ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO))
    
    @property
    def endpoint(self) -> str:
        """Return the database endpoint."""
        return self.instance.db_instance_endpoint_address
    
    @property
    def port(self) -> str:
        """Return the database port."""
        return self.instance.db_instance_endpoint_port
    
    @property
    def database_name(self) -> str:
        """Return the database name."""
        return "aegis_claims"

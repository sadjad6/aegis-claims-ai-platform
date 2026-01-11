"""
Redshift Construct for AegisClaims AI Platform.

Creates a Redshift cluster for analytics and SaaS reporting,
matching the original Terraform Redshift module configuration.
"""

from constructs import Construct
from aws_cdk import (
    aws_redshift_alpha as redshift,
    aws_ec2 as ec2,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput,
)


class RedshiftConstruct(Construct):
    """
    Redshift cluster construct for analytics.
    
    Features:
    - Encryption enabled
    - Enhanced VPC routing
    - IAM role for S3 access
    - Environment-specific node count
    - Automated snapshots
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        vpc: ec2.IVpc,
        s3_bucket_arn: str,
        node_type: str = "dc2.large",
        number_of_nodes: int = 1,
        snapshot_retention_days: int = 1,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create security group for Redshift
        self.security_group = ec2.SecurityGroup(
            self,
            "SecurityGroup",
            security_group_name=f"aegis-redshift-sg-{env_name}",
            description="Security group for Redshift",
            vpc=vpc,
            allow_all_outbound=True,
        )
        
        # Allow Redshift access from within VPC
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(5439),
            description="Redshift access from VPC",
        )
        
        # Create IAM role for Redshift to access S3
        self.redshift_role = iam.Role(
            self,
            "RedshiftRole",
            role_name=f"aegis-redshift-role-{env_name}",
            assumed_by=iam.ServicePrincipal("redshift.amazonaws.com"),
        )
        
        # Add S3 read policy
        self.redshift_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:ListBucket",
                ],
                resources=[
                    s3_bucket_arn,
                    f"{s3_bucket_arn}/*",
                ],
            )
        )
        
        # Create subnet group
        subnet_group = redshift.ClusterSubnetGroup(
            self,
            "SubnetGroup",
            description=f"Subnet group for AegisClaims Redshift - {env_name}",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )
        
        # Determine cluster type
        cluster_type = (
            redshift.ClusterType.MULTI_NODE if number_of_nodes > 1 
            else redshift.ClusterType.SINGLE_NODE
        )
        
        # Create Redshift cluster
        self.cluster = redshift.Cluster(
            self,
            "Cluster",
            cluster_name=f"aegis-analytics-{env_name}",
            master_user=redshift.Login(master_username="admin"),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self.security_group],
            subnet_group=subnet_group,
            default_database_name="aegis_analytics",
            node_type=self._parse_node_type(node_type),
            cluster_type=cluster_type,
            number_of_nodes=number_of_nodes if number_of_nodes > 1 else None,
            encrypted=True,
            enhanced_vpc_routing=True,
            roles=[self.redshift_role],
            removal_policy=RemovalPolicy.SNAPSHOT if env_name == "prod" else RemovalPolicy.DESTROY,
            preferred_maintenance_window="sun:05:00-sun:06:00",
        )
        
        # Outputs
        CfnOutput(
            self,
            "ClusterEndpoint",
            value=self.cluster.cluster_endpoint.hostname,
            description="Redshift Cluster Endpoint",
        )
        
        CfnOutput(
            self,
            "ClusterIdentifier",
            value=self.cluster.cluster_name,
            description="Redshift Cluster Identifier",
        )
        
        CfnOutput(
            self,
            "IamRoleArn",
            value=self.redshift_role.role_arn,
            description="Redshift IAM Role ARN",
        )
    
    def _parse_node_type(self, node_type: str) -> redshift.NodeType:
        """Parse node type string to CDK NodeType."""
        node_mapping = {
            "dc2.large": redshift.NodeType.DC2_LARGE,
            "dc2.8xlarge": redshift.NodeType.DC2_8XLARGE,
            "ra3.xlplus": redshift.NodeType.RA3_XLPLUS,
            "ra3.4xlarge": redshift.NodeType.RA3_4XLARGE,
            "ra3.16xlarge": redshift.NodeType.RA3_16XLARGE,
        }
        return node_mapping.get(node_type, redshift.NodeType.DC2_LARGE)
    
    @property
    def cluster_endpoint(self) -> str:
        """Return the cluster endpoint."""
        return self.cluster.cluster_endpoint.hostname
    
    @property
    def database_name(self) -> str:
        """Return the database name."""
        return "aegis_analytics"
    
    @property
    def iam_role_arn(self) -> str:
        """Return the IAM role ARN."""
        return self.redshift_role.role_arn

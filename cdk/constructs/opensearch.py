"""
OpenSearch Construct for AegisClaims AI Platform.

Creates an OpenSearch domain for vector database (RAG & similarity search),
matching the original Terraform OpenSearch module configuration.
"""

from constructs import Construct
from aws_cdk import (
    aws_opensearchservice as opensearch,
    aws_ec2 as ec2,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput,
)


class OpenSearchConstruct(Construct):
    """
    OpenSearch domain construct for vector database.
    
    Features:
    - OpenSearch 2.11
    - Encryption at rest and node-to-node
    - HTTPS enforced (TLS 1.2+)
    - Fine-grained access control
    - kNN index support for vector embeddings
    - Environment-specific cluster sizing
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        vpc: ec2.IVpc = None,
        instance_type: str = "t3.small.search",
        instance_count: int = 1,
        volume_size: int = 20,
        dedicated_master_enabled: bool = False,
        zone_awareness_enabled: bool = False,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Determine capacity configuration
        capacity_config = opensearch.CapacityConfig(
            data_node_instance_type=instance_type,
            data_nodes=instance_count,
            master_node_instance_type="m6g.large.search" if dedicated_master_enabled else None,
            master_nodes=3 if dedicated_master_enabled else None,
        )
        
        # Zone awareness configuration
        zone_awareness = None
        if zone_awareness_enabled:
            zone_awareness = opensearch.ZoneAwarenessConfig(
                enabled=True,
                availability_zone_count=2,
            )
        
        # EBS configuration
        ebs_options = opensearch.EbsOptions(
            enabled=True,
            volume_size=volume_size,
            volume_type=ec2.EbsDeviceVolumeType.GP3,
        )
        
        # Create the OpenSearch domain
        self.domain = opensearch.Domain(
            self,
            "Domain",
            domain_name=f"aegis-claims-vectors-{env_name}",
            version=opensearch.EngineVersion.OPENSEARCH_2_11,
            capacity=capacity_config,
            ebs=ebs_options,
            zone_awareness=zone_awareness,
            encryption_at_rest=opensearch.EncryptionAtRestOptions(enabled=True),
            node_to_node_encryption=True,
            enforce_https=True,
            tls_security_policy=opensearch.TLSSecurityPolicy.TLS_1_2,
            fine_grained_access_control=opensearch.AdvancedSecurityOptions(
                master_user_name="admin",
            ),
            removal_policy=RemovalPolicy.RETAIN if env_name == "prod" else RemovalPolicy.DESTROY,
        )
        
        # Add access policy allowing access from anywhere (to be restricted by fine-grained access control)
        self.domain.add_access_policies(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=["es:*"],
                resources=[f"{self.domain.domain_arn}/*"],
            )
        )
        
        # Outputs
        CfnOutput(
            self,
            "DomainEndpoint",
            value=self.domain.domain_endpoint,
            description="OpenSearch Domain Endpoint",
        )
        
        CfnOutput(
            self,
            "DomainArn",
            value=self.domain.domain_arn,
            description="OpenSearch Domain ARN",
        )
    
    @property
    def domain_endpoint(self) -> str:
        """Return the domain endpoint."""
        return self.domain.domain_endpoint
    
    @property
    def domain_arn(self) -> str:
        """Return the domain ARN."""
        return self.domain.domain_arn

"""
VPC Construct for AegisClaims AI Platform.

Creates a VPC with public and private subnets across 2 availability zones,
matching the original Terraform VPC module configuration.
"""

from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    CfnOutput,
)


class VpcConstruct(Construct):
    """
    VPC construct with public and private subnets.
    
    Creates:
    - VPC with configurable CIDR block
    - 2 public subnets with auto-assign public IP
    - 2 private subnets
    - Internet Gateway
    - NAT Gateways (configurable)
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        vpc_cidr: str = "10.0.0.0/16",
        enable_nat_gateway: bool = True,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create VPC with public and private subnets
        self.vpc = ec2.Vpc(
            self,
            "Vpc",
            vpc_name=f"aegis-claims-vpc-{env_name}",
            ip_addresses=ec2.IpAddresses.cidr(vpc_cidr),
            max_azs=2,
            nat_gateways=1 if enable_nat_gateway else 0,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                    map_public_ip_on_launch=True,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS if enable_nat_gateway else ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )
        
        # Add tags to VPC
        self.vpc.node.default_child.tags.set_tag("Environment", env_name)
        self.vpc.node.default_child.tags.set_tag("Project", "AegisClaimsAI")
        
        # Tag subnets
        for i, subnet in enumerate(self.vpc.public_subnets):
            subnet.node.default_child.tags.set_tag("Name", f"aegis-public-{i}-{env_name}")
            
        for i, subnet in enumerate(self.vpc.private_subnets):
            subnet.node.default_child.tags.set_tag("Name", f"aegis-private-{i}-{env_name}")
        
        # Outputs
        CfnOutput(
            self,
            "VpcId",
            value=self.vpc.vpc_id,
            description="VPC ID",
            export_name=f"aegis-vpc-id-{env_name}",
        )
        
        CfnOutput(
            self,
            "VpcCidr",
            value=self.vpc.vpc_cidr_block,
            description="VPC CIDR Block",
        )
    
    @property
    def vpc_id(self) -> str:
        """Return the VPC ID."""
        return self.vpc.vpc_id
    
    @property
    def vpc_cidr_block(self) -> str:
        """Return the VPC CIDR block."""
        return self.vpc.vpc_cidr_block
    
    @property
    def private_subnets(self) -> list:
        """Return private subnets."""
        return self.vpc.private_subnets
    
    @property
    def public_subnets(self) -> list:
        """Return public subnets."""
        return self.vpc.public_subnets
    
    @property
    def private_subnet_ids(self) -> list:
        """Return private subnet IDs."""
        return [subnet.subnet_id for subnet in self.vpc.private_subnets]
    
    @property
    def public_subnet_ids(self) -> list:
        """Return public subnet IDs."""
        return [subnet.subnet_id for subnet in self.vpc.public_subnets]

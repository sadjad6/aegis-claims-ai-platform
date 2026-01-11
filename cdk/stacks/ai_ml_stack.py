"""
AI/ML Stack for AegisClaims AI Platform.

This stack creates the AI/ML infrastructure components including
Bedrock and SageMaker configurations.
"""

from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from config.environments import EnvironmentConfig
from constructs import AiMlConstruct


class AiMlStack(Stack):
    """
    AI/ML services stack for Bedrock and SageMaker.
    
    Creates AI/ML infrastructure components that are separated from
    the main infrastructure stack for independent deployment.
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: EnvironmentConfig,
        vpc: ec2.IVpc,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        
        # AI/ML construct with Bedrock and SageMaker
        self.ai_ml_construct = AiMlConstruct(
            self,
            "AiMl",
            env_name=config.env_name,
            sagemaker_instance_type=config.sagemaker_instance_type,
        )

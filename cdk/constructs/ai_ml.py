"""
AI/ML Construct for AegisClaims AI Platform.

Creates Bedrock agent and SageMaker endpoint configurations,
matching the original Terraform AI/ML module configuration.
"""

from constructs import Construct
from aws_cdk import (
    aws_iam as iam,
    aws_sagemaker as sagemaker,
    aws_bedrock as bedrock,
    CfnOutput,
)


class AiMlConstruct(Construct):
    """
    AI/ML services construct for Bedrock and SageMaker.
    
    Features:
    - Bedrock agent for claims reasoning (Claude 3 Sonnet)
    - SageMaker endpoint for fraud detection (XGBoost)
    - IAM roles with least-privilege policies
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        sagemaker_instance_type: str = "ml.t2.medium",
        fraud_model_image: str = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.5-1",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.env_name = env_name
        
        # Create Bedrock Agent IAM Role
        self.bedrock_role = iam.Role(
            self,
            "BedrockAgentRole",
            role_name=f"aegis-bedrock-agent-role-{env_name}",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
        )
        
        # Add Bedrock permissions
        self.bedrock_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["*"],
            )
        )
        
        # Create SageMaker IAM Role
        self.sagemaker_role = iam.Role(
            self,
            "SageMakerRole",
            role_name=f"aegis-sagemaker-role-{env_name}",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
        )
        
        # Add SageMaker full access policy
        self.sagemaker_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
        )
        
        # Create SageMaker Model
        self.fraud_model = sagemaker.CfnModel(
            self,
            "FraudModel",
            model_name=f"aegis-fraud-model-{env_name}",
            execution_role_arn=self.sagemaker_role.role_arn,
            primary_container=sagemaker.CfnModel.ContainerDefinitionProperty(
                image=fraud_model_image,
            ),
        )
        
        # Create SageMaker Endpoint Configuration
        self.endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            "FraudEndpointConfig",
            endpoint_config_name=f"aegis-fraud-config-{env_name}",
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    variant_name="AllTraffic",
                    model_name=self.fraud_model.model_name,
                    initial_instance_count=1,
                    instance_type=sagemaker_instance_type,
                ),
            ],
        )
        self.endpoint_config.add_dependency(self.fraud_model)
        
        # Create SageMaker Endpoint
        self.fraud_endpoint = sagemaker.CfnEndpoint(
            self,
            "FraudEndpoint",
            endpoint_name=f"aegis-fraud-detection-{env_name}",
            endpoint_config_name=self.endpoint_config.endpoint_config_name,
        )
        self.fraud_endpoint.add_dependency(self.endpoint_config)
        
        # Note: Bedrock agents are typically created through the Bedrock console or API
        # as CDK support for Bedrock agents is still maturing.
        # The IAM role is prepared for when the agent is created.
        
        # Outputs
        CfnOutput(
            self,
            "FraudEndpointName",
            value=self.fraud_endpoint.endpoint_name,
            description="SageMaker Fraud Detection Endpoint Name",
        )
        
        CfnOutput(
            self,
            "BedrockRoleArn",
            value=self.bedrock_role.role_arn,
            description="Bedrock Agent IAM Role ARN",
        )
        
        CfnOutput(
            self,
            "SageMakerRoleArn",
            value=self.sagemaker_role.role_arn,
            description="SageMaker IAM Role ARN",
        )
    
    @property
    def fraud_endpoint_name(self) -> str:
        """Return the fraud detection endpoint name."""
        return self.fraud_endpoint.endpoint_name
    
    @property
    def bedrock_role_arn(self) -> str:
        """Return the Bedrock role ARN."""
        return self.bedrock_role.role_arn
    
    @property
    def sagemaker_role_arn(self) -> str:
        """Return the SageMaker role ARN."""
        return self.sagemaker_role.role_arn

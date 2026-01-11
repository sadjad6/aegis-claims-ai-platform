#!/usr/bin/env python3
"""
AegisClaims AI Platform - AWS CDK Application

This is the main entry point for the AWS CDK application.
It creates infrastructure stacks for dev, staging, and prod environments.
"""

import os
import aws_cdk as cdk

from stacks.aegis_stack import AegisClaimsStack
from stacks.ai_ml_stack import AiMlStack
from config.environments import get_environment_config


app = cdk.App()

# Get environment from context or default to 'dev'
env_name = app.node.try_get_context("env") or "dev"

# Get environment-specific configuration
config = get_environment_config(env_name)

# Define AWS environment
aws_env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=config.region
)

# Create the main infrastructure stack
main_stack = AegisClaimsStack(
    app,
    f"AegisClaimsStack-{env_name.capitalize()}",
    config=config,
    env=aws_env,
    description=f"AegisClaims AI Platform infrastructure for {env_name} environment"
)

# Create the AI/ML services stack
ai_ml_stack = AiMlStack(
    app,
    f"AegisAiMlStack-{env_name.capitalize()}",
    config=config,
    vpc=main_stack.vpc,
    env=aws_env,
    description=f"AegisClaims AI/ML services for {env_name} environment"
)

# Add dependency - AI/ML stack depends on main stack
ai_ml_stack.add_dependency(main_stack)

# Add tags to all resources
cdk.Tags.of(app).add("Project", "AegisClaimsAI")
cdk.Tags.of(app).add("Environment", env_name)
cdk.Tags.of(app).add("ManagedBy", "AWS-CDK")

app.synth()

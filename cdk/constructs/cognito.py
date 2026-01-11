"""
Cognito Construct for AegisClaims AI Platform.

Creates a Cognito user pool with custom attributes and RBAC groups,
matching the original Terraform Cognito module configuration.
"""

from constructs import Construct
from aws_cdk import (
    aws_cognito as cognito,
    RemovalPolicy,
    CfnOutput,
)


class CognitoConstruct(Construct):
    """
    Cognito user pool construct for authentication.
    
    Features:
    - Strong password policy (12+ chars, mixed case, numbers, symbols)
    - Optional MFA
    - Custom attributes: tenant_id, role
    - RBAC groups: TenantAdmin, ClaimsAdjuster, Supervisor, AIOps
    - OAuth 2.0 flows: code, implicit
    - Scopes: email, openid, profile
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        callback_urls: list = None,
        logout_urls: list = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Set default URLs
        if callback_urls is None:
            callback_urls = ["http://localhost:3000/callback"]
        if logout_urls is None:
            logout_urls = ["http://localhost:3000/logout"]
        
        # Create User Pool
        self.user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name=f"aegis-claims-users-{env_name}",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=True,
            ),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
            ),
            mfa=cognito.Mfa.OPTIONAL,
            mfa_second_factor=cognito.MfaSecondFactor(
                otp=True,
                sms=False,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            custom_attributes={
                "tenant_id": cognito.StringAttribute(
                    min_len=1,
                    max_len=256,
                    mutable=True,
                ),
                "role": cognito.StringAttribute(
                    min_len=1,
                    max_len=50,
                    mutable=True,
                ),
            },
            removal_policy=RemovalPolicy.RETAIN if env_name == "prod" else RemovalPolicy.DESTROY,
        )
        
        # Create User Pool Domain
        self.domain = self.user_pool.add_domain(
            "Domain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=f"aegis-claims-{env_name}",
            ),
        )
        
        # Create User Pool Client
        self.client = self.user_pool.add_client(
            "WebClient",
            user_pool_client_name=f"aegis-web-client-{env_name}",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True,
                ),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE,
                ],
                callback_urls=callback_urls,
                logout_urls=logout_urls,
            ),
            supported_identity_providers=[
                cognito.UserPoolClientIdentityProvider.COGNITO,
            ],
        )
        
        # Create RBAC Groups
        self._create_user_groups()
        
        # Outputs
        CfnOutput(
            self,
            "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID",
        )
        
        CfnOutput(
            self,
            "UserPoolClientId",
            value=self.client.user_pool_client_id,
            description="Cognito User Pool Client ID",
        )
        
        CfnOutput(
            self,
            "UserPoolDomain",
            value=self.domain.domain_name,
            description="Cognito User Pool Domain",
        )
    
    def _create_user_groups(self):
        """Create RBAC user groups."""
        groups = [
            ("TenantAdmin", "Tenant administrators with full access"),
            ("ClaimsAdjuster", "Claims adjusters who review and process claims"),
            ("Supervisor", "Supervisors who approve escalated decisions"),
            ("AIOps", "AI Operations team for model monitoring"),
        ]
        
        for group_name, description in groups:
            cognito.CfnUserPoolGroup(
                self,
                f"Group{group_name}",
                user_pool_id=self.user_pool.user_pool_id,
                group_name=group_name,
                description=description,
            )
    
    @property
    def user_pool_id(self) -> str:
        """Return the user pool ID."""
        return self.user_pool.user_pool_id
    
    @property
    def user_pool_client_id(self) -> str:
        """Return the user pool client ID."""
        return self.client.user_pool_client_id

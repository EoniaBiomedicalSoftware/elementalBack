from pydantic import Field, SecretStr
from pydantic import model_validator
from typing import Optional, Dict, Any
from app.elemental.common import ElementalSchema

from app.elemental.exceptions import ConfigurationError


class OAuthProviderSettings(ElementalSchema):
    client_id: str
    client_secret: SecretStr = Field(repr=False)
    scope: list[str] = Field(default_factory=list)
    redirect_uri: str
    additional_params: Dict[str, Any] = Field(
        default_factory=dict,
        repr=False
    )


class GoogleSettings(OAuthProviderSettings):
    pass


class GitHubSettings(OAuthProviderSettings):
    pass


class FacebookSettings(OAuthProviderSettings):
    pass


class MicrosoftSettings(OAuthProviderSettings):
    pass


class OAuthSettings(ElementalSchema):
    providers: Dict[str, OAuthProviderSettings] = Field(
        default_factory=dict,
        description="Dictionary of configured OAuth providers (e.g., {'google': GoogleSettings(...), 'github': GitHubSettings(...)})"
    )
    default_provider: Optional[str] = None

    @model_validator(mode="after")
    def validate_default_provider(self):
        if self.default_provider and self.default_provider not in self.providers:
            raise ConfigurationError(
                f"Default provider '{self.default_provider}' is not defined in the 'providers' dictionary."
            )
        return self
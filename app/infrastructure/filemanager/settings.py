from pydantic import Field, SecretStr
from pydantic import model_validator
from typing import (
    Optional, Literal, Dict, List
)

from app.elemental.common import ElementalSchema
from app.elemental.exceptions import ConfigurationError

class LocalSettings(ElementalSchema):
    path: SecretStr = Field(
        description="Local storage path"
    )


class S3Settings(ElementalSchema):
    bucket: str
    region: str
    access_key: SecretStr = Field(description="AWS access key", repr=False)
    secret_key: SecretStr = Field(description="AWS secret key", repr=False)


class AzureSettings(ElementalSchema):
    container: str
    connection_string: SecretStr = Field(description="Azure connection string", repr=False)


class FileAllowedType(ElementalSchema):
    type: str
    allowed_extensions: List[str]
    allowed_mimes: List[str]
    max_file_size: int = Field(
        default=1024 * 1024 * 10,
        description="Maximum file size in bytes"
    )

    @model_validator(mode="after")
    def validate_local(self):
        self.allowed_extensions = [ext.lower() for ext in self.allowed_extensions]

        if self.max_file_size <= 0:
            raise ConfigurationError(
                f"max_file_size for file type '{self.type}' must be greater than zero in file manager settings."
            )

        return self

class FileManagerSettings(ElementalSchema):
    storage_type: Literal["local", "s3", "azure"] = Field(
        "local", description="Storage provider"
    )
    allowed_file_types: Dict[str, FileAllowedType] = Field(
        default_factory=dict,
        description="A dictionary of allowed file types and their properties"
    )

    local: Optional[LocalSettings] = None
    s3: Optional[S3Settings] = None
    azure: Optional[AzureSettings] = None

    @model_validator(mode="after")
    def validate_provider_settings(self):
        provider_map = {
            "local": self.local,
            "s3": self.s3,
            "azure": self.azure,
        }

        selected = provider_map[self.storage_type]

        if selected is None:
            raise ConfigurationError(
                f"Settings for FileManager provider '{self.storage_type}' must be defined"
            )

        if not self.allowed_file_types:
            raise ConfigurationError(
                "At least one file type (e.g., 'images', 'documents') must be defined in 'allowed_file_types'."
            )

        return self

from pydantic import Field, EmailStr, model_validator, SecretStr
from app.elemental.common import ElementalSchema
from app.elemental.exceptions import ConfigurationError


class EmailSettings(ElementalSchema):
    server: str = Field(description="SMTP server hostname", repr=False)
    port: int = Field(description="SMTP server port")
    username: str = Field(description="SMTP username", repr=False)
    password: SecretStr = Field(description="SMTP password", repr=False)
    sender: EmailStr = Field(description="Default sender email address")

    use_tls: bool = Field(True, description="Enable STARTTLS")
    use_ssl: bool = Field(False, description="Enable SSL/TLS")
    timeout: int = Field(10, description="SMTP connection timeout in seconds")

    @model_validator(mode="after")
    def validate_connection_security(self):
        if self.use_tls and self.use_ssl:
            raise ConfigurationError("Select either use_tls or use_ssl, not both.")

        if self.port not in [25, 465, 587, 2525]:
            pass

        return self
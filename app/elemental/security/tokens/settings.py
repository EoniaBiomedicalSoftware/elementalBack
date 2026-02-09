from datetime import timedelta
from pydantic import Field, SecretStr

from ...common.schemas import ElementalSchema


class _AccessToken(ElementalSchema):
    expire_minutes: int = 0
    expire_seconds: int = 0
    expire_hours: int = 1
    expire_days: int = 0

    @property
    def expire_delta(self) -> timedelta:
        # Returns a timedelta object for easy use with JWT libraries
        return timedelta(
            seconds=self.expire_seconds,
            minutes=self.expire_minutes,
            hours=self.expire_hours,
            days=self.expire_days
        )

class _RefreshToken(ElementalSchema):
    expire_minutes: int = 0
    expire_seconds: int = 0
    expire_hours: int = 0
    expire_days: int = 7

    @property
    def expire_delta(self) -> timedelta:
        # Returns a timedelta object for easy use with JWT libraries
        return timedelta(
            seconds=self.expire_seconds,
            minutes=self.expire_minutes,
            hours=self.expire_hours,
            days=self.expire_days
        )


class ElementalJWTSettings(ElementalSchema):
    """
    Represents JWT configuration settings for token generation and validation.

    This class holds the necessary configuration for JWT tokens, including algorithm,
    secret key, and token expiration settings. It is specifically designed to facilitate
    JWT-related operations by organizing input settings and converting expiration data
    to time deltas for usability in JWT workflows.

    Attributes:
        algorithm: The algorithm used for JWT signing. Default is "HS256".
        secret_key: The secret key used for encoding and decoding JSON Web Tokens. Has a
            minimum length of 8 characters.
    """
    algorithm: str = "HS256"
    secret_key: SecretStr = Field(default="secret", min_length=8)

    access_token: _AccessToken = _AccessToken()
    refresh_token: _RefreshToken = _RefreshToken()

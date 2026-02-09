from typing import Optional, Any
from app.elemental.exceptions import ExternalServiceError, NotFoundError, UnauthorizedError
from app.elemental.exceptions.base import ElementalBaseAppException
from app.elemental.common import ElementalErrorCode


class OAuthError(ExternalServiceError):
    """
    Base exception for all OAuth errors.
    Inherits from ExternalServiceError (HTTP 502).
    """
    def __init__(
        self,
        message: str = "OAuth provider error",
        details: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.OAUTH_ERROR,
            details=details,
        )


class ProviderNotConfiguredError(OAuthError):
    """
    Raised when the OAuth provider (Google, GitHub, etc.) is missing keys in settings.
    """
    def __init__(self, provider_name: str, **kwargs):
        message = f"OAuth provider '{provider_name}' is not properly configured on the server."
        super().__init__(message=message, **kwargs)


class ProviderNotFoundError(NotFoundError):
    """
    Raised when the client requests a provider that doesn't exist in our system.
    Maps to HTTP 404.
    """
    def __init__(self, provider_name: str, **kwargs):
        super().__init__(
            resource="OAuth Provider",
            field="name",
            value=provider_name,
            **kwargs
        )


class OAuthInvalidTokenError(ElementalBaseAppException):
    """
    Raised when the token returned by the provider is invalid or expired.
    Maps to HTTP 401.
    """
    def __init__(self, message: str = "The OAuth token provided is invalid or expired", **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.INVALID_TOKEN,
            **kwargs
        )


class InvalidCredentialsError(UnauthorizedError):
    """
    Raised when the OAuth exchange fails due to wrong client secrets or codes.
    Maps to HTTP 401.
    """
    def __init__(self, message: str = "Invalid OAuth credentials or exchange code"):
        super().__init__(
            message=message,
        )


class OAuthDataError(OAuthError):
    """
    Raised when the provider returns a malformed response or unexpected user data.
    Maps to HTTP 502.
    """
    def __init__(self, message: str = "Received invalid data from OAuth provider", **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.BAD_GATEWAY,
            **kwargs
        )
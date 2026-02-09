import traceback
from typing import Dict, Any, Optional

# 1. Base and Common
from .base import ElementalBaseAppException
from ..common import ElementalErrorCode

# 2. Domain Specific Exceptions
from .application import (
    ConfigurationError,
    RateLimitError
)
from .external import (
    ExternalServiceError,
    ExternalServiceAuthenticationError,
    ExternalServiceTimeoutError
)
from .auth import (
    AuthenticationError,
    UnauthorizedError,
    TokenExpiredError,
    TokenRevokedError,
    ForbiddenError,
    AccountDisabledError,
    AccountNotVerifiedError
)
from .validations import (
    ValidationError,
    NotFoundError,
    DuplicateError,
    MissingFieldError,
    InvalidFormatError,
    InvalidChoiceError,
    InvalidLengthError,
    ConflictError,
    NotAllowedError
)

__all__ = [
    'ElementalBaseAppException',
    'ElementalErrorCode',
    'ConfigurationError',
    'RateLimitError',
    'ExternalServiceError',
    'ExternalServiceAuthenticationError',
    'ExternalServiceTimeoutError',
    'AuthenticationError',
    'UnauthorizedError',
    'TokenExpiredError',
    'TokenRevokedError',
    'ForbiddenError',
    'AccountDisabledError',
    'AccountNotVerifiedError',
    'ValidationError',
    'ConflictError',
    'NotFoundError',
    'NotAllowedError',
    'DuplicateError',
    'MissingFieldError',
    'InvalidFormatError',
    'InvalidChoiceError',
    'InvalidLengthError',
    'ElementalExceptionHandler'
]


# --- Utilities ---

def log_exception(
    exc: Exception,
    context: Optional[Dict[str, Any]] = None,
    level: str = "error"
) -> None:
    context = context or {}

    log_data: dict[str, Any] = {
        "exception_type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
        **context
    }

    if isinstance(exc, ElementalBaseAppException):
        log_data.update(
            {
            "error_code": exc.error_code,
            "http_status": exc.http_status,
            "details": exc.details
            }
        )

    print(f"[{level.upper()}] {log_data}")


def format_exception_response(exc: ElementalBaseAppException) -> Dict[str, Any]:
    """
    Standardizes the JSON response for all custom app exceptions.
    """
    return {
        "status_code": exc.http_status,
        "content": {
            "error": True,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    }


def is_retriable_error(exc: Exception) -> bool:
    """Checks if the error is transient and can be retried."""
    retriable_errors = (
        ExternalServiceError,
        RateLimitError,
    )
    return isinstance(exc, retriable_errors)


def get_error_severity(exc: Exception) -> str:
    """Determines the logging priority."""
    if isinstance(exc, (ValidationError, NotFoundError)):
        return "low"
    elif isinstance(exc, (DuplicateError, AuthenticationError, ForbiddenError)):
        return "medium"
    elif isinstance(exc, ExternalServiceError):
        return "high"
    elif isinstance(exc, (ConfigurationError, RateLimitError)):
        return "critical"
    return "medium"


# --- Main Handler ---

class ElementalExceptionHandler:
    def __init__(self, log_exceptions: bool = True):
        self.log_exceptions = log_exceptions

    def handle(
        self,
        exc: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Final entry point to catch any exception and turn it into a valid API response.
        """
        if self.log_exceptions:
            severity = get_error_severity(exc)
            log_level = "error" if severity in ["high", "critical"] else "warning"
            log_exception(exc, context, log_level)

        if isinstance(exc, ElementalBaseAppException):
            return format_exception_response(exc)

        # Fallback for unexpected Python exceptions (e.g. KeyError, TypeError)
        return {
            "status_code": 500,
            "content": {
                "error": True,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred on the server.",
                "details": {"type": type(exc).__name__} if self.log_exceptions else {}
            }
        }
from typing import Optional, Dict, Any
from app.elemental.common import ElementalErrorCode
from .base import ElementalBaseAppException


class ExternalServiceError(ElementalBaseAppException):
    def __init__(
        self,
        message: Optional[str] = None,
        error_code: ElementalErrorCode = ElementalErrorCode.EXTERNAL_SERVICE_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details
        )


class ExternalServiceTimeoutError(ExternalServiceError):
    def __init__(
        self,
        service_name: str,
        timeout_seconds: Optional[float] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Service '{service_name}' did not respond in time."
            if timeout_seconds is not None:
                message += f" (Timeout: {timeout_seconds}s)"

        super().__init__(
            message=message,
            error_code=ElementalErrorCode.GATEWAY_TIMEOUT,
            details=details,
        )
        self.timeout_seconds = timeout_seconds


class ExternalServiceAuthenticationError(ExternalServiceError):
    def __init__(
        self,
        message: str = "Failed to authenticate with the external service.",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.EXTERNAL_SERVICE_ERROR,
            details=details,
        )
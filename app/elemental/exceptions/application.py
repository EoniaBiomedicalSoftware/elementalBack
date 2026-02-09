from app.elemental.common import ElementalErrorCode
from .base import ElementalBaseAppException


class ConfigurationError(ElementalBaseAppException):
    """
    Raised when there is a problem with the application's configuration.
    (HTTP 500 Internal Server Error)
    """
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.INTERNAL_SERVER_ERROR,
            **kwargs
        )


class RateLimitError(ElementalBaseAppException):
    """
    Raised when a client exceeds the number of allowed requests in a given time frame.
    (HTTP 429 Too Many Requests)
    """
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.RATE_LIMIT_ERROR,
            **kwargs
        )
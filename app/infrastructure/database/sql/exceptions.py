from typing import Optional, Dict, Any
from app.elemental.common import ElementalErrorCode
from app.elemental.exceptions import ExternalServiceError, ExternalServiceAuthenticationError


class DatabaseError(ExternalServiceError):
    """
    Generic database error.
    Inherits from ExternalServiceError (HTTP 502 Bad Gateway by default).
    """
    def __init__(
        self,
        message: str = "Database transaction or generic error.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.EXTERNAL_SERVICE_ERROR,
            details=details,
        )


class DatabaseAuthenticationError(ExternalServiceAuthenticationError):
    """
    Raised when the application cannot authenticate with the database server.
    """
    def __init__(
        self,
        message: str = "Database authentication failed (invalid credentials).",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            details=details,
        )


class DatabaseConnectionError(DatabaseError):
    """
    Raised when the database server is unreachable.
    Maps to HTTP 503 Service Unavailable.
    """
    def __init__(self, message: str = "Failed to connect to the database."):
        super().__init__(
            message=message,
        )

class DatabaseInitializationError(DatabaseError):
    """
    Raised during app startup if migrations or initial connections fail.
    """
    def __init__(self, message: str = "Database not initialized or structurally invalid."):
        super().__init__(
            message=message,
        )
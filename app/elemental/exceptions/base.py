from typing import Any, Dict, Optional
from app.elemental.common import ElementalErrorCode


class ElementalBaseAppException(Exception):
    """
    Base exception for all custom errors in the application.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: ElementalErrorCode = ElementalErrorCode.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        self._error_enum = error_code

        self.http_status: int = error_code.http_code
        self.error_code: str = error_code.name  # (ej: "USER_NOT_FOUND")

        self.message: str = message or error_code.default_message # (ej: "User not found.")

        self.details: dict = details or {}

        super().__init__(self.message)
from typing import Any, List, Optional, Dict
from app.elemental.common import ElementalErrorCode
from .base import ElementalBaseAppException


class ValidationError(ElementalBaseAppException):
    """Base for 422 Unprocessable Entity errors."""
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.VALIDATION_ERROR, # Pass the Enum object
            **kwargs
        )


class NotAllowedError(ElementalBaseAppException):
    """Base for 400 Bad Request errors."""
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.NOT_ALLOWED,
            **kwargs
        )

class NotFoundError(ElementalBaseAppException):
    """Base for 404 Not Found errors."""
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.NOT_FOUND,
            **kwargs
        )


class DuplicateError(ElementalBaseAppException):
    """Base for 409 Conflict errors."""
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.DUPLICATE_ERROR,
            **kwargs
        )

class MissingFieldError(ValidationError):
    """Raised when a required field is missing from the input data."""
    def __init__(self, field_name: str, **kwargs):
        message = f"The required field '{field_name}' is missing."
        details = {"field": field_name, "reason": "missing"}
        super().__init__(message=message, details=details, **kwargs)


class InvalidFormatError(ValidationError):
    """Raised when a field's value has an incorrect format (e.g., bad email)."""
    def __init__(self, field_name: str, reason: Optional[str] = None, **kwargs):
        message = f"The field '{field_name}' has an invalid format."
        if reason:
            message += f" Reason: {reason}."
        details = {"field": field_name, "reason": "invalid_format", "details": reason}
        super().__init__(message=message, details=details, **kwargs)


class InvalidLengthError(ValidationError):
    """Raised when a field's value is too short or too long."""
    def __init__(
        self,
        field_name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        **kwargs
    ):
        parts = []
        if min_length is not None: parts.append(f"minimum length is {min_length}")
        if max_length is not None: parts.append(f"maximum length is {max_length}")

        reason = " and ".join(parts)
        message = f"The field '{field_name}' has an invalid length. Expected: {reason}."
        details = {
            "field": field_name,
            "reason": "invalid_length",
            "min_length": min_length,
            "max_length": max_length
        }
        super().__init__(message=message, details=details, **kwargs)


class InvalidChoiceError(ValidationError):
    """Raised when a field's value is not one of the allowed choices."""
    def __init__(self, field_name: str, value: Any, allowed_choices: List[Any], **kwargs):
        message = f"The value '{value}' is not a valid choice for field '{field_name}'."
        details = {
            "field": field_name,
            "reason": "invalid_choice",
            "value": value,
            "allowed_choices": allowed_choices
        }
        super().__init__(message=message, details=details, **kwargs)


class ConflictError(ElementalBaseAppException):
    def __init__(
        self,
        message: str = "A conflict occurred with the current state of the resource.",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            http_status=409,
            error_code=ElementalErrorCode.RESOURCE_STATE_CONFLICT,
            message=message,
            details=details
        )
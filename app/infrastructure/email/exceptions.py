from typing import Optional, Any
from app.elemental.common import ElementalErrorCode
from app.elemental.exceptions import ExternalServiceError


class EmailError(ExternalServiceError):
    """Generic base exception for email service issues."""
    def __init__(
        self,
        message: str = "Email service error",
        error_code: ElementalErrorCode = ElementalErrorCode.EXTERNAL_SERVICE_ERROR,
        details: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
        )


class EmailConnectionError(EmailError):
    """Raised when the connection to the SMTP server or API fails."""
    def __init__(self, message: str = "Email connection error", **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            details="EMAIL_SERVICE_UNAVAILABLE",
            **kwargs
        )


class EmailTemplateError(EmailError):
    """Raised when an email template is missing or corrupted."""
    def __init__(self, message: str = "Email template error", **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.VALIDATION_ERROR,
            details="EMAIL_VALIDATION_ERROR",
            **kwargs
        )


class EmailContextValidationError(EmailError):
    """Raised when the dynamic data for the template is invalid or missing."""
    def __init__(self, message: str = "Email context validation error", **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.VALIDATION_ERROR,
            details="EMAIL_CONTEXT_VALIDATION_ERROR",
            **kwargs
        )

class EmailAttachmentError(EmailError):
    """Raised when processing email attachments fails (size, format, etc)."""
    def __init__(self, message: str = "Email attachment processing error", **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.VALIDATION_ERROR,
            details="EMAIL_ATTACHMENT_ERROR",
            **kwargs
        )


class EmailRecipientsRefused(EmailError):
    """Raised when the server rejects one or more recipient addresses."""
    def __init__(self, message: str = "Email recipients refused by server", **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.VALIDATION_ERROR,
            details="EMAIL_RECIPIENTS_REFUSED",
            **kwargs
        )


class EmailSenderRefused(EmailError):
    """Raised when the server rejects the sender address or identity."""
    def __init__(self, message: str = "Email sender refused by server", **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.FORBIDDEN,
            details="EMAIL_SENDER_REFUSED",
            **kwargs
        )


class EmailDataError(EmailError):
    """Raised when the email payload/body is malformed."""
    def __init__(self, message: str = "Email message data error", **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.INTERNAL_SERVER_ERROR,
            details="EMAIL_DATA_ERROR",
            **kwargs
        )
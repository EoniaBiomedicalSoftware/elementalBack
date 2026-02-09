from typing import Any, Optional
from app.elemental.exceptions import (
    ExternalServiceError,
    NotFoundError,
    ValidationError,
)
from app.elemental.common import ElementalErrorCode


class FileManagerError(ExternalServiceError):
    """
    Base exception for all file manager errors.
    Inherits from ExternalServiceError, mapping to 502 (Bad Gateway).
    """
    def __init__(self, message: str = "File manager error", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.EXTERNAL_SERVICE_ERROR,
            details=details
        )

class FileNotFound(NotFoundError):
    """
    Raised when a requested file does not exist. Maps to 404 (Not Found).
    """
    def __init__(self, file_path: str, message: Optional[str] = None):
        # We use the standard NotFoundError(resource, field, value) format
        super().__init__(
            resource="File",
            field="path",
            value=file_path,
            message=message
        )


class FileUploadError(FileManagerError):
    """
    Raised when an error occurs during file upload.
    """
    def __init__(self, message: str = "Failed to upload file", details: Optional[Any] = None):
        super().__init__(message=message, details=details)


class FileUpdateError(FileManagerError):
    """
    Raised when a file cannot be updated.
    """
    def __init__(self, message: str = "Failed to update file", details: Optional[Any] = None):
        super().__init__(message=message, details=details)


class FileDeleteError(FileManagerError):
    """
    Raised when a file cannot be deleted.
    """
    def __init__(self, message: str = "Failed to delete file", details: Optional[Any] = None):
        super().__init__(message=message, details=details)


class FileValidationError(ValidationError):
    """
    Raised for validation-related issues (size, extension, mime, path, etc.).
    Maps to 422 (Unprocessable Entity).
    """
    def __init__(self, message: str = "File validation error", details: Optional[Any] = None):
        super().__init__(message=message, details=details)


class FileAccessError(FileManagerError):
    """
    Raised when a file cannot be accessed (permissions, I/O errors, locks, etc.).
    """
    def __init__(self, message: str = "File access error", details: Optional[Any] = None):
        super().__init__(message=message, details=details)
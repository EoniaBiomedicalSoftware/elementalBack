import pytest
from unittest.mock import MagicMock
from app.elemental.exceptions import (
    ElementalBaseAppException,
    ElementalErrorCode,
    ElementalExceptionHandler,
    log_exception,
    format_exception_response,
    is_retriable_error,
    get_error_severity,
    validations,
    auth,
    application,
    external
)

# --- Exception Classes ---

def test_elemental_base_app_exception():
    """Must instantiate correctly with defaults."""
    exc = ElementalBaseAppException(
        message="Test error",
        error_code=ElementalErrorCode.INTERNAL_SERVER_ERROR,
        details={"info": "extra"}
    )
    assert exc.message == "Test error"
    assert exc.http_status == 500
    assert exc.error_code == "INTERNAL_SERVER_ERROR"
    assert exc.details == {"info": "extra"}

def test_validation_error_defaults():
    """ValidationError must have default code 422."""
    exc = validations.ValidationError("Invalid")
    assert exc.http_status == 422
    assert exc.error_code == "VALIDATION_ERROR"

def test_not_found_error_defaults():
    """NotFoundError must have default code 404."""
    exc = validations.NotFoundError()
    assert exc.http_status == 404
    assert exc.error_code == "NOT_FOUND"

# --- Utils ---

def test_format_exception_response():
    """Must generate standard JSON structure."""
    exc = ElementalBaseAppException(
        message="Oops",
        error_code=ElementalErrorCode.INVALID_INPUT
    )
    resp = format_exception_response(exc)
    
    assert resp["status_code"] == 400
    assert resp["content"]["error"] is True
    assert resp["content"]["message"] == "Oops"
    assert resp["content"]["error_code"] == "INVALID_INPUT"

def test_is_retriable_error():
    """Must identify retriable errors."""
    assert is_retriable_error(application.RateLimitError())
    assert is_retriable_error(external.ExternalServiceError())
    assert not is_retriable_error(validations.ValidationError("No"))

def test_get_error_severity():
    """Must assign correct severity."""
    assert get_error_severity(application.ConfigurationError()) == "critical"
    # AuthenticationError is from auth module, not validations
    assert get_error_severity(auth.AuthenticationError()) == "medium"
    assert get_error_severity(validations.ValidationError("User error")) == "low"

# --- Handler ---

@pytest.fixture
def handler():
    return ElementalExceptionHandler(log_exceptions=False)

def test_handler_elemental_exception(handler):
    """Must handle own exceptions by formatting them."""
    exc = auth.UnauthorizedError("Login first")
    resp = handler.handle(exc)
    assert resp["status_code"] == 401
    assert resp["content"]["message"] == "Login first"

def test_handler_unexpected_exception(handler):
    """Must handle unexpected exceptions as 500."""
    exc = ValueError("Boom")
    resp = handler.handle(exc)
    assert resp["status_code"] == 500
    assert resp["content"]["error_code"] == "INTERNAL_SERVER_ERROR"

def test_log_exception_calls_print(capsys):
    """Must print structured log (mocking print)."""
    exc = ValueError("TestLog")
    log_exception(exc, level="error")
    captured = capsys.readouterr()
    assert "[ERROR]" in captured.out
    assert "TestLog" in captured.out

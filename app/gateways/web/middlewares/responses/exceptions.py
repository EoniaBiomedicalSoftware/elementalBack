import os
import traceback
from typing import Optional

from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.elemental.logging import get_logger
from app.elemental.common import ElementalErrorCode
from app.elemental.common.responses import parse_response
from app.elemental.exceptions import (
    ElementalExceptionHandler,
    ElementalBaseAppException
)

_logger = None


def get_exception_middleware_logger():
    global _logger
    if _logger is None:
        _logger = get_logger("fastapi_exception_middleware")
    return _logger


class ExceptionParserMiddleware(BaseHTTPMiddleware):
    logger = get_exception_middleware_logger()
    status_mapping = ElementalErrorCode.to_dict()

    def __init__(self, app):
        super().__init__(app)
        _is_development = self._is_development()
        self.exception_handler = ElementalExceptionHandler(log_exceptions=_is_development)
        self.include_traceback = self._is_development()

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except ElementalBaseAppException as exc:
            return await self._handle_elemental_exception(request, exc)
        except ValidationError as exc:
            return await self._handle_pydantic_validation_error(request, exc)
        except Exception as exc:
            return await self._handle_generic_exception(request, exc)

    async def _handle_pydantic_validation_error(self, request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""
        validation_errors = exc.errors()
        simplified_details = {
            str(error.get('loc')[-1]) if error.get('loc') else 'general': error.get('msg', "Validation failed.")
            for error in validation_errors
        }

        first_error_msg = next(iter(simplified_details.values()), "Input validation failed.")
        status_code = self._get_status_code_from_error_code("VALIDATION_ERROR")

        self.logger.warning(f"Validation Error (Pydantic): {first_error_msg} for {request.method} {request.url}")

        content = parse_response(
            status_code=status_code,
            error_code="VALIDATION_ERROR",
            message=f"Validation failed: {first_error_msg}",
            details=simplified_details,
            path=str(request.url.path),
            method=request.method
        )
        return JSONResponse(status_code=status_code, content=content)

    async def _handle_elemental_exception(self, request: Request, exc: ElementalBaseAppException) -> JSONResponse:
        """Handle ElementalBaseAppException."""
        status_code = self._get_status_code_from_error_code(exc.error_code)

        self.logger.warning(f"ElementalException: {exc.error_code} - {exc.message} for {request.method} {request.url}")

        content = parse_response(
            status_code=status_code,
            error_code=exc.error_code,
            message=exc.message,
            details=getattr(exc, 'details', {}),
            path=str(request.url.path),
            method=request.method
        )
        return JSONResponse(status_code=status_code, content=content)

    async def _handle_generic_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle any other unhandled exception (500)."""
        self.logger.exception(f"Unhandled Exception: {request.method} {request.url} - {repr(exc)}")

        details = {}
        if self.include_traceback:
            details["traceback"] = traceback.format_exc().split('\n')[-5:]

        content = parse_response(
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal error occurred.",
            details=details,
            path=str(request.url.path),
            method=request.method
        )
        return JSONResponse(status_code=500, content=content)

    def _get_status_code_from_error_code(self, error_code: Optional[str]) -> int:
        """Map your error codes to HTTP status codes"""

        return self.status_mapping.get(error_code, 500)

    @staticmethod
    def _is_development() -> bool:
        """Check if running in a development environment"""
        env = os.getenv("app_env", "development").lower()
        return env in ["development", "dev", "local", "debug"]


exception_parser_middleware = (
    ExceptionParserMiddleware,
    {}
)
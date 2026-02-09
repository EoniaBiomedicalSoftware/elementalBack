import time
import os
from typing import Dict, Any, Optional

from pydantic import ValidationError

from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.elemental.logging import get_logger
from app.elemental.common import ElementalErrorCode

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

    def __init__(
        self,
        app,
        log_exceptions: bool = True
    ):
        super().__init__(app)
        self.exception_handler = ElementalExceptionHandler(log_exceptions=log_exceptions)
        self.include_traceback = self._is_development()

    async def dispatch(
        self,
        request: Request,
        call_next
    ):
        try:
            response: Response = await call_next(request)
            return response

        except ElementalBaseAppException as exc:
            return await self._handle_elemental_exception(request, exc)

        except ValidationError as exc:
            return await self._handle_pydantic_validation_error(request, exc)

        except Exception as exc:
            return await self._handle_generic_exception(request, exc)

    async def _handle_pydantic_validation_error(
        self,
        request: Request,
        exc: ValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors by transforming them into a simplified Elemental format."""

        validation_errors = exc.errors()

        simplified_details = {}
        first_error_msg = "Input validation failed."

        for error in validation_errors:
            field = str(error.get('loc')[-1]) if error.get('loc') else 'general'
            message = error.get('msg', "Validation failed.")

            if not simplified_details:
                first_error_msg = message

            simplified_details[field] = message

        status_code = self._get_status_code_from_error_code("VALIDATION_ERROR")

        self.logger.warning(
            f"Validation Error (Pydantic): {first_error_msg}. {len(validation_errors)} total issues "
            f"for {request.method} {request.url}"
        )

        error_response = {
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": f"Validation failed: {first_error_msg}",
            "details": simplified_details,
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": time.time()
        }

        return JSONResponse(
            status_code=status_code,
            content=error_response
        )

    async def _handle_elemental_exception(
        self,
        request: Request,
        exc: ElementalBaseAppException
    ) -> JSONResponse:
        """Handle ElementalBaseAppException"""
        
        context = self._build_request_context(request)
        
        error_response = self.exception_handler.handle(exc, context)
        
        error_response.update({
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": time.time()
        })
        
        status_code = self._get_status_code_from_error_code(exc.error_code)
        
        self.logger.warning(
            f"ElementalException: {exc.error_code} - {exc.message} "
            f"for {request.method} {request.url}"
        )
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )

    async def _handle_generic_exception(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Handle any other exception"""
        context = self._build_request_context(request)

        error_response = self.exception_handler.handle(exc, context)

        if "details" not in error_response:
            error_response["details"] = {}

        # Add request context
        error_response.update({
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": time.time()
        })

        # Add traceback in development
        if self.include_traceback:
            import traceback
            error_response["details"]["traceback"] = traceback.format_exc().split('\n')[-10:]

        self.logger.exception(
            f"Unhandled Exception: {request.method} {request.url} - {repr(exc)}"
        )

        return JSONResponse(
            status_code=500,
            content=error_response
        )

    @staticmethod
    def _build_request_context(request: Request) -> Dict[str, Any]:
        """Build request context for logging"""
        return {
            "path": str(request.url.path),
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "query_params": dict(request.query_params) if request.query_params else {},
            "timestamp": time.time()
        }

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
    {"log_exceptions": True}
)
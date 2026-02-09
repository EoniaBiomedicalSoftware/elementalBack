# OWASP Top 10: A09: Security Logging

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.elemental.logging import get_logger


_logger = None


def get_security_middleware_logger():
    global _logger
    if _logger is None:
        _logger = get_logger("fastapi_security_middleware")
    return _logger


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging security-relevant events such as authentication failures,
    authorization failures, and rate limit violations.
    """
    logger = get_security_middleware_logger()

    def __init__(self, app, log_success_events: bool = False):
        super().__init__(app)
        self.log_success_events = log_success_events

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Log authentication failures (401)
        if response.status_code == 401:
            self._log_security_event("auth_failure", request)

        # Log authorization failures (403)
        elif response.status_code == 403:
            self._log_security_event("authz_failure", request)

        # Log rate limit violations (429)
        elif response.status_code == 429:
            self._log_security_event("rate_limit_exceeded", request)

        # Optionally log successful requests
        elif self.log_success_events and 200 <= response.status_code < 300:
            self._log_security_event("request_success", request)

        return response

    def _log_security_event(
            self,
            event_type: str,
            request: Request,
            user_id: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None
    ):
        """Log security-relevant events in a structured JSON format"""

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "path": str(request.url.path),
            "method": request.method,
            "user_id": user_id,
            "details": details or {}
        }

        self.logger.info(json.dumps(event))


security_logging_middleware = (
    SecurityLoggingMiddleware,
    {"log_success_events": False}
)

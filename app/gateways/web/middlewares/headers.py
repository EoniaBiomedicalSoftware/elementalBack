import os
import secrets
from starlette.middleware.base import BaseHTTPMiddleware


# OWASP Top 10 Security Risks, A05
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    def __init__(self, app):
        super().__init__(app)
        self.is_dev = self._is_development()

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        # Prevent clickjacking by disallowing iframe embedding
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing attacks
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable the browser's XSS filter (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        if self.is_dev:
            csp =  (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net;"
            )

        else:
            csp = (
                "default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}'; "
                f"style-src 'self' 'nonce-{nonce}'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "upgrade-insecure-requests;"
            )

        response.headers["Content-Security-Policy"] = csp

        # Strict Transport Security - force HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Control referrer information sent with requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Disable browser features that aren't needed
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response

    @staticmethod
    def _is_development() -> bool:
        """Check if running in a development environment"""
        env = os.getenv("app_env", "development").lower()
        return env in ["development", "dev", "local", "debug"]


headers_middleware = (
    SecurityHeadersMiddleware,
    {}
)
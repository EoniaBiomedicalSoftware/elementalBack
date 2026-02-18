from datetime import datetime
from typing import Any, Optional


def parse_response(
    data: Any = None,
    error_code: Optional[str] = None,
    message: Optional[str] = None,
    details: Optional[dict] = None,
    status_code: int = 200,
    path: str = "",
    method: str = ""
) -> dict:
    """
    Standardizes the API response format for both success and error cases.
    """
    is_success = 200 <= status_code < 300

    # Build the standardized structure
    return {
        "success": is_success,
        "status_code": status_code,
        "path": path,
        "method": method,
        "timestamp": datetime.utcnow().timestamp(),
        "data": data if is_success else None,
        "error": None if is_success else {
            "code": error_code or "INTERNAL_ERROR",
            "message": message or "An unexpected error occurred.",
            "details": details or {}
        },
    }
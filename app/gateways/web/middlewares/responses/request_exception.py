import time
from starlette.requests import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse


async def elemental_form_error_handler(request: Request, exc: RequestValidationError):
    """
    Directly handles the 422 errors that bypass the middleware.
    """
    validation_errors = exc.errors()
    simplified_details = {}
    first_error_msg = "Input validation failed."

    for error in validation_errors:
        # Get field name: 'body', 'field_name' -> field_name
        field = str(error.get('loc')[-1]) if error.get('loc') else 'general'
        message = error.get('msg', "Validation failed.")

        if not simplified_details:
            first_error_msg = message

        simplified_details[field] = message

    # Build response following your Elemental pattern
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": f"Validation failed: {first_error_msg}",
            "details": simplified_details,
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": time.time()
        }
    )
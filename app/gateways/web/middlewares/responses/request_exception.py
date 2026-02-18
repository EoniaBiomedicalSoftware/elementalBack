from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.elemental.common.responses import parse_response


async def elemental_form_error_handler(request: Request, exc: RequestValidationError):
    """
    Directly handles the 422 errors that bypass the middleware
    using the standardized Elemental response format.
    """
    validation_errors = exc.errors()
    simplified_details = {}
    first_error_msg = "Input validation failed."

    for error in validation_errors:
        # Extract field name from the location tuple
        field = str(error.get('loc')[-1]) if error.get('loc') else 'general'
        message = error.get('msg', "Validation failed.")

        if not simplified_details:
            first_error_msg = message

        simplified_details[field] = message

    # Generate the standardized structure using your parser
    content = parse_response(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message=f"Validation failed: {first_error_msg}",
        details=simplified_details,
        path=str(request.url.path),
        method=request.method
    )

    return JSONResponse(
        status_code=422,
        content=content
    )
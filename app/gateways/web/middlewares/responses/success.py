import json
from typing import Optional, List
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.elemental.common.responses import parse_response

JSON_CONTENT_TYPES = [
    "application/json",
    "application/json; charset=utf-8"
]


class SuccessParserMiddleware(BaseHTTPMiddleware):
    _exclude_paths = [
        "/openapi.json",
        "/docs",
        "/redoc",
        "/",
    ]

    def __init__(self, app, exclude_paths: Optional[List[str]] = None):
        super().__init__(app)
        if exclude_paths:
            self._exclude_paths.extend(exclude_paths)

        self.exclude_paths = self._exclude_paths

    async def dispatch(self, request: Request, call_next):
        # Skip exclusion paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        response: Response = await call_next(request)

        # Process only successful JSON responses
        if 200 <= response.status_code < 300:
            content_type = response.headers.get("content-type", "")

            if not any(ct in content_type for ct in JSON_CONTENT_TYPES):
                return response

            # Consume the response body
            response_body = b''
            async for chunk in response.body_iterator: # noqa
                response_body += chunk

            try:
                # Load original data
                if response_body.strip():
                    original_data = json.loads(response_body.decode('utf-8'))
                else:
                    original_data = {}

                # Use your standardized parser
                standard_response = parse_response(
                    data=original_data,
                    status_code=response.status_code,
                    path=str(request.url.path),
                    method=request.method
                )

                # Prepare headers (removing content-length so it's recalculated)
                headers = dict(response.headers)
                headers.pop('content-length', None)

                return JSONResponse(
                    content=standard_response,
                    status_code=response.status_code,
                    headers=headers
                )

            except json.JSONDecodeError:
                # If it's not valid JSON, return the original content as is
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=content_type
                )

        return response


# Configuration tuple for FastAPI/Starlette
success_parser_middleware = (
    SuccessParserMiddleware,
    {"exclude_paths": []}
)
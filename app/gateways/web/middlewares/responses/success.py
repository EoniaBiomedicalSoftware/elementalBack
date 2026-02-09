import json
import time
from typing import Optional, List
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any, Dict

JSON_CONTENT_TYPES = [
    "application/json",
    "application/json; charset=utf-8"
]

class SuccessParserMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, exclude_paths: Optional[List[str]] = None):
        super().__init__(app)
        _exclude_paths = [
            "/openapi.json",
            "/docs",
            "/redoc",
            "/",
        ]

        if exclude_paths:
            _exclude_paths.extend(exclude_paths)

        self.exclude_paths = _exclude_paths

    async def dispatch(self, request: Request, call_next):

        if request.url.path in self.exclude_paths:
            return await call_next(request)

        response: Response = await call_next(request)

        if 200 <= response.status_code < 300:
            content_type = response.headers.get("content-type", "")

            if not any(ct in content_type for ct in JSON_CONTENT_TYPES):
                return response

            response_body = b''
            async for chunk in response.body_iterator:
                response_body += chunk

            try:
                if response_body.strip():
                    original_data: Any = json.loads(response_body.decode('utf-8'))
                else:
                    original_data = {}

                standard_response: Dict[str, Any] = {
                    "success": True,
                    "status_code": response.status_code,
                    "timestamp": time.time(),
                    "data": original_data
                }

                headers = dict(response.headers)
                if 'content-length' in headers:
                    del headers['content-length']

                new_response = JSONResponse(
                    content=standard_response,
                    status_code=response.status_code,
                    headers=headers
                )

                return new_response

            except json.JSONDecodeError:
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=content_type
                )

        return response

success_parser_middleware = (
    SuccessParserMiddleware,
    {}
)
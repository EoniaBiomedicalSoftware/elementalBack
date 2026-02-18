from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = {}

class StandardResponse(BaseModel, Generic[T]):
    success: bool
    status_code: int
    path: str
    method: str
    timestamp: float
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Custom API",
        version="1.0.0",
        routes=app.routes,
    )

    for path in openapi_schema["paths"].values():
        for method in path.values():
            responses = method.get("responses", {})

            for code, response in responses.items():
                # Process both success (2xx) and errors (4xx, 5xx)
                content = response.get("content", {}).get("application/json", {})
                original_schema = content.get("schema")

                if original_schema:
                    # Determine if it's an error based on status code
                    is_error = int(code) >= 400

                    content["schema"] = {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "default": not is_error},
                            "status_code": {"type": "integer", "default": int(code)},
                            "path": {"type": "string"},
                            "method": {"type": "string"},
                            "timestamp": {"type": "number"},
                            "data": original_schema if not is_error else {"type": "object", "nullable": True},
                            "error": {
                                "type": "object",
                                "nullable": not is_error,
                                "properties": {
                                    "code": {"type": "string"},
                                    "message": {"type": "string"},
                                    "details": original_schema if is_error else {"type": "object"}
                                }
                            }
                        }
                    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema
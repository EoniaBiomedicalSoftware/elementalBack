from fastapi.middleware.cors import CORSMiddleware
from app.elemental.settings import get_settings

_settings = get_settings()
_cors_settings = _settings.application.cors

cors_middleware = (
    CORSMiddleware,
    {
        "allow_origins": _cors_settings.origins,
        "allow_credentials": _cors_settings.allow_credentials,
        "allow_methods": _cors_settings.allow_methods,
        "allow_headers": _cors_settings.allow_headers,
        "max_age": _cors_settings.max_age,
    }
)

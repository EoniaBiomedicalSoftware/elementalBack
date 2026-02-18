from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.elemental.settings import get_settings

from .middlewares import (
    logging_middleware,
    cors_middleware,
    exception_parser_middleware,
    success_parser_middleware,
    headers_middleware,
    security_logging_middleware,
    elemental_form_error_handler
)

from .routers import (
    elemental_router,
    get_all_routers,
    custom_openapi
)

from .lifespan import app_lifespan


def __init_routers__(_app_: FastAPI, api_prefix: str = '') -> None:
    
    for router in get_all_routers():
        elemental_router.include_router(router)

    _app_.include_router(
        router=elemental_router,
        prefix=api_prefix
    )
    _app_.openapi = lambda: custom_openapi(_app_)


def __init_middlewares__(
    _app_: FastAPI,
) -> None:

    middleware_list = [
        cors_middleware,
        logging_middleware,
        headers_middleware,
        success_parser_middleware,
        exception_parser_middleware,
        security_logging_middleware
    ]

    for middleware_class, options in middleware_list:
        _app_.add_middleware(middleware_class, **options)
    _app_.add_exception_handler(RequestValidationError, elemental_form_error_handler)


def create_app() -> FastAPI:
    _settings = get_settings()
    _app_settings = _settings.application

    _app_ = FastAPI(
        version=_app_settings.app_version,
        title=_app_settings.app_name,
        description=_app_settings.app_description,
        swagger_url='/docs',
        redoc_url='/',
        openapi_url='/openapi.json',
        debug=_app_settings.debug,
        lifespan=app_lifespan
    )
    
    __init_routers__(_app_, api_prefix=_app_settings.api_prefix)
    
    __init_middlewares__(_app_)

    return _app_

import time

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from sqlalchemy.exc import SQLAlchemyError

from app.elemental.logging import get_logger


_logger = None

def get_middleware_logger():
    global _logger
    if _logger is None:
        _logger = get_logger("fastapi_logging_middleware")
    return _logger


class LoggingMiddleware(BaseHTTPMiddleware):

    logger = get_middleware_logger()

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        self.logger.info(f"Request: {request.method} {request.url}")

        try:
            response: Response = await call_next(request)

            process_time = time.time() - start_time

            self.logger.info(
                f"Response: {response.status_code} "
                f"for {request.method} {request.url} "
                f"({process_time:.2f}s)"
            )

            return response

        except SQLAlchemyError as db_ex:
            self.logger.error(
                f"Database Error during request: {request.method} {request.url} "
                f"- Error Details: {str(db_ex)}"
            )
            raise

        except Exception as ex:
            self.logger.exception(
                f"Error during request: {request.method} {request.url} - {repr(ex)}"
            )
            raise


logging_middleware = (
    LoggingMiddleware,
    {}
)

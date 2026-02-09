from logging import Logger
from typing import Optional, AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.exc import SQLAlchemyError

from app.elemental.logging import get_logger

from .settings import DatabaseSettings
from .exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseInitializationError,
)

# Global instances for the singleton-like behavior
_logger: Optional[Logger] = None
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_db_logger() -> Logger:
    """Lazy initialization of the database logger."""
    global _logger
    if _logger is None:
        _logger = get_logger("database")
    return _logger


def is_database_initialized() -> bool:
    """Checks if the database engine and factory are ready."""
    return _session_factory is not None


def get_engine() -> AsyncEngine:
    """Returns the current engine or raises an error if not initialized."""
    if _engine is None:
        raise DatabaseInitializationError(
            "Database engine not initialized. Call init_database() first."
        )
    return _engine


async def test_database_connection() -> None:
    """Performs a 'ping' to the database to ensure connectivity."""
    logger = get_db_logger()

    if not _session_factory:
        raise DatabaseInitializationError(
            "Cannot test connection: Session factory not initialized."
        )

    try:
        async with _session_factory() as session: # noqa
            result = await session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("Database connectivity test: SUCCESS")
            else:
                raise DatabaseError("Database test query returned unexpected result.")

    except SQLAlchemyError as e:
        logger.error(f"Database connectivity test: FAILED - {str(e)}")
        raise DatabaseConnectionError(f"Could not connect to database: {e}") from e


async def init_database(settings: DatabaseSettings) -> None:
    """Initializes the engine and session factory based on provided settings."""
    global _engine, _session_factory
    logger = get_db_logger()

    try:
        logger.info(f"Initializing database: {settings.driver}://{settings.host}")

        # Connection string construction
        if settings.driver.startswith('sqlite'):
            url = f"{settings.driver}:///{settings.name}"
            connect_args = {"check_same_thread": False}
            pool_kwargs = {}
        else:
            url = (
                f"{settings.driver}://"
                f"{settings.user}:{settings.password.get_secret_value()}"
                f"@{settings.host}:{settings.port}/{settings.name}"
            )
            connect_args = {}
            pool_kwargs = {
                "pool_size": settings.pool_size,
                "max_overflow": settings.max_overflow,
            }

        _engine = create_async_engine(
            url,
            echo=settings.echo,
            future=True,
            connect_args=connect_args,
            **pool_kwargs
        )

        _session_factory = async_sessionmaker(
            _engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

        # Immediate health check
        await test_database_connection()

    except Exception as e:
        logger.critical(f"Database initialization failed: {e}")
        # Reset globals to avoid half-baked states
        _engine = None
        _session_factory = None
        raise


async def get_session() -> AsyncSession:
    """Manual session creator. Useful for background tasks or scripts."""
    if _session_factory is None:
        raise DatabaseInitializationError("Database factory not initialized.")
    return _session_factory() # noqa


async def get_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an AsyncSession.
    Automatically handles session lifecycle and transactions.
    """
    if _session_factory is None:
        raise DatabaseInitializationError("Database factory not initialized.")

    async with _session_factory() as session: # noqa
        try:
            # We use session.begin() to start a transaction context
            async with session.begin():
                yield session
            # Auto-commit happens here if no exception occurred
        except Exception:
            # Auto-rollback happens here on any exception
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database() -> None:
    """Cleanup method for application shutdown."""
    global _engine, _session_factory
    if _engine:
        get_db_logger().info("Disposing database engine...")
        await _engine.dispose()
        _engine = None
        _session_factory = None
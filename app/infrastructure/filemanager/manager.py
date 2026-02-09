from typing import Optional
from logging import Logger

from app.elemental.logging import get_logger

from .settings import FileManagerSettings
from .drivers.local import LocalFileManager
from .exceptions import FileManagerError


_logger: Optional[Logger] = None
_provider = None


def get_filemanager_logger() -> Logger:
    global _logger
    if _logger is None:
        _logger = get_logger("filemanager")
    return _logger


async def init_filemanager(settings: FileManagerSettings) -> None:
    global _provider

    logger = get_filemanager_logger()

    try:
        if settings.storage_type == "local":
            _provider = LocalFileManager(settings)
        # elif settings.storage_type == "s3":
        #     _provider = S3FileManager(settings)
        # elif settings.storage_type == "azure":
        #     _provider = AzureFileManager(settings)
        else:
            raise FileManagerError(f"Invalid provider: {settings.storage_type}")

        logger.info(f"FileManager initialized with provider: {type(_provider).__name__}")

    except Exception as e:
        logger.error(f"Failed to initialize FileManager: {e}")
        _provider = None
        raise FileManagerError(str(e))


def get_filemanager():
    if _provider is None:
        raise FileManagerError("FileManager not initialized")
    return _provider

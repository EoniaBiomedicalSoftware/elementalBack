import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .formatters import get_formatter

_LOGGER_REGISTRY = {}


def setup_elemental_logger(name: str = "global_logger") -> logging.Logger:
    if name in _LOGGER_REGISTRY:
        return _LOGGER_REGISTRY[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(get_formatter("colored"))

    log_file = Path("logs/app.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(get_formatter("detailed"))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    _LOGGER_REGISTRY[name] = logger
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get or create a logger instance
    """
    return setup_elemental_logger(name or "global_logger")

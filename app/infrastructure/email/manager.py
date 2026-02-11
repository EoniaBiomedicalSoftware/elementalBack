import importlib
import pkgutil
from logging import Logger
from pathlib import Path
from typing import Dict, Any, Optional

from app.elemental.logging import get_logger

try:
    import app.src.shared.email_templates
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Email templates not found, in order to use this module email templates must exist in the nexus package.")

from .settings import EmailSettings
from .drivers import EmailServiceManager
from .exceptions import (
    EmailConnectionError,
)

_logger = None
_email_service: Optional[EmailServiceManager] = None

_templates_dir = Path('app') / 'src' / 'shared' / 'email_templates'

_email_templates_context: Dict[str, Dict[str, Any]] = {}


def get_application_email_context() -> dict:
    global _email_templates_context
    logger = get_email_logger()

    src_path = app.src.shared.email_templates.__path__

    for _, module_name, is_pkg in pkgutil.iter_modules(src_path):
        if not is_pkg:
            continue

        logger.debug(f"Checking module: {module_name} (pkg: {is_pkg})")

        try:
            mod = importlib.import_module(
                f"app.src.shared.email_templates.{module_name}"
            )

            if hasattr(mod, "register_templates"):
                context_dict = getattr(mod, "register_templates")

                if isinstance(context_dict, dict):
                    _email_templates_context.update(context_dict)
                    logger.info(
                        f"Templates from {module_name} added"
                    )
            else:
                logger.warning(
                    f"Module {module_name} does not have a register_templates defined."
                )

        except ModuleNotFoundError as e:
            logger.warning(
                f"Email Context not found in {module_name}: {e}"
            )

    return _email_templates_context


def get_email_logger() -> Logger:
    global _logger
    if _logger is None:
        _logger = get_logger("email_logger")
    return _logger


async def create_email_service(
    templates_dir: Path,
    templates_context: Dict[str, Dict[str, Any]],
    email_settings: EmailSettings
) -> EmailServiceManager:

    logger = get_email_logger()

    logger.info("Creating EmailService...")

    return EmailServiceManager(
        templates_dir=templates_dir,
        templates_context=templates_context,
        logger=logger,
        settings=email_settings
    )


async def init_email_service(
    email_settings: EmailSettings
) -> EmailServiceManager:

    global _email_service

    logger = get_email_logger()
    application_email_context = get_application_email_context()

    if not application_email_context:
        logger.warning(
            "No email templates registered in the application."
        )

    try:
        logger.info("Initializing global email service...")

        _email_service = await create_email_service(
            templates_dir=_templates_dir,
            templates_context=application_email_context,
            email_settings=email_settings
        )

        is_connected = await _email_service.test_connection()

        if not is_connected:
            logger.error("Failed to connect to email service, verify settings and try again.")
            raise EmailConnectionError("Failed to connect to email service")

        logger.info("Global email service initialized")
        return _email_service

    except Exception as e:
        logger.error(f"Failed to initialize global email service: {e}")
        raise EmailConnectionError(f"Failed to initialize email service: {e}") from e


def get_email_service() -> EmailServiceManager:
    if not _email_service:
        raise EmailConnectionError("Email service not initialized. Call init_email_service() first.")

    return _email_service


def is_email_service_initialized() -> bool:
    return _email_service is not None
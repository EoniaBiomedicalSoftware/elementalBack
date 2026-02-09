from typing import Dict, Optional
from logging import Logger

from app.elemental.logging import get_logger

from .settings import OAuthSettings
from .drivers import OAuthProviderBase
from .factory import get_driver_class
from .exceptions import OAuthError, ProviderNotFoundError

_logger: Optional[Logger] = None
_providers: Dict[str, OAuthProviderBase] = {}


def get_oauth_logger() -> Logger:
    global _logger
    if _logger is None:
        _logger = get_logger("oauth_logger")
    return _logger


async def init_oauth(settings: OAuthSettings) -> None:
    global _providers
    logger = get_oauth_logger()

    try:
        for provider_name, provider_settings in settings.providers.items():
            provider_class = get_driver_class(provider_name)

            _providers[provider_name] = provider_class(provider_settings)

            logger.info(f"OAuth provider '{provider_name}' initialized with class: {provider_class.__name__}")

    except Exception as e:
        logger.error(f"Failed to initialize OAuth providers: {e}")
        _providers = {}
        raise OAuthError(str(e))


def get_oauth_provider(name: str) -> OAuthProviderBase:
    provider = _providers.get(name)
    if provider is None:
        raise ProviderNotFoundError(f"OAuth provider '{name}' not found.")
    return provider


async def close_oauth():
   global _providers
   _providers.clear()

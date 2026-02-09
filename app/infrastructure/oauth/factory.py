from typing import Dict, Type
from .drivers.base import OAuthProviderBase
from .drivers.google import GoogleOAuthProvider

_STRATEGIES: Dict[str, Type[OAuthProviderBase]] = {
    "google": GoogleOAuthProvider,
}

def get_driver_class(name: str) -> Type[OAuthProviderBase]:
    cls = _STRATEGIES.get(name.lower())
    if not cls:
        raise ValueError(f"OAuth driver '{name}' is not supported.")
    return cls
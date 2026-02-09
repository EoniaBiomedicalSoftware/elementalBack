from typing import Optional, TypeVar, Type
from .elemental import ElementalSettings

T = TypeVar("T", bound=ElementalSettings)

_settings: Optional[ElementalSettings] = None


def init_settings(settings_instance: ElementalSettings) -> None:
    global _settings
    _settings = settings_instance


def get_settings(cast_type: Type[T] = ElementalSettings) -> T:
    if _settings is None:
        raise RuntimeError("Settings have not been initialized. Call set_settings() first.")
    return _settings
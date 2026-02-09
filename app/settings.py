from .elemental.settings import ElementalSettings
from .elemental.security import ElementalJWTSettings

from .infrastructure.oauth import OAuthSettings

class ApplicationSettings(ElementalSettings):
    jwt: ElementalJWTSettings

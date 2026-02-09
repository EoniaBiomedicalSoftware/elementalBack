from abc import ABC, abstractmethod
from typing import Dict, Any
from ..settings import OAuthProviderSettings


class OAuthProviderBase(ABC):
    def __init__(self, settings: OAuthProviderSettings):
        self.settings = settings

    # @abstractmethod
    # def get_authorization_url(self, state: Optional[str] = None) -> str:
    #     """Generate the authorization URL for the OAuth provider"""
    #     pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information using the access token"""
        pass

    # @abstractmethod
    # async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
    #     """Refresh the access token using refresh token"""
    #     pass
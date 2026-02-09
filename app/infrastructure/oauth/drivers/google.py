import httpx
from typing import Dict, Any

from .base import OAuthProviderBase

from ..exceptions import OAuthError, OAuthInvalidTokenError
from ..settings import GoogleSettings


class GoogleOAuthProvider(OAuthProviderBase):
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self, settings: GoogleSettings):
        super().__init__(settings)
        self.client_secret = settings.client_secret.get_secret_value()

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        data = {
            "client_id": self.settings.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.settings.redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.TOKEN_URL, data=data)

            if response.status_code != 200:
                raise OAuthError(
                    message=f"Failed to exchange code for token: {response.text}",
                    details={"status": response.status_code, "provider": "google"}
                )

            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.USER_INFO_URL, headers=headers)

            if response.status_code != 200:
                raise OAuthInvalidTokenError(
                    message="Failed to fetch user info from Google, token may be invalid."
                )

            return response.json()

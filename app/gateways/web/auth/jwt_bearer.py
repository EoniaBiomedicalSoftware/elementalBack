from typing import Optional

from jwt.exceptions import PyJWTError
from jwt.exceptions import ExpiredSignatureError

from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from app.elemental.exceptions import AuthenticationError
from app.elemental.security.tokens import decode_token
from app.elemental.security.tokens import ElementalTokenTypes


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[dict]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if not credentials:
            raise AuthenticationError(message="Missing authorization header.")

        if not credentials.scheme == "Bearer":
            raise AuthenticationError(
                message="Invalid authorization scheme. Expected Bearer.",
            )

        token = credentials.credentials
        payload = self.get_payload(token)
        if not payload:
            raise AuthenticationError(message="Invalid token.")

        if payload.get("type") != ElementalTokenTypes.ACCESS:
            raise AuthenticationError(message="Invalid token type.")

        return payload

    @staticmethod
    def get_payload(token: str) -> Optional[dict]:
        try:
            return decode_token(token)
        except (ExpiredSignatureError, PyJWTError):
            return None
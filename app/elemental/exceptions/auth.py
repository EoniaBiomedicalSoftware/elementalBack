from app.elemental.common import ElementalErrorCode
from .base import ElementalBaseAppException

# --- BASE 401 UNAUTHORIZED ---
class AuthenticationError(ElementalBaseAppException):
    def __init__(
        self,
        error_code:ElementalErrorCode=ElementalErrorCode.AUTHENTICATION_ERROR,
        message: str = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            **kwargs
        )

class UnauthorizedError(AuthenticationError):
    def __init__(self, message: str = None):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.UNAUTHORIZED,
        )

class TokenExpiredError(AuthenticationError):
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.TOKEN_EXPIRED,
            **kwargs
        )

class TokenRevokedError(AuthenticationError):
    def __init__(self, message: str = None):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.TOKEN_REVOKED,
        )


# --- BASE 403 FORBIDDEN ---
class ForbiddenError(ElementalBaseAppException):
    def __init__(
        self,
        message: str = None,
        error_code: ElementalErrorCode = ElementalErrorCode.FORBIDDEN,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            **kwargs
        )

class AccountDisabledError(ForbiddenError):
    def __init__(self, message: str = None):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.ACCOUNT_DISABLED,
        )


class AccountNotVerifiedError(ForbiddenError):
    def __init__(self, message: str = None):
        super().__init__(
            message=message,
            error_code=ElementalErrorCode.ACCOUNT_NOT_VERIFIED,
        )
from typing import Optional

import jwt
from datetime import datetime, timedelta, timezone
from jwt.exceptions import ExpiredSignatureError, PyJWTError

from ...settings import get_settings
from .types import ElementalTokenTypes
from ...exceptions.auth import TokenExpiredError, UnauthorizedError


def _expiration_for(
    token_type, *,
    days=0, hours=0, minutes=0, seconds=0
) -> datetime:
    _app_settings = get_settings()
    _settings = _app_settings.jwt

    """Resolve expiration rules."""
    custom = any([days, hours, minutes, seconds])

    if custom:
        return datetime.now(timezone.utc) + timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        )

    if token_type == ElementalTokenTypes.ACCESS or token_type == "general":
        delta = _settings.access_token.expire_delta
    elif token_type == ElementalTokenTypes.REFRESH:
        delta = _settings.refresh_token.expire_delta
    else:
        raise ValueError(f"Unknown token type '{token_type}'.")

    return datetime.now(timezone.utc) + delta

def _create_token(
    data: dict,
    token_type: str,
    sub_key: Optional[str] = None, **kwargs
) -> str:
    _app_settings = get_settings()
    _settings = _app_settings.jwt

    _secret = _settings.secret_key.get_secret_value()
    _algorithm = _settings.algorithm

    """Internal helper to build and encode JWT with extra data support."""
    if not isinstance(data, dict):
        raise ValueError("Data must be a dict")

    exp = _expiration_for(token_type, **kwargs)

    if sub_key:
        if sub_key not in data.keys():
            raise ValueError(
                f"Missing '{sub_key}' key in data."
                f"Available keys: {', '.join(data.keys())}"
            )
        sub = str(data[sub_key])
    else:
        sub = str(data.get("id") or data.get("sub") or data.get("user_id"))

    # 1. Base claims (Flat structure)
    payload = {
        "sub": sub,
        "type": token_type,
        "exp": int(exp.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "version": data.get("version") or data.get("token_version", 1)
    }

    # 2. Merge extra data (Avoiding reserved keys)
    reserved_keys = list(payload.keys()) + ["id", "token_type"]
    extra_data = {k: v for k, v in data.items() if k not in reserved_keys}
    payload.update(extra_data)

    return jwt.encode(payload, _secret, algorithm=_algorithm)

def create_access_token(data: dict) -> str:
    return _create_token(data, ElementalTokenTypes.ACCESS)

def create_refresh_token(data: dict) -> str:
    return _create_token(data, ElementalTokenTypes.REFRESH)

def create_general_token(
    data: dict,
    token_type="general",
    days=0, hours=0, minutes=0, seconds=0
) -> str:
    return _create_token(data, token_type, days=days, hours=hours, minutes=minutes, seconds=seconds)

def decode_token(token: str) -> dict:
    _app_settings = get_settings()
    _settings = _app_settings.jwt

    _secret = _settings.secret_key.get_secret_value()
    _algorithm = _settings.algorithm

    """Decodes token and raises custom Elemental exceptions."""
    try:
        return jwt.decode(token, _secret, algorithms=[_algorithm])
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except PyJWTError as e:
        print(e)
        raise UnauthorizedError(message="Invalid or malformed JWT token")
    except Exception as e:
        raise UnauthorizedError(message=f"Could not validate credentials: {str(e)}")
import pytest
import jwt
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from app.elemental.security.tokens.provider import (
    create_access_token,
    create_refresh_token,
    create_general_token,
    decode_token
)
from app.elemental.exceptions.auth import TokenExpiredError, UnauthorizedError

# --- Fixture ---

@pytest.fixture
def mock_token_settings():
    """JWT configuration mock."""
    with patch("app.elemental.security.tokens.provider._settings") as mock_settings:
        mock_settings.algorithm = "HS256"
        mock_settings.secret_key.get_secret_value.return_value = "super-secret-key"
        
        # Configure simulated expirations
        mock_settings.access_token.expire_delta = timedelta(minutes=15)
        mock_settings.refresh_token.expire_delta = timedelta(days=7)
        
        yield mock_settings

# --- Creation Tests ---

def test_create_access_token_payload(mock_token_settings):
    """Must create a token with correct claims."""
    data = {"sub": "user123", "role": "admin"}
    token = create_access_token(data)
    
    decoded = jwt.decode(
        token,
        "super-secret-key",
        algorithms=["HS256"]
    )
    
    assert decoded["sub"] == "user123"
    assert decoded["role"] == "admin"
    assert decoded["type"] == "access"
    assert "exp" in decoded

def test_create_refresh_token_type(mock_token_settings):
    """Must create a refresh token with correct type."""
    token = create_refresh_token({"id": "user123"})
    decoded = jwt.decode(token, "super-secret-key", algorithms=["HS256"])
    assert decoded["type"] == "refresh"

def test_create_token_missing_sub_behavior(mock_token_settings):
    """Must use 'None' if no subject is found (current behavior)."""
    # Current code converts None to "None"
    token = create_access_token({"data": "missing_id"})
    decoded = jwt.decode(token, "super-secret-key", algorithms=["HS256"])
    assert decoded["sub"] == "None"

def test_create_general_token_custom_expiry(mock_token_settings):
    """Must allow custom expiration."""
    token = create_general_token(
        {"id": "1"}, 
        token_type="reset_password",
        minutes=5
    )
    decoded = jwt.decode(token, "super-secret-key", algorithms=["HS256"])
    
    # Verify approximate expiration (this may vary by microseconds)
    issue_time = datetime.now(timezone.utc).timestamp()
    assert decoded["exp"] - issue_time <= 305  # 5 min + margin
    assert decoded["type"] == "reset_password"

# --- Decoding Tests ---

def test_decode_token_valid(mock_token_settings):
    """Must decode a valid token."""
    token = jwt.encode(
        {"sub": "123", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "super-secret-key",
        algorithm="HS256"
    )
    payload = decode_token(token)
    assert payload["sub"] == "123"

def test_decode_token_expired(mock_token_settings):
    """Must raise TokenExpiredError if token expired."""
    expired_token = jwt.encode(
        {"sub": "123", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        "super-secret-key",
        algorithm="HS256"
    )
    with pytest.raises(TokenExpiredError):
        decode_token(expired_token)

def test_decode_token_invalid_signature(mock_token_settings):
    """Must raise UnauthorizedError if signature is invalid."""
    # Token signed with another key
    fake_token = jwt.encode(
        {"sub": "123"},
        "wrong-key",
        algorithm="HS256"
    )
    with pytest.raises(UnauthorizedError):
        decode_token(fake_token)

def test_decode_token_malformed(mock_token_settings):
    """Must handle malformed tokens."""
    with pytest.raises(UnauthorizedError):
        decode_token("this.is.not.a.token")

import pytest
from unittest.mock import MagicMock, patch
from app.elemental.security.passwords.utils import (
    get_password_hash,
    verify_password,
    validate_password_strength,
    generate_secure_password,
    PasswordStrengthError,
    InvalidLengthError
)

# --- Hash Tests ---

@patch("app.elemental.security.passwords.utils._pwd_context")
def test_get_password_hash(mock_context):
    """Must call hash context."""
    mock_context.hash.return_value = "hashed_secret"
    result = get_password_hash("secret")
    
    mock_context.hash.assert_called_with("secret")
    assert result == "hashed_secret"

@patch("app.elemental.security.passwords.utils._pwd_context")
def test_verify_password(mock_context):
    """Must verify password correctly."""
    verify_password("plain", "hash")
    mock_context.verify.assert_called_with("plain", "hash")

# --- Strength Tests ---

def test_validate_password_strength_valid():
    """Must validate a strong password."""
    # 8 chars, Upper, Lower, Number, default special allowed
    pwd = "Password1!"
    assert validate_password_strength(
        pwd,
        min_length=8,
        require_uppercase=True,
        require_lowercase=True,
        require_number=True,
        require_special=True
    )

def test_validate_password_strength_too_short():
    """Must raise error if too short."""
    with pytest.raises(InvalidLengthError):
        validate_password_strength("Short1!", min_length=10)

def test_validate_password_strength_missing_requirements():
    """Must verify each requirement individually."""
    # Missing uppercase
    with pytest.raises(PasswordStrengthError) as exc:
        validate_password_strength("lowercase1!", require_uppercase=True)
    assert "uppercase" in str(exc.value)

    # Missing lowercase
    with pytest.raises(PasswordStrengthError) as exc:
        validate_password_strength("UPPERCASE1!", require_lowercase=True)
    assert "lowercase" in str(exc.value)

    # Missing number
    with pytest.raises(PasswordStrengthError) as exc:
        validate_password_strength("NoNumber!", require_number=True)
    assert "number" in str(exc.value)
    
    # Missing special
    with pytest.raises(PasswordStrengthError) as exc:
        validate_password_strength("NoSpecial1", require_special=True)
    assert "special character" in str(exc.value)

# --- Generator Tests ---

def test_generate_secure_password_length():
    """Must generate password of correct length."""
    pwd = generate_secure_password(length=16)
    assert len(pwd) == 16

def test_generate_secure_password_complexity():
    """Must include all required character types."""
    # Test multiple times to avoid false positives due to randomness
    for _ in range(5):
        pwd = generate_secure_password(
            length=20,
            require_uppercase=True,
            require_lowercase=True,
            require_number=True,
            require_special=True
        )
        assert any(c.isupper() for c in pwd)
        assert any(c.islower() for c in pwd)
        assert any(c.isdigit() for c in pwd)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd)

def test_generate_secure_password_custom_length():
    """Must respect custom length."""
    pwd = generate_secure_password(length=50)
    assert len(pwd) == 50

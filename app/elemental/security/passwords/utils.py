import re
import secrets
import string
from passlib.context import CryptContext

from ...exceptions import InvalidLengthError, ValidationError


# Specialized error for password rules
class PasswordStrengthError(ValidationError):
    """Raised when a password does not meet security complexity requirements."""

    def __init__(self, reason: str, **kwargs):
        super().__init__(
            message=f"Password security requirement failed: {reason}",
            details={"reason": reason},
            **kwargs
        )

# OWASP Top 10 A02
_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def get_password_hash(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


def needs_rehashing(hashed_password: str) -> bool:
    return _pwd_context.needs_update(hashed_password)


def validate_password_strength(
        password: str,
        *,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_number: bool = True,
        require_special: bool = False,
        special_chars_pattern: str = r"[!@#$%^&*()_+=\[\]{};':\"\\|,.<>/?`~-]"
) -> bool:
    if len(password) < min_length:
        raise InvalidLengthError(field_name="password", min_length=min_length)

    if require_uppercase and not re.search(r"[A-Z]", password):
        raise PasswordStrengthError("At least one uppercase letter required")

    if require_lowercase and not re.search(r"[a-z]", password):
        raise PasswordStrengthError("At least one lowercase letter required")

    if require_number and not re.search(r"\d", password):
        raise PasswordStrengthError("At least one number required")

    if require_special and not re.search(special_chars_pattern, password):
        raise PasswordStrengthError("At least one special character required")

    return True


def generate_secure_password(
        length: int = 12,
        *,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_number: bool = True,
        require_special: bool = True
) -> str:
    # Define pools clearly
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    pools = []
    password_chars = []

    if require_uppercase:
        pools.append(uppercase)
        password_chars.append(secrets.choice(uppercase))
    if require_lowercase:
        pools.append(lowercase)
        password_chars.append(secrets.choice(lowercase))
    if require_number:
        pools.append(digits)
        password_chars.append(secrets.choice(digits))
    if require_special:
        pools.append(special)
        password_chars.append(secrets.choice(special))

    all_chars = "".join(pools)

    remaining_length = length - len(password_chars)
    for _ in range(remaining_length):
        password_chars.append(secrets.choice(all_chars))

    # Secure shuffle
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)
import pytest
from app.elemental.security.roles import (
    validate_roles,
    check_user_role,
    require_role,
    extract_user_info,
    get_user_permissions,
    has_permission
)
from app.elemental.exceptions import ForbiddenError, UnauthorizedError

def test_validate_roles_valid():
    """Must allow strings and integers."""
    validate_roles("admin", "user", 1, 2)
    assert True  # If it doesn't raise exception, it passes

def test_validate_roles_invalid():
    """Must raise ValueError for disallowed types."""
    with pytest.raises(ValueError):
        validate_roles("admin", None)

def test_check_user_role_returns_true():
    """Must return True if the role is in the list."""
    payload = {"role": "admin"}
    assert check_user_role(payload, ["admin", "user"])

def test_check_user_role_returns_false():
    """Must return False if the role does not match."""
    payload = {"role": "guest"}
    assert not check_user_role(payload, ["admin", "superadmin"])

def test_require_role_success():
    """Must return the payload if the role is valid."""
    payload = {"role": "admin", "data": 123}
    result = require_role(payload, "admin")
    assert result == payload

def test_require_role_no_token():
    """Must raise UnauthorizedError if there is no payload."""
    with pytest.raises(UnauthorizedError):
        require_role({}, "admin")
    with pytest.raises(UnauthorizedError):
        require_role(None, "admin")

def test_require_role_forbidden():
    """Must raise ForbiddenError if the role is incorrect."""
    payload = {"role": "user"}
    with pytest.raises(ForbiddenError):
        require_role(payload, "admin")

def test_extract_user_info():
    """Must correctly extract defined fields."""
    payload = {
        "id": 1,
        "username": "test",
        "role": "user",
        "email": "test@test.com",
        "iat": 100,
        "exp": 200,
        "extra": "ignored"
    }
    info = extract_user_info(payload)
    assert info["id"] == 1
    assert info["username"] == "test"
    assert "extra" not in info

def test_get_user_permissions_and_has_permission():
    """Must verify permissions correctly."""
    payload = {"permissions": ["read", "write"]}
    
    assert get_user_permissions(payload) == ["read", "write"]
    
    assert has_permission(payload, "read")
    assert not has_permission(payload, "delete")

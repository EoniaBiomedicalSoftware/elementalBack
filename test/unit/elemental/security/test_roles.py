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
    """Debe permitir cadenas y enteros."""
    validate_roles("admin", "user", 1, 2)
    assert True  # Si no lanza excepción, pasa

def test_validate_roles_invalid():
    """Debe lanzar ValueError para tipos no permitidos."""
    with pytest.raises(ValueError):
        validate_roles("admin", None)

def test_check_user_role_returns_true():
    """Debe retornar True si el rol está en la lista."""
    payload = {"role": "admin"}
    assert check_user_role(payload, ["admin", "user"])

def test_check_user_role_returns_false():
    """Debe retornar False si el rol no coincide."""
    payload = {"role": "guest"}
    assert not check_user_role(payload, ["admin", "superadmin"])

def test_require_role_success():
    """Debe retornar el payload si el rol es válido."""
    payload = {"role": "admin", "data": 123}
    result = require_role(payload, "admin")
    assert result == payload

def test_require_role_no_token():
    """Debe lanzar UnauthorizedError si no hay payload."""
    with pytest.raises(UnauthorizedError):
        require_role({}, "admin")
    with pytest.raises(UnauthorizedError):
        require_role(None, "admin")

def test_require_role_forbidden():
    """Debe lanzar ForbiddenError si el rol es incorrecto."""
    payload = {"role": "user"}
    with pytest.raises(ForbiddenError):
        require_role(payload, "admin")

def test_extract_user_info():
    """Debe extraer correctamente los campos definidos."""
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
    """Debe verificar permisos correctamente."""
    payload = {"permissions": ["read", "write"]}
    
    assert get_user_permissions(payload) == ["read", "write"]
    
    assert has_permission(payload, "read")
    assert not has_permission(payload, "delete")

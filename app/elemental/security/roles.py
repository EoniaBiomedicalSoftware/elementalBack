from typing import List, Union
from ..exceptions import ForbiddenError, UnauthorizedError


def validate_roles(
    *allowed_roles: Union[str, int]
) -> None:
    # Ensure all roles provided are of valid types
    if not all(isinstance(role, (str, int)) for role in allowed_roles):
        raise ValueError("Roles must be string or int type")


def check_user_role(
    token_payload: dict,
    allowed_roles: Union[List[Union[str, int]], tuple]
) -> bool:
    # Check if the user's role is within the allowed list
    validate_roles(*allowed_roles)

    role = token_payload.get("role")
    return role in allowed_roles if role else False


def require_role(
    token_payload: dict,
    *allowed_roles: Union[str, int]
) -> dict:
    # Enforce role requirement and raise exception if unauthorized
    if not token_payload:
        raise UnauthorizedError("No authentication token provided")

    if not check_user_role(token_payload, allowed_roles):
        user_role = token_payload.get("role", "None")
        raise ForbiddenError(f"Operation not permitted for role: {user_role}")

    return token_payload


def extract_user_info(
    token_payload: dict
) -> dict:
    # Map raw payload to a structured dictionary
    return {
        "sub": token_payload.get("id") or token_payload.get("sub"),
        "role": token_payload.get("role"),
        "email": token_payload.get("email"),
        "iat": token_payload.get("iat"),
        "exp": token_payload.get("exp"),
    }


def get_user_permissions(
    token_payload: dict
) -> List[str]:
    # Retrieve the permissions list from the payload
    return token_payload.get("permissions", [])


def has_permission(
    token_payload: dict,
    required_permission: str
) -> bool:
    # Check if a specific permission exists in the payload
    return required_permission in get_user_permissions(token_payload)
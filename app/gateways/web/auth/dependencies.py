from typing import Dict, Any, Union
from fastapi import Depends, HTTPException, status

from .jwt_bearer import JWTBearer
from app.elemental.security.roles import require_role, extract_user_info, has_permission, get_user_permissions
from app.elemental.exceptions import ForbiddenError, UnauthorizedError, AuthenticationError

jwt_bearer = JWTBearer()


async def get_current_user_payload(
    payload: dict = Depends(jwt_bearer)
) -> Dict[str, Any]:
    return payload

async def get_current_user_info(
    payload: Dict[str, Any] = Depends(get_current_user_payload)
) -> Dict[str, Any]:
    return extract_user_info(payload)


async def get_current_user_id(
    user_info: Dict[str, Any] = Depends(get_current_user_info)
) -> str:
    user_id = user_info.get("id") or user_info.get("sub")
    if user_id is None:
        raise AuthenticationError(
            message="Token missing user identification"
        )
    return user_id


async def get_current_user_role(
    user_info: Dict[str, Any] = Depends(get_current_user_info)
) -> Union[str, int]:
    role = user_info.get("role")
    if role is None:
        raise AuthenticationError(
            message="Token missing user role"
        )
    return role

def require_roles(*allowed_roles: Union[str, int]):
    async def check_roles(
        payload: Dict[str, Any] = Depends(get_current_user_payload)
    ) -> Dict[str, Any]:
        return require_role(payload, *allowed_roles)

    return check_roles
#
#

# async def get_current_user_permissions(
#     payload: Dict[str, Any] = Depends(get_current_user_payload)
# ) -> List[str]:
#     return get_user_permissions(payload)
#
#

# def require_permission(required_permission: str):
#     async def check_permission(
#             payload: Dict[str, Any] = Depends(get_current_user_payload)
#     ) -> Dict[str, Any]:
#         if not has_permission(payload, required_permission):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Permission required: {required_permission}"
#             )
#         return payload
#
#     return check_permission
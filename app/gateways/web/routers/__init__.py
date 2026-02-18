from fastapi import APIRouter
from .src_routers import get_all_routers
from .docs import custom_openapi


elemental_router = APIRouter()

@elemental_router.get("/ping")
async def ping() -> bool:
    return True


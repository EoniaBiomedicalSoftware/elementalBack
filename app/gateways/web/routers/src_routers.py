import pkgutil
import importlib
from pathlib import Path
from fastapi import APIRouter

from app.elemental.logging import get_logger

_logger = None


def get_router_logger():
    global _logger
    if _logger is None:
        _logger = get_logger("api_routers")
    return _logger


def get_all_routers() -> list[APIRouter]:
    logger = get_router_logger()
    
    all_applications_routers: list[APIRouter] = []
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_path = project_root / "src"

    if not src_path.exists():
        logger.error(f"Source path not found at {src_path}")
        return []

    for _, module_name, is_pkg in pkgutil.iter_modules([str(src_path)]):
        if module_name == "shared":
            continue
        
        if not is_pkg:
            continue

        try:
            mod = importlib.import_module(f"app.src.{module_name}.gateways.api.router")
            
            if hasattr(mod, "api_router"):
                all_applications_routers.append(mod.api_router)
                logger.info(
                    f"Router added: {module_name}"
                )
            
            else:
                logger.warning(
                    f"No 'api_router' found on {module_name}"
                )
        
        except ModuleNotFoundError as e:
            logger.error(
                f"No router.py on {module_name}: {e}"
            )
    
    return all_applications_routers
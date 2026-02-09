from fastapi import FastAPI
from contextlib import asynccontextmanager
from importlib import import_module

from app.elemental.logging import get_logger
from app.elemental.settings import get_settings
from app.infrastructure import infrastructure_modules


@asynccontextmanager
async def app_lifespan(
    _: FastAPI,
):
    settings = get_settings()

    logger = get_logger("fastapi_lifespan")

    loaded_services: list[str] = []
    loaded_modules: dict[str, object] = {}

    # --- INIT PHASE ---
    try:
        for key, module_path in infrastructure_modules.items():
            if not hasattr(settings, key):
                logger.warning(f"Skipping {key}: no '{key}' configuration found.")
                continue

            logger.info(f"Initializing {key} service...")

            module = import_module(module_path)
            loaded_modules[key] = module

            init_func = (
                getattr(module, f"init_{key}_service", None)
                or getattr(module, f"init_{key}", None)
            )

            if init_func is None:
                logger.error(f"Initialization function not found for service: {key}")
                raise RuntimeError(f"Missing init function for {key}")

            await init_func(getattr(settings, key))
            loaded_services.append(key)

        yield

    finally:
        # =========================
        # SHUTDOWN PHASE
        # =========================
        logger.info("Shutting down services...")

        for key in reversed(loaded_services):
            module = loaded_modules.get(key)
            if module is None:
                logger.warning(f"Module for {key} not found during shutdown.")
                continue

            close_func = (
                getattr(module, f"close_{key}_service", None)
                or getattr(module, f"close_{key}", None)
            )

            if not close_func:
                logger.warning(f"No shutdown function found for {key}")
                continue

            try:
                await close_func()
                logger.info(f"{key} service shutdown complete.")
            except Exception as e:
                logger.error(f"Error shutting down {key}: {e}")

        logger.info("All services shut down.")

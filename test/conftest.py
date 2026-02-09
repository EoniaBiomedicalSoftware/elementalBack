import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Permite usar fixtures asíncronas en toda la sesión."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
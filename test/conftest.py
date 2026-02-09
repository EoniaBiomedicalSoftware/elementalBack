import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Allows the use of asynchronous fixtures throughout the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
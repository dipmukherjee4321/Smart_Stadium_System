"""
Conftest for Smart Stadium OS backend tests.
Provides shared fixtures for async HTTP client, JWT tokens, and app lifecycle.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from services.security_service import SecurityService
from datetime import timedelta


@pytest.fixture(scope="session")
def admin_token():
    """Session-scoped admin JWT token."""
    return SecurityService.create_access_token(
        data={"sub": "admin", "role": "ELITE_ADMIN"},
        expires_delta=timedelta(minutes=60),
    )


@pytest.fixture(scope="session")
def auth_headers(admin_token):
    """Session-scoped auth headers."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def async_client():
    """Provide a test ASGI client that imports the app per test."""
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

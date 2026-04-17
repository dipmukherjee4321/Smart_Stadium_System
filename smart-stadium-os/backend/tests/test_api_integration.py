"""
Comprehensive Health & API Integration Tests.
Covers the full HTTP lifecycle for all API endpoints with JWT guards.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from services.security_service import SecurityService
from datetime import timedelta


@pytest.fixture
def admin_token():
    """Generate a valid admin JWT for use in protected endpoint tests."""
    return SecurityService.create_access_token(
        data={"sub": "admin", "role": "ELITE_ADMIN"},
        expires_delta=timedelta(minutes=30)
    )


@pytest.fixture
def auth_headers(admin_token):
    """Return authorization headers with a valid Bearer token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Tests for public health endpoints."""

    async def test_health_check_returns_200(self):
        """The /health endpoint must return 200 OK."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/api/ops/health")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert data["status"] == "healthy"


@pytest.mark.asyncio
class TestRoutingEndpoint:
    """Tests for the authenticated routing endpoint."""

    async def test_unauthenticated_route_returns_401(self):
        """The /route endpoint must reject unauthenticated requests."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/api/nav/route?start=North_Gate&end=South_Gate")
        assert res.status_code == 401

    async def test_authenticated_route_returns_valid_payload(self, auth_headers):
        """Authenticated /route must return a multipath payload."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(
                "/api/nav/route?start=North_Gate&end=South_Gate",
                headers=auth_headers
            )
        assert res.status_code == 200
        data = res.json()
        assert "primary" in data
        assert "alternative" in data
        assert "baseline" in data

    async def test_route_with_same_start_end_returns_400(self, auth_headers):
        """Routing to the same zone should return HTTP 400."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(
                "/api/nav/route?start=North_Gate&end=North_Gate",
                headers=auth_headers
            )
        assert res.status_code == 400

    async def test_route_with_invalid_zone_returns_400(self, auth_headers):
        """Invalid zone names must return HTTP 400."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(
                "/api/nav/route?start=DOES_NOT_EXIST&end=South_Gate",
                headers=auth_headers
            )
        assert res.status_code == 400


@pytest.mark.asyncio
class TestAlertEndpoint:
    """Tests for the alert broadcast endpoint."""

    async def test_valid_alert_returns_success(self, auth_headers):
        """A valid alert payload must return a success message."""
        payload = {"zone": "Food_Court", "severity": "HIGH", "message": "Test alert"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/safety/alert", json=payload, headers=auth_headers)
        # Alert endpoint is now protected, expect 200 with valid token
        assert res.status_code == 200

    async def test_invalid_alert_zone_too_long_returns_422(self, auth_headers):
        """Zone names exceeding validation limits should return 422."""
        payload = {"zone": "A" * 200, "severity": "HIGH", "message": "Test"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/safety/alert", json=payload, headers=auth_headers)
        assert res.status_code == 422

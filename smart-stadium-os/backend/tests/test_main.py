"""
Integrated API Tests — Smart Stadium OS
=========================================
Tests the end-to-end flow of the FastAPI application, including
security middleware, JWT authentication, and routing logic.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_security_headers():
    """Verify that elite security headers are present on all responses."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/ops/health")
        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "Content-Security-Policy" in response.headers
        assert "Referrer-Policy" in response.headers

@pytest.mark.asyncio
async def test_unauthorized_routing_access():
    """Verify that the /route endpoint is protected by JWT."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/nav/route?start=North_Gate&end=South_Gate")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_full_auth_flow():
    """Tests login -> token usage -> protected route access."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Login
        login_res = await ac.post("/api/security/login", data={
            "username": "admin",
            "password": "stadium_elite"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Access protected routing
        route_res = await ac.get(
            "/api/nav/route?start=North_Gate&end=South_Gate",
            headers=headers
        )
        assert route_res.status_code == 200
        assert "primary" in route_res.json()

        # 3. Access protected alerts
        alert_res = await ac.post(
            "/api/safety/alert",
            headers=headers,
            json={
                "zone": "Food_Court",
                "severity": "HIGH",
                "message": "Test Alert"
            }
        )
        assert alert_res.status_code == 200

@pytest.mark.asyncio
async def test_rate_limiting():
    """Ensures that the rate limiter middleware is active."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Slam the health endpoint
        for _ in range(35):
            res = await ac.get("/api/ops/health")
        
        # The 31st+ request should be rate limited (limit is 30)
        assert res.status_code == 429
        assert "retry_after_seconds" in res.json()

"""
Health Monitoring API Module
=============================
Provides a /health endpoint for readiness/liveness probes.
"""

from fastapi import APIRouter
from services.websocket_manager import manager
from models.schemas import HealthResponse
import time

router = APIRouter()
START_TIME = time.time()

@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Returns system health status and diagnostics.
    Used by Cloud Run for resource monitoring.
    """
    return HealthResponse(
        status="healthy",
        active_connections=manager.active_count,
        uptime_seconds=time.time() - START_TIME,
        version="2.3.0"
    )

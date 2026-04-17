"""
Alerts API Module
==================
Handles the POST /alert endpoint for manual emergency triggers.
Ensures strict validation via Pydantic model.
"""

from fastapi import APIRouter, HTTPException, Depends
from models.schemas import AlertRequest
from services.ai_engine import ai_engine
from services.websocket_manager import manager
from services.cloud_logger import ops_logger as logger
from services.security_service import get_current_user

router = APIRouter()

@router.post("/alert")
async def trigger_manual_alert(
    alert: AlertRequest, 
    current_user: dict = Depends(get_current_user)
):
    """
    Triggers a manual override alert for a specific zone.
    Broadcasts the emergency state to all connected clients.
    """
    logger.warning(f"Manual alert triggered for {alert.zone}: {alert.message}")
    
    # 1. Update AI Engine internal state
    ai_engine.override_zone(alert.zone, alert.severity)
    
    # 2. Broadcast emergency event
    await manager.broadcast_event(
        event_type="EMERGENCY_EVACUTION",
        payload={
            "zone": alert.zone,
            "severity": alert.severity,
            "message": alert.message
        }
    )
    
    return {"status": "Alert broadcasted successfully", "zone": alert.zone}

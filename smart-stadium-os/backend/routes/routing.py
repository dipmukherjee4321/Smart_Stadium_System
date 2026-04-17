"""
Routing API Module
===================
Handles the GET /route endpoint for AI-enhanced navigation.
Instrumented with Cloud Trace and JWT authentication for elite security.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from services.graph_routing import find_multi_route
from services.ai_engine import ai_engine
from services.cloud_logger import ops_logger
from services.trace_service import tracer
from services.security_service import get_current_user
from models.schemas import MultiRouteResponse

router = APIRouter()

@router.get("/route", response_model=MultiRouteResponse)
async def get_multi_path(
    start: str = Query(..., min_length=1, max_length=64, description="Starting zone name"),
    end: str = Query(..., min_length=1, max_length=64, description="Destination zone name"),
    user: dict = Depends(get_current_user),
):
    """
    Elite Neural Routing: Finds Primary, Alternative, and Baseline paths.
    Protected by JWT. Instrumented with GCP Cloud Trace for end-to-end observability.
    """
    ops_logger.info(f"Multi-Route requested by '{user.get('sub')}': {start} -> {end}")

    with tracer.start_as_current_span(
        "compute_stadium_route",
        attributes={"stadium.start_zone": start, "stadium.end_zone": end},
    ) as span:
        try:
            result = find_multi_route(ai_engine, start, end)
            span.set_attribute("stadium.primary_path_length", len(result.primary.path))
            return result
        except ValueError as e:
            span.record_exception(e)
            ops_logger.error(f"Routing validation error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            span.record_exception(e)
            ops_logger.error(f"Routing computation error: {e}")
            raise HTTPException(status_code=500, detail="Neural computation error.")

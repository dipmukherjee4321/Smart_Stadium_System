"""
Pydantic Schemas — Request & Response Models
=============================================
All API input/output contracts are enforced here via Pydantic v2.
This ensures type safety, automatic validation, and clear OpenAPI docs.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

VALID_ZONES = {
    "North_Gate", "Concourse_A", "Restroom_1",
    "Food_Court", "Section_101", "Media_Zone", "South_Gate",
}

VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


class AlertRequest(BaseModel):
    """
    Payload schema for POST /alert endpoint.

    Attributes:
        zone: The target zone identifier (must be a valid stadium node).
        severity: Alert severity level.
        message: Human-readable description of the emergency (max 500 chars).
    """

    zone: str = Field(..., min_length=1, max_length=64, description="Stadium zone identifier")
    severity: str = Field("HIGH", description="Alert severity tier")
    message: str = Field(..., min_length=1, max_length=500, description="Alert message")

    @field_validator("zone")
    @classmethod
    def zone_must_be_valid(cls, v: str) -> str:
        """Reject unknown zone identifiers to prevent injection attacks."""
        if v not in VALID_ZONES:
            raise ValueError(
                f"Unknown zone '{v}'. Valid zones: {sorted(VALID_ZONES)}"
            )
        return v

    @field_validator("severity")
    @classmethod
    def severity_must_be_valid(cls, v: str) -> str:
        """Enforce severity to a known tier."""
        v = v.upper()
        if v not in VALID_SEVERITIES:
            raise ValueError(
                f"Invalid severity '{v}'. Must be one of: {sorted(VALID_SEVERITIES)}"
            )
        return v

    @field_validator("message")
    @classmethod
    def message_must_not_be_empty(cls, v: str) -> str:
        """Sanitize and validate emergency message."""
        v = v.strip()
        if not v:
            raise ValueError("Alert message cannot be empty.")
        if len(v) > 500:
            raise ValueError("Alert message must not exceed 500 characters.")
        return v


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------


class RouteEdge(BaseModel):
    """Schema for a single edge in a route."""
    start: str
    end: str
    weight: float


class RouteResponse(BaseModel):
    """
    Response schema for a single route.
    """
    path: List[str]
    estimated_cost: float
    time_saved_estimate: int
    ai_narrative: str


class MultiRouteResponse(BaseModel):
    """
    Elite Response schema returning multiple routing options for comparison.
    """
    primary: RouteResponse
    alternative: RouteResponse
    baseline: RouteResponse


class RouteErrorResponse(BaseModel):
# ... rest of file ...
    """Response when routing fails (e.g., invalid nodes)."""

    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Response schema for GET /health endpoint."""

    status: str
    active_connections: int
    uptime_seconds: float
    version: str

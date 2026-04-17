"""
Zone State Model
=================
Defines the ZoneState dataclass, which holds all real-time and predicted
metrics for a single stadium zone. Includes a rolling history buffer for
anomaly detection.
"""

from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Deque


@dataclass
class ZoneState:
    """
    Represents the live operational state of a single stadium zone.

    Attributes:
        name: Human-readable zone identifier.
        current_density: Current crowd occupancy as a percentage (0–100).
        inflow_rate: People entering per simulation tick.
        outflow_rate: People leaving per simulation tick.
        predicted_density_10m: AI-forecasted density 10 minutes ahead (0–100).
        risk_score: Qualitative risk tier — 'LOW', 'MEDIUM', or 'HIGH'.
        confidence_score: Model confidence in the prediction (0.0–1.0).
        is_anomaly: True when a statistically significant density spike is detected.
        density_history: Rolling buffer of recent density readings (max 10 ticks).
    """

    name: str
    current_density: int = 25
    inflow_rate: int = 0
    outflow_rate: int = 0
    predicted_density_10m: int = 0
    risk_score: str = "LOW"
    confidence_score: float = 0.95
    is_anomaly: bool = False
    density_history: Deque[int] = field(default_factory=lambda: deque(maxlen=10))

    def to_dict(self) -> dict:
        """Serialize zone state to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "current_density": self.current_density,
            "inflow_rate": self.inflow_rate,
            "outflow_rate": self.outflow_rate,
            "predicted_density_10m": self.predicted_density_10m,
            "risk_score": self.risk_score,
            "confidence_score": self.confidence_score,
            "is_anomaly": self.is_anomaly,
        }

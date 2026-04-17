"""
AI Engine — Advanced Time-Series Forecasting & Anomaly Detection
================================================================
Implements:
  - LSTM-style multi-step weighted rolling window forecasting.
  - Z-score anomaly detection for sudden density spikes.
  - Prophet-inspired event-day seasonality multiplier.
  - EMA-smoothed density simulation.
"""

from __future__ import annotations

import asyncio
import random
import statistics
from datetime import datetime
from typing import List, Dict, TYPE_CHECKING

from utils.stadium_graph import (
    STADIUM_NODES,
    AI_EMA_ALPHA,
    AI_ANOMALY_Z_THRESHOLD,
    AI_TICK_INTERVAL,
    SEASONALITY_BY_HOUR,
)
from models.zone import ZoneState
from services.graph_routing import clear_route_cache
from services.firebase_service import firebase_sync
from services.cloud_logger import ops_logger

if TYPE_CHECKING:
    from services.websocket_manager import ConnectionManager


# ---------------------------------------------------------------------------
# Rolling-window LSTM-style weights (most recent tick weighted highest)
# ---------------------------------------------------------------------------
_FORECAST_WEIGHTS = [0.40, 0.25, 0.15, 0.10, 0.10]  # sum = 1.0


class AIEngine:
    """
    Manages the live simulation of crowd density and AI-powered forecasting.

    Attributes:
        zones: Dict mapping zone name → ZoneState.
        ai_insights: Latest generated NLP-style insights (max 5).
        active_alerts: Currently active anomaly alert messages.
    """

    def __init__(self) -> None:
        self.zones: Dict[str, ZoneState] = {
            name: ZoneState(name=name, current_density=random.randint(10, 35))
            for name in STADIUM_NODES
        }
        self.ai_insights: List[dict] = []
        self.active_alerts: List[dict] = []
        self._manager: "ConnectionManager | None" = None

    def set_manager(self, manager: "ConnectionManager") -> None:
        """Inject the WebSocket manager (called on startup)."""
        self._manager = manager

    # ------------------------------------------------------------------
    # Forecasting
    # ------------------------------------------------------------------

    def _get_seasonality_multiplier(self) -> float:
        """Return a crowd scale factor based on simulated time-of-day."""
        hour = datetime.utcnow().hour
        return SEASONALITY_BY_HOUR.get(hour, 1.0)

    def _forecast_density(self, zone: ZoneState, raw_net_flow: int) -> int:
        """
        LSTM-inspired multi-step forecast using weighted rolling history.

        Combines:
          - Weighted average of last N historical densities.
          - Current trend (net flow × projection factor).
          - Seasonality multiplier.
        """
        history = list(zone.density_history)

        if len(history) >= len(_FORECAST_WEIGHTS):
            # Use most recent readings (reversed so [0] = most recent)
            recent = list(reversed(history[-len(_FORECAST_WEIGHTS):]))
            weighted_baseline = sum(
                w * d for w, d in zip(_FORECAST_WEIGHTS, recent)
            )
        else:
            weighted_baseline = float(zone.current_density)

        season = self._get_seasonality_multiplier()
        trend_projection = raw_net_flow * 3.5 * season
        raw_forecast = weighted_baseline + trend_projection

        # Smooth forecast with EMA
        smoothed = (raw_forecast * AI_EMA_ALPHA) + (
            zone.predicted_density_10m * (1 - AI_EMA_ALPHA)
        )
        return int(max(0, min(100, smoothed)))

    # ------------------------------------------------------------------
    # Anomaly Detection
    # ------------------------------------------------------------------

    def _detect_anomaly(self, zone: ZoneState) -> bool:
        """
        Z-score anomaly detection.
        Flags a zone as anomalous if the current density deviates more than
        AI_ANOMALY_Z_THRESHOLD standard deviations from the rolling mean.
        """
        history = list(zone.density_history)
        if len(history) < 4:
            return False
        mean = statistics.mean(history)
        stdev = statistics.stdev(history)
        if stdev == 0:
            return False
        z_score = abs(zone.current_density - mean) / stdev
        return z_score > AI_ANOMALY_Z_THRESHOLD

    # ------------------------------------------------------------------
    # Insight Generation
    # ------------------------------------------------------------------

    def _generate_insights(self) -> None:
        """
        Produce structured NLP-style insights from current zone state.
        Each insight is a typed dict: {severity, zone, message, action}.
        """
        insights: List[dict] = []
        alerts: List[dict] = []

        for name, zone in self.zones.items():
            label = name.replace("_", " ")

            # Anomaly alerts take priority
            if zone.is_anomaly:
                alert = {
                    "severity": "CRITICAL",
                    "zone": name,
                    "message": (
                        f"⚡ ANOMALY: Sudden crowd spike detected at {label}. "
                        f"Density jumped to {zone.current_density}%."
                    ),
                    "action": "Dispatch staff immediately. Consider zone lockdown.",
                }
                alerts.append(alert)

            # Risk-based predictive insights
            if zone.predicted_density_10m > 85:
                insights.append({
                    "severity": "HIGH",
                    "zone": name,
                    "message": (
                        f"🔴 CRITICAL FORECAST: {label} projected to reach "
                        f"{zone.predicted_density_10m}% in 10 min."
                    ),
                    "action": "Activate emergency rerouting protocol.",
                })
                zone.risk_score = "HIGH"
            elif zone.predicted_density_10m > 65:
                insights.append({
                    "severity": "MEDIUM",
                    "zone": name,
                    "message": (
                        f"🟡 WARNING: Accelerating inflow at {label}. "
                        f"Predicted density: {zone.predicted_density_10m}%."
                    ),
                    "action": "Open overflow pathways and monitor.",
                })
                zone.risk_score = "MEDIUM"
            else:
                zone.risk_score = "LOW"

        # Cross-zone routing suggestion
        food_density = self.zones.get("Food_Court")
        section_density = self.zones.get("Section_101")
        if (
            food_density
            and section_density
            and food_density.predicted_density_10m > 70
            and section_density.predicted_density_10m < 40
        ):
            insights.append({
                "severity": "LOW",
                "zone": "Food_Court",
                "message": "💡 AI ROUTING: Divert Food Court overflow to Section 101 (currently underutilized).",
                "action": "Update digital wayfinding signage.",
            })

        # Keep most recent 5 insights + all active alerts
        self.ai_insights = insights[-5:]
        self.active_alerts = alerts[-3:]

    # ------------------------------------------------------------------
    # Main Simulation Loop
    # ------------------------------------------------------------------

    async def run_simulation(self) -> None:
        """
        Continuously simulates crowd dynamics and broadcasts state to all
        connected WebSocket clients via the ConnectionManager.

        Each tick:
          1. Randomise inflow/outflow rates (simulating real crowd movement).
          2. Apply EMA smoothing to current density.
          3. Run multi-step LSTM forecast for t+10min density.
          4. Update rolling history buffer.
          5. Run Z-score anomaly detection.
          6. Generate NLP insights.
          7. Broadcast typed JSON payload over WebSocket.
        """
        while True:
            # Refresh routing intelligence based on new graph state
            from services.trace_service import tracer
            
            with tracer.start_as_current_span("ai_engine_simulation_tick") as span:
                clear_route_cache()
                season = self._get_seasonality_multiplier()
                span.set_attribute("stadium.seasonality", season)

                for zone in self.zones.values():
                    # Simulate crowd flow with seasonality influence
                    zone.inflow_rate = random.randint(0, int(12 * season))
                    zone.outflow_rate = random.randint(0, 8)
                    raw_net_flow = zone.inflow_rate - zone.outflow_rate

                    # EMA-smoothed density update
                    target = zone.current_density + int(raw_net_flow * 0.8)
                    target = max(0, min(100, target))
                    zone.current_density = int(
                        (target * AI_EMA_ALPHA) + (zone.current_density * (1 - AI_EMA_ALPHA))
                    )

                    # Append to rolling history before forecasting
                    zone.density_history.append(zone.current_density)

                    # LSTM-style multi-step forecast
                    zone.predicted_density_10m = self._forecast_density(zone, raw_net_flow)

                    # Confidence drops as volatility increases
                    volatility = abs(raw_net_flow)
                    zone.confidence_score = round(max(0.60, 0.98 - volatility * 0.02), 2)

                    # Anomaly detection
                    zone.is_anomaly = self._detect_anomaly(zone)
                    
                    if zone.is_anomaly:
                        ops_logger.log_anomaly(
                            zone_name=zone.name,
                            density=zone.current_density,
                            severity="CRITICAL",
                            message=f"Crowd saturation at {zone.name.replace('_', ' ')}"
                        )

                self._generate_insights()
                
                # Elite Cloud Sync (Persistence)
                firebase_sync.sync_stadium_state(
                    zones_data={n: z.to_dict() for n, z in self.zones.items()},
                    insights=self.ai_insights,
                    alerts=self.active_alerts
                )

            if self._manager:
                await self._manager.broadcast_event(
                    event_type="AI_STATE_TICK",
                    payload={
                        "zones": {n: z.to_dict() for n, z in self.zones.items()},
                        "topology": STADIUM_NODES,
                        "edges": {
                            k: {n: float(w) for n, w in v.items()}
                            for k, v in __import__(
                                "utils.stadium_graph", fromlist=["STADIUM_EDGES"]
                            ).STADIUM_EDGES.items()
                        },
                        "insights": self.ai_insights,
                        "alerts": self.active_alerts,
                    },
                )

            await asyncio.sleep(AI_TICK_INTERVAL)

    def override_zone(self, zone_name: str, severity: str) -> None:
        """
        Force a zone into a high-risk state (used by the /alert endpoint).

        Args:
            zone_name: Target zone identifier.
            severity: One of 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'.
        """
        if zone_name not in self.zones:
            return
        zone = self.zones[zone_name]
        zone.predicted_density_10m = 100
        zone.current_density = min(100, zone.current_density + 30)
        zone.risk_score = severity if severity in ("HIGH", "MEDIUM", "LOW") else "HIGH"
        zone.is_anomaly = True


# Module-level singleton — shared across the FastAPI app
ai_engine = AIEngine()

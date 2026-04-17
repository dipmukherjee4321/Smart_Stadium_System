"""
Stadium Graph Constants
========================
Defines the physical topology of the stadium as a weighted, undirected graph.
Node coordinates (x, y) are canvas percentages (0–100) for the 2D Digital Twin.
Edge weights represent base traversal distance (in abstract units).
"""

from typing import Dict, Tuple

# Node layout mapped to canvas coordinates (x%, y%)
STADIUM_NODES: Dict[str, Dict[str, float]] = {
    "North_Gate":  {"x": 50, "y": 8},
    "Concourse_A": {"x": 28, "y": 30},
    "Restroom_1":  {"x": 72, "y": 30},
    "Food_Court":  {"x": 18, "y": 62},
    "Section_101": {"x": 82, "y": 62},
    "South_Gate":  {"x": 50, "y": 88},
    "Media_Zone":  {"x": 50, "y": 48},
}

# Adjacency list with base edge weights (physical distance units)
STADIUM_EDGES: Dict[str, Dict[str, float]] = {
    "North_Gate":  {"Concourse_A": 2.0, "Restroom_1": 5.0},
    "Concourse_A": {"North_Gate": 2.0, "Media_Zone": 2.5, "Food_Court": 4.0},
    "Restroom_1":  {"North_Gate": 5.0, "Media_Zone": 2.5, "Section_101": 2.0},
    "Food_Court":  {"Concourse_A": 4.0, "South_Gate": 6.0},
    "Media_Zone":  {"Concourse_A": 2.5, "Restroom_1": 2.5, "Section_101": 3.0, "South_Gate": 4.5},
    "Section_101": {"Restroom_1": 2.0, "Media_Zone": 3.0, "South_Gate": 7.0},
    "South_Gate":  {"Food_Court": 6.0, "Media_Zone": 4.5, "Section_101": 7.0},
}

# Penalty applied to A* cost per risk tier
RISK_PENALTIES: Dict[str, float] = {
    "HIGH":   1000.0,
    "MEDIUM":  30.0,
    "LOW":      0.0,
}

# Density weight coefficients for A* cost function
# cost = distance + (CURRENT_W × current_density) + (PREDICTED_W × predicted_density_10m)
DENSITY_WEIGHT_CURRENT:   float = 0.6
DENSITY_WEIGHT_PREDICTED: float = 0.4

# AI Engine configuration
AI_EMA_ALPHA:          float = 0.3   # Smoothing factor (lower = smoother)
AI_ANOMALY_Z_THRESHOLD: float = 2.5  # Z-score threshold for anomaly detection
AI_HISTORY_WINDOW:     int   = 10    # Number of ticks to retain for statistics
AI_TICK_INTERVAL:      float = 2.5   # Seconds between AI simulation ticks

# Event-day seasonality multipliers (hour → crowd scale factor)
# Simulates realistic stadium crowd patterns
SEASONALITY_BY_HOUR: Dict[int, float] = {
    0: 0.3, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.3,
    6: 0.4, 7: 0.5, 8: 0.6, 9: 0.7, 10: 0.8, 11: 0.9,
    12: 1.0, 13: 1.1, 14: 1.2, 15: 1.3, 16: 1.4, 17: 1.5,
    18: 1.6, 19: 1.7, 20: 1.5, 21: 1.3, 22: 1.0, 23: 0.7,
}

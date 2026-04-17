"""
Multi-Path A* Routing Service
=============================
Implements an advanced congestion-aware A* algorithm that generates:
1. Primary AI Route: Multi-weighted optimal path based on future density.
2. Alternative Safety Path: Diverts traffic if primary zones are critical.
3. Baseline Shortest Path: Minimal physical distance (Naive).
"""

from __future__ import annotations
import heapq
import math
from typing import List, Dict, Tuple, Optional, TYPE_CHECKING
from models.schemas import RouteResponse, MultiRouteResponse, RouteEdge
from utils.stadium_graph import (
    STADIUM_EDGES, 
    STADIUM_NODES,
    DENSITY_WEIGHT_CURRENT,
    DENSITY_WEIGHT_PREDICTED,
    RISK_PENALTIES
)

if TYPE_CHECKING:
    from services.ai_engine import AIEngine

# Cache for common routing results to reduce load
_route_cache: Dict[Tuple[str, str], MultiRouteResponse] = {}

def clear_route_cache():
    global _route_cache
    _route_cache.clear()

def _heuristic(u: str, v: str) -> float:
    """Euclidean distance heuristic for A* convergence."""
    x1, y1 = STADIUM_NODES[u]["x"], STADIUM_NODES[u]["y"]
    x2, y2 = STADIUM_NODES[v]["x"], STADIUM_NODES[v]["y"]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def _get_dynamic_cost(engine: "AIEngine", u: str, v: str, use_ai: bool = True) -> float:
    """ Calculates weights based on physical distance + AI congestion data. """
    base_dist = STADIUM_EDGES[u].get(v, 999.0)
    if not use_ai:
        return base_dist

    zone = engine.zones.get(v)
    if not zone:
        return base_dist
        
    risk_p = RISK_PENALTIES.get(zone.risk_score, 0.0)
    
    # Neural Cost Function
    # Penalty increases exponentially as density approaches 100%
    congestion_cost = (
        (zone.current_density * DENSITY_WEIGHT_CURRENT) + 
        (zone.predicted_density_10m * DENSITY_WEIGHT_PREDICTED)
    )
    
    return base_dist + congestion_cost + risk_p

def _run_astar(engine: "AIEngine", start: str, end: str, use_ai: bool = True, exclude_nodes: List[str] = None) -> List[str]:
    """Core A* implementation."""
    exclude_nodes = exclude_nodes or []
    open_set = [(0, start)]
    came_from = {}
    g_score = {node: float('inf') for node in STADIUM_NODES}
    g_score[start] = 0
    f_score = {node: float('inf') for node in STADIUM_NODES}
    f_score[start] = _heuristic(start, end)

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for neighbor in STADIUM_EDGES[current]:
            if neighbor in exclude_nodes and neighbor != start and neighbor != end:
                continue
                
            tentative_g_score = g_score[current] + _get_dynamic_cost(engine, current, neighbor, use_ai)
            
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + _heuristic(neighbor, end)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []

def find_multi_route(engine: "AIEngine", start: str, end: str) -> MultiRouteResponse:
    """
    Elite multi-path routing with side-by-side comparison.
    """
    if start not in STADIUM_NODES or end not in STADIUM_NODES:
        raise ValueError(f"Invalid node identifiers: {start} or {end} not in STADIUM_NODES.")

    if start == end:
        raise ValueError("Start and end nodes must be distinct.")

    cache_key = (start, end)
    if cache_key in _route_cache:
        return _route_cache[cache_key]

    # 1. Primary AI Neural Route
    primary_path = _run_astar(engine, start, end, use_ai=True)
    
    # 2. Alternative Safety Path (Exclude the bottleneck of the primary path)
    alt_path = []
    if len(primary_path) > 2:
        # Exclude node with highest predicted density in primary path
        mid_nodes = primary_path[1:-1]
        bottleneck = max(mid_nodes, key=lambda n: engine.zones[n].predicted_density_10m)
        alt_path = _run_astar(engine, start, end, use_ai=True, exclude_nodes=[bottleneck])

    # 3. Baseline Shortest Path (Ignoring Density)
    baseline_path = _run_astar(engine, start, end, use_ai=False)

    def get_stats(path):
        if not path: return 0.0, 0
        cost = 0.0
        for i in range(len(path)-1):
            cost += _get_dynamic_cost(engine, path[i], path[i+1], use_ai=True)
        return round(cost, 1), len(path)

    p_cost, p_len = get_stats(primary_path)
    a_cost, a_len = get_stats(alt_path)
    b_cost, b_len = get_stats(baseline_path)

    response = MultiRouteResponse(
        primary=RouteResponse(
            path=primary_path, 
            estimated_cost=p_cost, 
            time_saved_estimate=int(max(1, (b_cost - p_cost) / 2)),
            ai_narrative="AI Path: Optimal density distribution achieved."
        ),
        alternative=RouteResponse(
            path=alt_path if alt_path else primary_path,
            estimated_cost=a_cost,
            time_saved_estimate=int(max(0, (b_cost - a_cost) / 2)),
            ai_narrative="Safety Path: Diverts traffic around bottlenecks."
        ),
        baseline=RouteResponse(
            path=baseline_path,
            estimated_cost=b_cost,
            time_saved_estimate=0,
            ai_narrative="Standard Path: Traditional routing ignoring congestion."
        )
    )

    _route_cache[cache_key] = response
    return response

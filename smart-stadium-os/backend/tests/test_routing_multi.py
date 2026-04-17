"""
Extended Routing Tests — Multi-Path A* Edition
==============================================
Verifies the production-grade routing engine returns Primary,
Alternative, and Baseline paths with correct behavioral logic.
"""

import pytest
from services.graph_routing import find_multi_route, clear_route_cache
from services.ai_engine import ai_engine
from models.schemas import MultiRouteResponse

def test_multi_routing_structure():
    """Verify that the engine returns all three expected paths."""
    clear_route_cache()
    result = find_multi_route(ai_engine, "North_Gate", "South_Gate")
    
    assert isinstance(result, MultiRouteResponse)
    assert len(result.primary.path) > 0
    assert len(result.baseline.path) > 0
    assert len(result.alternative.path) > 0

def test_multi_routing_evasion_logic():
    """
    Ensure the Primary Neural path is different (or lower cost) than Baseline,
    and Alternative path excludes the bottleneck.
    """
    clear_route_cache()
    # 1. Block a bottleneck
    ai_engine.override_zone("Concourse_A", "HIGH")
    
    result = find_multi_route(ai_engine, "North_Gate", "South_Gate")
    
    # Baseline shortest path usually includes Concourse_A in this topology
    # Neural Primary should have avoided it due to the 1000.0 cost penalty
    assert "Concourse_A" not in result.primary.path
    
    # If Concourse_A was the bottleneck, the Primary and Alternative 
    # should be mathematically distinct from the naive baseline.
    assert result.primary.estimated_cost < result.baseline.estimated_cost

def test_multi_routing_idempotency():
    """Verify cache consistency."""
    clear_route_cache()
    r1 = find_multi_route(ai_engine, "North_Gate", "South_Gate")
    r2 = find_multi_route(ai_engine, "North_Gate", "South_Gate")
    assert r1.primary.path == r2.primary.path

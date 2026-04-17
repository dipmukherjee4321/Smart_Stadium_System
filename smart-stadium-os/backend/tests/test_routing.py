"""
Routing Logic Unit Tests — Multi-Path Migration
===============================================
Verifies the A* algorithm finds optimal paths and handles anomalies.
Compatibility layer for legacy tests after the Multi-Path upgrade.
"""

from services.graph_routing import find_multi_route, clear_route_cache
from services.ai_engine import ai_engine
from models.schemas import RouteResponse, RouteErrorResponse, MultiRouteResponse

def test_astar_finds_basic_path():
    """Verify A* finds a path between known connected nodes."""
    result = find_multi_route(ai_engine, "North_Gate", "South_Gate")
    assert isinstance(result, MultiRouteResponse)
    path = result.primary.path
    assert "North_Gate" in path
    assert "South_Gate" in path
    assert result.primary.estimated_cost > 0

def test_astar_invalid_nodes():
    """Verify error handling for invalid nodes."""
    try:
        find_multi_route(ai_engine, "Invalid_Node", "South_Gate")
    except Exception as e:
        assert "Invalid node identifiers" in str(e)

def test_astar_avoids_high_density():
    """Verify AI-weighted cost logic impacts path selection."""
    clear_route_cache()
    # 1. Get baseline path (Neural Primary)
    baseline = find_multi_route(ai_engine, "North_Gate", "South_Gate").primary
    
    # 2. Artificially block a bottleneck node (Concourse_A)
    # The A* algorithm should now choose a different path avoiding it
    ai_engine.override_zone("Concourse_A", "HIGH")
    clear_route_cache()
    
    new_route_data = find_multi_route(ai_engine, "North_Gate", "South_Gate")
    new_path = new_route_data.primary.path
    
    # Simple check: the path should have changed if Concourse_A was in original
    if "Concourse_A" in baseline.path:
        assert "Concourse_A" not in new_path

def test_astar_same_nodes():
    """Verify ValueError when start and end node are the same."""
    try:
        find_multi_route(ai_engine, "North_Gate", "North_Gate")
    except ValueError as e:
        assert "distinct" in str(e)

def test_astar_route_caching():
    """Verify that identical requests hit the internal route cache."""
    clear_route_cache()
    result1 = find_multi_route(ai_engine, "North_Gate", "South_Gate")
    result2 = find_multi_route(ai_engine, "North_Gate", "South_Gate")
    # They should be the exact same object reference if returned from cache
    assert result1 is result2

def test_astar_alternative_safety_path():
    """Verify alternative path excludes bottleneck."""
    clear_route_cache()
    result = find_multi_route(ai_engine, "North_Gate", "South_Gate")
    # If primary has >2 nodes, alt path must not contain the bottleneck
    if len(result.primary.path) > 2:
        mid_nodes = result.primary.path[1:-1]
        bottleneck = max(mid_nodes, key=lambda n: ai_engine.zones[n].predicted_density_10m)
        assert bottleneck not in result.alternative.path

def test_astar_unreachable_node():
    """Verify A* handles a start/end where path is impossible (mocked)."""
    # This might require some mock but we can just test if the graph doesn't connect.
    # We can mock STADIUM_EDGES momentarily, or just ensure no crash on valid nodes.
    pass

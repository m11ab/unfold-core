"""
Integration tests for the compiled LangGraph agent.

These tests run the full agent workflow to ensure all components are correctly
integrated. We use a combination of mocked LLM calls for speed and reliability,
and a single, marked "live" test to verify the end-to-end connection with the
actual LLM service.
"""

import pytest
import json
from typing import Dict, Any
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

# Load environment variables (e.g., GOOGLE_API_KEY) before importing the agent
load_dotenv()

from src.agent.graph import get_agent_runnable, llm as original_llm
from src.core.models import Quest, Coordinates, TransitLeg, WalkingLeg, VehicleType

# Mark all tests in this file as integration tests.
# You can run only unit tests with `pytest -m "not integration"`.
pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def agent_runnable():
    """Fixture to compile the agent runnable once for all tests in this module."""
    return get_agent_runnable()

def run_graph_with_final_state(agent, initial_state) -> Dict[str, Any]:
    """Helper function to run the graph and return only the final state."""
    final_state = None
    for state_update in agent.stream(initial_state):
        final_state = state_update
    
    # Ensure we always return a valid state dictionary
    if final_state is None:
        pytest.fail("Agent failed to produce any state updates")
    
    assert isinstance(final_state, dict), f"Expected dict, got {type(final_state)}"
    return final_state

def test_efficiency_path_is_correct(agent_runnable):
    """
    Tests the 'EFFICIENCY' path. This path should NOT call the final synthesis LLM
    and should produce a simple, formatted string.
    """
    # 1. Input
    user_request = "What's the quickest way from Old Town to Purvciems?"
    initial_state = {"original_user_request": user_request}

    # 2. Action
    final_state = run_graph_with_final_state(agent_runnable, initial_state)

    # 3. Assertions
    assert final_state is not None
    assert final_state.get("intent") == "EFFICIENCY"
    assert final_state.get("transit_plan") is not None
    assert len(final_state.get("transit_plan", [])) > 0
    # The 'synthesize_quest' node should not have been run, so 'final_quest' should be None
    assert final_state.get("final_quest") is None
    # Check for keywords specific to the efficiency response format
    final_response = final_state.get("final_response", "")
    assert "Efficient Route:" in final_response
    assert "Depart:" in final_response
    assert "Arrive:" in final_response

def test_discovery_path_with_mocked_llm(agent_runnable, monkeypatch):
    """
    Tests the 'DISCOVERY' path using a MOCKED LLM for the final synthesis step.
    This allows us to test the graph's logic without a slow and expensive API call,
    and to verify that the agent correctly structures the data for the LLM.
    """
    # 1. Setup Mock LLM
    mock_llm = MagicMock()
    # Define the predictable, perfect JSON output our mock LLM will return
    mock_quest_json = Quest(
        title="Mocked Adventure",
        description="A journey crafted by a test.",
        legs=[
            WalkingLeg(start_location_name="Start", end_location_name="Bus Stop", duration_minutes=5, distance_meters=400, instructions="Walk to the bus stop.", pois=[]),
            TransitLeg(vehicle_type=VehicleType.BUS, route_short_name="17", trip_headsign="Abrenes iela", start_stop_name="Purvciems", end_stop_name="Central Station", departure_time="13:45", arrival_time="14:05", num_stops=10)
        ],
        total_duration_minutes=25
    ).json()
    
    # We create a mock response object that mimics the real LLM's output
    mock_response = MagicMock()
    mock_response.content = mock_quest_json
    mock_llm.invoke.return_value = mock_response
    
    # Use monkeypatch to replace the real LLM with our mock for the duration of this test
    monkeypatch.setattr("src.agent.graph.llm", mock_llm)

    # 2. Input
    user_request = "I want to go from Purvciems to Old Town"
    initial_state = {"original_user_request": user_request}
    
    # 3. Action
    final_state = run_graph_with_final_state(agent_runnable, initial_state)

    # 4. Assertions
    assert final_state is not None
    assert final_state.get("intent") == "DISCOVERY"
    assert final_state.get("transit_plan") is not None
    assert final_state.get("start_area_pois") is not None
    assert final_state.get("end_area_pois") is not None
    
    # Assert that the mock LLM was called once
    mock_llm.invoke.assert_called_once()
    
    # Assert that the final state contains the Quest object created from our mock's JSON
    final_quest = final_state.get("final_quest")
    assert isinstance(final_quest, Quest)
    assert final_quest.title == "Mocked Adventure"
    
    # Assert that the final response string was formatted correctly
    final_response = final_state.get("final_response", "")
    assert "Quest: Mocked Adventure" in final_response
    assert "Walk (5 mins)" in final_response

@pytest.mark.live_llm
def test_discovery_path_with_live_llm(agent_runnable):
    """
    Tests the full 'DISCOVERY' path with a LIVE LLM call.
    This test is marked as 'live_llm' and can be skipped during normal unit testing
    to save time and cost. Run with `pytest -m "live_llm"`.
    """
    # Restore the original LLM if it was mocked
    # Note: In a larger test suite, fixtures would handle this more cleanly.
    import src.agent.graph
    src.agent.graph.llm = original_llm

    # 1. Input
    user_request = "Show me an interesting journey from Old Town to Purvciems this afternoon arriving by 15:00"
    initial_state = {"original_user_request": user_request}

    # 2. Action
    final_state = run_graph_with_final_state(agent_runnable, initial_state)

    # 3. Assertions
    assert final_state is not None
    # Check that there were no errors in the final state
    assert not final_state.get("errors")
    
    assert final_state.get("intent") == "DISCOVERY"
    assert final_state.get("transit_plan") is not None
    
    # We can't know the exact content, but we can check the structure and type
    final_quest = final_state.get("final_quest")
    assert isinstance(final_quest, Quest)
    assert len(final_quest.title) > 5 # Title should not be empty
    assert len(final_quest.legs) > 1 # Should have at least one transit and one walking leg

    final_response = final_state.get("final_response", "")
    assert "Quest:" in final_response

# --- Additional Integration Tests for Complete Coverage ---

def test_input_parsing_node_functionality(agent_runnable):
    """
    Tests that the parse_user_request node correctly extracts locations and timing.
    """
    user_request = "I want to go from Purvciems to Old Town, arriving around 14:00"
    initial_state = {"original_user_request": user_request}
    
    final_state = run_graph_with_final_state(agent_runnable, initial_state)
    
    # Check that coordinates were parsed correctly
    assert final_state.get("start_coords") is not None
    assert final_state.get("end_coords") is not None
    assert final_state.get("arrival_time") is not None
    
    # Verify coordinate structure
    start_coords = final_state["start_coords"]
    end_coords = final_state["end_coords"]
    assert isinstance(start_coords, Coordinates)
    assert isinstance(end_coords, Coordinates)
    assert start_coords.latitude != end_coords.latitude  # Different locations

def test_intent_detection_with_efficiency_keywords(agent_runnable):
    """
    Tests that the determine_intent node correctly identifies EFFICIENCY requests.
    """
    test_cases = [
        "What's the quickest way from Old Town to Purvciems?",
        "I need the fastest route from Agenskalns to Central",
        "Show me the most efficient path to get there"
    ]
    
    for user_request in test_cases:
        initial_state = {"original_user_request": user_request}
        final_state = run_graph_with_final_state(agent_runnable, initial_state)
        
        assert final_state.get("intent") == "EFFICIENCY", f"Failed for: {user_request}"

def test_intent_detection_with_discovery_keywords(agent_runnable):
    """
    Tests that the determine_intent node correctly identifies DISCOVERY requests.
    """
    test_cases = [
        "Show me an interesting journey from Old Town to Purvciems",
        "I want to explore the route to Central Station",
        "Take me from here to there with some stops along the way"
    ]
    
    for user_request in test_cases:
        initial_state = {"original_user_request": user_request}
        final_state = run_graph_with_final_state(agent_runnable, initial_state)
        
        assert final_state.get("intent") == "DISCOVERY", f"Failed for: {user_request}"

def test_error_handling_missing_coordinates(agent_runnable):
    """
    Tests error handling when coordinates cannot be resolved.
    """
    user_request = "I want to go from NonexistentPlace to AnotherFakePlace"
    initial_state = {"original_user_request": user_request}
    
    final_state = run_graph_with_final_state(agent_runnable, initial_state)
    
    # Should handle gracefully with error messages
    assert final_state is not None
    errors = final_state.get("errors", [])
    assert len(errors) > 0  # Should have error messages
    
    final_response = final_state.get("final_response", "")
    assert "sorry" in final_response.lower() or "error" in final_response.lower()

def test_poi_retrieval_nodes(agent_runnable):
    """
    Tests that POI retrieval nodes return valid data structure.
    """
    user_request = "I want to go from Old Town to Purvciems"
    initial_state = {"original_user_request": user_request}
    
    final_state = run_graph_with_final_state(agent_runnable, initial_state)
    
    # For discovery path, should have POI data
    if final_state.get("intent") == "DISCOVERY":
        start_pois = final_state.get("start_area_pois", [])
        end_pois = final_state.get("end_area_pois", [])
        
        # Should return lists (even if empty)
        assert isinstance(start_pois, list)
        assert isinstance(end_pois, list)
        
        # If POIs are found, check structure
        for poi_list in [start_pois, end_pois]:
            for poi in poi_list:
                assert isinstance(poi, dict)
                assert "poi_id" in poi
                assert "title" in poi

def test_transit_planning_node(agent_runnable):
    """
    Tests that the transit planning node returns valid transit data.
    """
    user_request = "I want to go from Old Town to Purvciems"
    initial_state = {"original_user_request": user_request}
    
    final_state = run_graph_with_final_state(agent_runnable, initial_state)
    
    transit_plan = final_state.get("transit_plan")
    assert transit_plan is not None
    
    # Should be a list of transit legs
    assert isinstance(transit_plan, list)
    
    # If transit is found, check structure
    if len(transit_plan) > 0:
        leg = transit_plan[0]
        assert isinstance(leg, dict)
        # Check for required transit leg fields
        required_fields = ["vehicle_type", "route_short_name", "start_stop_name", "end_stop_name"]
        for field in required_fields:
            assert field in leg

def test_quest_synthesis_with_invalid_json_fallback(agent_runnable, monkeypatch):
    """
    Tests error handling when LLM returns invalid JSON for quest synthesis.
    """
    # Mock LLM that returns invalid JSON
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "This is not valid JSON for a quest"
    mock_llm.invoke.return_value = mock_response
    
    monkeypatch.setattr("src.agent.graph.llm", mock_llm)
    
    user_request = "Show me an interesting journey from Old Town to Purvciems"
    initial_state = {"original_user_request": user_request}
    
    final_state = run_graph_with_final_state(agent_runnable, initial_state)
    
    # Should handle the error gracefully
    assert final_state is not None
    final_response = final_state.get("final_response", "")
    assert len(final_response) > 0  # Should still provide some response
    
    # Check that errors were logged
    errors = final_state.get("errors", [])
    assert len(errors) > 0

def test_empty_input_handling(agent_runnable):
    """
    Tests handling of empty or whitespace-only input.
    """
    test_cases = ["", "   ", "\n\t  "]
    
    for user_request in test_cases:
        initial_state = {"original_user_request": user_request}
        final_state = run_graph_with_final_state(agent_runnable, initial_state)
        
        # Should handle gracefully without crashing
        assert final_state is not None
        final_response = final_state.get("final_response", "")
        assert len(final_response) > 0  # Should provide some response

def test_graph_structure_completeness(agent_runnable):
    """
    Meta-test: Ensures the graph structure contains all expected nodes.
    """
    # This test verifies the graph was compiled correctly
    graph = agent_runnable
    
    # Expected nodes based on graph.py
    expected_nodes = [
        "parse_user_request", 
        "determine_intent", 
        "plan_transit_route",
        "find_start_area_pois", 
        "find_end_area_pois", 
        "synthesize_quest",
        "format_simple_response"
    ]
    
    # Get the compiled graph's nodes
    graph_nodes = list(graph.graph.nodes.keys())
    
    for expected_node in expected_nodes:
        assert expected_node in graph_nodes, f"Missing node: {expected_node}"

def test_state_progression_efficiency_path(agent_runnable):
    """
    Tests that state fields are populated correctly through the efficiency path.
    """
    user_request = "What's the quickest way from Old Town to Purvciems?"
    initial_state = {"original_user_request": user_request}
    
    final_state = run_graph_with_final_state(agent_runnable, initial_state)
    
    # Required fields for efficiency path
    assert final_state.get("original_user_request") == user_request
    assert final_state.get("start_coords") is not None
    assert final_state.get("end_coords") is not None
    assert final_state.get("intent") == "EFFICIENCY"
    assert final_state.get("transit_plan") is not None
    assert final_state.get("final_response") is not None
    
    # Should NOT have quest synthesis fields for efficiency path
    assert final_state.get("final_quest") is None
    assert final_state.get("start_area_pois") is None
    assert final_state.get("end_area_pois") is None

def test_state_progression_discovery_path(agent_runnable, monkeypatch):
    """
    Tests that state fields are populated correctly through the discovery path.
    """
    # Mock LLM for predictable results
    mock_llm = MagicMock()
    mock_quest = Quest(
        title="Test Quest",
        description="A test journey",
        legs=[],
        total_duration_minutes=30
    )
    mock_response = MagicMock()
    mock_response.content = mock_quest.json()
    mock_llm.invoke.return_value = mock_response
    
    monkeypatch.setattr("src.agent.graph.llm", mock_llm)
    
    user_request = "Show me an interesting journey from Old Town to Purvciems"
    initial_state = {"original_user_request": user_request}
    
    final_state = run_graph_with_final_state(agent_runnable, initial_state)
    
    # Required fields for discovery path
    assert final_state.get("original_user_request") == user_request
    assert final_state.get("start_coords") is not None
    assert final_state.get("end_coords") is not None
    assert final_state.get("intent") == "DISCOVERY"
    assert final_state.get("transit_plan") is not None
    assert final_state.get("start_area_pois") is not None
    assert final_state.get("end_area_pois") is not None
    assert final_state.get("final_quest") is not None
    assert final_state.get("final_response") is not None
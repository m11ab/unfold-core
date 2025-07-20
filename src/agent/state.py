"""
Defines the state object for the unfold.quest LangGraph agent.

The AgentState is the central "memory" of our application for a single run.
It's a TypedDict that gets passed between all the nodes in the graph. Each node
can read from the state and write its results back to the state, progressively
building up the information needed to generate the final quest.

This state structure follows the agent workflow outlined in our project vision:
1. Parse user input and determine intent
2. Plan transit routes and find relevant POIs  
3. Synthesize everything into a narrative-driven quest
"""

from typing import TypedDict, List, Optional, Literal, Union

# We import our core Pydantic models to use them as types within our state.
# This ensures that the data carried in our state is validated and structured.
from src.core.models import Coordinates, TransitLeg, POI, Quest, WalkingLeg

# The intent is a controlled vocabulary, so we use Literal for type safety.
Intent = Literal["DISCOVERY", "EFFICIENCY"]

class AgentState(TypedDict):
    """
    Represents the full state of our agent's workflow for a single user request.
    
    This state progresses through the following phases:
    1. Input Processing: Parse user request, extract coordinates and timing
    2. Intent Detection: Determine if user wants efficiency or discovery  
    3. Route Planning: Find transit routes and walking segments
    4. POI Discovery: Find relevant points of interest along the route
    5. Quest Synthesis: Combine everything into a narrative quest
    """
    # --- Initial User Input ---
    original_user_request: str
    
    # --- Parsed & Enriched Input ---
    # These fields are populated by the first nodes in the graph.
    start_coords: Optional[Coordinates]
    end_coords: Optional[Coordinates]
    arrival_time: Optional[str]  # Stored in "HH:MM" format
    departure_time: Optional[str]  # Alternative to arrival_time, also "HH:MM" format
    
    # --- Core Decision-Making ---
    # The output of our Context & Intent Engine.
    intent: Optional[Intent]
    
    # --- Intermediate Tool Outputs ---
    # The results from calling our deterministic tools.
    transit_plan: Optional[List[TransitLeg]]
    walking_segments: Optional[List[WalkingLeg]]  # Walking portions of the journey
    route_pois: Optional[List[POI]]  # POIs discovered along the planned route
    start_area_pois: Optional[List[POI]]  # POIs near the starting location
    end_area_pois: Optional[List[POI]]  # POIs near the destination
    
    # --- Quest Generation Support ---
    quest_theme: Optional[str]  # e.g., "The Merchant's Gambit", "Art Nouveau Adventure"
    estimated_total_duration: Optional[int]  # Total journey time in minutes
    discovery_opportunities: Optional[List[str]]  # Narrative hooks for the quest
    
    # --- Final Synthesized Output ---
    # The final, user-facing quest object.
    final_quest: Optional[Quest]
    
    # A simple, formatted string version of the final quest for easy display.
    final_response: Optional[str]
    
    # --- Error Handling & Debugging ---
    errors: Optional[List[str]]  # Any errors encountered during processing
    debug_info: Optional[dict]  # Additional debug information for development
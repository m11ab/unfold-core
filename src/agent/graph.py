"""
The core agentic workflow for unfold.quest, built using LangGraph.

This module defines the stateful graph that orchestrates the entire process of
transforming a user's request into a narrative-driven quest. It follows the
"Workflow with an Agentic Heart" pattern, where deterministic tasks are handled by
tools and the final creative synthesis is handled by an LLM.
"""

import os
import json
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START

# Import the state and models we've defined. This is the "memory" of our agent.
from .state import AgentState, Intent
from src.core.models import Coordinates, Quest

# Import the deterministic "hands" of our agent.
from src.tools.poi_retriever import retrieve_nearby_pois_as_dict
from src.tools.transit_planner import plan_transit_journey_as_dict

# --- 1. Agent Configuration & Initialization ---

# Initialize the LLM. For this prototype, we'll use Gemini 2.5 Flash.
# The API key should be set as an environment variable (GOOGLE_API_KEY).
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# Define the Pydantic model for structured output when parsing the user request.
class ParsedUserRequest(BaseModel):
    """Structured representation of the user's initial request."""
    start_location_query: str = Field(description="The starting location mentioned by the user, e.g., 'Purvciems'.")
    end_location_query: str = Field(description="The destination location mentioned by the user, e.g., 'Old Town'.")
    arrival_time: Optional[str] = Field(description="The desired arrival time in HH:MM format, if mentioned.")

structured_llm = llm.with_structured_output(ParsedUserRequest)

# --- 2. Graph Nodes: The Steps of the Agent's "Thought Process" ---

def parse_user_request(state: AgentState) -> dict:
    """
    Node 1: Parses the user's natural language request into a structured format.
    This is the entry point of the graph.
    """
    print("---NODE: PARSING USER REQUEST---")
    prompt = f"""
    You are an expert at parsing user requests for a journey planning app.
    Parse the following user request and extract the starting location, destination, and desired arrival time.
    The current time is {datetime.now().strftime('%Y-%m-%d %H:%M')}.
    
    User Request: "{state['original_user_request']}"
    """
    parsed_request = structured_llm.invoke(prompt)
    
    # For this prototype, we'll use fixed coordinates for known locations.
    # A production version would use a geocoding API.
    location_map = {
        "purvciems": Coordinates(latitude=56.9634, longitude=24.1953),
        "old town": Coordinates(latitude=56.9496, longitude=24.1052),
        "agenskalns": Coordinates(latitude=56.9363, longitude=24.0722)
    }
    
    start_coords = location_map.get(parsed_request.start_location_query.lower())
    end_coords = location_map.get(parsed_request.end_location_query.lower())

    return {
        "start_coords": start_coords,
        "end_coords": end_coords,
        "arrival_time": parsed_request.arrival_time or "14:00" # Default arrival time
    }

def determine_intent(state: AgentState) -> dict:
    """
    Node 2: The Context & Intent Engine. Determines if the user wants a quick
    journey or a discovery-focused quest.
    """
    print("---NODE: DETERMINING INTENT---")
    # For the prototype, we use a simple rule-based engine.
    # A production version would use more sophisticated signals (see docs).
    request = state['original_user_request'].lower()
    if "quickest" in request or "fastest" in request:
        intent = "EFFICIENCY"
    else:
        # Default to discovery for the prototype to showcase the main feature
        intent = "DISCOVERY"
    
    print(f"Intent determined as: {intent}")
    return {"intent": intent}

def plan_transit_route(state: AgentState) -> dict:
    """Node 3: Calls the transit planner tool to get the logistical backbone."""
    print("---NODE: PLANNING TRANSIT ROUTE---")
    
    # Check if we have valid coordinates
    if not state.get('start_coords') or not state.get('end_coords'):
        print("Warning: Missing coordinates for transit planning")
        return {"transit_plan": None, "errors": ["Missing start or end coordinates"]}
    
    # Check if we have arrival time
    arrival_time = state.get('arrival_time')
    if not arrival_time:
        arrival_time = "14:00"  # Default fallback
    
    try:
        start_coords = state['start_coords']
        end_coords = state['end_coords']
        assert start_coords is not None, "Start coordinates are required"
        assert end_coords is not None, "End coordinates are required"
        
        plan = plan_transit_journey_as_dict(
            start_latitude=start_coords.latitude,
            start_longitude=start_coords.longitude,
            end_latitude=end_coords.latitude,
            end_longitude=end_coords.longitude,
            arrival_time=arrival_time
        )
        return {"transit_plan": plan}
    except Exception as e:
        print(f"Error planning transit route: {e}")
        return {"transit_plan": None, "errors": [f"Transit planning failed: {str(e)}"]}

def find_start_area_pois(state: AgentState) -> dict:
    """Node 4a: Finds POIs near the starting location for the 'Discovery' path."""
    print("---NODE: FINDING START AREA POIS---")
    
    if not state.get('start_coords'):
        print("Warning: No start coordinates available for POI search")
        return {"start_area_pois": []}
    
    try:
        start_coords = state['start_coords']
        assert start_coords is not None, "Start coordinates are required"
        
        pois = retrieve_nearby_pois_as_dict(
            latitude=start_coords.latitude,
            longitude=start_coords.longitude,
            max_results=3
        )
        return {"start_area_pois": pois}
    except Exception as e:
        print(f"Error finding start area POIs: {e}")
        return {"start_area_pois": [], "errors": [f"POI search failed: {str(e)}"]}

def find_end_area_pois(state: AgentState) -> dict:
    """Node 4b: Finds POIs near the destination for the 'Discovery' path."""
    print("---NODE: FINDING END AREA POIS---")
    
    if not state.get('end_coords'):
        print("Warning: No end coordinates available for POI search")
        return {"end_area_pois": []}
    
    try:
        end_coords = state['end_coords']
        assert end_coords is not None, "End coordinates are required"
        
        pois = retrieve_nearby_pois_as_dict(
            latitude=end_coords.latitude,
            longitude=end_coords.longitude,
            max_results=3
        )
        return {"end_area_pois": pois}
    except Exception as e:
        print(f"Error finding end area POIs: {e}")
        return {"end_area_pois": [], "errors": [f"POI search failed: {str(e)}"]}

def synthesize_quest(state: AgentState) -> dict:
    """
    Node 5 (The Agentic Heart): Takes all collected data and synthesizes the
    final, narrative-driven quest.
    """
    print("---NODE: SYNTHESIZING QUEST---")
    
    # Check if we have the required data
    if not state.get('transit_plan'):
        return {
            "final_response": "Sorry, I couldn't plan a transit route for your journey.",
            "errors": ["No transit plan available for quest synthesis"]
        }
    
    try:
        prompt = f"""
        You are the "Personal Adventure Architect" for the unfold.quest app. Your goal is to
        transform a boring transit plan into an engaging, narrative-driven micro-quest.

        You have the following information:
        - User Request: "{state.get('original_user_request', 'Unknown request')}"
        - Transit Plan: {json.dumps(state.get('transit_plan', {}), indent=2)}
        - Interesting places near the start: {json.dumps(state.get('start_area_pois', []), indent=2)}
        - Interesting places near the destination: {json.dumps(state.get('end_area_pois', []), indent=2)}

        Your task is to create a final "Quest" object. Be creative and thematic!
        1.  Give the quest a fun, creative title.
        2.  Write a short, engaging description for the whole adventure.
        3.  Construct the `legs` of the journey:
            -   Create a `WalkingLeg` to get from the start to the first bus stop. Incorporate one of the `start_area_pois` into the instructions.
            -   Include the `TransitLeg` from the provided plan.
            -   Create a `WalkingLeg` to get from the final bus stop to the destination. Incorporate one of the `end_area_pois` into the instructions.
        4.  Calculate the total duration. Assume walking speed is 5 km/h (12 mins/km).
        5.  Return ONLY a valid JSON object that conforms to the Pydantic `Quest` model.
        """
        
        response = llm.invoke(prompt)
        quest_json = json.loads(response.content)
        
        # Validate the LLM's output with our Pydantic model
        final_quest = Quest(**quest_json)
        
        # Create a simple formatted string for display
        formatted_response = f"**Quest: {final_quest.title}**\n\n_{final_quest.description}_\n\n"
        for i, leg in enumerate(final_quest.legs):
            formatted_response += f"**Part {i+1}:** "
            if hasattr(leg, 'duration_minutes'):  # WalkingLeg
                formatted_response += f"Walk ({leg.duration_minutes} mins)\n"
                formatted_response += f"> {leg.instructions}\n\n"
            else:  # TransitLeg
                formatted_response += f"Take the {leg.vehicle_type} {leg.route_short_name}\n"
                formatted_response += f"> From {leg.start_stop_name} to {leg.end_stop_name}\n\n"

        return {"final_quest": final_quest, "final_response": formatted_response}
        
    except Exception as e:
        print(f"Error synthesizing quest: {e}")
        # Fallback to a simple response
        transit_plan = state.get('transit_plan', [])
        if transit_plan and len(transit_plan) > 0:
            leg = transit_plan[0]
            simple_response = (
                f"**Your Journey:**\n\n"
                f"Take the **{leg.get('vehicle_type', 'transport')} {leg.get('route_short_name', 'N/A')}** "
                f"from **{leg.get('start_stop_name', 'your starting point')}** "
                f"to **{leg.get('end_stop_name', 'your destination')}**."
            )
            return {"final_response": simple_response, "errors": [f"Quest synthesis failed: {str(e)}"]}
        else:
            return {
                "final_response": "I couldn't create a detailed quest, but you should be able to reach your destination.",
                "errors": [f"Quest synthesis failed: {str(e)}"]
            }

def format_simple_response(state: AgentState) -> dict:
    """Node 6: Formats a simple, efficient response for the 'Efficiency' path."""
    print("---NODE: FORMATTING SIMPLE RESPONSE---")
    
    transit_plan = state.get('transit_plan')
    if not transit_plan or len(transit_plan) == 0:
        return {"final_response": "Sorry, I could not find a direct transit route for your journey."}
    
    try:
        leg = transit_plan[0]
        response = (
            f"**Your Efficient Route:**\n\n"
            f"1.  **Depart:** Head to **{leg.get('start_stop_name', 'the starting stop')}** to catch the "
            f"**{leg.get('vehicle_type', 'transport')} {leg.get('route_short_name', 'N/A')}** "
            f"(towards {leg.get('trip_headsign', 'your destination')}) at **{leg.get('departure_time', 'the scheduled time')}**.\n"
            f"2.  **Arrive:** You will arrive at **{leg.get('end_stop_name', 'your destination')}** "
            f"at approximately **{leg.get('arrival_time', 'the scheduled time')}**."
        )
        return {"final_response": response}
    except Exception as e:
        print(f"Error formatting simple response: {e}")
        return {
            "final_response": "I found a transit route for you, but couldn't format the details properly.",
            "errors": [f"Response formatting failed: {str(e)}"]
        }

# --- 3. Graph Edges: Defining the Flow of Logic ---

def route_by_intent(state: AgentState) -> Literal["efficiency_path", "discovery_path"]:
    """
    This is the conditional edge. It reads the `intent` from the state and
    decides which path the graph should take next.
    """
    if state.get('intent') == "EFFICIENCY":
        return "efficiency_path"
    else:
        return "discovery_path"

def route_after_planning(state: AgentState) -> Literal["efficiency_path", "discovery_path"]:
    """
    Routes to the appropriate next step after transit planning is complete.
    """
    if state.get('intent') == "EFFICIENCY":
        return "efficiency_path"
    else:
        return "discovery_path"

# --- 4. Assembling the Graph ---

def get_agent_runnable():
    """
    Builds and compiles the LangGraph agent using best practices.
    
    The graph follows this structure:
    1. Parse user request → 2. Determine intent → 3. Route by intent
    4a. Discovery path: Plan → Find POIs → Synthesize quest
    4b. Efficiency path: Plan → Format simple response
    """
    builder = StateGraph(AgentState)

    # Add all nodes to the graph
    builder.add_node("parse_user_request", parse_user_request)
    builder.add_node("determine_intent", determine_intent)
    builder.add_node("plan_transit_route", plan_transit_route)
    builder.add_node("find_start_area_pois", find_start_area_pois)
    builder.add_node("find_end_area_pois", find_end_area_pois)
    builder.add_node("synthesize_quest", synthesize_quest)
    builder.add_node("format_simple_response", format_simple_response)

    # Define the initial flow
    builder.add_edge(START, "parse_user_request")
    builder.add_edge("parse_user_request", "determine_intent")
    
    # Route based on intent after determining it
    builder.add_conditional_edges(
        "determine_intent",
        route_by_intent,
        {
            "efficiency_path": "plan_transit_route",
            "discovery_path": "plan_transit_route"  # Both paths need transit planning
        }
    )
    
    # After transit planning, route again based on intent
    builder.add_conditional_edges(
        "plan_transit_route",
        route_after_planning,
        {
            "efficiency_path": "format_simple_response",
            "discovery_path": "find_start_area_pois"
        }
    )
    
    # Discovery path continues
    builder.add_edge("find_start_area_pois", "find_end_area_pois")
    builder.add_edge("find_end_area_pois", "synthesize_quest")
    
    # Both paths end
    builder.add_edge("synthesize_quest", END)
    builder.add_edge("format_simple_response", END)
    
    # Compile and return the final runnable agent
    return builder.compile()
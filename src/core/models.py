"""
Core Pydantic models for the unfold.quest application.

This module defines the primary data structures that are used throughout the application,
from data loading and tool execution to the agent's state management. Using Pydantic
ensures data consistency, validation, and provides excellent editor support.
"""

from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field

# --- Enums for Controlled Vocabularies ---

class POICategory(str, Enum):
    """Enumeration for the primary category of a Point of Interest."""
    ART = "Art"
    HISTORY = "History"
    ARCHITECTURE = "Architecture"
    NATURE = "Nature"
    FOOD_DRINK = "Food & Drink"
    HIDDEN_GEM = "Hidden Gem"

class POIType(str, Enum):
    """Enumeration for the physical type of a Point of Interest."""
    OUTDOOR = "Outdoor"
    INDOOR = "Indoor"

class VehicleType(str, Enum):
    """Enumeration for the type of public transport vehicle."""
    BUS = "Bus"
    TRAM = "Tram"
    TROLLEYBUS = "Trolleybus"

# --- POI and its Sub-Models (The "What") ---

class Coordinates(BaseModel):
    """Represents a geographical coordinate pair."""
    latitude: float
    longitude: float

class NarrativeHooks(BaseModel):
    """
    A collection of structured text snippets designed to give the AI agent
    creative, context-specific material for generating its narrative.
    """
    history: Optional[str] = Field(None, description="A brief historical fact or story.")
    fun_fact: Optional[str] = Field(None, description="A surprising or fun detail.")
    architectural_detail: Optional[str] = Field(None, description="A specific detail about the building or structure.")

class Media(BaseModel):
    """Represents media associated with a POI, like images."""
    image_url: Optional[str] = Field(None, description="A direct URL to a representative image.")
    attribution_text: Optional[str] = Field(None, description="Credit for the image source.")

class PracticalInfo(BaseModel):
    """
    Contains practical, operational information about the POI needed for
    planning and user guidance.
    """
    type: POIType
    cost: str = Field(..., description="E.g., Free, €, €€, €€€")
    operating_hours: str = Field(..., description="E.g., 24/7, Mo-Fr 09:00-17:00")
    estimated_duration_minutes: int = Field(..., description="Best estimate for a brief visit.")

class POI(BaseModel):
    """
    The complete, validated data model for a single Point of Interest (POI).
    This structure mirrors the schema defined in our data/pois/ JSON files.
    """
    poi_id: str = Field(..., description="A unique, machine-readable ID, e.g., riga_cat_house")
    title: str = Field(..., description="The primary human-readable name of the POI.")
    coordinates: Coordinates
    address: str = Field(..., description="The human-readable street address.")
    category: POICategory
    description: str = Field(..., description="A concise, engaging summary suitable for a mobile app.")
    narrative_hooks: NarrativeHooks
    media: Media
    practical_info: PracticalInfo

# --- Journey Leg Models (The "How") ---

class TransitLeg(BaseModel):
    """Represents a single, unbroken leg of a journey on public transport."""
    vehicle_type: VehicleType
    route_short_name: str = Field(..., description="The route number, e.g., '17' or '11'.")
    trip_headsign: str = Field(..., description="The destination sign on the vehicle, e.g., 'Abrenes iela'.")
    start_stop_name: str
    end_stop_name: str
    departure_time: str = Field(..., description="Scheduled departure time in HH:MM format.")
    arrival_time: str = Field(..., description="Scheduled arrival time in HH:MM format.")
    num_stops: int = Field(..., description="The number of stops on this leg of the journey.")

class WalkingLeg(BaseModel):
    """Represents a single, unbroken leg of a journey on foot."""
    start_location_name: str = Field(..., description="e.g., 'Your Location', 'Central Station'")
    end_location_name: str = Field(..., description="e.g., 'Bus Stop Miera iela', 'Your Destination'")
    duration_minutes: int
    distance_meters: int
    instructions: str = Field(..., description="Narrative instructions for this leg of the walk.")
    pois: List[POI] = Field(default_factory=list, description="A list of POIs to be discovered on this leg.")

# --- The Final Composite Model (The "Story") ---

class Quest(BaseModel):
    """
    The final, user-facing output of the agent. A composite object that
    describes the entire journey as a narrative-driven quest.
    """
    title: str = Field(..., description="A creative, engaging title for the quest.")
    description: str = Field(..., description="A short summary of the entire adventure.")
    legs: List[Union[WalkingLeg, TransitLeg]] = Field(..., description="The sequential steps of the journey.")
    total_duration_minutes: int
    reward_points: int = Field(default=50)
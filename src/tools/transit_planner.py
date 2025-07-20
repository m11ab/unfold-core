"""
Tool for planning public transport journeys using static GTFS data.

This module encapsulates all logic for loading, parsing, and querying the GTFS
dataset for Riga. It provides functionality to find the nearest stops to a given
coordinate and plan a direct, no-transfer journey between two points.

Note: The current implementation is a simplified proof-of-concept and does not
handle journeys that require transfers. This is a documented limitation for the
prototype and a key area for future development.
"""

import os
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
from typing import List, Optional

import pandas as pd

# We import our validated Pydantic models from the core module. This ensures that
# any data returned by this tool conforms to our application's standard structure.
from src.core.models import Coordinates, TransitLeg, VehicleType

# --- Constants and Configuration ---
GTFS_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'gtfs')

# --- Helper Functions ---

def haversine_distance(coord1: Coordinates, coord2: Coordinates) -> float:
    """Calculates the distance in kilometers between two points on Earth."""
    R = 6371.0
    lat1, lon1 = radians(coord1.latitude), radians(coord1.longitude)
    lat2, lon2 = radians(coord2.latitude), radians(coord2.longitude)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def _map_route_type_to_vehicle(route_type: int) -> VehicleType:
    """Maps GTFS route_type integer to our VehicleType enum for Riga's specific codes."""
    # Based on Riga's GTFS `routes.txt` file
    if route_type in [0, 2, 900]:  # 0/2 for Tram, 900 also used for Tram
        return VehicleType.TRAM
    if route_type == 3 or route_type == 700: # 3 for Bus, 700 also used for Bus
        return VehicleType.BUS
    if route_type == 800: # 800 for Trolleybus
        return VehicleType.TROLLEYBUS
    return VehicleType.BUS  # Default to bus if type is unknown

# --- Core Journey Planning Logic ---

class TransitPlanner:
    """
    A class to manage the loading of GTFS data and planning of journeys.

    Designed as a singleton to load the GTFS data into pandas DataFrames only
    once at startup for efficient querying.
    """
    
    def __init__(self):
        """Initialize the planner and load GTFS data into memory."""
        self.stops_df: Optional[pd.DataFrame] = None
        self.timetable_df: Optional[pd.DataFrame] = None
        self._load_gtfs_data()
    
    def _load_gtfs_data(self):
        """Loads and pre-processes GTFS data into efficient DataFrames."""
        try:
            # Load core GTFS files using explicit dtypes for stability
            stops_path = os.path.join(GTFS_DATA_DIR, 'stops.txt')
            stop_times_path = os.path.join(GTFS_DATA_DIR, 'stop_times.txt')
            trips_path = os.path.join(GTFS_DATA_DIR, 'trips.txt')
            routes_path = os.path.join(GTFS_DATA_DIR, 'routes.txt')
            
            self.stops_df = pd.read_csv(stops_path, dtype={'stop_id': str})
            stop_times_df = pd.read_csv(stop_times_path, dtype={'trip_id': str, 'stop_id': str})
            trips_df = pd.read_csv(trips_path, dtype={'route_id': str, 'trip_id': str, 'service_id': str})
            routes_df = pd.read_csv(routes_path, dtype={'route_id': str})

            # CRITICAL FIX: Properly handle GTFS times that can exceed 23:59:59.
            # Pandas to_timedelta is the correct and robust way to do this.
            stop_times_df['arrival_time_td'] = pd.to_timedelta(stop_times_df['arrival_time'])
            
            # Create a single, denormalized timetable for efficient lookups.
            timetable = pd.merge(stop_times_df, trips_df, on='trip_id')
            self.timetable_df = pd.merge(timetable, routes_df, on='route_id')
            
            print(f"Successfully loaded GTFS data for {len(routes_df)} routes.")
        except FileNotFoundError as e:
            print(f"Error: GTFS data file not found. Make sure data is in {GTFS_DATA_DIR}. Details: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading GTFS data: {e}")

    def _find_nearest_stop(self, location: Coordinates) -> Optional[dict]:
        """Finds the closest transit stop to a given coordinate."""
        if self.stops_df is None or self.stops_df.empty:
            print("Warning: No stops data available.")
            return None
        
        try:
            distances = self.stops_df.apply(
                lambda row: haversine_distance(
                    location, 
                    Coordinates(latitude=row['stop_lat'], longitude=row['stop_lon'])
                ),
                axis=1
            )
            nearest_stop_index = distances.idxmin()
            nearest_stop = self.stops_df.loc[nearest_stop_index].to_dict()
            
            # Add distance information for debugging/logging
            nearest_distance = distances.iloc[nearest_stop_index]
            nearest_stop['distance_km'] = round(nearest_distance, 3)
            
            return nearest_stop
        except Exception as e:
            print(f"Error finding nearest stop: {e}")
            return None

    def plan_journey(self, start_coords: Coordinates, end_coords: Coordinates, arrival_time_str: str) -> Optional[List[TransitLeg]]:
        """
        Plans a direct, no-transfer journey between two points based on a desired arrival time.
        """
        if self.timetable_df is None or self.timetable_df.empty:
            print("Error: GTFS timetable data is not loaded.")
            return None

        # 1. Find nearest stops to start and end coordinates
        start_stop = self._find_nearest_stop(start_coords)
        end_stop = self._find_nearest_stop(end_coords)
        
        if not start_stop or not end_stop:
            print("Error: Could not find nearest stops for the given coordinates.")
            return None
        
        start_stop_id = start_stop['stop_id']
        end_stop_id = end_stop['stop_id']
        
        print(f"Planning journey from '{start_stop['stop_name']}' to '{end_stop['stop_name']}'")
        
        # Handle case where start and end stops are the same
        if start_stop_id == end_stop_id:
            print("Warning: Start and end stops are the same. No journey needed.")
            return None
        
        # 2. Find all trips that service BOTH the start and end stop
        trips_at_start = self.timetable_df[self.timetable_df['stop_id'] == start_stop_id]
        trips_at_end = self.timetable_df[self.timetable_df['stop_id'] == end_stop_id]
        
        if trips_at_start.empty or trips_at_end.empty:
            print(f"No trips found serving one or both stops.")
            return None
        
        # Merge to find common trip_ids
        common_trips = pd.merge(trips_at_start, trips_at_end, on='trip_id', suffixes=('_start', '_end'))
        
        if common_trips.empty:
            print("No direct routes found between the selected stops.")
            return None
        
        # 3. Filter for valid trips: correct direction and time window
        # Correct direction: The sequence number at the start stop must be less than at the end stop.
        valid_direction_trips = common_trips[common_trips['stop_sequence_start'] < common_trips['stop_sequence_end']]
        
        if valid_direction_trips.empty:
            print("No direct trips found in the correct direction.")
            return None

        # Correct time window: The trip must arrive at the destination *before* the desired arrival time.
        try:
            arrival_time_td = pd.to_timedelta(f"{arrival_time_str}:00")
        except ValueError:
            print(f"Invalid arrival time format: {arrival_time_str}. Expected HH:MM format.")
            return None
            
        on_time_trips = valid_direction_trips[valid_direction_trips['arrival_time_td_end'] <= arrival_time_td]

        if on_time_trips.empty:
            print(f"No trips found arriving before {arrival_time_str}.")
            return None

        # 4. Select the BEST trip: the one that arrives the latest, but still on time.
        # This minimizes waiting time for the user.
        best_trip = on_time_trips.loc[on_time_trips['arrival_time_td_end'].idxmax()]

        # 5. Format the result into our Pydantic model for a clean, validated output
        num_stops = int(best_trip['stop_sequence_end'] - best_trip['stop_sequence_start'])
        
        try:
            transit_leg = TransitLeg(
                vehicle_type=_map_route_type_to_vehicle(best_trip['route_type_start']),
                route_short_name=str(best_trip['route_short_name_start']),
                trip_headsign=str(best_trip['trip_headsign_start']),
                start_stop_name=str(start_stop['stop_name']),
                end_stop_name=str(end_stop['stop_name']),
                departure_time=str(best_trip['departure_time_start'])[:-3], # Remove seconds for HH:MM format
                arrival_time=str(best_trip['arrival_time_end'])[:-3], # Remove seconds for HH:MM format
                num_stops=num_stops
            )
            
            print(f"Found journey: {transit_leg.route_short_name} from {transit_leg.start_stop_name} to {transit_leg.end_stop_name}")
            
            # Return as a list to support future multi-leg journey plans
            return [transit_leg]
            
        except Exception as e:
            print(f"Error creating TransitLeg model: {e}")
            return None

# --- Tool Function for Agent Integration ---

_transit_planner_instance = None

def get_transit_planner() -> TransitPlanner:
    """Gets the singleton TransitPlanner instance, creating it if necessary."""
    global _transit_planner_instance
    if _transit_planner_instance is None:
        _transit_planner_instance = TransitPlanner()
    return _transit_planner_instance

def plan_transit_journey(start_latitude: float, start_longitude: float, 
                         end_latitude: float, end_longitude: float, 
                         arrival_time: str) -> Optional[List[TransitLeg]]:
    """
    Main tool function for the LangGraph agent to plan a journey.
    
    This is the primary interface that returns full Pydantic models for type safety.
    
    Args:
        start_latitude: Latitude of the starting point.
        start_longitude: Longitude of the starting point.
        end_latitude: Latitude of the ending point.
        end_longitude: Longitude of the ending point.
        arrival_time: Desired arrival time in "HH:MM" format (e.g., "14:30").
        
    Returns:
        A list of TransitLeg models, or None if no direct route is found.
    """
    planner = get_transit_planner()
    start_coords = Coordinates(latitude=start_latitude, longitude=start_longitude)
    end_coords = Coordinates(latitude=end_latitude, longitude=end_longitude)

    return planner.plan_journey(start_coords, end_coords, arrival_time)

def plan_transit_journey_as_dict(start_latitude: float, start_longitude: float, 
                                end_latitude: float, end_longitude: float, 
                                arrival_time: str) -> Optional[List[dict]]:
    """
    Legacy function that returns transit legs as dictionaries for backward compatibility.
    
    Args:
        start_latitude: Latitude of the starting point.
        start_longitude: Longitude of the starting point.
        end_latitude: Latitude of the ending point.
        end_longitude: Longitude of the ending point.
        arrival_time: Desired arrival time in "HH:MM" format (e.g., "14:30").
        
    Returns:
        A list containing transit leg dictionaries, or None if no direct route is found.
    """
    journey_plan = plan_transit_journey(start_latitude, start_longitude, 
                                      end_latitude, end_longitude, arrival_time)
    
    if journey_plan:
        return [leg.dict() for leg in journey_plan]
    
    return None
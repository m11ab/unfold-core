"""
Tool for retrieving Points of Interest (POIs) from the curated local dataset.

This module encapsulates all logic for loading, parsing, and querying the POI
JSON files stored in the `/data/pois/` directory. It uses the Haversine formula
for accurate distance calculation between geographical coordinates.
"""

import os
import json
from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict, Optional

# We import our validated Pydantic model from the core module. This ensures that
# any data returned by this tool conforms to our application's standard structure.
from src.core.models import POI, Coordinates
from pydantic import BaseModel, Field

# --- Extended Models for Tool Results ---

class POIWithDistance(POI):
    """
    Extends the base POI model to include calculated distance information.
    
    This model is used when returning POIs from geospatial queries to provide
    the caller with both the complete POI data and the calculated distance.
    """
    distance_km: float = Field(..., description="Distance from query point in kilometers")

# --- Constants and Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'pois')

# --- Helper Functions ---

def haversine_distance(coord1: Coordinates, coord2: Coordinates) -> float:
    """
    Calculate the distance in kilometers between two points on Earth
    (specified in decimal degrees) using the Haversine formula.
    """
    # Earth radius in kilometers
    R = 6371.0

    lat1, lon1 = radians(coord1.latitude), radians(coord1.longitude)
    lat2, lon2 = radians(coord2.latitude), radians(coord2.longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# --- Core Data Loading and Retrieval Logic ---

class POIRetriever:
    """
    A class to manage the loading and querying of POI data.

    This class is designed as a singleton pattern (though not strictly enforced)
    to load the data from disk only once and keep it in memory for fast,
    repeated lookups. This is efficient for a prototype with a manageable
    dataset size.
    """
    
    def __init__(self):
        """Initialize the POI retriever and load all POI data into memory."""
        self.pois: List[POI] = []
        self._load_all_pois()
    
    def _load_all_pois(self):
        """
        Load all POI data from JSON files in the data directory.
        
        This method scans the /data/pois/ directory for JSON files and loads
        all POIs into memory for fast querying.
        """
        if not os.path.exists(DATA_DIR):
            raise FileNotFoundError(f"POI data directory not found: {DATA_DIR}")
        
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.json') and filename.startswith('poi-'):
                file_path = os.path.join(DATA_DIR, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Extract POIs from the 'pois' array in each file
                    if 'pois' in data and isinstance(data['pois'], list):
                        for poi_data in data['pois']:
                            try:
                                # Convert to our Pydantic model for validation
                                poi = POI(**poi_data)
                                self.pois.append(poi)
                            except Exception as e:
                                print(f"Warning: Failed to parse POI in {filename}: {e}")
                                continue
                                
                except Exception as e:
                    print(f"Warning: Failed to load POI file {filename}: {e}")
                    continue
        
        print(f"Loaded {len(self.pois)} POIs from {DATA_DIR}")
    
    def find_nearby_pois(self, location: Coordinates, radius_km: float = 2.0, 
                        max_results: int = 10, category: Optional[str] = None) -> List[POIWithDistance]:
        """
        Find POIs within a specified radius of a given location.
        
        Args:
            location: The center point for the search
            radius_km: Search radius in kilometers (default: 2.0)
            max_results: Maximum number of results to return (default: 10)
            category: Optional category filter (e.g., "History", "Art", "Food & Drink")
            
        Returns:
            List of POIWithDistance models, sorted by distance (closest first)
        """
        results = []
        
        for poi in self.pois:
            # Calculate distance to the POI
            distance = haversine_distance(location, poi.coordinates)
            
            # Filter by radius
            if distance <= radius_km:
                # Filter by category if specified
                if category is None or poi.category.lower() == category.lower():
                    # Create POIWithDistance by copying all POI fields and adding distance
                    poi_with_distance = POIWithDistance(
                        **poi.dict(),
                        distance_km=round(distance, 2)
                    )
                    results.append(poi_with_distance)
        
        # Sort by distance and limit results
        results.sort(key=lambda x: x.distance_km)
        return results[:max_results]
    
    def get_poi_by_id(self, poi_id: str) -> Optional[POI]:
        """
        Retrieve a specific POI by its ID.
        
        Args:
            poi_id: The unique identifier for the POI
            
        Returns:
            POI model or None if not found
        """
        for poi in self.pois:
            if poi.poi_id == poi_id:
                return poi
        return None
    
    def get_pois_by_category(self, category: str, max_results: int = 20) -> List[POI]:
        """
        Get all POIs matching a specific category.
        
        Args:
            category: The category to filter by (e.g., "Architecture", "History")
            max_results: Maximum number of results to return
            
        Returns:
            List of POI models
        """
        results = []
        
        for poi in self.pois:
            if poi.category.lower() == category.lower():
                results.append(poi)
                
                if len(results) >= max_results:
                    break
        
        return results


# --- Tool Function for Agent Integration ---

# Global instance - loaded once when the module is imported
_poi_retriever_instance = None

def get_poi_retriever() -> POIRetriever:
    """Get the singleton POI retriever instance."""
    global _poi_retriever_instance
    if _poi_retriever_instance is None:
        _poi_retriever_instance = POIRetriever()
    return _poi_retriever_instance

def retrieve_nearby_pois(latitude: float, longitude: float, 
                        radius_km: float = 2.0, max_results: int = 10, 
                        category: Optional[str] = None) -> List[POIWithDistance]:
    """
    Main tool function for the agent to retrieve nearby POIs.
    
    This is the primary interface that the LangGraph agent will use.
    Returns full Pydantic models for type safety and auto-completion.
    
    Args:
        latitude: Latitude of the search center
        longitude: Longitude of the search center  
        radius_km: Search radius in kilometers
        max_results: Maximum number of POIs to return
        category: Optional category filter
        
    Returns:
        List of POIWithDistance models with distance information
    """
    retriever = get_poi_retriever()
    location = Coordinates(latitude=latitude, longitude=longitude)
    return retriever.find_nearby_pois(location, radius_km, max_results, category)

def retrieve_nearby_pois_as_dict(latitude: float, longitude: float, 
                                radius_km: float = 2.0, max_results: int = 10, 
                                category: Optional[str] = None) -> List[Dict]:
    """
    Legacy function that returns POIs as dictionaries for backward compatibility.
    
    Args:
        latitude: Latitude of the search center
        longitude: Longitude of the search center  
        radius_km: Search radius in kilometers
        max_results: Maximum number of POIs to return
        category: Optional category filter
        
    Returns:
        List of POI dictionaries with distance information
    """
    pois = retrieve_nearby_pois(latitude, longitude, radius_km, max_results, category)
    return [poi.dict() for poi in pois]
"""
Unit tests for the deterministic tools in the src/tools/ directory.

These tests ensure that our data retrieval and processing functions work as
expected with controlled, mock data. They do not involve any LLM calls and
should run quickly.
"""

import pytest
from src.core.models import Coordinates
from src.tools import poi_retriever, transit_planner

# --- Fixture for Mock POI Data ---

@pytest.fixture
def mock_poi_data(tmp_path, monkeypatch):
    """
    Creates a temporary, controlled POI JSON file and patches the POIRetriever
    to use this file instead of the real data.
    """
    data_dir = tmp_path / "data"
    pois_dir = data_dir / "pois"
    pois_dir.mkdir(parents=True)
    
    mock_pois = {
        "metadata": {"schema_version": "1.0"},
        "pois": [
            {
                "poi_id": "riga_central_market",
                "title": "Riga Central Market",
                "coordinates": {"latitude": 56.9442, "longitude": 24.1148},
                "address": "Nēģu iela 7, Riga",
                "category": "Food & Drink",
                "description": "One of Europe's largest markets.",
                "narrative_hooks": {"history": "Housed in former Zeppelin hangars."},
                "media": {},
                "practical_info": {"type": "Indoor", "cost": "Free", "operating_hours": "07:00-18:00", "estimated_duration_minutes": 60}
            },
            {
                "poi_id": "latvian_academy_of_sciences",
                "title": "Latvian Academy of Sciences",
                "coordinates": {"latitude": 56.9448, "longitude": 24.1231},
                "address": "Akadēmijas laukums 1, Riga",
                "category": "Architecture",
                "description": "A Stalinist skyscraper with a viewing platform.",
                "narrative_hooks": {"fun_fact": "Known locally as 'Stalin's Birthday Cake'."},
                "media": {},
                "practical_info": {"type": "Indoor", "cost": "€", "operating_hours": "10:00-22:00", "estimated_duration_minutes": 30}
            }
        ]
    }
    
    poi_file = pois_dir / "poi-test-data.json"
    import json
    poi_file.write_text(json.dumps(mock_pois))  # Proper JSON serialization

    # Use monkeypatch to make the tool use our temporary directory
    monkeypatch.setattr(poi_retriever, "DATA_DIR", str(pois_dir))
    return poi_retriever.POIRetriever()

# --- Tests for POI Retriever ---

def test_poi_retriever_loading(mock_poi_data):
    """Tests if the POIRetriever loads the correct number of POIs."""
    assert len(mock_poi_data.pois) == 2
    assert mock_poi_data.pois[0].poi_id == "riga_central_market"

def test_find_nearby_pois(mock_poi_data):
    """Tests the core geospatial search functionality."""
    # Coordinates very close to the Central Market
    search_location = Coordinates(latitude=56.9443, longitude=24.1150)
    nearby_pois = mock_poi_data.find_nearby_pois(location=search_location, max_results=1)
    
    assert len(nearby_pois) == 1
    assert nearby_pois[0].poi_id == "riga_central_market"
    assert hasattr(nearby_pois[0], 'distance_km')

def test_get_poi_by_id(mock_poi_data):
    """Tests retrieving a POI by its unique ID."""
    poi = mock_poi_data.get_poi_by_id("latvian_academy_of_sciences")
    assert poi is not None
    assert poi.title == "Latvian Academy of Sciences"
    
    poi_none = mock_poi_data.get_poi_by_id("non_existent_id")
    assert poi_none is None

# --- Fixture for Mock GTFS Data ---

@pytest.fixture
def mock_gtfs_data(tmp_path, monkeypatch):
    """
    Creates temporary, minimal GTFS .txt files and patches the TransitPlanner
    to use them.
    """
    gtfs_dir = tmp_path / "gtfs"
    gtfs_dir.mkdir()

    # Create minimal but valid GTFS files as strings
    stops_txt = "stop_id,stop_name,stop_lat,stop_lon\nstop_A,Central Station,56.947,24.113\nstop_B,Market,56.944,24.115\nstop_C,University,56.950,24.105"
    routes_txt = "route_id,route_short_name,route_type\nroute_1,10,3" # Bus 10
    trips_txt = "route_id,service_id,trip_id,trip_headsign\ntrip_1,weekday,trip_1,University"
    stop_times_txt = "trip_id,arrival_time,departure_time,stop_id,stop_sequence\ntrip_1,10:00:00,10:00:00,stop_A,1\ntrip_1,10:05:00,10:05:00,stop_B,2\ntrip_1,10:10:00,10:10:00,stop_C,3"

    (gtfs_dir / "stops.txt").write_text(stops_txt)
    (gtfs_dir / "routes.txt").write_text(routes_txt)
    (gtfs_dir / "trips.txt").write_text(trips_txt)
    (gtfs_dir / "stop_times.txt").write_text(stop_times_txt)

    # Patch the transit_planner module to use this temp directory
    monkeypatch.setattr(transit_planner, "GTFS_DATA_DIR", str(gtfs_dir))
    return transit_planner.TransitPlanner()

# --- Tests for Transit Planner ---

def test_transit_planner_loading(mock_gtfs_data):
    """Tests if the TransitPlanner loads mock GTFS data correctly."""
    assert mock_gtfs_data.stops_df is not None
    assert mock_gtfs_data.timetable_df is not None
    assert len(mock_gtfs_data.stops_df) == 3

def test_plan_journey_direct_route_found(mock_gtfs_data):
    """Tests planning a valid, direct journey."""
    start_coords = Coordinates(latitude=56.947, longitude=24.113) # Central Station
    end_coords = Coordinates(latitude=56.950, longitude=24.105) # University
    plan = mock_gtfs_data.plan_journey(start_coords, end_coords, arrival_time_str="10:15")

    assert plan is not None
    assert len(plan) == 1
    leg = plan[0]
    assert leg.route_short_name == "10"
    assert leg.start_stop_name == "Central Station"
    assert leg.end_stop_name == "University"
    assert leg.arrival_time == "10:10"

def test_plan_journey_no_route_too_late(mock_gtfs_data):
    """Tests that no route is found if the desired arrival time is too early."""
    start_coords = Coordinates(latitude=56.947, longitude=24.113)
    end_coords = Coordinates(latitude=56.950, longitude=24.105)
    plan = mock_gtfs_data.plan_journey(start_coords, end_coords, arrival_time_str="09:00")
    
    assert plan is None

# --- Additional POI Retriever Tests for Complete Coverage ---

def test_find_nearby_pois_with_radius_filter(mock_poi_data):
    """Tests the radius filtering functionality."""
    # Test with very small radius - should find nothing
    search_location = Coordinates(latitude=56.9443, longitude=24.1150)
    nearby_pois = mock_poi_data.find_nearby_pois(location=search_location, radius_km=0.001)
    assert len(nearby_pois) == 0
    
    # Test with larger radius - should find both POIs
    nearby_pois = mock_poi_data.find_nearby_pois(location=search_location, radius_km=5.0)
    assert len(nearby_pois) == 2

def test_find_nearby_pois_with_category_filter(mock_poi_data):
    """Tests category filtering functionality."""
    search_location = Coordinates(latitude=56.9443, longitude=24.1150)
    
    # Filter by Food & Drink category
    food_pois = mock_poi_data.find_nearby_pois(
        location=search_location, 
        radius_km=5.0, 
        category="Food & Drink"
    )
    assert len(food_pois) == 1
    assert food_pois[0].category == "Food & Drink"
    
    # Filter by Architecture category
    arch_pois = mock_poi_data.find_nearby_pois(
        location=search_location, 
        radius_km=5.0, 
        category="Architecture"
    )
    assert len(arch_pois) == 1
    assert arch_pois[0].category == "Architecture"
    
    # Filter by non-existent category
    none_pois = mock_poi_data.find_nearby_pois(
        location=search_location, 
        radius_km=5.0, 
        category="NonExistent"
    )
    assert len(none_pois) == 0

def test_find_nearby_pois_max_results_limit(mock_poi_data):
    """Tests the max_results parameter."""
    search_location = Coordinates(latitude=56.9445, longitude=24.1190)
    
    # Should return only 1 result even though 2 are within radius
    nearby_pois = mock_poi_data.find_nearby_pois(
        location=search_location, 
        radius_km=5.0, 
        max_results=1
    )
    assert len(nearby_pois) == 1

def test_find_nearby_pois_distance_calculation(mock_poi_data):
    """Tests that distance is calculated correctly and POIs are sorted by distance."""
    search_location = Coordinates(latitude=56.9445, longitude=24.1190)
    nearby_pois = mock_poi_data.find_nearby_pois(location=search_location, radius_km=5.0)
    
    # Should have 2 POIs
    assert len(nearby_pois) == 2
    
    # Check that distance is calculated and included
    for poi in nearby_pois:
        assert hasattr(poi, 'distance_km')
        assert poi.distance_km > 0
    
    # Check that results are sorted by distance (closest first)
    if len(nearby_pois) > 1:
        assert nearby_pois[0].distance_km <= nearby_pois[1].distance_km

def test_get_pois_by_category(mock_poi_data):
    """Tests retrieving POIs by category."""
    food_pois = mock_poi_data.get_pois_by_category("Food & Drink")
    assert len(food_pois) == 1
    assert food_pois[0].poi_id == "riga_central_market"
    
    arch_pois = mock_poi_data.get_pois_by_category("Architecture")
    assert len(arch_pois) == 1
    assert arch_pois[0].poi_id == "latvian_academy_of_sciences"
    
    # Test case insensitive matching
    food_pois_lower = mock_poi_data.get_pois_by_category("food & drink")
    assert len(food_pois_lower) == 1

def test_get_pois_by_category_max_results(mock_poi_data):
    """Tests the max_results parameter for category search."""
    # This will only work meaningfully with more test data, but we can test the logic
    all_pois = mock_poi_data.get_pois_by_category("Food & Drink", max_results=10)
    limited_pois = mock_poi_data.get_pois_by_category("Food & Drink", max_results=1)
    
    assert len(limited_pois) <= len(all_pois)
    assert len(limited_pois) <= 1

# --- Tests for Module-Level Functions ---

def test_haversine_distance_function():
    """Tests the standalone haversine distance calculation function."""
    from src.tools.poi_retriever import haversine_distance
    
    # Test with known coordinates (approximately 1 km apart)
    coord1 = Coordinates(latitude=56.9443, longitude=24.1150)
    coord2 = Coordinates(latitude=56.9453, longitude=24.1160)
    
    distance = haversine_distance(coord1, coord2)
    assert distance > 0
    assert distance < 2.0  # Should be less than 2 km
    
    # Test with same coordinates
    distance_same = haversine_distance(coord1, coord1)
    assert distance_same == 0.0

def test_retrieve_nearby_pois_function(mock_poi_data, monkeypatch):
    """Tests the module-level retrieve_nearby_pois function."""
    from src.tools import poi_retriever
    
    # Mock the singleton instance
    monkeypatch.setattr(poi_retriever, "_poi_retriever_instance", mock_poi_data)
    
    # Test the function
    pois = poi_retriever.retrieve_nearby_pois(
        latitude=56.9443, 
        longitude=24.1150, 
        radius_km=5.0, 
        max_results=10
    )
    
    assert len(pois) == 2
    assert all(hasattr(poi, 'distance_km') for poi in pois)

def test_retrieve_nearby_pois_as_dict_function(mock_poi_data, monkeypatch):
    """Tests the dictionary-returning function."""
    from src.tools import poi_retriever
    
    # Mock the singleton instance
    monkeypatch.setattr(poi_retriever, "_poi_retriever_instance", mock_poi_data)
    
    # Test the function
    pois_dict = poi_retriever.retrieve_nearby_pois_as_dict(
        latitude=56.9443, 
        longitude=24.1150, 
        radius_km=5.0, 
        max_results=10
    )
    
    assert len(pois_dict) == 2
    assert all(isinstance(poi, dict) for poi in pois_dict)
    assert all('distance_km' in poi for poi in pois_dict)

# --- Additional Transit Planner Tests ---

def test_haversine_distance_transit_function():
    """Tests the haversine distance function in transit_planner module."""
    from src.tools.transit_planner import haversine_distance
    
    coord1 = Coordinates(latitude=56.947, longitude=24.113)
    coord2 = Coordinates(latitude=56.950, longitude=24.105)
    
    distance = haversine_distance(coord1, coord2)
    assert distance > 0
    assert distance < 1.0  # Should be less than 1 km for these coordinates

def test_find_nearest_stop(mock_gtfs_data):
    """Tests finding the nearest transit stop."""
    # Coordinates very close to Central Station
    location = Coordinates(latitude=56.947, longitude=24.113)
    nearest_stop = mock_gtfs_data._find_nearest_stop(location)
    
    assert nearest_stop is not None
    assert nearest_stop['stop_name'] == 'Central Station'
    assert 'distance_km' in nearest_stop

def test_find_nearest_stop_with_distance(mock_gtfs_data):
    """Tests finding nearest stop with distance calculation."""
    # Location slightly away from any stop
    location = Coordinates(latitude=56.948, longitude=24.114)
    nearest_stop = mock_gtfs_data._find_nearest_stop(location)
    
    assert nearest_stop is not None
    assert nearest_stop['distance_km'] > 0

def test_plan_journey_same_location(mock_gtfs_data):
    """Tests planning a journey with same start and end coordinates."""
    location = Coordinates(latitude=56.947, longitude=24.113)
    plan = mock_gtfs_data.plan_journey(location, location, arrival_time_str="10:15")
    
    # Should return None or empty plan for same location
    assert plan is None or len(plan) == 0

def test_plan_journey_no_stops_nearby(mock_gtfs_data):
    """Tests planning when no stops are near the coordinates."""
    # Very far coordinates
    far_start = Coordinates(latitude=50.0, longitude=20.0)
    far_end = Coordinates(latitude=50.1, longitude=20.1)
    
    plan = mock_gtfs_data.plan_journey(far_start, far_end, arrival_time_str="10:15")
    assert plan is None

def test_transit_planner_module_functions(mock_gtfs_data, monkeypatch):
    """Tests the module-level transit planning functions."""
    from src.tools import transit_planner
    
    # Mock the singleton instance
    monkeypatch.setattr(transit_planner, "_transit_planner_instance", mock_gtfs_data)
    
    # Test plan_transit_journey function
    journey = transit_planner.plan_transit_journey(
        start_latitude=56.947,
        start_longitude=24.113,
        end_latitude=56.950,
        end_longitude=24.105,
        arrival_time="10:15"
    )
    
    assert journey is not None
    assert len(journey) == 1
    assert journey[0].route_short_name == "10"

def test_plan_transit_journey_as_dict(mock_gtfs_data, monkeypatch):
    """Tests the dictionary-returning transit planning function."""
    from src.tools import transit_planner
    
    # Mock the singleton instance
    monkeypatch.setattr(transit_planner, "_transit_planner_instance", mock_gtfs_data)
    
    # Test the dictionary function
    journey_dict = transit_planner.plan_transit_journey_as_dict(
        start_latitude=56.947,
        start_longitude=24.113,
        end_latitude=56.950,
        end_longitude=24.105,
        arrival_time="10:15"
    )
    
    assert journey_dict is not None
    assert len(journey_dict) == 1
    assert isinstance(journey_dict[0], dict)
    assert journey_dict[0]['route_short_name'] == "10"

# --- Error Handling Tests ---

def test_poi_retriever_empty_directory(tmp_path, monkeypatch):
    """Tests POI retriever behavior with empty data directory."""
    empty_dir = tmp_path / "empty_pois"
    empty_dir.mkdir()
    
    monkeypatch.setattr(poi_retriever, "DATA_DIR", str(empty_dir))
    
    # Should create retriever with empty POI list
    retriever = poi_retriever.POIRetriever()
    assert len(retriever.pois) == 0

def test_poi_retriever_invalid_json(tmp_path, monkeypatch):
    """Tests POI retriever behavior with invalid JSON files."""
    invalid_dir = tmp_path / "invalid_pois"
    invalid_dir.mkdir()
    
    # Create invalid JSON file
    invalid_file = invalid_dir / "poi-invalid.json"
    invalid_file.write_text("This is not valid JSON")
    
    monkeypatch.setattr(poi_retriever, "DATA_DIR", str(invalid_dir))
    
    # Should handle gracefully and continue
    retriever = poi_retriever.POIRetriever()
    assert len(retriever.pois) == 0

def test_poi_retriever_missing_directory(monkeypatch):
    """Tests POI retriever behavior when data directory doesn't exist."""
    monkeypatch.setattr(poi_retriever, "DATA_DIR", "/nonexistent/directory")
    
    # Should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        poi_retriever.POIRetriever()

# --- Edge Case Tests ---

def test_empty_coordinates_handling():
    """Tests handling of edge case coordinates."""
    from src.tools.poi_retriever import haversine_distance
    
    # Test with zero coordinates
    zero_coord = Coordinates(latitude=0.0, longitude=0.0)
    other_coord = Coordinates(latitude=1.0, longitude=1.0)
    
    distance = haversine_distance(zero_coord, other_coord)
    assert distance > 0
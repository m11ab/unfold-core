# GTFS Data Directory

> **Data Source & Liability Disclaimer**
>
> The data in this directory is the official General Transit Feed Specification (GTFS) dataset provided by Rīgas Satiksme via the Latvian Open Data Portal. It represents a static snapshot of the public transport schedule for a specific period. As this data is not a real-time feed, it will not reflect unplanned disruptions, traffic delays, or service changes made after its publication date. The project maintainers are not responsible for the accuracy of the source data and disclaim all liability for damages arising from its use.

## Source Information

-   **Data Provider:** Rīgas Satiksme (Riga public transport)
-   **Official Dataset Page:** [Rīgas Satiksme Route Schedules](https://data.gov.lv/dati/lv/dataset/marsrutu-saraksti-rigas-satiksme-sabiedriskajam-transportam)
-   **Direct Download for June 2025:** [MarsrutuSaraksti06_2025.zip](https://data.gov.lv/dati/dataset/6d78358a-0095-4ce3-b119-6cde5d0ac54f/resource/5bda805a-bb3e-4327-8580-7a6954a1551d/download/marsrutusaraksti06_2025.zip)
-   **Format:** General Transit Feed Specification (GTFS)
-   **License:** Creative Commons CC0 1.0

## Files and Their Purpose

This directory contains the unzipped components of the GTFS feed:

-   `agency.txt`: Information about the transit agency (Rīgas Satiksme).
-   `routes.txt`: All public transport routes (bus, tram, trolleybus) in Riga.
-   `stops.txt`: All stops and stations, with their names and precise geographic coordinates.
-   `trips.txt`: Individual scheduled trips for each route (e.g., the 08:15 trip on Route 17).
-   `stop_times.txt`: The core timetable data: when each trip arrives at and departs from each stop.
-   `calendar.txt`: Defines the regular service schedules (e.g., which services run on weekdays vs. weekends).
-   `calendar_dates.txt`: Defines exceptions to the regular schedule (e.g., for holidays or special events).
-   `shapes.txt`: Geospatial shapes (polylines) that define the exact physical path of each route on the map.

## How This Data Is Used in unfold.quest

This static dataset is the foundation of our agent's journey planning capabilities.

-   **Scheduled Journey Planning:** The agent uses this data to calculate optimal public transport routes, find transfer points, and construct a complete, scheduled itinerary for a user's journey from A to B.
-   **Context for Micro-Quests:** By knowing the exact path (`shapes.txt`) and stop locations (`stops.txt`) of a planned transit leg, the agent can intelligently find and suggest relevant Points of Interest for the walking portions at the start and end of the trip.
-   **Time & Location Anchoring:** The scheduled times and stop locations provide the fixed anchors around which the agent builds the entire quest timeline.

## Usage Guidelines

-   **Schema Compliance:** All files follow the official GTFS specification. Refer to the [GTFS Reference](https://developers.google.com/transit/gtfs/reference) for details.
-   **Data Freshness:** This dataset is a monthly snapshot. For operational use, always check the official source for the latest version.
-   **Integration:** All programmatic interaction with this data should be handled by the tools in `/src/tools/transit_planner.py`, which encapsulate the logic for querying these files.

## Contribution & Updates

-   **DO NOT EDIT THESE FILES MANUALLY.**
-   To update the data, download the latest GTFS `.zip` archive from the official source, remove the old `.txt` files, and unzip the new archive in this directory.
-   It is best practice to validate the new data using a GTFS validation tool before committing it.
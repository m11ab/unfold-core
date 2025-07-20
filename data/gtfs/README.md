# GTFS Data Directory

> **Legal Disclosure & Liability Disclaimer**
>
> The GTFS data in this directory was collected from public sources and processed using generative AI tools. The information may contain inaccuracies, errors, or outdated content. It does not reflect the views of the project authors or design team. Users are solely responsible for verifying the accuracy and appropriateness of the data before use. The project maintainers disclaim all liability for damages arising from its use.

## Source

- **Dataset:** [MarsrutuSaraksti06_2025.zip](https://data.gov.lv/dati/dataset/6d78358a-0095-4ce3-b119-6cde5d0ac54f/resource/5bda805a-bb3e-4327-8580-7a6954a1551d/download/marsrutusaraksti06_2025.zip)
- **Provider:** Rīgas Satiksme (Riga public transport)
- **Format:** [General Transit Feed Specification (GTFS)](https://developers.google.com/transit/gtfs/reference)

## Files and Their Purpose

- `agency.txt` — Information about the transit agency.
- `routes.txt` — All public transport routes (bus, tram, trolleybus, etc.) in Riga.
- `stops.txt` — All stops and stations, with names and coordinates.
- `trips.txt` — Individual scheduled trips for each route.
- `stop_times.txt` — Timetables: when each trip stops at each stop.
- `calendar.txt` — Regular service schedules (which days each service runs).
- `calendar_dates.txt` — Exceptions to the regular schedule (holidays, special events).
- `shapes.txt` — Geospatial shapes (polylines) for the physical path of each route.

## How This Data Is Used in unfold.quest

- **Journey Planning:** The agent uses GTFS data to generate public transport routes, schedules, and transfer options for user journeys.
- **Contextual Micro-Quests:** By combining GTFS with POI data, the app can suggest interesting stops or detours along a user’s route.
- **Time & Location Awareness:** Accurate stop locations and schedules enable the agent to provide real-time, context-aware suggestions.

## Usage Guidelines

- **Schema Compliance:** All files follow the official GTFS specification. See the [GTFS Reference](https://developers.google.com/transit/gtfs/reference) for details.
- **Data Freshness:** This dataset reflects the schedule as of June 2025. For up-to-date information, always check the latest data from the provider.
- **Integration:** Use the provided tools in `src/tools/transit_planner.py` to query and process GTFS data for the agent.

## Contribution & Updates

- Do not edit these files manually. To update, download the latest GTFS feed from the official source and replace the files.
- Validate the data using GTFS validation tools before use.

---

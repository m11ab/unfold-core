# Data Management Strategy for unfold.quest

-   **Status:** Adopted
-   **Date:** 2025-07-16
-   **Owner:** Project Lead

## 1. Guiding Principles

Our approach to data management is guided by three core principles:

1.  **Start Simple, Scale Gracefully:** For the initial prototype, we will prioritize simplicity and speed of development. Our data structures and storage methods will be chosen for ease of use, with a clear and documented path for scaling to a more robust, production-grade system.
2.  **Structure for Creativity:** All data will be structured not just for retrieval, but to provide maximum creative fodder for our AI agent. This means using rich, nested objects (`narrative_hooks`, `practical_info`) instead of flat, monolithic text blobs.
3.  **Quality Over Quantity:** A small dataset of high-quality, verified, and genuinely interesting points is more valuable than a large dataset of low-quality, auto-generated points. Our processes will always prioritize data quality and verification.

## 2. Data Classes & Schemas

We have defined three primary classes of data that power the `unfold.quest` experience. The JSON schemas below serve as the definitive structure for our data.

### 2.1. `POI (Point of Interest)` - **IN SCOPE FOR PROTOTYPE**

A static, physical location with unique attributes. This is the foundational data class for the prototype.
*Examples: A statue, a historic building, a specific piece of street art, a park.*

**JSON Schema:**
```json
{
  "poi_id": "string",
  "title": "string",
  "coordinates": {
    "latitude": "float",
    "longitude": "float"
  },
  "address": "string",
  "category": "enum" /* E.g., Art, History, Architecture, Nature, Food & Drink, Hidden Gem */,
  "description": "string",
  "narrative_hooks": {
    "history": "string | null",
    "fun_fact": "string | null",
    "architectural_detail": "string | null"
  },
  "media": {
    "image_url": "string | null",
    "attribution_text": "string | null"
  },
  "practical_info": {
    "type": "enum" /* E.g., Outdoor, Indoor */,
    "cost": "string" /* E.g., Free, €, €€, €€€ */,
    "operating_hours": "string" /* E.g., 24/7, Mo-Fr 09:00-17:00 */,
    "estimated_duration_minutes": "integer"
  }
}
```

### 2.2. `Ephemeral Event` - **OUT OF SCOPE FOR PROTOTYPE**

A time-bound occurrence at a specific location.
*Examples: A weekend farmers' market, a street music festival, a temporary art installation.*

**JSON Schema:**
```json
{
  "event_id": "string",
  "poi_id": "string | null" /* Foreign key if the event is at a known POI */,
  "title": "string",
  "coordinates": {
    "latitude": "float",
    "longitude": "float"
  },
  "address": "string",
  "category": "enum" /* E.g., Market, Music, Festival, Art */,
  "description": "string",
  "narrative_hooks": {
    "context": "string | null" /* E.g., 'Part of the annual Riga Light Festival' */
  },
  "media": {
    "image_url": "string | null",
    "attribution_text": "string | null"
  },
  "practical_info": {
    "cost": "string",
    "start_datetime": "string" /* ISO 8601 Format */,
    "end_datetime": "string" /* ISO 8601 Format */,
    "event_url": "string | null"
  }
}
```

### 2.3. `Experiential Route` - **OUT OF SCOPE FOR PROTOTYPE**

A defined path where the journey itself is the main point of interest.
*Examples: A street renowned for its architecture, a scenic riverfront promenade, a "graffiti alley."*

**JSON Schema:**
```json
{
  "route_id": "string",
  "title": "string",
  "description": "string",
  "category": "enum" /* E.g., Scenic, Architectural, Historical */,
  "path": {
    "type": "LineString",
    "coordinates": [
      ["float", "float"], /* [longitude, latitude] */
      ["float", "float"],
      ...
    ]
  },
  "practical_info": {
    "estimated_duration_minutes": "integer",
    "total_distance_meters": "integer"
  }
}
```

## 3. Data Lifecycle Management (CRUD)

This section details our strategy for Collecting, Storing, Retrieving, Updating, and Deleting our data.

### 3.1. Collection

**Prototype Phase:**
-   **Methodology:** Manual, research-driven collection, followed by cross-validation.
-   **Scope:** A curated "golden dataset" of 50-100 POIs for a limited pilot area.

**Production Phase (Roadmap):**
-   **Methodology:** A **three-tier hybrid pipeline**: Tier 1 (Authoritative APIs), Tier 2 (AI Discovery), and Tier 3 (Community Input).

### 3.2. Storage

**Prototype Phase:**
-   **Format:** A single `JSON` file (`data/pois/riga_pois.json`) containing a list of `POI` objects.
-   **Rationale:** Simplicity, zero setup overhead, and human-readability.

**Production Phase (Roadmap):**
-   **Database:** A cloud-native **NoSQL document database** (e.g., MongoDB, Firestore) and a dedicated **vector database** (e.g., Qdrant).

### 3.3. Retrieval

**Prototype Phase:**
-   **Methodology:** In-memory geospatial query within the `poi_retriever.py` tool.
-   **Rationale:** Extremely fast for a small dataset, no database dependency.

**Production Phase (Roadmap):**
-   **Methodology:** A combination of geospatial queries against the NoSQL database and vector similarity searches against the vector database.

### 3.4. Updating & Deleting (Maintenance)

**Prototype Phase:**
-   **Process:** Manual edits to the `riga_pois.json` file, committed to Git.

**Production Phase (Roadmap):**
-   **Process:** A hybrid model of automated updates from APIs, a human curation interface, and community flagging for review.

## 4. Governance, Security, and Versioning

Beyond the basic lifecycle, the following cross-cutting concerns are critical to our data strategy.

### 4.1. Data Governance

-   **Schema Management:** Any proposed changes to the data schemas defined in Section 2 must be documented in an Architecture Decision Record (ADR) and approved by the project lead. This prevents schema drift and ensures consistency.
-   **Data Quality Ownership:** The project lead is the ultimate owner of data quality. In the production phase, a dedicated curation team will be responsible for reviewing flagged content and maintaining the quality standards of the POI database.

### 4.2. Data Security & Privacy

-   **Public Data:** The POI, Event, and Route data we collect is considered public information. There are no special security requirements for this data at rest.
-   **User Data (Production Phase):** The system will eventually collect user-generated data (e.g., feedback, flagged content, created quests) and usage data (e.g., location history). This data will be treated as **highly sensitive Personally Identifiable Information (PII)**.
-   **Privacy Policy:** A comprehensive privacy policy will be developed before any user data is collected.
-   **Anonymization:** All analytics and model training will be performed on fully anonymized and aggregated data to protect user privacy. We will **never** store raw, identifiable location history logs long-term.

### 4.3. Data Versioning

-   **Prototype Phase:** The `riga_pois.json` file will be versioned directly in our Git repository. This provides a full history of changes and allows for easy rollbacks. We may consider using Git LFS (Large File Storage) if the data files become too large.
-   **Production Phase (Roadmap):** A database versioning or snapshotting strategy will be implemented. This ensures that we can roll back the entire dataset in case of a catastrophic data corruption event. A history of changes for each POI document will be maintained to track its evolution over time.

## 5. Strategic Implications

This comprehensive strategy ensures that we can start lean and fast for our prototype while having a clear, scalable, and quality-focused plan for building a world-class data platform. By defining our governance and security principles from day one, we build a foundation of trust and reliability that will be critical for long-term success and community adoption.
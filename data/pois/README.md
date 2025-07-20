# Points of Interest (POIs) Data Directory

> **Legal Disclosure & Liability Disclaimer**
>
> The information and data presented in this directory have been collected and/or synthesized using generative AI tools (including, but not limited to, Perplexity and Gemini) from publicly available internet sources. As such, the content may contain inaccuracies, errors, or outdated information. The data does not reflect the views or opinions of the project authors, contributors, or design team. All users are solely responsible for verifying the accuracy, legality, and appropriateness of any information before relying on it or using it in any context. The authors, contributors, and maintainers of this project expressly disclaim any and all liability for damages or losses arising from the use or misuse of the information contained herein. Use at your own risk.

This folder contains curated, high-quality JSON datasets of hyper-local Points of Interest (POIs) for the unfold.quest prototype. Each file represents a specific district or thematic area in Riga, Latvia, and is structured to maximize both creative narrative potential and data integrity.

## Folder Contents

- `poi-agenskalns-01.json`, `poi-agenskalns-02.json`: POIs in Āgenskalns, focusing on historic wooden architecture and the market.
- `poi-kengarags.json`: POIs in Ķengarags, highlighting public art and community spaces.
- `poi-maskavas.json`: POIs in Maskavas Forštate, focusing on Jewish heritage and historical sites.
- `poi-mezaparks-01.json`, `poi-mezaparks-02.json`: POIs in Mežaparks, including the Grand Bandstand and cultural landmarks.
- `poi-osta.json`: POIs in Pētersala-Andrejsala, featuring transformative industrial and cultural sites.
- `poi-purvciems.json`: POIs in Purvciems, with a focus on Soviet-era public art and urban planning.
- `poi-vecriga-centrs-01.json`, `poi-vecriga-centrs-02.json`: POIs in Vecrīga (Old Town) and Centrs, covering hidden courtyards and Art Nouveau architecture.
- `poi-vef.json`: POIs in the VEF district, documenting industrial heritage.

Each file contains:
- A `metadata` block describing the source, schema version, and creation date.
- A `pois` array, where each object is a POI with rich narrative and practical fields.

## Data Structure

POI entries follow a strict schema (see `/docs/concept/data-management-strategy.md`):

```json
{
  "poi_id": "string",
  "title": "string",
  "coordinates": { "latitude": "float", "longitude": "float" },
  "address": "string",
  "category": "enum",
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
    "type": "enum",
    "cost": "string",
    "operating_hours": "string",
    "estimated_duration_minutes": "integer"
  }
}
```

## Data Handling Guidelines

- **Quality First:** Only include POIs that are well-researched, verified, and offer genuine narrative or experiential value.
- **Schema Compliance:** All entries must strictly follow the schema above. Use nulls for unavailable fields, never omit required keys.
- **Rich Narrative:** Populate `narrative_hooks` to provide context, fun facts, and architectural or cultural details for each POI.
- **Versioning:** Update the `schema_version` in `metadata` if the schema changes.
- **Provenance:** Always fill out the `source_document_title` and `created_at` fields in `metadata`.
- **No Sensitive Data:** Do not include personal or sensitive information.

## Contribution Workflow

1. Draft new or updated POI files in a separate branch.
2. Validate JSON structure (use a linter or schema validator).
3. Ensure narrative quality and factual accuracy.
4. Submit a pull request for review.

## Purpose

These datasets power the AI agent’s ability to generate engaging, context-aware micro-quests for users, transforming routine journeys into meaningful adventures—see the main project [README](../../README.md) and [project vision](../../docs/concept/project_vision.md) for more.

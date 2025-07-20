# ADR-002: Pivot to Static GTFS for Transit Data

-   **Status:** Accepted
-   **Date:** 2025-07-18
-   **Deciders:** Maksim Ilin

## Context and Problem Statement

The initial vision for "unfold.quest" included real-time public transport guidance. This would involve features like live vehicle tracking, delay notifications, and dynamic re-routing based on current traffic conditions. The successful implementation of such features is entirely dependent on the availability of a reliable, public, real-time transit data feed, typically in the GTFS-RT (Realtime) format.

Our deep research phase, specifically the findings documented in `docs/research/01-riga-data-ecosystem.md`, revealed a critical technical constraint: The pilot city's transit authority, Rīgas Satiksme, does not provide an official, public GTFS-RT feed. While static GTFS schedule data is available and updated monthly, there is no sanctioned method for accessing live vehicle positions or service alerts.

This presents a direct conflict with our initial technical assumptions. We must decide how to source our transit data, as this choice will fundamentally impact the application's core functionality, reliability, and development scope.

## Considered Alternatives

### 1. Develop a Web Scraper for Unofficial Real-Time Data

-   **Description:** Some third-party websites and community projects provide quasi-real-time data by scraping Rīgas Satiksme's internal-facing systems. We could build our own scraper to power our real-time features.
-   **Reasons for Rejection:**
    -   **High Brittleness:** Scrapers are notoriously fragile. Any change to the source website's HTML structure or internal API would break our application, requiring constant, reactive maintenance.
    -   **Ethical and Legal Ambiguity:** Scraping may violate the terms of service of the source website and puts the project in a legally gray area.
    -   **Unreliability:** The scraped data would have no service-level agreement (SLA). It could be inaccurate, latent, or become unavailable at any time without notice.
    -   **High Development Cost:** Building and maintaining a robust scraper would consume a significant portion of our one-week prototype sprint, distracting from our core innovation areas.

### 2. De-scope Transit Features Entirely

-   **Description:** We could remove the public transport component and build a walking-only "Serendipity Walker" application.
-   **Reasons for Rejection:**
    -   **Reduces Core Value Proposition:** This would abandon our core synthesized concept of blending transit and walking. The project's scope and potential impact would be drastically reduced.
    -   **Lower Sustainability Impact:** A walking-only app has a much smaller potential to influence modal shift and reduce carbon emissions compared to one that actively promotes public transport.

## Decision

We have decided to **pivot the core concept from a "real-time transit tracker" to a "pre-journey intelligent planner."** Our application will exclusively use the **official, static GTFS data feed** provided by `data.gov.lv` as the single source of truth for all public transport routing.

This means we will not attempt to provide live vehicle tracking or real-time delay information in the prototype. The agent's transit plans will be based on the published schedules.

## Consequences

### Positive Consequences

-   **Increased Reliability & Robustness:** By relying solely on an official, structured data source, our prototype's core functionality will be exceptionally stable and predictable. We avoid the entire class of errors associated with fragile data scraping.
-   **Reduced Development Scope:** This decision removes a complex, high-maintenance component from our one-week sprint, allowing us to focus our limited time and resources on the truly novel aspects of our project: the Context & Intent Engine, the LangGraph workflow, and the narrative synthesis.
-   **Clearer User Experience:** The application now has a well-defined purpose as a *planning* tool. This manages user expectations effectively. The user understands that "unfold.quest" helps them architect an amazing journey *before* they leave the house.
-   **Demonstrates Mature Planning:** Acknowledging data limitations and designing a robust system around them is a sign of mature engineering and research methodology, which will be a strength in our competition submission.

### Negative Consequences

-   **No Real-Time Information:** The most significant consequence is that our application cannot account for real-world transit disruptions, such as traffic delays, vehicle breakdowns, or route cancellations. The plan our agent provides is based on the ideal schedule.
-   **Potential for Data Staleness:** Since the GTFS feed is updated monthly, there may be minor inaccuracies in the schedule towards the end of a given month before the next update is released.
-   **Reduced "In-the-Moment" Utility:** The app is less useful for a user who is already mid-journey and needs immediate, real-time guidance. Its primary utility is in the planning phase.

## References

-   `docs/research/01-riga-data-ecosystem.md` - The research report that identified the lack of a GTFS-RT feed.
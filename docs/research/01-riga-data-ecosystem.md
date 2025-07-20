# Research Finding 01: Riga Data Ecosystem Analysis

-   **Status:** Completed
-   **Date:** 2025-07-17
-   **Key Question:** What is the availability, quality, and accessibility of public transport and payment/ticketing data for Riga, Latvia, and what is the technical feasibility of using it for a real-time consumer mobility application?

## Executive Summary (TL;DR)

The public data infrastructure in Riga presents a significant technical constraint that dictates our application's core functionality.

1.  **Public Transport Data:** Rīgas Satiksme provides high-quality **static GTFS schedule data** with a permissive license, making it excellent for **scheduled journey planning**. However, there is **no official public GTFS-RT (Realtime) feed**. This makes building reliable real-time features like live vehicle tracking or delay notifications technically infeasible for a prototype without resorting to high-risk, unofficial methods.
2.  **Payment & Ticketing:** The dominant mobile payment platform, **Mobilly, operates as a closed ecosystem**. There are no public developer APIs for third-party consumer applications to initiate payments or integrate ticketing. Access is restricted to formal B2B merchant partnerships.

**Verdict:** The Riga data ecosystem is **highly suitable for a pre-journey intelligent planner** but **unsuitable for a real-time transit assistant** with integrated ticketing. This finding is the basis for ADR-002, which pivots our project's focus accordingly.

---

## 1. Rīgas Satiksme (Public Transport Data)

### 1.1. Static Data (GTFS) - ✅ Available and Suitable

This is the data feed containing all scheduled routes, stops, stop times, and paths for Riga's public transport network.

-   **Format:** Standard GTFS `.txt` format, compliant with the Google specification.
-   **Content:** Covers the entire network, including 6 tram lines, 22 trolleybus routes, and 52 bus routes.
-   **Source:** Published officially on Latvia's Open Data Portal.
    -   **Primary Reference:** [LV Open Data Portal - Rīgas Satiksme Datasets](https://data.gov.lv/dati/lv/dataset?tags=Mar%C5%A1ruti)
-   **Update Frequency:** Updated once per month. While not real-time, this is sufficient for scheduled planning.
-   **License:** **CC0 1.0 (Creative Commons)**. This is a permissive license that allows for unrestricted reuse, including for commercial purposes, without attribution.
-   **Quality:** The data is consistent and well-structured, making it reliable for our use case.

**Conclusion:** The static GTFS feed is our foundational dataset. It is reliable, official, and provides everything needed to build a robust journey planner tool (`src/tools/transit_planner.py`).

### 1.2. Real-Time Data (GTFS-RT) - ❌ Not Available

This is the data feed that would provide live vehicle positions, trip updates (delays), and service alerts.

-   **Official Availability:** **There is no official, public GTFS-RT feed provided by Rīgas Satiksme.** Our research found no documentation or endpoints for such a service.
-   **Existing "Real-Time" Systems:** Rīgas Satiksme's own solutions rely on proprietary systems, such as QR codes at bus stops that link to a web page showing upcoming departures for that specific stop. This is not a scalable or accessible method for a third-party application.
    -   **Primary Reference:** [Rīgas Satiksme - Real-time Information Announcement](https://www.rigassatiksme.lv/en/current%20information/real-time-information-on-riga-s-public-transport-schedule-is-available-on-the-rigas-satiksme-website/)
-   **Unofficial Alternatives:** We identified community-developed projects that attempt to provide real-time data by "scraping" information from Rīgas Satiksme's non-public systems.
    -   **Example Reference:** [GitHub - jmalinens/rigas-satiksme-api](https://github.com/jmalinens/rigas-satiksme-api) (An unofficial PHP API wrapper).
-   **Viability of Unofficial Methods:** We have explicitly decided against using these methods due to:
    -   **High Brittleness:** They are prone to breaking without notice.
    -   **Unreliability:** There are no guarantees of data accuracy or uptime.
    -   **Legal/Ethical Concerns:** Scraping may violate terms of service.

**Conclusion:** We cannot build reliable real-time features. This directly leads to the decision in **ADR-002** to focus on pre-journey planning.

## 2. Mobilly (Payment & Ticketing)

### 2.1. Ecosystem Analysis

Mobilly is the de facto standard for mobile payments in Riga, covering parking, transit tickets, event entry, and more. It operates as a licensed electronic money institution.

-   **Primary Reference:** [Mobilly Website](https://mobilly.lv/en/)

### 2.2. Developer API & Integration - ❌ Not Available

Our investigation sought a developer portal or API documentation that would allow `unfold.quest` to either initiate a ticket purchase on behalf of the user or deep-link into the Mobilly app in a structured way.

-   **API Availability:** **No public-facing developer portal or consumer-app-focused API exists.** Mobilly's API access is exclusively for vetted business partners.
-   **Integration Model:** Mobilly operates on a **B2B merchant partnership model**. Integration requires a formal written agreement, a compliance process, and direct business engagement. It is not a self-service platform for developers.
    -   **Primary Reference:** [Mobilly Payment Service Contract Regulations (PDF)](https://mobilly.lv/wp-content/uploads/2018/10/Mobilly_regulation-of-the-payment-service-contract_01.02.2023-en_gb-1.pdf)
    -   **Primary Reference:** [Mobilly Merchant Account Rules (PDF)](https://mobilly.lv/wp-content/uploads/2023/03/AppendixNr.1_ENKAA_noteikumi_Tirgotajam_01.11.2022_V3_ENG.pdf)
-   **Technical Barriers:** Due to its status as a financial institution, access to its systems is tightly controlled to comply with regulations and protect user data.

**Conclusion:** Direct integration for ticketing or payments is **not feasible** for our prototype. The platform operates as a "walled garden," accessible only to official merchants.

## 3. Strategic Implications for `unfold.quest`

This research provides clear and unavoidable technical constraints that directly shape our project's scope and value proposition.

1.  **Core Functionality:** The application must be designed as a **pre-journey intelligent planner**. Its strength will come from the quality of its plans and the richness of the experience it designs, not from real-time operational guidance.
2.  **Ticketing:** Payment and ticketing features are **out of scope** for the prototype. In the app's user flow, after presenting the quest, we will simply instruct the user to purchase their ticket using their preferred method (e.g., Mobilly, e-talons).
3.  **Focus Shift:** These constraints are beneficial for the prototype. They allow us to divert all our development resources away from brittle data integration challenges and focus them on our core innovations: the AI-driven **Context & Intent Engine**, the **LangGraph workflow**, and the **narrative synthesis** that makes our user experience unique.
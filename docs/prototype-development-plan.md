
### **Project Development Plan: `unfold.quest` Prototype Sprint**

-   **Document Status:** Adopted
-   **Date:** 2025-07-18
-   **Owner:** Project Team
-   **Sprint Duration:** One Week

### **1. Project Context & Objectives**

This document outlines the development plan for creating a functional prototype of **`unfold.quest`**, an AI-powered personal mobility companion. The primary objective of this one-week sprint is to produce a high-quality, demonstrable proof-of-concept for submission to the **European Universities Competition on Artificial Intelligence**.

The prototype will serve as a "vertical slice" of the full application vision, focusing on proving the viability of the core user experience: transforming a standard A-to-B journey in Riga into an engaging, AI-generated "micro-quest."

### **2. Work Completed (Pre-Sprint Phase)**

The project has successfully completed a rigorous planning and research phase. All foundational assets required for development are now in place and documented within the project repository.

-   **Conceptual Foundation:** A comprehensive `project_vision.md` has been established.
-   **Technical Architecture:** Key architectural decisions, such as the use of **LangGraph** (`ADR-001`) and the strategic pivot to **static GTFS data** (`ADR-002`), have been documented.
-   **Data Strategy:** A complete `data-management-strategy.md` has been created, defining our data schemas and lifecycle.
-   **Data Acquisition:**
    -   The official static **GTFS data** for Rīgas Satiksme has been acquired and stored in `data/gtfs/`.
    -   A high-quality, curated **"golden dataset" of POIs** for key Riga districts has been researched and stored in `data/pois/`.
-   **Project Scaffolding:** The full project repository structure, including documentation, has been created and version-controlled in Git.

### **3. Planned Work (The One-Week Sprint)**

The sprint is structured as a four-stage, "inside-out" development process designed to build upon a tested foundation at each step.

#### **Stage 1: Foundation - Defining Data Structures (Day 1)**

-   **Objective:** To create the validated data models that will serve as the common language for the entire application.
-   **File:** `src/core/models.py`
-   **Tasks:**
    1.  Implement Pydantic models for `POI`, `TransitLeg`, `WalkingLeg`, and the composite `Quest`.
    2.  Ensure models include necessary data validation (e.g., coordinate formats, enums for categories).

#### **Stage 2: Building Blocks - Implementing Deterministic Tools (Day 2)**

-   **Objective:** To build the reliable, non-AI "calculators" that provide the agent with its core data.
-   **Files:** `src/tools/poi_retriever.py`, `src/tools/transit_planner.py`, `tests/test_tools.py`
-   **Tasks:**
    1.  Implement the `find_nearest_pois` function to query the curated POI JSON files.
    2.  Implement the `plan_journey` function to query the static GTFS data files.
    3.  Write and pass unit tests for both tools to verify their correctness with known inputs.

#### **Stage 3: The Brain - Assembling the Agentic Workflow (Day 3)**

-   **Objective:** To construct the LangGraph-based agent that orchestrates the tools and logic.
-   **Files:** `src/agent/state.py`, `src/agent/graph.py`
-   **Tasks:**
    1.  Define the `AgentState` TypedDict/Pydantic model.
    2.  Implement the graph nodes, including the `Context & Intent Engine` logic.
    3.  Wire the nodes and tools together into a compiled LangGraph agent.

#### **Stage 4: The Interface - Connecting to the User (Day 4)**

-   **Objective:** To build the user-facing interface and connect the full end-to-end flow.
-   **File:** `app.py`
-   **Tasks:**
    1.  Engineer the final prompt for the `synthesize_experience` node.
    2.  Develop a simple Gradio web UI with input and output components.
    3.  Integrate the compiled agent with the Gradio backend, ensuring a smooth user experience.

#### **Final Phase: Polish & Documentation (Day 5)**

-   **Objective:** To refine the prototype and prepare all submission materials.
-   **Tasks:**
    1.  Refine UI, add comments to code, and finalize documentation (`ADRs`, `READMEs`).
    2.  Record a high-quality video/GIF demonstration of the prototype.
    3.  Draft the 3,000-word competition proposal based on our completed documentation.

### **4. Development Approach & Methodology**

Our approach combines principles of **agile development**, **rigorous documentation**, and **continuous integration**.

-   **Agile Sprint:** The one-week plan is a time-boxed sprint with clear daily objectives. This ensures focus and momentum.
-   **Inside-Out Development:** We build the most fundamental components first (data models, tools) before assembling them into more complex systems (the agent). This is a low-risk, highly robust approach.
-   **Test-Driven Mentality:** We will write tests for our core, deterministic components (the tools) before relying on them in the more complex agent. This prevents cascading failures and simplifies debugging.
-   **Single Source of Truth:** The `docs/` directory will be treated as the single source of truth for all conceptual and architectural decisions. Any deviation from the plan must be justified with an update to the relevant document.
-   **Version Control:** All code, data, and documentation will be committed to our Git repository daily, providing a full history of the project's evolution.
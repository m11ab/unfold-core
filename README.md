# unfold.quest

> **Legal Disclosure & Liability Disclaimer**
>
> The information and data presented in this project have been collected and/or synthesized using generative AI tools (including, but not limited to, Perplexity and Gemini) from publicly available internet sources. As such, the content may contain inaccuracies, errors, or outdated information. The data does not reflect the views or opinions of the project authors, contributors, or design team. All users are solely responsible for verifying the accuracy, legality, and appropriateness of any information before relying on it or using it in any context. The authors, contributors, and maintainers of this project expressly disclaim any and all liability for damages or losses arising from the use or misuse of the information contained herein. Use at your own risk.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status](https://img.shields.io/badge/Status-Prototype-blue.svg)](https://github.com/m11ab/unfold-core)
[![Competition](https://img.shields.io/badge/Competition-EU_AI_Challenge-9cf.svg)](https://www.haw-hamburg.de/en/ftz-nk/programmes-and-networks/european-universities-competition-on-artificial-intelligence/)

An AI-powered personal mobility companion that transforms routine urban travel into a continuous, gamified journey of discovery.

---

## 1. Project Context & Vision

**unfold.quest** is an AI research prototype initially developed for the **[European Universities Competition on Artificial Intelligence](https://www.haw-hamburg.de/en/ftz-nk/programmes-and-networks/european-universities-competition-on-artificial-intelligence/)**, with a focus on Sustainable Development.

Our vision is to re-enchant the urban environment by making sustainable mobility (public transport and walking) the most engaging and rewarding choice. We are building a **Personal Adventure Architect**—an AI agent that intelligently blends efficient journey planning with curated, serendipitous "micro-quests," turning every trip into a unique story.

**Pilot City: Riga, Latvia**

Riga has been chosen as the initial testbed due to its comprehensive static public transport data (GTFS), its rich cultural and historical fabric, and its dynamic, four-season environment, which provides a perfect challenge for our context-aware AI agent.

**This is a Prototype**

This repository contains the initial proof-of-concept. The concept is designed to be highly iterative and will evolve significantly based on feedback from the research community, local urban communities, and potential users. Our goal is to build *with* the community, not just *for* it.

## 2. The Core Concept

The agent solves the "monotony of the commute" by transforming a standard A-to-B journey plan into a multi-part quest. It achieves this through:

-   **Context & Intent Engine:** An initial step to determine if the user is in "Efficiency Mode" or "Discovery Mode," ensuring our suggestions are helpful, not intrusive.
-   **Intelligent Quest Design:** The agent uses a toolset to combine scheduled public transport routes with novel walking paths featuring hyper-local points of interest (e.g., street art, historical landmarks, pop-up events).
-   **Narrative Synthesis:** The final output is not a list of directions but a cohesive, narrative-driven quest that gives purpose and delight to the entire door-to-door journey.

## 3. Technology Stack

This project leverages a modern, robust, and observable technology stack, designed for building stateful AI agentic workflows.

-   **Agent Framework:** **LangGraph** (Python) for building reliable, stateful, and debuggable agent graphs.
-   **LLM Engine:** **Gemini / Mistral** (via API) for core reasoning and narrative synthesis.
-   **Vector Store:** **ChromaDB** for local development, with a clear path to a cloud-native solution like **Qdrant**.
-   **Data Formats:** **Parquet** & **JSON** for efficient storage of curated datasets (POIs, GTFS).
-   **UI / Demo:** **Gradio** for rapid, interactive web-based prototyping.
-   **Observability:** **LangSmith** or **Arize Phoenix** for tracing, debugging, and evaluating agent performance.

## 4. Project Structure

This repository is structured to be clear for both human developers and LLM-powered assistants. The architecture separates data, application logic, agent definition, and tools into distinct modules.

```

unfold-core/
│
├── .env.example             # Template for environment variables (API keys, etc.)
├── app.py                   # Main entry point for the Gradio web application.
├── requirements.txt         # Python package dependencies.
├── README.md                # You are here.
├── LICENSE                  # The full text of the Apache 2.0 License.
│
├── data/
│   ├── gtfs/                # Contains the static GTFS data for Riga's public transport.
│   └── pois/                # Contains curated, hyper-local Points of Interest (POIs) for the prototype.
│
├── docs/
│   ├── adr/                 # Architecture Decision Records (ADRs) explaining key technical choices.
│   │   ├── 001-choice-of-langgraph.md
│   │   └── 002-pivot-to-static-gtfs.md
│   ├── concept/             # High-level project vision and conceptual documents.
│   │   └── project_vision.md
│   └── research/            # Reports and findings from our initial deep research phase.
│       ├── 01-riga-data-ecosystem.md
│       └── 02-hci-patterns.md
│
├── notebooks/
│   ├── 01_data_exploration.ipynb  # Initial exploration of GTFS and POI data.
│   └── 02_agent_prototyping.ipynb # Prototyping and testing agent chains and tools.
│
├── src/
│   ├── __init__.py
│   ├── agent/               # Core agent logic and LangGraph graph definition.
│   │   ├── graph.py         # Defines the nodes, edges, and state of the main agent workflow.
│   │   └── state.py         # Pydantic models defining the agent's state object.
│   │
│   ├── tools/               # Implementation of the custom tools the agent can use.
│   │   ├── transit_planner.py # Tool for querying the static GTFS data.
│   │   ├── poi_retriever.py   # Tool for retrieving points of interest from the /data directory.
│   │   └── ...              # Other tools as developed.
│   │
│   └── core/                # Core application logic, shared utilities, and data models.
│       └── models.py        # Pydantic models for data structures (e.g., Quest, POI).
│
└── tests/
    ├── test_tools.py        # Unit tests for the agent's tools.
    └── test_agent.py        # Integration tests for the agent workflow.

```

## 5. Getting Started

Follow these steps to set up and run the prototype locally.

### Prerequisites

-   Python 3.10+
-   An API key for your chosen LLM provider (e.g., Google AI Studio, Mistral AI).

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/m11ab/unfold-core.git
    cd unfold-core
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    -   Copy the example file: `cp .env.example .env`
    -   Edit the `.env` file and add your `LLM_API_KEY`.

### Running the Prototype

Launch the Gradio web application with the following command:

```bash
python app.py
```

Open your web browser and navigate to the local URL provided (usually `http://127.0.0.1:7860`).

## 6. Roadmap & Future Development

This prototype is the first step in a larger research journey. Our roadmap is focused on evolving this concept into a robust, scalable, and socially integrated platform.

-   **Phase 2: The Scalable Content Pipeline:** Implement the three-tier hybrid system (API ingestion, AI social media mining, and community validation) to automate the discovery of hyper-local POIs.
-   **Phase 3: The Social Layer:** Introduce the "Crews" system, allowing users to form neighborhood-based teams to collaboratively explore and map their districts.
-   **Phase 4: The Endless Game:** Implement procedurally generated "Route Bounties" and a "Pathfinder" system that empowers users to create their own challenges, ensuring long-term engagement.

## 7. Contributing

We welcome collaboration and feedback from all corners. This project thrives on interdisciplinary input. If you are interested in contributing, please start by opening an issue on GitHub to discuss your ideas, suggest features, or report bugs.

When you are ready to contribute code, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a Pull Request for review.

## 8. License

This project's core functionality is licensed under the **Apache License 2.0**. A copy of the license is available in the `LICENSE` file in this repository.

This license was chosen to encourage broad adoption and collaboration while providing a clear and standard legal framework for all contributors and users.

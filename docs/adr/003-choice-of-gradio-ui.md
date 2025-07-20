# ADR-003: Choice of a Minimalist Gradio UI for the Prototype

-   **Status:** Accepted
-   **Date:** 2025-07-19
-   **Deciders:** Maksim Ilin

## Context and Problem Statement

For our one-week prototype sprint, we require a functional user interface (UI) to demonstrate the capabilities of the `unfold.quest` agent. The primary purpose of this UI is to serve as an effective demonstration tool for the European AI Competition.

The key requirements for the UI are:
1.  **Rapid Development:** It must be buildable within the limited timeframe of our sprint (approximately one day).
2.  **Effective Demonstration:** It must clearly showcase our project's core innovation—the agent's ability to parse natural language and generate a rich, narrative-driven quest.
3.  **Ease of Use:** It must be immediately understandable and usable by a non-technical evaluator (e.g., a competition judge) with zero onboarding.
4.  **Low Overhead:** It should not distract development resources from the core AI and agentic workflow, which is the main subject of our research and the competition entry.

## Considered Alternatives

### 1. Full-Stack Web Application (e.g., FastAPI + React/Vue)

-   **Description:** A production-grade web application with a Python backend (FastAPI/Flask) and a modern JavaScript frontend (React, Vue, Svelte), potentially including an interactive map component (e.g., Leaflet, Mapbox).
-   **Reasons for Rejection:**
    -   **Prohibitively High Development Time:** The complexity of setting up a full-stack application, including a build system, component libraries, and API communication, is far outside the scope of a one-week sprint.
    -   **Distraction from Core Innovation:** This approach would shift the focus from developing the AI agent to frontend web development, which is not the primary evaluation criterion of the AI competition.

### 2. Complex Gradio/Streamlit UI with Advanced Features

-   **Description:** A more feature-rich interface using Gradio or Streamlit, but with additional components like an interactive map, user history, or configuration options.
-   **Reasons for Rejection:**
    -   **Unnecessary Complexity:** While an interactive map would be visually appealing, it does not help demonstrate the core novelty of our agent, which is the *narrative synthesis*. Implementing and debugging map integrations would add significant time for marginal demonstration value.
    -   **"Prototype Bloat":** Adding features like user history would make the UI more cluttered and less focused on the single, critical user journey we need to demonstrate.

### 3. Command-Line Interface (CLI)

-   **Description:** A simple Python script that runs in the terminal, taking user input and printing the agent's response as plain text.
-   **Reasons for Rejection:**
    -   **Lacks Visual Impact:** A key part of our concept is the engaging, well-formatted "Quest" output. A CLI cannot render the Markdown formatting (bolding, italics, lists) that makes the output compelling and readable.
    -   **Poor User Experience for Demonstration:** A CLI is not an intuitive or impressive way to showcase a modern AI application to a competition panel.

## Decision

We will implement the prototype's user interface using a **minimalist but highly effective Gradio application.**

The design will be composed of only the essential components required to prove our concept, specifically:
-   A single `gr.Textbox` for user input, to highlight the agent's natural language understanding.
-   A `gr.Button` to trigger the agent.
-   A `gr.Markdown` output component, to beautifully render the agent's formatted narrative response.
-   A `gr.Examples` component, to make the application instantly usable for evaluators and remove any friction to a successful demonstration.

This approach directly aligns with our "Keep it Simple" principle and focuses all attention on the output and intelligence of our AI agent.

## Consequences

### Positive Consequences

-   **Rapid Development:** A simple Gradio app can be built and polished in a matter of hours, allowing us to stay on schedule.
-   **Focus on Core Innovation:** This choice allows us to dedicate nearly the entire sprint to the AI components, which are the most important part of our submission.
-   **High-Impact Demonstration:** The chosen components are perfectly suited to our needs. The Markdown output will showcase the quality of our agent's narrative generation, and the `gr.Examples` will ensure a smooth and successful evaluation experience.

### Negative Consequences

-   **Not Production-Ready:** The UI will lack features expected of a production application, such as user accounts, saved history, or an interactive map. This is a deliberate and accepted trade-off.
-   **Limited Visual Polish:** While Gradio themes are clean, the UI will not have the unique branding or visual flair of a custom-designed frontend. This is acceptable for a technical prototype where the AI's functionality is the main focus.

## References

-   **Gradio Documentation:** [https://www.gradio.app/docs/](https://www.gradio.app/docs/)
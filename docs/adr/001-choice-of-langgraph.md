# ADR-001: Choice of LangGraph for Agentic Workflow Orchestration

-   **Status:** Accepted
-   **Date:** 2025-07-18
-   **Deciders:** Maksim Ilin

## Context and Problem Statement

The core of the "unfold.quest" application is an AI agent that must perform a multi-step, stateful process to generate a user journey. This process is not a single, monolithic LLM call; it requires a sequence of actions with conditional logic:

1.  Parse user input to determine intent ("Efficiency" vs. "Discovery").
2.  Based on intent, conditionally execute a series of tool calls.
3.  For a "Discovery" quest, the agent must:
    a.  Plan a transit route using a `transit_planner` tool.
    b.  Retrieve points of interest (POIs) using a `poi_retriever` tool.
    c.  Synthesize all gathered data into a final, creative narrative.
4.  The system must be reliable, observable, and easy to debug. We need to trace the flow of data and decisions through the entire process to ensure quality and identify failures.

A simple, linear script or a highly abstract agent framework would hide this complexity, making the system brittle and difficult to debug or modify. We need a framework that provides explicit control over the flow of logic and state.

## Considered Alternatives

### 1. Simple Python Script with Sequential Function Calls

-   **Description:** A standard procedural script that calls functions for each step in a fixed order.
-   **Reasons for Rejection:**
    -   **Poor State Management:** State would have to be passed manually between functions, leading to complex and error-prone function signatures.
    -   **Lack of Observability:** No built-in mechanism for tracing the execution flow or integrating with tools like LangSmith.
    -   **Inflexible Logic:** Implementing conditional logic (e.g., our "Efficiency" vs. "Discovery" branch) would require cumbersome `if/else` structures that would be difficult to modify or extend.
    -   **No Concurrency:** Would be difficult to parallelize tool calls where possible.

### 2. Standard LangChain Agent Executor (e.g., ReAct Framework)

-   **Description:** Use a high-level agent constructor like `create_react_agent`, where the LLM itself decides which tool to call next in a "thought-action-observation" loop.
-   **Reasons for Rejection:**
    -   **Lack of Control:** The logic flow is largely determined by the LLM, not the developer. This is excellent for open-ended research assistants but less reliable for a production workflow where certain steps *must* be executed deterministically.
    -   **Reduced Reliability:** The success of the entire chain depends on the LLM consistently choosing the correct sequence of tools. This can be brittle, especially with smaller or less capable models.
    -   **Debugging Complexity:** Debugging the "chain of thought" of the LLM is more difficult than debugging an explicit, developer-defined graph. It's harder to pinpoint why the agent failed to call a necessary tool.

### 3. Building a Custom State Machine from Scratch

-   **Description:** Develop our own state machine or workflow engine in Python.
-   **Reasons for Rejection:**
    -   **High Development Overhead:** This would involve reinventing the wheel. LangGraph already provides a robust, well-tested implementation of the core concepts we need (state management, nodes, edges).
    -   **Maintenance Burden:** We would be responsible for maintaining and extending this custom framework, diverting focus from our core application logic.
    -   **No Ecosystem Integration:** We would lose the seamless integration with the broader AI ecosystem (e.g., LangSmith, LangChain Core) that LangGraph provides out-of-the-box.

## Decision

We have decided to implement the core logic of the "unfold.quest" agent using the **LangGraph** library.

LangGraph provides the optimal balance. It gives us the explicit control and reliability of a custom state machine without the high development overhead. It allows us to define our workflow as a deterministic graph, ensuring key steps are always executed, while still providing the flexibility to incorporate LLM-driven decisions at specific nodes. This "Workflow with an Agentic Heart" approach directly addresses our core requirements.

## Consequences

### Positive Consequences

-   **Explicit Control & Reliability:** Aligns with our "workflow-first" principle. We design the flow, reducing the risk of procedural errors from the LLM.
-   **Superior Observability & Debugging:** LangGraph's state-centric design provides a perfect trace of the agent's "thought process," which is invaluable for debugging and quality assurance.
-   **Modularity & Maintainability:** Each node is a distinct Python function, forcing a clean separation of concerns and making the codebase easier to manage and scale.
-   **Clear Path to Future Complexity:** The framework is built to handle cycles and more complex logic, providing a robust architectural path for future evolution without requiring a rewrite.

### Negative Consequences

-   **Increased Verbosity:** LangGraph requires more explicit code to define the state, nodes, and edges compared to high-level agent constructors. This is a deliberate trade-off for control and reliability.
-   **Slightly Steeper Initial Learning Curve:** The graph-based paradigm may take slightly longer to grasp for developers new to it, but the long-term benefits in debugging and maintainability justify this initial investment.

## References

-   **LangGraph Documentation:** [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
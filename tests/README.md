# Tests for `unfold.quest`

This directory contains all the automated tests for the `unfold.quest` project. Our testing strategy is crucial for ensuring the reliability of our individual components and the correct integration of the entire agentic workflow.

## Testing Philosophy

We follow a two-tiered testing approach:

1.  **Unit Tests:** These are fast, isolated tests that verify the correctness of our deterministic "tools" (e.g., `poi_retriever`, `transit_planner`). They use controlled, mock data and **do not** make external API calls (e.g., to an LLM). They are designed to be run frequently during development.

2.  **Integration Tests:** These tests verify the entire compiled LangGraph agent from end-to-end. They check that all nodes, edges, and tools are correctly wired together. These tests may involve live, external API calls (e.g., to the Google Gemini API) and are therefore slower and potentially costly to run.

## Test Files

-   `test_tools.py`: Contains **unit tests** for all modules in the `src/tools/` directory. It uses `pytest` fixtures to create temporary mock data files, ensuring the tests are isolated and reproducible.

-   `test_agent.py`: Contains **integration tests** for the compiled agent defined in `src/agent/graph.py`. It includes tests for different logical paths (e.g., "Efficiency" vs. "Discovery") and uses a combination of mocked and live LLM calls.

## How to Run Tests

### Prerequisites

1.  Ensure you have `pytest` installed. It is included in our `requirements.txt`.
2.  Make sure your virtual environment is activated.

### Running All Tests

To run all unit and integration tests (including live LLM calls), navigate to the root of the `unfold-core` directory and simply run:

```bash
pytest
```

### Running Only Fast Unit Tests

During active development, you will often want to run only the fast unit tests and skip the slower, live LLM integration tests. We use `pytest` markers for this.

To run all tests *except* those marked as `live_llm`:

```bash
pytest -m "not live_llm"
```

### Running Only a Specific Test

To run a single test file:

```bash
pytest tests/test_tools.py
```

To run a single test function within a file:

```bash
pytest tests/test_agent.py::test_efficiency_path_is_correct
```

## Environment Variables

The integration tests in `test_agent.py` require a valid API key for the LLM service. Ensure that your `.env` file at the root of the project is correctly configured with your `GOOGLE_API_KEY`. The tests are designed to load this file automatically. The unit tests in `test_tools.py` do not require any environment variables.
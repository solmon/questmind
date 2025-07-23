# re-agent

A local agent project built with [langGraph](https://github.com/langchain-ai/langgraph), [Gradio](https://gradio.app/), and [Geminiapi](https://github.com/google/gemini-api) as the LLM backend.

## Features
- Agent logic with langGraph
- UI with Gradio
- Geminiapi for LLM
- Monorepo integration (UV, poe, pydantic)

## Quickstart

1. Install dependencies:
   ```sh
   uv pip install -r requirements.txt
   ```
2. Run the agent UI:
   ```sh
   poe dev
   ```

## Project Structure
- `main.py`: Entrypoint for the agent and Gradio UI
- `requirements.txt`: Python dependencies
- `pyproject.toml`: Project metadata and poe tasks

---

This project is for local development and experimentation only.

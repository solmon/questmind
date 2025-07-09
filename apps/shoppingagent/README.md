# ShoppingAgent

A prototype shopping agent using LangGraph for workflow orchestration and Gradio for the UI, supporting human-in-the-loop review.

## Features
- LangGraph-based workflow: LLM agent node + human review node
- Gradio UI for easy interaction
- Designed for extensibility (add more nodes, connect to real LLMs, etc.)

## Quickstart
1. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python main.py
   ```

## Human-in-the-loop
The agent's output is always routed through a human review step before finalizing any action.

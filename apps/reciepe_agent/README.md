# Recipe Agent

A LangGraph-based AI agent for recipe management and cooking assistance.

## Features

- Recipe search and recommendations
- Ingredient substitutions
- Cooking instructions and tips
- Meal planning assistance
- Dietary restrictions support

## Technology Stack

- **LangGraph**: Framework for building agents
- **Model Context Protocol**: Agent communication
- **FastAPI**: Web framework for APIs
- **Pydantic**: Data validation
- **UV**: Package management

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the agent:
```bash
poe agent
```

4. Start the API server:
```bash
poe serve
```

## Usage

### CLI Interface
```bash
python main.py
```

### API Interface
Visit `http://localhost:8000/docs` for the interactive API documentation.

### Graph Development
```bash
poe graph
```

### Graph Inspection
```bash
poe inspect
```

## Project Structure

```
reciepe_agent/
├── main.py              # Main entry point
├── agent/               # Agent implementation
│   ├── __init__.py
│   ├── graph.py         # LangGraph definition
│   ├── nodes.py         # Graph nodes
│   ├── tools.py         # Agent tools
│   └── state.py         # Agent state
├── api/                 # FastAPI routes
│   ├── __init__.py
│   └── routes.py
├── models/              # Pydantic models
│   ├── __init__.py
│   └── recipe.py
├── services/            # Business logic
│   ├── __init__.py
│   └── recipe_service.py
└── tests/               # Test files
    ├── __init__.py
    └── test_agent.py
```

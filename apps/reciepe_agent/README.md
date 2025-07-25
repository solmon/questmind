# Recipe Agent

A LangGraph-based AI agent for recipe management, cooking assistance, and intelligent ingredient shopping.

## Features

- 🍳 Recipe search and recommendations
- 🛒 **Intelligent ingredient search using MCP tools**
- 🛍️ **Shopping cart management with real grocery stores**
- 🔄 Ingredient substitutions  
- 📋 Cooking instructions and tips
- 📅 Meal planning assistance
- 🥗 Dietary restrictions support

## New Enhanced Workflow

1. **Recipe Discovery**: User searches for recipes
2. **Ingredient Intelligence**: LLM proactively offers to search for ingredients using MCP tools
3. **Real Store Search**: Agent searches actual grocery stores for ingredients with prices and availability
4. **Smart Cart Management**: User confirms ingredients and agent adds them to shopping cart
5. **Seamless Integration**: All through natural conversation with the LLM

## Technology Stack

- **LangGraph**: Framework for building agents with tool calling
- **Model Context Protocol (MCP)**: Real grocery store integrations
- **FastAPI**: Web framework for APIs
- **Google Gemini**: LLM with tool calling capabilities
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
# Add your GEMINI_API_KEY and other credentials
```

3. (Optional) Set up MCP servers for real grocery store integration:
```bash
# See mcp_integration_example.py for detailed instructions
```

4. Run the agent:
```bash
poe agent
```

5. Start the API server:
```bash
poe serve
```

## Usage

### CLI Interface
```bash
python main.py cli
```

Example conversation:
```
You: Find me a recipe for chicken carbonara
Agent: [Finds recipes with ingredients]

You: Can you help me get the ingredients?
Agent: [Uses MCP tools to search grocery stores]
       [Shows prices and availability]
       [Asks for confirmation to add to cart]

You: Yes, add them to my cart
Agent: [Adds ingredients to grocery cart]
       [Provides checkout link]
```

### API Interface
Visit `http://localhost:8000/docs` for the interactive API documentation.

### Testing the Enhanced Workflow
```bash
python test_corrected_workflow.py
```

## Architecture

### Correct Implementation ✅

- **LLM-Driven Tool Calling**: The LLM decides when and how to use tools
- **MCP Tools Integration**: Real grocery stores accessible as standard tools
- **Intelligent Workflow**: Agent proactively offers ingredient search after finding recipes
- **Natural Conversation**: User interacts naturally, LLM handles tool orchestration

### Key Components

1. **Tool-Calling LLM Node**: Uses Google Gemini with bound tools
2. **MCP Integration**: Real grocery store APIs via Model Context Protocol
3. **Smart Routing**: LLM chooses appropriate tools based on conversation context
4. **Tool Node**: Executes LLM's tool calls and returns results

## Project Structure

```
reciepe_agent/
├── main.py                          # Main entry point
├── test_corrected_workflow.py       # Test the enhanced workflow
├── mcp_integration_example.py       # MCP setup examples
├── agent/                          # Agent implementation
│   ├── graph.py                    # LangGraph with tool calling
│   ├── nodes.py                    # Tool-calling LLM node
│   ├── tools.py                    # Recipe + ingredient search tools
│   └── state.py                    # Agent state management
├── api/                           # FastAPI routes
│   └── routes.py
└── MCP_INTEGRATION.md            # MCP setup documentation
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

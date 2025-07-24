# MCP Integration for Recipe Agent

This document explains how to use Model Context Protocol (MCP) servers with the Recipe Agent.

## Overview

The Recipe Agent now supports dynamic loading of MCP tools using the `langchain_mcp_adapters.client` library. This allows you to extend the agent's capabilities by connecting to external MCP servers.

## Current Implementation

The agent is currently configured to use a math MCP server via HTTP transport:

```python
MultiServerMCPClient({
    "math": {
        "transport": "streamable_http",
        "url": "http://localhost:8000/mcp/"
    }
})
```

## Usage

### 1. Using the Agent with MCP Tools

```python
from agent.graph import run_recipe_agent_with_mcp

# Run agent with MCP tools (async)
result = await run_recipe_agent_with_mcp("Find me a recipe for chocolate cake")
```

### 2. Using the Agent without MCP Tools

```python
from agent.graph import run_recipe_agent

# Run agent with static tools only (sync)
result = run_recipe_agent("Find me a recipe for chocolate cake")
```

### 3. Manual MCP Tool Loading

```python
from agent.graph import initialize_mcp_client, create_recipe_agent

# Initialize MCP tools
await initialize_mcp_client()

# Create agent with MCP tools
agent = create_recipe_agent(include_mcp_tools=True)
```

## Configuration

### Current Setup

The current implementation uses a hardcoded configuration for demonstration. To use different MCP servers, modify the `initialize_mcp_client()` function in `agent/graph.py`.

### Future Configuration Options

The codebase includes infrastructure for environment-based configuration (see `mcp_config.example`), but this is not currently used by the simplified implementation.

## Error Handling

The implementation includes comprehensive error handling:

- If MCP tools fail to load, the agent falls back to static tools
- Missing dependencies are handled gracefully with warnings
- Connection failures are logged but don't prevent agent operation

## Development Notes

### Key Files

- `agent/graph.py` - Main MCP integration logic
- `agent/tools.py` - Static recipe tools
- `mcp_config.example` - Example configuration options

### Dependencies

- `langchain-mcp-adapters` - Required for MCP client functionality
- `langchain-core` - For tool interfaces
- `langgraph` - For agent graph structure

### Testing

To test MCP integration:

1. Ensure you have an MCP server running on `http://localhost:8000/mcp/`
2. Run the agent with: `await run_recipe_agent_with_mcp("your query")`
3. Check logs for MCP tool loading status

## Extending MCP Support

To add new MCP servers:

1. Modify the `initialize_mcp_client()` function
2. Add new server configurations to the `MultiServerMCPClient` constructor
3. Ensure proper error handling for new servers

Example:

```python
_mcp_client = MultiServerMCPClient({
    "math": {
        "transport": "streamable_http",
        "url": "http://localhost:8000/mcp/"
    },
    "recipes": {
        "transport": "streamable_http", 
        "url": "http://localhost:8001/recipe-mcp/"
    }
})
```

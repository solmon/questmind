"""Recipe Agent LangGraph Implementation."""

import asyncio
import logging
from typing import Literal, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool

from agent.state import RecipeAgentState
from agent.nodes import (
    classify_intent_node,
    search_recipes_node,
    # recommend_recipes_node,
    # substitute_ingredients_node,
    # create_meal_plan_node,
    llm_response_node,
    human_input_node
)
from agent.tools import recipe_tools

# MCP client setup with error handling
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("langchain_mcp_adapters not available. Running without MCP tools.")

logger = logging.getLogger(__name__)

# Global variables for MCP tools
_mcp_client: Optional[any] = None
_mcp_tools: List[BaseTool] = []


async def initialize_mcp_client():
    """Initialize MCP client and load tools."""
    global _mcp_client, _mcp_tools
    
    if not MCP_AVAILABLE:
        logger.warning("MCP not available, skipping initialization")
        return []
    
    try:
        # Initialize MCP client
        _mcp_client = MultiServerMCPClient(
            {
                "math": {
                    "transport": "streamable_http",
                    "url": "http://localhost:8000/mcp/"
                },
            }
        )
        
        # Get tools asynchronously
        _mcp_tools = await _mcp_client.get_tools()
        logger.info(f"Loaded {len(_mcp_tools)} MCP tools")
        return _mcp_tools
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP client: {e}")
        _mcp_tools = []
        return []


def get_mcp_tools() -> List[BaseTool]:
    """Get cached MCP tools."""
    return _mcp_tools.copy()


# def route_intent(state: RecipeAgentState) -> Literal["search", "recommend", "substitute", "plan", "nutrition", "general"]:
def route_intent(state: RecipeAgentState) -> Literal["search", "general"]:
    """Route based on classified intent."""
    intent = state.get("intent", "general")
    return intent


def should_continue(state: RecipeAgentState) -> Literal["continue", "end"]:
    """Determine if processing should continue."""
    if state.get("processing_complete", False):
        return "end"
    if state.get("error_message"):
        return "end"
    return "continue"


def create_recipe_agent(include_mcp_tools: bool = False) -> StateGraph:
    """Create the Recipe Agent graph.
    
    Args:
        include_mcp_tools: Whether to include MCP tools in the agent
    """
    
    # Create the graph
    workflow = StateGraph(RecipeAgentState)
    
    # Add nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("search_recipes", search_recipes_node)
    # workflow.add_node("recommend_recipes", recommend_recipes_node)
    # workflow.add_node("substitute_ingredients", substitute_ingredients_node)
    # workflow.add_node("create_meal_plan", create_meal_plan_node)
    workflow.add_node("llm_response", llm_response_node)
    workflow.add_node("human_input", human_input_node)
    
    # Prepare tools
    all_tools = recipe_tools.copy()
    
    # Add MCP tools if requested and available
    if include_mcp_tools:
        mcp_tools = get_mcp_tools()
        if mcp_tools:
            all_tools.extend(mcp_tools)
            logger.info(f"Added {len(mcp_tools)} MCP tools to agent")
        else:
            logger.warning("MCP tools requested but none available")
    
    # Add tool node for all tools
    tool_node = ToolNode(all_tools)
    workflow.add_node("tools", tool_node)

    # Set entry point
    workflow.set_entry_point("classify_intent")
    
    # Add conditional routing from classify_intent
    workflow.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "search": "search_recipes",
            # "recommend": "recommend_recipes", 
            # "substitute": "substitute_ingredients",
            # "plan": "create_meal_plan",
            # "nutrition": "llm_response",
            "general": "llm_response"
        }
    )
    
    # Add edges from processing nodes to LLM response
    workflow.add_edge("search_recipes", "llm_response")
    # workflow.add_edge("recommend_recipes", "llm_response") 
    # workflow.add_edge("substitute_ingredients", "llm_response")
    # workflow.add_edge("create_meal_plan", "llm_response")
    
    # Add conditional edge from LLM response
    workflow.add_conditional_edges(
        "llm_response",
        should_continue,
        {
            "continue": "human_input",
            "end": END
        }
    )
    
    # Add edge from human input back to classify intent for follow-up queries
    workflow.add_edge("human_input", "classify_intent")
    
    # Compile the graph
    return workflow.compile()


# Create the default agent instance (without MCP tools for now)
recipe_agent = create_recipe_agent()


async def create_recipe_agent_with_mcp() -> StateGraph:
    """Create the Recipe Agent graph with MCP tools loaded."""
    try:
        # Initialize MCP tools first
        await initialize_mcp_client()
        # Create agent with MCP tools
        agent = create_recipe_agent(include_mcp_tools=True)
        logger.info("Successfully created recipe agent with MCP tools")
        return agent
    except Exception as e:
        logger.error(f"Failed to create agent with MCP tools: {e}")
        logger.info("Falling back to agent without MCP tools")
        return create_recipe_agent(include_mcp_tools=False)


def run_recipe_agent(query: str, **kwargs) -> dict:
    """Run the recipe agent with a query (static tools only)."""
    initial_state = {
        "user_query": query,
        "messages": [HumanMessage(content=query)],
        "recipes": [],
        "search_results": [],
        "recommendations": [],
        "ingredient_substitutions": {},
        "meal_plan": None,
        "dietary_restrictions": kwargs.get("dietary_restrictions", []),
        "cuisine_preference": kwargs.get("cuisine_preference"),
        "needs_user_input": False,
        "error_message": None,
        "processing_complete": False,
        "tool_outputs": {}
    }
    
    # Run the agent
    result = recipe_agent.invoke(initial_state)
    return result


async def run_recipe_agent_with_mcp(query: str, **kwargs) -> dict:
    """Run the recipe agent with a query (including MCP tools)."""
    initial_state = {
        "user_query": query,
        "messages": [HumanMessage(content=query)],
        "recipes": [],
        "search_results": [],
        "recommendations": [],
        "ingredient_substitutions": {},
        "meal_plan": None,
        "dietary_restrictions": kwargs.get("dietary_restrictions", []),
        "cuisine_preference": kwargs.get("cuisine_preference"),
        "needs_user_input": False,
        "error_message": None,
        "processing_complete": False,
        "tool_outputs": {}
    }
    
    # Create agent with MCP tools
    agent = await create_recipe_agent_with_mcp()
    
    # Run the agent
    result = agent.invoke(initial_state)
    return result

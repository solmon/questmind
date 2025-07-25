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
    recipe_llm_node,
    ingredient_confirmation_node,
    grocery_llm_node,
    cart_confirmation_node,
    add_to_cart_node,
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
                "grocery": {
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


def route_intent(state: RecipeAgentState) -> Literal["search", "general"]:
    """Route based on classified intent."""
    intent = state.get("intent", "general")
    return intent

def route_check_user_confirmation(state: RecipeAgentState) -> Literal["yes", "no"]:
    """Route based on user confirmation."""
    user_query = state.get("user_query", "").lower()
    print(f"User query for confirmation: {user_query}")
    if user_query in ["yes", "proceed", "continue"]:
        return "yes"
    return "no"


# def route_after_recipe_search(state: RecipeAgentState) -> Literal["recipe_llm", "end"]:
#     """Route after recipe search to recipe LLM."""
#     if state.get("recipes"):
#         return "recipe_llm"
#     return "end"


def route_user_response(state: RecipeAgentState) -> Literal["ingredient_confirmation", "grocery_llm", "add_to_cart", "recipe_llm", "end"]:
    """Route based on user response and workflow stage."""
    workflow_stage = state.get("workflow_stage", "recipe_search")
    print(f"Current workflow stage: {workflow_stage}")
    
    # After recipe display, check if user wants to proceed with ingredients
    if workflow_stage == "recipe_display" and route_check_user_confirmation(state) == "yes":
        return "ingredient_confirmation"
    # Handle user confirmation for ingredients
    elif workflow_stage == "user_confirmed_ingredients" and state.get("user_wants_ingredients"):
        return "ingredient_confirmation"
    elif workflow_stage == "ingredient_confirmation" and route_check_user_confirmation(state) == "yes":
        state["ingredients_confirmed"] = True
        return "grocery_llm"
    elif workflow_stage == "cart_confirmation" and state.get("grocery_items_confirmed"):
        return "add_to_cart"
    elif state.get("user_query", "").lower() in ["back", "change recipe", "new recipe", "different recipe"]:
        return "recipe_llm"
    else:
        return "end"




def should_call_tools(state: RecipeAgentState) -> Literal["tools", "cart_confirmation"]:
    """Check if grocery LLM wants to call tools."""
    messages = state.get("messages", [])
    if messages and hasattr(messages[-1], 'tool_calls') and messages[-1].tool_calls:
        return "tools"
    return "cart_confirmation"


def should_continue(state: RecipeAgentState) -> Literal["continue", "end"]:
    """Determine if processing should continue."""
    if state.get("processing_complete", False):
        return "end"
    if state.get("error_message"):
        return "end"
    return "continue"


def create_recipe_agent(include_mcp_tools: bool = False) -> StateGraph:
    """Create the Recipe Agent graph with enhanced workflow.
    
    Args:
        include_mcp_tools: Whether to include MCP tools in the agent
    """
    
    # Create the graph
    workflow = StateGraph(RecipeAgentState)
    
    # Add nodes for the enhanced workflow
    workflow.add_node("classify_intent", classify_intent_node)
    # workflow.add_node("search_recipes", search_recipes_node)
    workflow.add_node("recipe_llm", recipe_llm_node)  # Dedicated recipe LLM
    workflow.add_node("ingredient_confirmation", ingredient_confirmation_node)
    workflow.add_node("grocery_llm", grocery_llm_node)  # Dedicated grocery LLM with MCP tools
    workflow.add_node("cart_confirmation", cart_confirmation_node)
    workflow.add_node("add_to_cart", add_to_cart_node)
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
    
    # Add tool node for all tools (mainly used by grocery_llm)
    tool_node = ToolNode(all_tools)
    workflow.add_node("tools", tool_node)

    # Set entry point
    workflow.set_entry_point("classify_intent")
    
    # WORKFLOW ROUTING:
    
    # 1. Intent classification -> Recipe search or general response
    workflow.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "search": "recipe_llm",
            "general": END  # Use recipe LLM for general queries too
        }
    )
    
    # 3. Recipe LLM -> Human input for confirmation to proceed with ingredients
    workflow.add_conditional_edges(
        "recipe_llm",
        lambda state: "human_input" if state.get("recipes") else "end",
        {
            "human_input": "human_input",
            "end": END
        }
    )
    
    # 4. Human input -> Route based on user response and stage
    workflow.add_conditional_edges(
        "human_input",
        route_user_response,
        {
            "ingredient_confirmation": "ingredient_confirmation",
            "grocery_llm": "grocery_llm", 
            "add_to_cart": "add_to_cart",
            "recipe_llm": "recipe_llm",  # Back to recipe search
            "end": END
        }
    )
    
    # 5. Ingredient confirmation -> Grocery LLM (auto-proceed for demo)
    workflow.add_conditional_edges(
        "ingredient_confirmation",
        lambda state: "grocery_llm" if state.get("ingredients_confirmed") else "end",
        {
            "grocery_llm": "grocery_llm",
            "end": "human_input"
        }
    )
    
    # 6. Grocery LLM -> Cart confirmation (check for searched ingredients)
    workflow.add_conditional_edges(
        "grocery_llm",
        lambda state: "cart_confirmation" if state.get("searched_ingredients") or state.get("workflow_stage") == "grocery_search_complete" else "end",
        {
            # "cart_confirmation": "cart_confirmation",
            "cart_confirmation": END,
            "end": END
        }
    )
    
    # 7. Tools -> Back to Grocery LLM (for tool result processing)
    workflow.add_edge("tools", "grocery_llm")
    
    # 8. Cart confirmation -> Add to cart (auto-proceed for demo)
    workflow.add_conditional_edges(
        "cart_confirmation",
        lambda state: "add_to_cart" if state.get("grocery_items_confirmed") else "end",
        {
            "add_to_cart": "add_to_cart",
            "end": END
        }
    )
    
    # 9. Add to cart -> End (workflow complete)
    workflow.add_edge("add_to_cart", END)
    
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
        "searched_ingredients": [],
        "ingredients_to_cart": [],        
        "needs_user_input": False,
        "user_wants_ingredients": None,
        "ingredients_confirmed": None,
        "grocery_items_confirmed": None,
        "workflow_stage": "initial",  # Start with initial instead of None
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
        "searched_ingredients": [],
        "ingredients_to_cart": [],
        "needs_user_input": False,
        "user_wants_ingredients": None,
        "ingredients_confirmed": None,
        "grocery_items_confirmed": None,
        "workflow_stage": "initial",  # Start with initial instead of None
        "error_message": None,
        "processing_complete": False,
        "tool_outputs": {}
    }
    
    # Create agent with MCP tools
    agent = await create_recipe_agent_with_mcp()
    
    # Run the agent
    result = agent.invoke(initial_state)
    return result

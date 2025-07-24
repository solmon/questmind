"""Recipe Agent LangGraph Implementation."""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage

from .state import RecipeAgentState
from .nodes import (
    classify_intent_node,
    search_recipes_node,
    recommend_recipes_node,
    substitute_ingredients_node,
    create_meal_plan_node,
    llm_response_node,
    human_input_node
)
from .tools import recipe_tools


def route_intent(state: RecipeAgentState) -> Literal["search", "recommend", "substitute", "plan", "nutrition", "general"]:
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


def create_recipe_agent() -> StateGraph:
    """Create the Recipe Agent graph."""
    
    # Create the graph
    workflow = StateGraph(RecipeAgentState)
    
    # Add nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("search_recipes", search_recipes_node)
    workflow.add_node("recommend_recipes", recommend_recipes_node)
    workflow.add_node("substitute_ingredients", substitute_ingredients_node)
    workflow.add_node("create_meal_plan", create_meal_plan_node)
    workflow.add_node("llm_response", llm_response_node)
    workflow.add_node("human_input", human_input_node)
    
    # Add tool node for recipe tools
    tool_node = ToolNode(recipe_tools)
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.set_entry_point("classify_intent")
    
    # Add conditional routing from classify_intent
    workflow.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "search": "search_recipes",
            "recommend": "recommend_recipes", 
            "substitute": "substitute_ingredients",
            "plan": "create_meal_plan",
            "nutrition": "llm_response",
            "general": "llm_response"
        }
    )
    
    # Add edges from processing nodes to LLM response
    workflow.add_edge("search_recipes", "llm_response")
    workflow.add_edge("recommend_recipes", "llm_response") 
    workflow.add_edge("substitute_ingredients", "llm_response")
    workflow.add_edge("create_meal_plan", "llm_response")
    
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


# Create the default agent instance
recipe_agent = create_recipe_agent()


def run_recipe_agent(query: str, **kwargs) -> dict:
    """Run the recipe agent with a query."""
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

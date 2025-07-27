"""Recipe Agent State definition."""

from typing import Dict, List, Optional, TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class RecipeAgentState(TypedDict):
    """State for the Recipe Agent."""
    
    # Conversation history
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Conversation messages to display
    display_messages: List[BaseMessage]

    # User query and intent
    user_query: Optional[str]
    intent: Optional[str]  # search, recommend, substitute, plan, etc.
    
    # Recipe-related data    
    recipes: List[Dict]
    selected_recipe: Optional[Dict]  # Recipe selected by user    

    plan_extract: Optional[str]  # Extracted plan from recipe article
    
    # ingredients: List[str]
    searched_ingredients: List[Dict]  # Ingredients found via MCP search
    ingredients_to_cart: List[Dict]   # Confirmed ingredients for cart
    
    # Search and recommendation data
    # search_results: List[Dict]
        
    # Processing flags    
    recipe_confirmed: Optional[bool]   # User confirmed ingredients for grocery search
    recipe_plan_confirmed: Optional[bool]   # User confirmed ingredients for grocery search

    grocery_items_confirmed: Optional[bool]  # User confirmed grocery items for cart
    workflow_stage: Optional[str]  # "recipe_search", "ingredient_confirmation", "grocery_search", "cart_confirmation"
    error_message: Optional[str]
    processing_complete: bool
    
    # Tool outputs
    tool_outputs: Dict[str, any]

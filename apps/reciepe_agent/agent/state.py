"""Recipe Agent State definition."""

from typing import Dict, List, Optional, TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class RecipeAgentState(TypedDict):
    """State for the Recipe Agent."""
    
    # Conversation history
    messages: Annotated[List[BaseMessage], add_messages]
    
    # User query and intent
    user_query: Optional[str]
    intent: Optional[str]  # search, recommend, substitute, plan, etc.
    
    # Recipe-related data
    recipes: List[Dict]
    selected_recipe: Optional[Dict]
    ingredients: List[str]
    dietary_restrictions: List[str]
    cuisine_preference: Optional[str]
    
    # Search and recommendation data
    search_results: List[Dict]
    recommendations: List[Dict]
    
    # Substitution data
    ingredient_substitutions: Dict[str, List[str]]
    
    # Meal planning data
    meal_plan: Optional[Dict]
    
    # Processing flags
    needs_user_input: bool
    error_message: Optional[str]
    processing_complete: bool
    
    # Tool outputs
    tool_outputs: Dict[str, any]

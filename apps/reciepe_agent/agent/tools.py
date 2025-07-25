"""Recipe Agent Tools."""

from agent.state import RecipeAgentState
import json
from typing import Dict, List, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class RecipeSearchInput(BaseModel):
    """Input for recipe search tool."""
    query: str = Field(description="Search query for recipes")
    cuisine: Optional[str] = Field(default=None, description="Cuisine type filter")
    dietary_restrictions: Optional[List[str]] = Field(default=None, description="Dietary restrictions")
    max_results: int = Field(default=10, description="Maximum number of results")

class PrintMessagesInput(BaseModel):
        """Input for print_messages tool."""
        messages: List[str] = Field(description="Array of messages to print to stdin")

@tool
def print_messages(input: PrintMessagesInput) -> Dict:
    """Prints an array of messages to the standard output."""
    for msg in input.messages:
        print(msg)
    return {"success": True, "printed_count": len(input.messages)}


def mock_recipes() -> List[Dict]:
    """Search for recipes based on query and filters."""
    # Mock implementation - replace with actual recipe search API
    mock_recipes = [
        {
            "id": "1",
            "title": "Classic Spaghetti Carbonara",
            "cuisine": "Italian",
            "prep_time": 15,
            "cook_time": 20,
            "servings": 4,
            "ingredients": [
                "400g spaghetti",
                "200g pancetta",
                "4 large eggs",
                "100g Pecorino Romano cheese",
                "Black pepper",
                "Salt"
            ],
            "instructions": [
                "Cook spaghetti in salted boiling water until al dente",
                "Cook pancetta until crispy",
                "Whisk eggs with cheese and pepper",
                "Combine hot pasta with pancetta",
                "Add egg mixture off heat, tossing quickly",
                "Serve immediately"
            ],
            "dietary_tags": ["gluten-containing"],
            "rating": 4.8
        },
        {
            "id": "2", 
            "title": "Vegetarian Buddha Bowl",
            "cuisine": "Fusion",
            "prep_time": 20,
            "cook_time": 25,
            "servings": 2,
            "ingredients": [
                "1 cup quinoa",
                "2 cups mixed vegetables",
                "1 avocado",
                "2 tbsp tahini",
                "1 lemon",
                "Olive oil",
                "Salt and pepper"
            ],
            "instructions": [
                "Cook quinoa according to package directions",
                "Roast vegetables with olive oil",
                "Make tahini dressing with lemon",
                "Assemble bowl with quinoa, vegetables, avocado",
                "Drizzle with dressing"
            ],
            "dietary_tags": ["vegetarian", "vegan", "gluten-free"],
            "rating": 4.6
        }
    ]
    
    return mock_recipes



# Export all tools
recipe_tools = [
    print_messages
]

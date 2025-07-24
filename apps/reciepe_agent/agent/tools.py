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


class IngredientSubstitutionInput(BaseModel):
    """Input for ingredient substitution tool."""
    ingredient: str = Field(description="Ingredient to find substitutions for")
    recipe_context: Optional[str] = Field(default=None, description="Recipe context for better substitutions")


class MealPlanInput(BaseModel):
    """Input for meal planning tool."""
    days: int = Field(default=7, description="Number of days to plan for")
    dietary_restrictions: Optional[List[str]] = Field(default=None, description="Dietary restrictions")
    cuisine_preferences: Optional[List[str]] = Field(default=None, description="Preferred cuisines")


@tool(args_schema=RecipeSearchInput)
def search_recipes(query: str, cuisine: Optional[str] = None, 
                  dietary_restrictions: Optional[List[str]] = None, 
                  max_results: int = 10) -> List[Dict]:
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
    
    # Filter based on query and preferences
    filtered_recipes = []
    for recipe in mock_recipes:
        if query.lower() in recipe["title"].lower() or query.lower() in recipe["cuisine"].lower():
            if cuisine and recipe["cuisine"].lower() != cuisine.lower():
                continue
            if dietary_restrictions:
                # Check if recipe meets dietary restrictions
                recipe_tags = recipe.get("dietary_tags", [])
                if "vegetarian" in dietary_restrictions and "vegetarian" not in recipe_tags:
                    continue
                if "gluten-free" in dietary_restrictions and "gluten-free" not in recipe_tags:
                    continue
            filtered_recipes.append(recipe)
    
    return filtered_recipes[:max_results]


@tool(args_schema=IngredientSubstitutionInput)
def find_ingredient_substitutions(ingredient: str, recipe_context: Optional[str] = None) -> Dict[str, List[str]]:
    """Find substitutions for a given ingredient."""
    # Mock substitution database
    substitutions_db = {
        "eggs": ["flax eggs (1 tbsp ground flaxseed + 3 tbsp water per egg)", 
                "applesauce (1/4 cup per egg)", "mashed banana (1/4 cup per egg)"],
        "butter": ["coconut oil", "olive oil", "vegan butter", "applesauce"],
        "milk": ["almond milk", "oat milk", "soy milk", "coconut milk"],
        "flour": ["almond flour", "coconut flour", "rice flour", "gluten-free flour blend"],
        "sugar": ["honey", "maple syrup", "stevia", "coconut sugar"],
        "cheese": ["nutritional yeast", "cashew cheese", "vegan cheese alternatives"],
        "meat": ["tofu", "tempeh", "seitan", "mushrooms", "lentils"]
    }
    
    ingredient_lower = ingredient.lower()
    substitutions = []
    
    # Find direct matches
    for key, subs in substitutions_db.items():
        if key in ingredient_lower or ingredient_lower in key:
            substitutions.extend(subs)
    
    if not substitutions:
        substitutions = ["No specific substitutions found. Consider consulting a recipe database or nutritionist."]
    
    return {
        "ingredient": ingredient,
        "substitutions": substitutions,
        "context": recipe_context
    }


@tool(args_schema=MealPlanInput)
def create_meal_plan(days: int = 7, dietary_restrictions: Optional[List[str]] = None,
                    cuisine_preferences: Optional[List[str]] = None) -> Dict:
    """Create a meal plan for the specified number of days."""
    # Mock meal plan generation
    meal_plan = {
        "duration": f"{days} days",
        "dietary_restrictions": dietary_restrictions or [],
        "cuisine_preferences": cuisine_preferences or [],
        "meals": {}
    }
    
    sample_meals = [
        {"name": "Overnight Oats with Berries", "type": "breakfast", "prep_time": 5},
        {"name": "Mediterranean Quinoa Salad", "type": "lunch", "prep_time": 15},
        {"name": "Grilled Salmon with Vegetables", "type": "dinner", "prep_time": 30},
        {"name": "Vegetable Stir Fry", "type": "dinner", "prep_time": 20},
        {"name": "Greek Yogurt Parfait", "type": "breakfast", "prep_time": 5},
        {"name": "Chicken Caesar Wrap", "type": "lunch", "prep_time": 10},
        {"name": "Pasta Primavera", "type": "dinner", "prep_time": 25}
    ]
    
    for day in range(1, days + 1):
        day_key = f"day_{day}"
        meal_plan["meals"][day_key] = {
            "breakfast": sample_meals[0],
            "lunch": sample_meals[1], 
            "dinner": sample_meals[2]
        }
    
    return meal_plan


@tool
def get_recipe_nutrition(recipe_id: str) -> Dict:
    """Get nutritional information for a recipe."""
    # Mock nutrition data
    nutrition_data = {
        "recipe_id": recipe_id,
        "calories": 450,
        "protein": "25g",
        "carbohydrates": "35g", 
        "fat": "20g",
        "fiber": "5g",
        "sugar": "8g",
        "sodium": "600mg"
    }
    return nutrition_data


@tool
def save_recipe_to_favorites(recipe_id: str, user_id: str = "default_user") -> Dict:
    """Save a recipe to user's favorites."""
    return {
        "success": True,
        "message": f"Recipe {recipe_id} saved to favorites for user {user_id}",
        "recipe_id": recipe_id,
        "user_id": user_id
    }


# Export all tools
recipe_tools = [
    search_recipes,
    find_ingredient_substitutions, 
    create_meal_plan,
    get_recipe_nutrition,
    save_recipe_to_favorites
]

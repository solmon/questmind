"""Recipe service for business logic."""

from typing import List, Optional, Dict, Any
import json
from models.recipe import Recipe, RecipeQuery, IngredientSubstitution, MealPlan


class RecipeService:
    """Service class for recipe-related business logic."""
    
    def __init__(self):
        """Initialize the recipe service."""
        self.recipes_cache = {}
        self.substitutions_cache = {}
        
    def search_recipes(self, query: RecipeQuery) -> List[Recipe]:
        """Search for recipes based on query parameters."""
        # This would typically interface with a real recipe database
        # For now, return mock data
        
        mock_recipes = [
            {
                "id": "1",
                "title": "Classic Spaghetti Carbonara",
                "description": "Authentic Italian pasta dish with eggs, cheese, and pancetta",
                "cuisine": "italian",
                "prep_time": 15,
                "cook_time": 20,
                "total_time": 35,
                "servings": 4,
                "difficulty": "medium",
                "ingredients": [
                    {"name": "spaghetti", "amount": "400", "unit": "g"},
                    {"name": "pancetta", "amount": "200", "unit": "g"},
                    {"name": "eggs", "amount": "4", "unit": "large"},
                    {"name": "Pecorino Romano cheese", "amount": "100", "unit": "g"},
                    {"name": "black pepper", "amount": "to taste"},
                    {"name": "salt", "amount": "to taste"}
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
                "rating": 4.8,
                "reviews_count": 1250
            },
            {
                "id": "2",
                "title": "Vegetarian Buddha Bowl",
                "description": "Healthy and colorful bowl with quinoa, roasted vegetables, and tahini dressing",
                "cuisine": "fusion",
                "prep_time": 20,
                "cook_time": 25,
                "total_time": 45,
                "servings": 2,
                "difficulty": "easy",
                "ingredients": [
                    {"name": "quinoa", "amount": "1", "unit": "cup"},
                    {"name": "mixed vegetables", "amount": "2", "unit": "cups"},
                    {"name": "avocado", "amount": "1", "unit": "large"},
                    {"name": "tahini", "amount": "2", "unit": "tbsp"},
                    {"name": "lemon", "amount": "1", "unit": "whole"},
                    {"name": "olive oil", "amount": "2", "unit": "tbsp"},
                    {"name": "salt", "amount": "to taste"},
                    {"name": "pepper", "amount": "to taste"}
                ],
                "instructions": [
                    "Cook quinoa according to package directions",
                    "Roast vegetables with olive oil at 400°F for 20 minutes",
                    "Make tahini dressing with lemon juice",
                    "Assemble bowl with quinoa, vegetables, and avocado",
                    "Drizzle with dressing and serve"
                ],
                "dietary_tags": ["vegetarian", "vegan", "gluten-free"],
                "rating": 4.6,
                "reviews_count": 890
            },
            {
                "id": "3",
                "title": "Chicken Tikka Masala",
                "description": "Creamy Indian curry with tender chicken in spiced tomato sauce",
                "cuisine": "indian",
                "prep_time": 30,
                "cook_time": 45,
                "total_time": 75,
                "servings": 6,
                "difficulty": "medium",
                "ingredients": [
                    {"name": "chicken breast", "amount": "2", "unit": "lbs"},
                    {"name": "yogurt", "amount": "1", "unit": "cup"},
                    {"name": "garam masala", "amount": "2", "unit": "tsp"},
                    {"name": "tomato sauce", "amount": "1", "unit": "can"},
                    {"name": "heavy cream", "amount": "1/2", "unit": "cup"},
                    {"name": "ginger", "amount": "2", "unit": "tbsp"},
                    {"name": "garlic", "amount": "4", "unit": "cloves"}
                ],
                "instructions": [
                    "Marinate chicken in yogurt and spices for 30 minutes",
                    "Grill or pan-cook chicken until done",
                    "Make sauce with tomatoes, cream, and spices",
                    "Combine chicken with sauce",
                    "Simmer for 15 minutes",
                    "Serve with rice or naan"
                ],
                "dietary_tags": ["gluten-free"],
                "rating": 4.7,
                "reviews_count": 2100
            }
        ]
        
        # Filter based on query
        filtered_recipes = []
        for recipe_data in mock_recipes:
            # Check if query matches title or cuisine
            if (query.query.lower() in recipe_data["title"].lower() or 
                query.query.lower() in recipe_data.get("cuisine", "").lower() or
                query.query.lower() == "popular"):
                
                # Apply filters
                if query.cuisine and recipe_data.get("cuisine") != query.cuisine.lower():
                    continue
                    
                if query.dietary_restrictions:
                    recipe_tags = recipe_data.get("dietary_tags", [])
                    if not any(restriction in recipe_tags for restriction in query.dietary_restrictions):
                        # For vegetarian/vegan, be more flexible
                        if "vegetarian" in query.dietary_restrictions and "vegetarian" not in recipe_tags:
                            continue
                        if "gluten-free" in query.dietary_restrictions and "gluten-free" not in recipe_tags:
                            continue
                
                if query.max_prep_time and recipe_data.get("prep_time", 0) > query.max_prep_time:
                    continue
                    
                if query.max_cook_time and recipe_data.get("cook_time", 0) > query.max_cook_time:
                    continue
                
                # Convert to Recipe model
                recipe = Recipe(**recipe_data)
                filtered_recipes.append(recipe)
        
        return filtered_recipes[:query.max_results]
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Get a specific recipe by ID."""
        # Mock implementation
        if recipe_id in self.recipes_cache:
            return self.recipes_cache[recipe_id]
        return None
    
    def get_ingredient_substitutions(self, ingredient: str, context: Optional[str] = None) -> IngredientSubstitution:
        """Get substitutions for an ingredient."""
        substitutions_db = {
            "eggs": {
                "substitutes": [
                    "flax eggs (1 tbsp ground flaxseed + 3 tbsp water per egg)",
                    "applesauce (1/4 cup per egg)",
                    "mashed banana (1/4 cup per egg)",
                    "commercial egg replacer"
                ],
                "notes": "Best for baking. Flax eggs work well for binding."
            },
            "butter": {
                "substitutes": [
                    "coconut oil (same amount)",
                    "olive oil (3/4 amount)",
                    "vegan butter (same amount)",
                    "applesauce (1/2 amount for baking)"
                ],
                "notes": "For baking, applesauce reduces fat content."
            },
            "milk": {
                "substitutes": [
                    "almond milk",
                    "oat milk", 
                    "soy milk",
                    "coconut milk",
                    "rice milk"
                ],
                "notes": "Use same amount. Coconut milk is richer."
            },
            "flour": {
                "substitutes": [
                    "almond flour (1:1 ratio)",
                    "coconut flour (1/4 amount)",
                    "rice flour (1:1 ratio)",
                    "gluten-free flour blend (1:1 ratio)"
                ],
                "notes": "Coconut flour is very absorbent, use less."
            },
            "sugar": {
                "substitutes": [
                    "honey (3/4 amount)",
                    "maple syrup (3/4 amount)",
                    "stevia (much less, to taste)",
                    "coconut sugar (1:1 ratio)"
                ],
                "notes": "Liquid sweeteners may affect texture."
            }
        }
        
        ingredient_lower = ingredient.lower()
        substitution_data = None
        
        # Find matching substitution
        for key, data in substitutions_db.items():
            if key in ingredient_lower or ingredient_lower in key:
                substitution_data = data
                break
        
        if not substitution_data:
            substitution_data = {
                "substitutes": ["No specific substitutions found. Consult a recipe database."],
                "notes": "Consider the ingredient's role in the recipe when substituting."
            }
        
        return IngredientSubstitution(
            original_ingredient=ingredient,
            substitutes=substitution_data["substitutes"],
            notes=substitution_data["notes"]
        )
    
    def create_meal_plan(self, days: int, dietary_restrictions: List[str] = None, 
                        cuisine_preferences: List[str] = None) -> MealPlan:
        """Create a meal plan."""
        # Mock meal plan creation
        dietary_restrictions = dietary_restrictions or []
        cuisine_preferences = cuisine_preferences or []
        
        # Create a simple meal plan
        meals = {}
        meal_types = ["breakfast", "lunch", "dinner"]
        
        sample_meals = {
            "breakfast": [
                {"id": "b1", "title": "Overnight Oats with Berries", "prep_time": 5},
                {"id": "b2", "title": "Avocado Toast", "prep_time": 10},
                {"id": "b3", "title": "Greek Yogurt Parfait", "prep_time": 5},
                {"id": "b4", "title": "Smoothie Bowl", "prep_time": 10}
            ],
            "lunch": [
                {"id": "l1", "title": "Mediterranean Quinoa Salad", "prep_time": 15},
                {"id": "l2", "title": "Chicken Caesar Wrap", "prep_time": 10},
                {"id": "l3", "title": "Veggie Burger Bowl", "prep_time": 20},
                {"id": "l4", "title": "Asian Noodle Soup", "prep_time": 25}
            ],
            "dinner": [
                {"id": "d1", "title": "Grilled Salmon with Vegetables", "prep_time": 30},
                {"id": "d2", "title": "Vegetable Stir Fry", "prep_time": 20},
                {"id": "d3", "title": "Pasta Primavera", "prep_time": 25},
                {"id": "d4", "title": "Lentil Curry", "prep_time": 35}
            ]
        }
        
        for day in range(1, days + 1):
            day_key = f"day_{day}"
            meals[day_key] = {}
            
            for meal_type in meal_types:
                # Rotate through available meals
                meal_index = (day - 1) % len(sample_meals[meal_type])
                meal_data = sample_meals[meal_type][meal_index]
                
                # Convert to Recipe object (simplified)
                meals[day_key][meal_type] = Recipe(
                    id=meal_data["id"],
                    title=meal_data["title"],
                    prep_time=meal_data["prep_time"],
                    dietary_tags=dietary_restrictions  # Simplified
                )
        
        return MealPlan(
            name=f"{days}-Day Meal Plan",
            duration_days=days,
            dietary_restrictions=dietary_restrictions,
            cuisine_preferences=cuisine_preferences,
            meals=meals
        )
    
    def get_nutrition_info(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Get nutrition information for a recipe."""
        # Mock nutrition data
        nutrition_db = {
            "1": {
                "calories": 450,
                "protein": "25g",
                "carbohydrates": "35g",
                "fat": "20g",
                "fiber": "3g",
                "sugar": "5g",
                "sodium": "600mg"
            },
            "2": {
                "calories": 320,
                "protein": "12g",
                "carbohydrates": "45g",
                "fat": "15g",
                "fiber": "8g",
                "sugar": "10g",
                "sodium": "300mg"
            }
        }
        
        return nutrition_db.get(recipe_id)
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Save user preferences."""
        # Mock implementation
        # In a real app, this would save to a database
        return True
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences."""
        # Mock implementation
        return {
            "dietary_restrictions": [],
            "cuisine_preferences": [],
            "favorite_recipes": []
        }

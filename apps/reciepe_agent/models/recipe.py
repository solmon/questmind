"""Recipe-related Pydantic models."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DietaryRestriction(str, Enum):
    """Enumeration of dietary restrictions."""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten-free"
    DAIRY_FREE = "dairy-free"
    NUT_FREE = "nut-free"
    KETO = "keto"
    PALEO = "paleo"
    LOW_CARB = "low-carb"
    LOW_FAT = "low-fat"
    LOW_SODIUM = "low-sodium"


class CuisineType(str, Enum):
    """Enumeration of cuisine types."""
    ITALIAN = "italian"
    CHINESE = "chinese"
    MEXICAN = "mexican"
    INDIAN = "indian"
    FRENCH = "french"
    JAPANESE = "japanese"
    THAI = "thai"
    MEDITERRANEAN = "mediterranean"
    AMERICAN = "american"
    FUSION = "fusion"


class Ingredient(BaseModel):
    """Model for a recipe ingredient."""
    name: str = Field(..., description="Name of the ingredient")
    amount: Optional[str] = Field(None, description="Amount/quantity")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    notes: Optional[str] = Field(None, description="Additional notes")


class NutritionInfo(BaseModel):
    """Model for nutritional information."""
    calories: Optional[int] = Field(None, description="Calories per serving")
    protein: Optional[str] = Field(None, description="Protein content")
    carbohydrates: Optional[str] = Field(None, description="Carbohydrate content")
    fat: Optional[str] = Field(None, description="Fat content")
    fiber: Optional[str] = Field(None, description="Fiber content")
    sugar: Optional[str] = Field(None, description="Sugar content")
    sodium: Optional[str] = Field(None, description="Sodium content")


class Recipe(BaseModel):
    """Model for a recipe."""
    id: str = Field(..., description="Unique recipe identifier")
    title: str = Field(..., description="Recipe title")
    description: Optional[str] = Field(None, description="Recipe description")
    cuisine: Optional[str] = Field(None, description="Cuisine type")
    prep_time: Optional[int] = Field(None, description="Preparation time in minutes")
    cook_time: Optional[int] = Field(None, description="Cooking time in minutes")
    total_time: Optional[int] = Field(None, description="Total time in minutes")
    servings: Optional[int] = Field(None, description="Number of servings")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    
    ingredients: List[Ingredient] = Field(default_factory=list, description="List of ingredients")
    instructions: List[str] = Field(default_factory=list, description="Cooking instructions")
    
    dietary_tags: List[str] = Field(default_factory=list, description="Dietary restriction tags")
    nutrition: Optional[NutritionInfo] = Field(None, description="Nutritional information")
    
    rating: Optional[float] = Field(None, description="Recipe rating")
    reviews_count: Optional[int] = Field(None, description="Number of reviews")
    
    source_url: Optional[str] = Field(None, description="Source URL")
    image_url: Optional[str] = Field(None, description="Recipe image URL")
    
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class RecipeQuery(BaseModel):
    """Model for recipe search queries."""
    query: str = Field(..., description="Search query")
    cuisine: Optional[str] = Field(None, description="Cuisine type filter")
    dietary_restrictions: Optional[List[str]] = Field(None, description="Dietary restrictions")
    max_prep_time: Optional[int] = Field(None, description="Maximum preparation time")
    max_cook_time: Optional[int] = Field(None, description="Maximum cooking time")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    max_results: int = Field(10, description="Maximum number of results")


class RecipeResponse(BaseModel):
    """Model for recipe search responses."""
    recipes: List[Recipe] = Field(default_factory=list, description="List of recipes")
    total_count: int = Field(0, description="Total number of matching recipes")
    query: str = Field(..., description="Original search query")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")


class IngredientSubstitution(BaseModel):
    """Model for ingredient substitutions."""
    original_ingredient: str = Field(..., description="Original ingredient")
    substitutes: List[str] = Field(default_factory=list, description="List of substitutes")
    notes: Optional[str] = Field(None, description="Substitution notes")
    ratio: Optional[str] = Field(None, description="Substitution ratio")


class MealPlan(BaseModel):
    """Model for meal plans."""
    id: Optional[str] = Field(None, description="Meal plan identifier")
    name: str = Field(..., description="Meal plan name")
    duration_days: int = Field(..., description="Duration in days")
    dietary_restrictions: List[str] = Field(default_factory=list, description="Dietary restrictions")
    cuisine_preferences: List[str] = Field(default_factory=list, description="Cuisine preferences")
    meals: Dict[str, Dict[str, Recipe]] = Field(default_factory=dict, description="Meals by day and type")
    shopping_list: Optional[List[Ingredient]] = Field(None, description="Generated shopping list")
    nutrition_summary: Optional[Dict[str, Any]] = Field(None, description="Nutrition summary")


class UserPreferences(BaseModel):
    """Model for user preferences."""
    user_id: str = Field(..., description="User identifier")
    dietary_restrictions: List[str] = Field(default_factory=list, description="Dietary restrictions")
    cuisine_preferences: List[str] = Field(default_factory=list, description="Preferred cuisines")
    disliked_ingredients: List[str] = Field(default_factory=list, description="Disliked ingredients")
    favorite_recipes: List[str] = Field(default_factory=list, description="Favorite recipe IDs")
    cooking_skill_level: Optional[str] = Field(None, description="Cooking skill level")
    max_prep_time: Optional[int] = Field(None, description="Maximum preferred prep time")
    serving_size_preference: Optional[int] = Field(None, description="Preferred serving size")

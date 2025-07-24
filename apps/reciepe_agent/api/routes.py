"""FastAPI routes for Recipe Agent."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.graph import run_recipe_agent


router = APIRouter(prefix="/api/v1", tags=["recipe-agent"])


class QueryRequest(BaseModel):
    """Request model for recipe queries."""
    query: str
    dietary_restrictions: Optional[List[str]] = None
    cuisine_preference: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for recipe queries."""
    success: bool
    message: str
    data: dict
    error: Optional[str] = None


@router.post("/query", response_model=QueryResponse)
async def query_recipe_agent(request: QueryRequest):
    """Query the recipe agent."""
    try:
        result = run_recipe_agent(
            query=request.query,
            dietary_restrictions=request.dietary_restrictions,
            cuisine_preference=request.cuisine_preference
        )
        
        # Extract relevant information from result
        response_data = {
            "intent": result.get("intent"),
            "recipes": result.get("recipes", []),
            "search_results": result.get("search_results", []),
            "recommendations": result.get("recommendations", []),
            "ingredient_substitutions": result.get("ingredient_substitutions", {}),
            "meal_plan": result.get("meal_plan"),
            "messages": [msg.content if hasattr(msg, 'content') else str(msg) 
                        for msg in result.get("messages", [])]
        }
        
        return QueryResponse(
            success=True,
            message="Query processed successfully",
            data=response_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "recipe-agent"}


@router.get("/recipes/search")
async def search_recipes_endpoint(
    q: str,
    cuisine: Optional[str] = None,
    dietary_restrictions: Optional[str] = None,
    max_results: int = 10
):
    """Search for recipes."""
    try:
        dietary_list = dietary_restrictions.split(",") if dietary_restrictions else []
        
        result = run_recipe_agent(
            query=f"search for {q}",
            dietary_restrictions=dietary_list,
            cuisine_preference=cuisine
        )
        
        return {
            "recipes": result.get("recipes", []),
            "total": len(result.get("recipes", []))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching recipes: {str(e)}"
        )


@router.get("/recipes/recommend")
async def recommend_recipes_endpoint(
    cuisine: Optional[str] = None,
    dietary_restrictions: Optional[str] = None,
    max_results: int = 5
):
    """Get recipe recommendations."""
    try:
        dietary_list = dietary_restrictions.split(",") if dietary_restrictions else []
        
        result = run_recipe_agent(
            query="recommend recipes",
            dietary_restrictions=dietary_list,
            cuisine_preference=cuisine
        )
        
        return {
            "recommendations": result.get("recommendations", []),
            "total": len(result.get("recommendations", []))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )


@router.post("/ingredients/substitute")
async def substitute_ingredient_endpoint(request: dict):
    """Find ingredient substitutions."""
    try:
        ingredient = request.get("ingredient")
        if not ingredient:
            raise HTTPException(status_code=400, detail="Ingredient is required")
        
        result = run_recipe_agent(
            query=f"substitute {ingredient}",
        )
        
        return {
            "substitutions": result.get("ingredient_substitutions", {}),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding substitutions: {str(e)}"
        )


@router.post("/meal-plan")
async def create_meal_plan_endpoint(request: dict):
    """Create a meal plan."""
    try:
        days = request.get("days", 7)
        dietary_restrictions = request.get("dietary_restrictions", [])
        
        result = run_recipe_agent(
            query=f"create a {days} day meal plan",
            dietary_restrictions=dietary_restrictions
        )
        
        return {
            "meal_plan": result.get("meal_plan"),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating meal plan: {str(e)}"
        )

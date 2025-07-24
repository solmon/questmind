"""Recipe Agent Graph Nodes."""
import os
from dotenv import load_dotenv

from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from agent.state import RecipeAgentState
from agent.tools import recipe_tools

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def classify_intent_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Classify the user's intent from their query."""
    user_query = state.get("user_query", "")
    
    # Simple intent classification logic
    query_lower = user_query.lower()
    
    if any(word in query_lower for word in ["search", "find", "recipe for", "how to make"]):
        intent = "search"
    elif any(word in query_lower for word in ["recommend", "suggest", "what should"]):
        intent = "recommend"
    elif any(word in query_lower for word in ["substitute", "replace", "instead of"]):
        intent = "substitute"
    elif any(word in query_lower for word in ["meal plan", "plan", "weekly", "menu"]):
        intent = "plan"
    elif any(word in query_lower for word in ["nutrition", "calories", "healthy"]):
        intent = "nutrition"
    else:
        intent = "general"
    
    return {
        "intent": intent,
        "processing_complete": False
    }


def search_recipes_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Search for recipes based on user query."""
    user_query = state.get("user_query", "")
    dietary_restrictions = state.get("dietary_restrictions", [])
    cuisine_preference = state.get("cuisine_preference")
    
    # Use the search_recipes tool
    from agent.tools import search_recipes
    
    try:
        results = search_recipes.invoke({
            "query": user_query,
            "cuisine": cuisine_preference,
            "dietary_restrictions": dietary_restrictions,
            "max_results": 5
        })
        
        return {
            "search_results": results,
            "recipes": results,
            "error_message": None
        }
    except Exception as e:
        return {
            "search_results": [],
            "recipes": [],
            "error_message": f"Error searching recipes: {str(e)}"
        }


def recommend_recipes_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Recommend recipes based on user preferences."""
    dietary_restrictions = state.get("dietary_restrictions", [])
    cuisine_preference = state.get("cuisine_preference")
    
    # For recommendations, we'll search with a general query
    from agent.tools import search_recipes
    
    try:
        results = search_recipes.invoke({
            "query": "popular",
            "cuisine": cuisine_preference,
            "dietary_restrictions": dietary_restrictions,
            "max_results": 3
        })
        
        return {
            "recommendations": results,
            "recipes": results,
            "error_message": None
        }
    except Exception as e:
        return {
            "recommendations": [],
            "recipes": [],
            "error_message": f"Error getting recommendations: {str(e)}"
        }


def substitute_ingredients_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Find ingredient substitutions."""
    user_query = state.get("user_query", "")
    
    # Extract ingredient from query (simple approach)
    # In a real implementation, you'd use NER or more sophisticated parsing
    ingredients_to_substitute = []
    
    # Simple keyword extraction
    words = user_query.lower().split()
    common_ingredients = ["eggs", "butter", "milk", "flour", "sugar", "cheese", "meat"]
    
    for ingredient in common_ingredients:
        if ingredient in user_query.lower():
            ingredients_to_substitute.append(ingredient)
    
    if not ingredients_to_substitute:
        # Try to extract from the query more generally
        for word in words:
            if len(word) > 3:  # Simple heuristic
                ingredients_to_substitute.append(word)
                break
    
    from agent.tools import find_ingredient_substitutions
    
    substitutions = {}
    for ingredient in ingredients_to_substitute[:3]:  # Limit to 3 ingredients
        try:
            result = find_ingredient_substitutions.invoke({
                "ingredient": ingredient,
                "recipe_context": user_query
            })
            substitutions[ingredient] = result
        except Exception as e:
            substitutions[ingredient] = {"error": str(e)}
    
    return {
        "ingredient_substitutions": substitutions,
        "error_message": None if substitutions else "No ingredients found to substitute"
    }


def create_meal_plan_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Create a meal plan."""
    dietary_restrictions = state.get("dietary_restrictions", [])
    user_query = state.get("user_query", "")
    
    # Extract duration from query (simple approach)
    days = 7  # default
    if "week" in user_query.lower():
        days = 7
    elif "day" in user_query.lower():
        # Try to extract number
        words = user_query.split()
        for i, word in enumerate(words):
            if word.isdigit():
                days = int(word)
                break
    
    from agent.tools import create_meal_plan
    
    try:
        meal_plan = create_meal_plan.invoke({
            "days": days,
            "dietary_restrictions": dietary_restrictions,
            "cuisine_preferences": None
        })
        
        return {
            "meal_plan": meal_plan,
            "error_message": None
        }
    except Exception as e:
        return {
            "meal_plan": None,
            "error_message": f"Error creating meal plan: {str(e)}"
        }


def llm_response_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Generate LLM response based on current state."""
    # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        transport="rest",  # Force REST API instead of gRPC
        client_options={"api_endpoint": "https://generativelanguage.googleapis.com"}
    )

    # Build context from state
    context_parts = []
    
    if state.get("recipes"):
        context_parts.append(f"Found {len(state['recipes'])} recipes")
    
    if state.get("search_results"):
        context_parts.append("Search results available")
    
    if state.get("recommendations"):
        context_parts.append("Recommendations available")
    
    if state.get("ingredient_substitutions"):
        context_parts.append("Ingredient substitutions available")
    
    if state.get("meal_plan"):
        context_parts.append("Meal plan created")
    
    if state.get("error_message"):
        context_parts.append(f"Error: {state['error_message']}")
    
    # Create system prompt
    system_prompt = """You are a helpful recipe assistant. You help users with:
    - Finding and recommending recipes
    - Suggesting ingredient substitutions
    - Creating meal plans
    - Providing cooking tips and nutrition information
    
    Be friendly, helpful, and specific in your responses. If you have specific recipe data, 
    include details like ingredients, cooking time, and instructions."""
    
    # Create user context
    user_query = state.get("user_query", "")
    context = " | ".join(context_parts) if context_parts else "No specific context"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"User query: {user_query}\nContext: {context}\n\nProvide a helpful response.")
    ])
    
    try:
        response = llm.invoke(prompt.format_messages())
        
        # Add to messages
        messages = state.get("messages", [])
        messages.append(AIMessage(content=response.content))
        
        return {
            "messages": messages,
            "processing_complete": True,
            "error_message": None
        }
    except Exception as e:
        return {
            "error_message": f"Error generating response: {str(e)}",
            "processing_complete": True
        }


def human_input_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Handle human input and update state."""
    # This node would typically be called when we need user input
    # For now, it's a placeholder
    return {
        "needs_user_input": False
    }

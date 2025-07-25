"""Recipe Agent Graph Nodes."""
import os
import sys
import asyncio
from dotenv import load_dotenv

from typing import Dict, Any
import re
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from agent.state import RecipeAgentState
from agent.tools import recipe_tools
from agent.tools import mock_recipes

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def classify_intent_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Classify the user's intent from their query."""
    user_query = state.get("user_query", "")
    
    # Simple intent classification logic
    query_lower = user_query.lower()
    
    if any(word in query_lower for word in ["search", "find", "recipe for", "how to make"]):
        intent = "search"
    else:
        intent = "general"
    
    return {
        "intent": intent,
        "workflow_stage": "initial",  # Initialize workflow stage
        "processing_complete": False
    }


def recipe_llm_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Dedicated LLM node for recipe search and refinement."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        transport="rest",
        client_options={"api_endpoint": "https://generativelanguage.googleapis.com"}
    )

    # Build context from state
    context_parts = []
    
    # if state.get("recipes"):
    #     recipes = state.get("recipes", [])
    #     context_parts.append(f"Found {len(recipes)} recipes")
    #     # Add recipe details for refinement
    #     for i, recipe in enumerate(recipes[:2]):
    #         context_parts.append(f"Recipe {i+1}: {recipe.get('title', 'Unknown')} - {len(recipe.get('ingredients', []))} ingredients")
    
    # if state.get("search_results"):
    #     context_parts.append("Search results available")
    
    # if state.get("error_message"):
    #     context_parts.append(f"Error: {state['error_message']}")
    
    # Create system prompt focused on recipes
    system_prompt = """You are a recipe specialist assistant. Your role is to:
    - Help users find and refine recipes
    - Provide detailed recipe information including ingredients, instructions, and cooking tips
    - Ask if the user wants to proceed with ingredient shopping once they're satisfied with a recipe

    When showing recipes, always ask if the user wants to:
    1. Refine or modify the recipe
    2. Search for a different recipe 
    3. Proceed with finding ingredients for this recipe

    Be friendly, detailed, and focus on the culinary aspects."""
    
    user_query = state.get("user_query", "")
    context = " | ".join(context_parts) if context_parts else "No specific context"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"User query: {user_query}\nContext: {context}\n\nProvide a helpful recipe-focused response.")
    ])
    
    try:
        # mock for reduce llm calls
        is_mock_recipes = True

        if is_mock_recipes:
            # Use mock recipes for demo purposes
            state["recipes"] = mock_recipes()

             # Print messages directly
            print(f"mocked the recipes:")
            
            return {
                "messages": [],
                "recipes": state["recipes"],
                "workflow_stage": "recipe_display",  # Set to recipe display stage for user confirmation
                "user_wants_ingredients": False,
                "needs_user_input": True,  # Require user input for confirmation
                "processing_complete": False,  # Don't complete, wait for user input
                "error_message": None
            }
        
        response = llm.invoke(prompt.format_messages())
        
        # Add to messages
        messages = state.get("messages", [])
        messages.append(AIMessage(content=response.content))
        # Try to extract recipes from the LLM response if present
        recipes = []
        if response and hasattr(response, "content"):
            # Simple heuristic: look for recipe titles and ingredients in the response
            recipe_blocks = re.findall(r"(?i)(recipe\s*[:\-]\s*.*?)(?:\n{2,}|$)", response.content, re.DOTALL)
            for block in recipe_blocks:
                title_match = re.search(r"(?i)recipe\s*[:\-]\s*(.*)", block)
                ingredients_match = re.findall(r"(?i)[•\-]\s*(.+)", block)
                if title_match:
                    title = title_match.group(1).strip()
                else:
                    title = "Recipe"
                recipes.append({
                    "title": title,
                    "ingredients": [i.strip() for i in ingredients_match] if ingredients_match else []
                })
        if recipes:
            state["recipes"] = recipes

        # Check if we have recipes to work with
        has_recipes = bool(state.get("recipes"))
        
        # Print messages directly
        for msg in messages:
            if hasattr(msg, 'content'):
                print(f"{type(msg).__name__}: {msg.content}")
            else:
                print(str(msg))

        return {
            "messages": messages,
            "workflow_stage": "recipe_display",  # Set to recipe display stage for user confirmation
            "user_wants_ingredients": False,
            "needs_user_input": True,  # Require user input for confirmation
            "processing_complete": False,  # Don't complete, wait for user input
            "error_message": None
        }
    except Exception as e:
        return {
            "error_message": f"Error in recipe LLM: {str(e)}",
            "processing_complete": True
        }


def ingredient_confirmation_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Display ingredients to user for confirmation before grocery search."""
    recipes = state.get("recipes", [])
    if not recipes:
        return {
            "error_message": "No recipes available for ingredient confirmation",
            "processing_complete": True
        }
    
    # Use the first/selected recipe
    selected_recipe = recipes[0]
    ingredients = selected_recipe.get("ingredients", [])
    
    if not ingredients:
        return {
            "error_message": "No ingredients found in the selected recipe",
            "processing_complete": True
        }
    
    # Create ingredient confirmation message
    ingredient_list = "\n".join([f"• {ingredient}" for ingredient in ingredients])
    confirmation_message = f"""
Here are the ingredients for {selected_recipe.get('title', 'the recipe')}:

{ingredient_list}

Would you like me to search for these ingredients in local grocery stores? 
You can say:
- "Yes" or "Proceed" to search for grocery items
- "Back" or "Change recipe" to go back to recipe search
- Modify specific ingredients if needed
"""
    # Print confirmation message directly
    print(confirmation_message)
    # Add confirmation message
    # messages = state.get("messages", [])
    # messages.append(AIMessage(content=confirmation_message))
    
    return {
        # "messages": messages,
        "selected_recipe": selected_recipe,
        "ingredients": ingredients,
        "workflow_stage": "ingredient_confirmation", 
        "needs_user_input": True,  # Auto-proceed for CLI demo
        "ingredients_confirmed": False,  # Auto-confirm for demo
        "processing_complete": False,
        "error_message": None
    }

async def grocery_llm_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Dedicated LLM node for grocery assistance using MCP tools."""
    from agent.graph import get_mcp_tools
    from agent.tools import recipe_tools

    # Get all available tools including MCP
    all_tools = recipe_tools.copy()
    mcp_tools = get_mcp_tools()
    if mcp_tools:
        all_tools.extend(mcp_tools)

    print(f"Using {len(all_tools)} tools for grocery search: {[tool.name for tool in all_tools]}")

    # Create LLM with tool binding for grocery search
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        transport="rest",
        client_options={"api_endpoint": "https://generativelanguage.googleapis.com"}
    )

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(all_tools)

    # Build context for grocery search
    ingredients = state.get("ingredients", [])
    selected_recipe = state.get("selected_recipe", {})

    context_parts = []
    if selected_recipe:
        context_parts.append(f"Recipe: {selected_recipe.get('title', 'Unknown')}")
    if ingredients:
        context_parts.append(f"Ingredients to search: {', '.join(ingredients[:5])}")

    # Create system prompt focused on grocery search
    system_prompt = f"""You are a grocery shopping assistant with access to {len(all_tools)} tools including MCP grocery store tools.

Your role is to:
- Search for recipe ingredients in local grocery stores using MCP tools available
- plan the actions on how to use the MCP tools
- Find the best prices and availability
- Show detailed product information including prices, stores, and availability
- Help users build their shopping cart

IMPORTANT: Use the available MCP grocery tools to search for each ingredient. Focus on:
1. Real store search using MCP tools
2. Price comparison across stores
3. Product availability and details
4. Clear presentation of shopping options

Available tools for grocery search: {[tool.name for tool in all_tools]}
prefferred location id for the store to tool is : 70300720
Always use tools to search for the ingredients and provide real grocery store results."""

    user_query = state.get("user_query", "")
    context = " | ".join(context_parts) if context_parts else "Ready to search for ingredients"

    print(f"Using system prompt: {system_prompt}")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"Please search for these ingredients in grocery stores: {', '.join(ingredients)}\nUser context: {user_query}\nAdditional context: {context}")
    ])

    try:
        # Get formatted messages
        formatted_messages = prompt.format_messages()

        # Call LLM with tools
        response = await llm_with_tools.ainvoke(formatted_messages)
        # response = None

        # Print response content
        print(f"LLM Response: {response.content}")

        # Add to messages
        messages = state.get("messages", [])
        messages.append(response)

        # Check if LLM wants to use tools
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_outputs = {}
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool = next((t for t in all_tools if t.name == tool_name), None)
                if tool:
                    try:
                        print(f"Invoking tool: {tool_name} with args: {tool_args}")
                        tool_result = await tool.ainvoke(tool_args)
                        print(f"Tool '{tool_name}' result: {tool_result}")
                        tool_outputs[tool_name] = tool_result
                    except Exception as tool_exc:
                        print(f"Error invoking tool '{tool_name}': {tool_exc}")
                        tool_outputs[tool_name] = {"error": str(tool_exc)}
                else:
                    print(f"Tool '{tool_name}' not found among available tools.")
                    tool_outputs[tool_name] = {"error": "Tool not found"}
            # Optionally, update searched_ingredients if tool results are ingredient searches
            searched_ingredients = []
            for result in tool_outputs.values():
                if isinstance(result, dict) and "product_id" in result:
                    searched_ingredients.append({
                        "name": result.get("title", "Unknown"),
                        "search_result": result
                    })
            state["tool_outputs"] = tool_outputs
            state["searched_ingredients"] = searched_ingredients
            return {
                "messages": messages,
                "tool_outputs": tool_outputs,
                "searched_ingredients": searched_ingredients,
                "workflow_stage": "grocery_search_complete",
                "needs_user_input": True,
                "processing_complete": False,
                "error_message": None
            }
        else:
            return {
                "messages": messages,
                "workflow_stage": "grocery_search_complete",
                "needs_user_input": True,
                "processing_complete": False,
                "error_message": None
            }

    except Exception as e:
        return {
            "error_message": f"Error in grocery LLM: {str(e)}",
            "processing_complete": True
        }


def cart_confirmation_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Show grocery search results and ask for cart confirmation."""
    searched_ingredients = state.get("searched_ingredients", [])
    tool_outputs = state.get("tool_outputs", {})
    
    if not searched_ingredients and not tool_outputs:
        return {
            "error_message": "No grocery search results available for cart confirmation",
            "processing_complete": True
        }
    
    # Build confirmation message from search results
    confirmation_parts = ["Here are the grocery items I found:\n"]
    
    total_estimated_cost = 0.0
    item_count = 0
    
    # Process searched ingredients or tool outputs
    if searched_ingredients:
        for item in searched_ingredients[:10]:  # Limit display
            name = item.get("name", "Unknown item")
            search_result = item.get("search_result", {})
            price = search_result.get("price", "N/A")
            store = search_result.get("store_name", search_result.get("store", "Unknown store"))
            availability = search_result.get("availability", "Unknown")
            
            confirmation_parts.append(f"• {name}: {price} at {store} ({availability})")
            
            # Try to calculate total
            if price and price.startswith("$"):
                try:
                    total_estimated_cost += float(price.replace("$", ""))
                    item_count += 1
                except:
                    pass
    
    if tool_outputs:
        confirmation_parts.append(f"\nTool search results: {len(tool_outputs)} searches completed")
    
    confirmation_parts.append(f"\nEstimated total: ${total_estimated_cost:.2f} for {item_count} items")
    confirmation_parts.append("\nWould you like to add these items to your cart?")
    confirmation_parts.append("Say 'Yes' to add to cart, 'Back' to search again, or 'Cancel' to start over.")
    
    confirmation_message = "\n".join(confirmation_parts)
    
    # Add confirmation message
    messages = state.get("messages", [])
    messages.append(AIMessage(content=confirmation_message))
    
    return {
        "messages": messages,
        "workflow_stage": "cart_confirmation",
        "needs_user_input": False,  # Auto-proceed for demo
        "grocery_items_confirmed": True,  # Auto-confirm for demo
        "processing_complete": False,
        "error_message": None
    }


def add_to_cart_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Add confirmed grocery items to cart."""
    searched_ingredients = state.get("searched_ingredients", [])
    
    if not searched_ingredients:
        return {
            "error_message": "No grocery items to add to cart",
            "processing_complete": True
        }
    
    # Simulate adding items to cart
    cart_items = []
    total_cost = 0.0
    
    for item in searched_ingredients:
        search_result = item.get("search_result", {})
        price_str = search_result.get("price", "$0.00")
        
        # Extract price
        try:
            price = float(price_str.replace("$", ""))
            total_cost += price
        except:
            price = 0.0
        
        cart_items.append({
            "name": item.get("name", "Unknown"),
            "price": price_str,
            "store": search_result.get("store_name", search_result.get("store", "Unknown")),
            "product_id": search_result.get("product_id", f"prod_{hash(item.get('name', '')) % 10000}")
        })
    
    # Create cart result
    cart_result = {
        "success": True,
        "cart_id": f"cart_{hash(str(cart_items)) % 100000}",
        "items": cart_items,
        "item_count": len(cart_items),
        "total_cost": f"${total_cost:.2f}",
        "store_info": "Multiple stores available",
        "checkout_url": "https://grocery-stores.com/checkout"
    }
    
    # Create success message
    success_message = f"""✅ Successfully added {len(cart_items)} items to your cart!

Cart Summary:
• Total items: {len(cart_items)}
• Estimated total: ${total_cost:.2f}
• Cart ID: {cart_result['cart_id']}

Your ingredients are ready for checkout. You can proceed to the stores or use online delivery options.

Thank you for using the Recipe Agent! 🛒👨‍🍳"""
    
    # Add success message
    messages = state.get("messages", [])
    messages.append(AIMessage(content=success_message))
    
    return {
        "messages": messages,
        "ingredients_to_cart": cart_items,
        "tool_outputs": {"cart_result": cart_result},
        "workflow_stage": "completed",
        "processing_complete": True,
        "error_message": None
    }


def human_input_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Handle human input and update state."""
    # In a real implementation, this would capture actual user input
    # display the current stage of the agent in the stdio
    print("\n🍽️ Recipe Agent Stage:")
    workflow_stage = state.get("workflow_stage", "hellooooo")
    print(f"  {workflow_stage}")
    # Capture user input from stdio
    user_input = input("Your response: ").strip()
    if user_input:
        return {
            "user_query": user_input,
            "needs_user_input": False
        }

    return {
        "needs_user_input": False,
        "processing_complete": True
    }

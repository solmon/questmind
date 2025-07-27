"""Recipe Agent Graph Nodes."""
import os
import sys
import asyncio
from dotenv import load_dotenv

from typing import Dict, Any

import re
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.state import RecipeAgentState
from agent.tools import recipe_tools
from agent.tools import mock_recipes
# context7 prompt imports
from prompts.system_prompts import RECIPE_SYSTEM_PROMPT, GROCERY_SYSTEM_PROMPT, RECIPE_PLAN_SYSTEM_PROMPT, GROCERY_EXEC_SYSTEM_PROMPT
from prompts.chat_prompts import RECIPE_CHAT_PROMPT, GROCERY_CHAT_PROMPT, RECIPE_ARTICLE_CHAT_PROMPT, GROCERY_EXEC_CHAT_PROMPT

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

# --- Modularized LLM Node Logic ---
def _select_llm_prompts_and_tools(state: RecipeAgentState):
    """Selects the correct prompt templates and tools for the current workflow stage."""
    
    from agent.graph import get_mcp_tools
    workflow_stage = state.get("workflow_stage", "recipe_llm")
    user_query = state.get("user_query", "")
    context_parts = []
    all_tools = recipe_tools.copy()

    if workflow_stage in ["recipe_execution", "grocery_llm", "grocery_searching", "grocery_search_complete"]:
        mcp_tools = get_mcp_tools()
        if mcp_tools:
            all_tools.extend(mcp_tools)
        # selected_recipe = state.get("selected_recipe", {})
        recipe_plan = state.get("plan_extract", {})
        # ingredients = state.get("ingredients", [])
        # if selected_recipe:
        #     context_parts.append(f"Recipe: {selected_recipe.get('title', 'Unknown')}")
        # if ingredients:
        #     context_parts.append(f"Ingredients to search: {', '.join(ingredients[:5])}")
        # context = " | ".join(context_parts) if context_parts else "Ready to search for ingredients"
        
        tool_names = ", ".join([tool.name for tool in all_tools])
        num_tools = len(all_tools)
        rendered_prompt = [
            GROCERY_EXEC_SYSTEM_PROMPT.format(num_tools=num_tools, tool_names=tool_names),
            GROCERY_EXEC_CHAT_PROMPT.format(user_query=recipe_plan)
        ]
        return rendered_prompt, all_tools, "execute"
    elif workflow_stage in ["recipe_planning"]:
        mcp_tools = get_mcp_tools()
        if mcp_tools:
            all_tools.extend(mcp_tools)
        tool_names = ", ".join([tool.name for tool in all_tools])
        num_tools = len(all_tools)
        context = " | ".join(context_parts) if context_parts else "No specific context"
        rendered_prompt = [
            RECIPE_PLAN_SYSTEM_PROMPT.format(num_tools=num_tools, tool_names=tool_names),
            RECIPE_ARTICLE_CHAT_PROMPT.format(selected_recipe=state.get("selected_recipe", {}), context=context)
        ]
        return rendered_prompt, all_tools, "plan"
    else:        
        context = " | ".join(context_parts) if context_parts else "No specific context"
        rendered_prompt = [
            RECIPE_SYSTEM_PROMPT.format(),
            RECIPE_CHAT_PROMPT.format(user_query=user_query, context=context)
        ]
        return rendered_prompt, all_tools, "recipe"

async def _invoke_llm_with_tools(llm, rendered_prompt, tools=None):
    """Invoke the LLM, binding tools if provided."""
    if tools:
        llm = llm.bind_tools(tools)
        print("Invoking LLM asynchronously with tools...")
        return llm.invoke(rendered_prompt)                
    else:
        # No tools, just invoke with the prompt
        print(f"Invoking LLM with prompt: {rendered_prompt}")
        return llm.invoke(rendered_prompt)       

def _extract_recipes_from_response(response):
    """Extract recipes from LLM response content."""
    recipes = []
    if response and hasattr(response, "content"):
        content = response.content
        # Try to extract title from the first line or bolded heading
        title_match = re.search(r"^(.*?recipe.*?)\n", content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Fallback: use first non-empty line
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            title = lines[0] if lines else "Recipe"
        # # Extract ingredients section (markdown style)
        # ingredients_section = re.search(r"\*\*Ingredients:\*\*(.*?)(\*\*Instructions:\*\*|$)", content, re.DOTALL | re.IGNORECASE)
        # ingredients = []
        # if ingredients_section:
        #     ingredients_text = ingredients_section.group(1)
        #     # Match markdown bullet points
        #     ingredients = re.findall(r"^\s*[\*\-•]\s+(.*)", ingredients_text, re.MULTILINE)
        #     # Remove bolded subheadings (e.g., **For the Lamb Filling:**)
        #     ingredients = [i for i in ingredients if not re.match(r"\*\*.*\*\*:", i)]
        recipes.append({
            "title": title,
            "recipe_msg": response.content
            # "title": title,
            # "ingredients": [i.strip() for i in ingredients] if ingredients else []
        })
    return recipes

async def llm_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Unified and modular LLM node for both recipe and grocery workflow stages."""
    # Select prompts and tools
    rendered_prompt, all_tools, mode = _select_llm_prompts_and_tools(state)
    user_query = state.get("user_query", "")
    # LLM setup
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        transport="rest",
        client_options={"api_endpoint": "https://generativelanguage.googleapis.com"}
    )
    try:
        # Mock for recipe mode
        if mode == "recipe":
            is_mock_recipes = False
            if is_mock_recipes:
                state["recipes"] = mock_recipes()
                print(f"mocked the recipes:")
                return {
                    "messages": [],
                    "recipes": state["recipes"],
                    "workflow_stage": "recipe_display",
                    "user_wants_ingredients": False,
                    "needs_user_input": True,
                    "processing_complete": False,
                    "error_message": None
                }
        
        # LLM invocation
        response = await _invoke_llm_with_tools(llm, rendered_prompt, all_tools if mode in ["plan","execute"] else None)
        # print(f"LLM Response: {getattr(response, 'content', response)}")
        messages = state.get("messages", [])
        if mode == "recipe":
            messages.append(AIMessage(content=response.content))
            recipes = _extract_recipes_from_response(response)
            if recipes:
                state["recipes"] = recipes
            for msg in messages:
                if hasattr(msg, 'content'):
                    print(f"{type(msg).__name__}: {msg.content}")
                else:
                    print(str(msg))
            return {
                "messages": messages,
                "recipes": state["recipes"],
                "workflow_stage": "recipe_display",
                "user_wants_ingredients": False,
                "needs_user_input": True,
                "processing_complete": False,
                "error_message": None
            }
        elif mode == "plan":
            messages.append(AIMessage(content=response.content))
            plan_extract = response.content
            
            return {
                "messages": messages,
                "workflow_stage": "recipe_plan_display",
                "plan_extract": plan_extract,
                "recipe_plan_confirmed": False                
            }
        elif mode == "execute":
            messages.append(AIMessage(content=response.content))    
            if hasattr(response, 'tool_calls') and response.tool_calls:                
                # Iterate over all tool_calls, invoke the tool, and capture the output
                tool_outputs = {}
                # for tool_call in response.tool_calls:
                #     tool_name = tool_call.get("name")
                #     tool_args = tool_call.get("args", {})
                #     # Find the tool by name
                #     tool = next((t for t in all_tools if t.name == tool_name), None)
                #     if tool:
                #         try:
                #             # context7: invoke tool and capture output
                #             output = await asyncio.to_thread(tool, **tool_args)
                #             tool_outputs[tool_name] = output
                #             print(f"Tool '{tool_name}' output: {output}")
                #         except Exception as e:
                #             tool_outputs[tool_name] = f"Error: {str(e)}"
                #             print(f"Error invoking tool '{tool_name}': {e}")
                #     else:
                #         tool_outputs[tool_name] = "Tool not found"
                #         print(f"Tool '{tool_name}' not found in available tools.")
                # messages.append(AIMessage(content="Executed all tool calls."))
                # state["tool_outputs"] = tool_outputs
                return {
                    "messages": messages,
                    "workflow_stage": "recipe_execution",
                    "needs_user_input": True,
                    "processing_complete": False,
                    "error_message": None
                }

            return {
                "messages": messages,
                "workflow_stage": "recipe_execution",               
                "processing_complete": False,
                "error_message": None
            }
        else:
            messages.append(response)
            if hasattr(response, 'tool_calls') and response.tool_calls:
                return {
                    "messages": messages,
                    "workflow_stage": "grocery_searching",
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
            "error_message": f"Error in LLM node: {str(e)}",
            "processing_complete": True
        }


def recipe_confirmation_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Display ingredients to user for confirmation before grocery search."""
    recipes = state.get("recipes", [])
    if not recipes:
        return {
            "error_message": "No recipes available for ingredient confirmation",
            "processing_complete": True
        }

    selected_recipe = state.get("selected_recipe", recipes[0] if recipes else {})
    # ingredients = state.get("ingredients", [])
    # ingredient_list = "\n".join([f"• {ingredient}" for ingredient in ingredients])


    confirmation_message = f"""
Here is the reciepe for {selected_recipe.get('title', 'the recipe')}:

{selected_recipe.get('recipe_msg', 'No recipe details available')}

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
        "workflow_stage": "recipe_confirmation", 
        "recipe_confirmed": False,  # Auto-confirm for demo        
    }

def recipe_plan_confirm_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Display ingredients to user for confirmation before grocery search."""
    recipes = state.get("plan_extract", {})
    if not recipes:
        return {
            "error_message": "No plan available for display",
            "processing_complete": True
        }

    selected_recipe = state.get("selected_recipe",{})

    # selected_recipe = state.get("selected_recipe", recipes[0] if recipes else {})
    # ingredients = state.get("ingredients", [])
    # ingredient_list = "\n".join([f"• {ingredient}" for ingredient in ingredients])


    confirmation_message = f"""
Here is the plan for reciepe execution for {selected_recipe.get('title', 'the recipe')}:

{recipes}

Would you like me to proceed with executing the plan? 
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
        "workflow_stage": "recipe_plan_display", 
        "recipe_plan_confirmed": False,  # Auto-confirm for demo        
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
    workflow_stage = state.get("workflow_stage", "recipe_search")
    print(f"Current workflow stage: {workflow_stage}")
    # Capture user input from stdio
    user_input = input("Your response: ").strip()


    if workflow_stage == "recipe_confirmation" and user_input in ["yes", "proceed", "continue"]:
        return {
            "recipe_confirmed": True,
            "workflow_stage": "recipe_planning",
            "user_query": user_input           
        }
    elif workflow_stage == "recipe_plan_display" and user_input in ["yes", "proceed", "confirm", "continue"]:
        return {
            "recipe_plan_confirmed": True,
            "workflow_stage": "recipe_execution",
            "user_query": user_input           
        }
    else:    
        return {
            "user_query": user_input
        }


# Add a new node for human approval before adding to cart
def human_approval_node(state: RecipeAgentState) -> dict:
    """Ask user to approve found grocery items before adding to cart."""
    searched_ingredients = state.get("searched_ingredients", [])
    tool_outputs = state.get("tool_outputs", {})
    if not searched_ingredients and not tool_outputs:
        return {
            "error_message": "No grocery search results available for approval",
            "processing_complete": True
        }
    # Build approval message
    approval_parts = ["Here are the grocery items I found:"]
    for item in searched_ingredients[:10]:
        name = item.get("name", "Unknown item")
        search_result = item.get("search_result", {})
        price = search_result.get("price", "N/A")
        store = search_result.get("store_name", search_result.get("store", "Unknown store"))
        approval_parts.append(f"• {name}: {price} at {store}")
    approval_parts.append("\nWould you like to add these items to your cart? (yes/no)")
    approval_message = "\n".join(approval_parts)
    print(approval_message)
    user_input = input("Approve items for cart? (yes/no): ").strip().lower()
    approved = user_input in ["yes", "y"]
    return {
        "messages": state.get("messages", []),
        "searched_ingredients": searched_ingredients,
        "tool_outputs": tool_outputs,
        "workflow_stage": "human_approval",
        "needs_user_input": False,
        "grocery_items_confirmed": approved,
        "processing_complete": False,
        "error_message": None
    }
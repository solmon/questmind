"""Main entry point for Recipe Agent."""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agent.graph import run_recipe_agent, recipe_agent, run_recipe_agent_with_mcp
from api.routes import router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Recipe Agent API",
    description="A LangGraph-based AI agent for recipe management and cooking assistance",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Recipe Agent API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


def run_cli():
    """Run the CLI interface."""
    print("🍳 Enhanced Recipe Agent CLI")
    print("=" * 50)
    print("Features:")
    print("• Separate Recipe and Grocery LLM assistants")
    print("• Structured workflow with confirmation points")
    print("• Real grocery store integration via MCP")
    print("• Can go back to recipe search anytime")
    print("=" * 50)
    print("Ask me to find recipes and I'll help you get the ingredients!")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Happy cooking!")
                break
            
            if not user_input:
                continue
            
            print("🤔 Processing working for you...")
            
            # Run the enhanced agent
            # result = run_recipe_agent(user_input)
            result = asyncio.run(run_recipe_agent_with_mcp(user_input))

            # Extract and display the response
            messages = result.get("display_messages", [])
            if messages:
                print(f"\n📝 Conversation ({len(messages)} messages):")
                for i, message in enumerate(messages):
                    if hasattr(message, 'content'):
                        print(f"\n🍽️ Recipe Agent: {message.content}")
                    else:
                        print(f"\n🍽️ Recipe Agent: {str(message)}")
            
            # Display workflow information
            workflow_stage = result.get("workflow_stage", "Not set")
            print(f"\n📊 Workflow Stage: {workflow_stage}")
            
            # Display additional information if available
            if result.get("recipes"):
                recipes = result.get("recipes", [])
                print(f"📚 Found {len(recipes)} recipes")
                for i, recipe in enumerate(recipes[:2]):  # Show first 2
                    print(f"   {i+1}. {recipe.get('title', 'Unknown')}")
                    ingredients = recipe.get('ingredients', [])
                    print(f"      Ingredients: {len(ingredients)} items")
                
            if result.get("searched_ingredients"):
                print(f"🛒 Found {len(result['searched_ingredients'])} grocery items")
                for ingredient in result['searched_ingredients'][:3]:  # Show first 3
                    search_result = ingredient.get('search_result', {})
                    print(f"  • {ingredient['name']}: {search_result.get('price', 'N/A')} at {search_result.get('store_name', search_result.get('store', 'Unknown'))}")
            
            if result.get("ingredients_to_cart"):
                cart_result = result.get("tool_outputs", {}).get("cart_result", {})
                print(f"🛍️ Added {cart_result.get('item_count', 0)} items to cart")
                print(f"💰 Total: {cart_result.get('total_cost', 'N/A')}")
                print(f"🆔 Cart ID: {cart_result.get('cart_id', 'N/A')}")
            
            # Show workflow state
            state_info = []
            if result.get("user_wants_ingredients"):
                state_info.append("User wants ingredients")
            if result.get("ingredients_confirmed"):
                state_info.append("Ingredients confirmed")
            if result.get("grocery_items_confirmed"):
                state_info.append("Cart items confirmed")
            
            if state_info:
                print(f"🔄 Status: {' → '.join(state_info)}")
            
            if result.get("error_message"):
                print(f"❌ Error: {result['error_message']}")
            
            print("-" * 70)
            
        except KeyboardInterrupt:
            print("\n👋 Happy cooking!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "cli":
            run_cli()
        elif command == "serve":
            # Start the FastAPI server
            host = os.getenv("API_HOST", "0.0.0.0")
            port = int(os.getenv("API_PORT", "8000"))
            uvicorn.run(app, host=host, port=port, reload=True)
        elif command == "dev":
            # Development mode
            print("🚀 Starting Recipe Agent in development mode...")
            run_cli()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: cli, serve, dev")
    else:
        # Default to CLI
        run_cli()


if __name__ == "__main__":
    main()

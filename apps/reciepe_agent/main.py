"""Main entry point for Recipe Agent."""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agent.graph import run_recipe_agent, recipe_agent
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
    print("🍳 Recipe Agent CLI")
    print("=" * 50)
    print("Ask me anything about recipes, cooking, meal planning, or ingredient substitutions!")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Happy cooking!")
                break
            
            if not user_input:
                continue
            
            print("🤔 Thinking...")
            
            # Run the agent
            result = run_recipe_agent(user_input)
            
            # Extract and display the response
            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    print(f"\n🍽️ Recipe Agent: {last_message.content}\n")
                else:
                    print(f"\n🍽️ Recipe Agent: {str(last_message)}\n")
            
            # Display additional information if available
            if result.get("recipes"):
                print(f"📚 Found {len(result['recipes'])} recipes")
            
            if result.get("meal_plan"):
                print("📅 Meal plan created")
            
            if result.get("ingredient_substitutions"):
                print("🔄 Ingredient substitutions found")
            
            if result.get("error_message"):
                print(f"❌ Error: {result['error_message']}")
            
            print("-" * 50)
            
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

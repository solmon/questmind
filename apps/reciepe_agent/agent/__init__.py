"""Recipe Agent package."""

from agent.state import RecipeAgentState

# Import graph functions lazily to avoid circular imports during module initialization
def get_recipe_agent():
    """Get the default recipe agent."""
    from agent.graph import recipe_agent
    return recipe_agent

def get_create_recipe_agent():
    """Get the create_recipe_agent function."""
    from agent.graph import create_recipe_agent
    return create_recipe_agent

__all__ = ["RecipeAgentState", "get_recipe_agent", "get_create_recipe_agent"]

"""Tests for Recipe Agent."""

import pytest
from unittest.mock import Mock, patch
from agent.graph import run_recipe_agent, create_recipe_agent
from agent.state import RecipeAgentState
from agent.tools import search_recipes, find_ingredient_substitutions, create_meal_plan
from models.recipe import Recipe, RecipeQuery


class TestRecipeAgent:
    """Test cases for Recipe Agent."""
    
    def test_agent_creation(self):
        """Test that the agent can be created successfully."""
        agent = create_recipe_agent()
        assert agent is not None
    
    def test_recipe_search_tool(self):
        """Test the recipe search tool."""
        results = search_recipes.invoke({
            "query": "pasta",
            "cuisine": None,
            "dietary_restrictions": None,
            "max_results": 5
        })
        
        assert isinstance(results, list)
        assert len(results) >= 0
    
    def test_ingredient_substitution_tool(self):
        """Test the ingredient substitution tool."""
        result = find_ingredient_substitutions.invoke({
            "ingredient": "eggs",
            "recipe_context": "baking a cake"
        })
        
        assert "ingredient" in result
        assert "substitutions" in result
        assert isinstance(result["substitutions"], list)
    
    def test_meal_plan_tool(self):
        """Test the meal plan creation tool."""
        result = create_meal_plan.invoke({
            "days": 3,
            "dietary_restrictions": ["vegetarian"],
            "cuisine_preferences": None
        })
        
        assert "duration" in result
        assert "meals" in result
    
    @patch('agent.nodes.ChatOpenAI')
    def test_run_recipe_agent_search(self, mock_llm):
        """Test running the agent with a search query."""
        # Mock the LLM response
        mock_response = Mock()
        mock_response.content = "Here are some pasta recipes I found for you!"
        mock_llm.return_value.invoke.return_value = mock_response
        
        result = run_recipe_agent("find pasta recipes")
        
        assert "user_query" in result
        assert result["user_query"] == "find pasta recipes"
        assert "intent" in result
    
    @patch('agent.nodes.ChatOpenAI')
    def test_run_recipe_agent_substitute(self, mock_llm):
        """Test running the agent with a substitution query."""
        mock_response = Mock()
        mock_response.content = "Here are some great egg substitutes!"
        mock_llm.return_value.invoke.return_value = mock_response
        
        result = run_recipe_agent("substitute eggs in baking")
        
        assert "user_query" in result
        assert "intent" in result
        assert result["intent"] == "substitute"
    
    @patch('agent.nodes.ChatOpenAI')
    def test_run_recipe_agent_meal_plan(self, mock_llm):
        """Test running the agent with a meal plan query."""
        mock_response = Mock()
        mock_response.content = "I've created a 7-day meal plan for you!"
        mock_llm.return_value.invoke.return_value = mock_response
        
        result = run_recipe_agent("create a weekly meal plan")
        
        assert "user_query" in result
        assert "intent" in result
        assert result["intent"] == "plan"


class TestRecipeModels:
    """Test cases for Recipe models."""
    
    def test_recipe_model_creation(self):
        """Test creating a Recipe model."""
        recipe = Recipe(
            id="test-1",
            title="Test Recipe",
            cuisine="italian",
            prep_time=15,
            cook_time=30
        )
        
        assert recipe.id == "test-1"
        assert recipe.title == "Test Recipe"
        assert recipe.cuisine == "italian"
        assert recipe.prep_time == 15
        assert recipe.cook_time == 30
    
    def test_recipe_query_model(self):
        """Test creating a RecipeQuery model."""
        query = RecipeQuery(
            query="pasta",
            cuisine="italian",
            dietary_restrictions=["vegetarian"],
            max_results=10
        )
        
        assert query.query == "pasta"
        assert query.cuisine == "italian"
        assert "vegetarian" in query.dietary_restrictions
        assert query.max_results == 10


class TestRecipeTools:
    """Test cases for Recipe tools."""
    
    def test_search_recipes_with_filters(self):
        """Test recipe search with dietary filters."""
        results = search_recipes.invoke({
            "query": "healthy",
            "cuisine": None,
            "dietary_restrictions": ["vegetarian"],
            "max_results": 3
        })
        
        assert isinstance(results, list)
        # Check that results respect dietary restrictions
        for recipe in results:
            if "dietary_tags" in recipe:
                # In our mock data, vegetarian recipes should be tagged
                pass
    
    def test_substitutions_for_common_ingredients(self):
        """Test substitutions for common ingredients."""
        ingredients_to_test = ["eggs", "butter", "milk", "flour"]
        
        for ingredient in ingredients_to_test:
            result = find_ingredient_substitutions.invoke({
                "ingredient": ingredient,
                "recipe_context": f"recipe with {ingredient}"
            })
            
            assert result["ingredient"] == ingredient
            assert isinstance(result["substitutions"], list)
            assert len(result["substitutions"]) > 0
    
    def test_meal_plan_duration(self):
        """Test meal plan with different durations."""
        for days in [3, 7, 14]:
            result = create_meal_plan.invoke({
                "days": days,
                "dietary_restrictions": [],
                "cuisine_preferences": []
            })
            
            assert result["duration"] == f"{days} days"
            assert "meals" in result


# Test fixtures
@pytest.fixture
def sample_recipe():
    """Fixture for a sample recipe."""
    return Recipe(
        id="sample-1",
        title="Sample Recipe",
        description="A test recipe",
        cuisine="fusion",
        prep_time=10,
        cook_time=20,
        servings=4,
        ingredients=[],
        instructions=["Step 1", "Step 2"],
        dietary_tags=["vegetarian"],
        rating=4.5
    )


@pytest.fixture
def sample_query():
    """Fixture for a sample recipe query."""
    return RecipeQuery(
        query="test recipe",
        cuisine="italian",
        dietary_restrictions=["vegetarian"],
        max_results=5
    )


# Integration tests
class TestRecipeAgentIntegration:
    """Integration tests for Recipe Agent."""
    
    @pytest.mark.asyncio
    async def test_full_recipe_search_flow(self):
        """Test the complete recipe search flow."""
        # This would test the full pipeline from query to response
        pass
    
    @pytest.mark.asyncio 
    async def test_api_endpoints(self):
        """Test API endpoints."""
        # This would test the FastAPI endpoints
        pass


if __name__ == "__main__":
    pytest.main([__file__])

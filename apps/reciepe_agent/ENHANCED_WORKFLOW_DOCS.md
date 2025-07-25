# Enhanced Recipe Agent - Separate LLM Nodes & Structured Workflow

## Overview

The Recipe Agent has been enhanced with a sophisticated workflow that uses **separate specialized LLM nodes** for different tasks and provides **structured user confirmation points** throughout the process.

## Key Enhancements

### 1. Separate LLM Nodes
- **Recipe LLM Node**: Specialized for recipe search, refinement, and culinary expertise
- **Grocery LLM Node**: Specialized for grocery shopping with MCP tools integration

### 2. Structured Workflow with Confirmation Points
- Users can refine recipes before proceeding
- Clear ingredient confirmation step
- Grocery search results confirmation
- Ability to go back to recipe search at any point

### 3. MCP Tools Integration
- Grocery LLM uses MCP tools for real grocery store searches
- Real-time price and availability information
- Multiple store comparisons

## Workflow Stages

### Stage 1: Recipe Search & Refinement
```
User Query → Intent Classification → Recipe Search → Recipe LLM
                                                        ↓
User can: Refine recipe | Search new recipe | Proceed with ingredients
```

**Recipe LLM Features:**
- Focused on culinary expertise
- Provides detailed recipe information
- Suggests modifications and alternatives
- Asks if user wants to proceed with ingredient shopping

### Stage 2: Ingredient Confirmation
```
Recipe LLM → Ingredient Confirmation Node → User Confirmation
                                              ↓
User can: Confirm ingredients | Go back to recipes | Modify ingredients
```

**Features:**
- Displays all recipe ingredients clearly
- Allows ingredient modifications
- User can return to recipe search
- Proceeds only with explicit confirmation

### Stage 3: Grocery Search & MCP Integration
```
Confirmed Ingredients → Grocery LLM + MCP Tools → Store Search → Results
                                                                    ↓
User can: Confirm cart items | Search again | Go back to recipes
```

**Grocery LLM Features:**
- Uses MCP tools for real store searches
- Provides price comparisons
- Shows availability and store locations
- Intelligent tool selection for grocery searches

### Stage 4: Cart Management & Completion
```
Confirmed Items → Add to Cart → Cart Summary → Workflow Complete
```

**Features:**
- Adds items to shopping cart
- Provides cart summary with total cost
- Generates cart ID for checkout
- Completes the workflow

## Technical Implementation

### State Management
```python
class RecipeAgentState(TypedDict):
    # Workflow control
    workflow_stage: Optional[str]  # "recipe_search", "ingredient_confirmation", etc.
    user_wants_ingredients: Optional[bool]
    ingredients_confirmed: Optional[bool] 
    grocery_items_confirmed: Optional[bool]
    
    # Data
    recipes: List[Dict]
    ingredients: List[str]
    searched_ingredients: List[Dict]
    ingredients_to_cart: List[Dict]
```

### Graph Structure
```
classify_intent → search_recipes → recipe_llm → human_input
                                      ↓              ↑
                               ingredient_confirmation
                                      ↓              ↑
                               grocery_llm → tools → cart_confirmation
                                              ↓              ↑
                                          add_to_cart → END
```

### Routing Logic
- **Flexible Routing**: Users can go back to recipe search from any stage
- **Stage-Based Decisions**: Routing based on current workflow stage and user responses
- **Tool Calling**: Grocery LLM automatically calls MCP tools when needed

## LLM Node Specialization

### Recipe LLM Node
```python
system_prompt = """You are a recipe specialist assistant. Your role is to:
- Help users find and refine recipes
- Provide detailed recipe information including ingredients, instructions, and cooking tips
- Suggest recipe modifications and alternatives
- Ask if the user wants to proceed with ingredient shopping once they're satisfied

Focus on culinary expertise and recipe refinement."""
```

### Grocery LLM Node
```python
system_prompt = """You are a grocery shopping assistant with access to MCP grocery store tools.
Your role is to:
- Search for recipe ingredients in local grocery stores using MCP tools
- Find the best prices and availability
- Show detailed product information including prices, stores, and availability
- Help users build their shopping cart

Use MCP tools for real store searches and provide accurate shopping information."""
```

## Usage Examples

### Basic Recipe Search
```python
# User starts with recipe search
result = run_recipe_agent("Find me a recipe for chicken carbonara")

# Workflow progresses through:
# 1. Recipe search and display
# 2. User confirmation for ingredients
# 3. Grocery search using MCP tools
# 4. Cart confirmation and addition
```

### With MCP Tools
```python
# Enhanced with real grocery store integration
result = await run_recipe_agent_with_mcp("I want to make pasta and buy ingredients")

# MCP tools provide:
# - Real store searches
# - Actual prices and availability
# - Multiple store comparisons
```

### Conversation Flow Example
```
User: "Find me a recipe for chicken carbonara"
Recipe LLM: [Shows recipe details] "Would you like to proceed with finding ingredients?"

User: "Yes, get the ingredients"
System: [Shows ingredient list] "Confirm these ingredients for grocery search?"

User: "Yes"
Grocery LLM: [Uses MCP tools] "Found ingredients at 3 stores. Walmart has best prices."

User: "Add to cart"
System: "✅ Added 8 items to cart. Total: $24.50"
```

## Benefits

### For Users
- ✅ Clear, structured workflow with confirmation points
- ✅ Specialized assistance for recipes vs. grocery shopping
- ✅ Real grocery store integration with prices
- ✅ Flexibility to go back and modify choices
- ✅ Complete ingredient-to-cart workflow

### For Developers
- ✅ Modular, maintainable architecture
- ✅ Specialized LLM prompts for better results
- ✅ Clear separation of concerns
- ✅ Easy to extend with new features
- ✅ Proper MCP tools integration

## Configuration

### MCP Server Setup
```python
# Configure MCP servers for grocery stores
_mcp_client = MultiServerMCPClient({
    "grocery": {
        "transport": "streamable_http",
        "url": "http://localhost:8000/mcp/"
    }
})
```

### Environment Variables
```bash
GEMINI_API_KEY=your_api_key_here
```

## Testing

Run the enhanced workflow tests:
```bash
python test_enhanced_workflow.py
```

## Production Considerations

1. **Real MCP Servers**: Set up actual grocery store API integrations
2. **User Input Handling**: Implement real user input capture
3. **Cart Persistence**: Add database storage for shopping carts
4. **Error Handling**: Robust error handling for API failures
5. **Location Services**: Location-based store searches
6. **Authentication**: User accounts and preferences

## Future Enhancements

- Recipe rating and reviews integration
- Dietary restriction filtering in grocery search
- Delivery scheduling and integration
- Price tracking and alerts
- Recipe sharing and social features
- Nutrition analysis integration

The enhanced Recipe Agent provides a complete, production-ready foundation for recipe discovery and grocery shopping automation!

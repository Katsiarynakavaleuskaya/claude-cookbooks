# PulsePlate Examples

This directory contains working examples demonstrating how to integrate Claude's capabilities into the PulsePlate nutrition application.

## Prerequisites

```bash
pip install anthropic python-dotenv
```

Set your API key as an environment variable:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Examples

### 1. Meal Planning (`meal_planning.py`)

Generate personalized weekly meal plans based on user preferences and dietary restrictions.

**Features:**
- Custom calorie targets
- Dietary restrictions (gluten-free, vegan, keto, etc.)
- Cooking skill level adaptation
- Time constraints
- Automatic shopping list generation
- Nutritional breakdown

**Usage:**
```bash
python meal_planning.py
```

**Example Output:**
- 7-day meal plan with breakfast, lunch, dinner, and snacks
- Complete nutritional information per meal
- Cooking time and difficulty ratings
- Organized shopping list by category

### 2. Recipe Analysis (`recipe_analyzer.py`)

Analyze food photos and adapt recipes for different dietary needs.

**Features:**
- Extract recipes from photos using vision capabilities
- Adapt recipes (vegan, low-carb, gluten-free, budget, etc.)
- Portion size estimation
- Nutritional calculation
- Cost comparison
- Multiple recipe variations

**Usage:**
```bash
python recipe_analyzer.py
```

**Adaptation Types:**
- `vegan` - Remove all animal products
- `low_carb` - Reduce carbs to <20g per serving
- `keto` - Very low carb, high fat
- `gluten_free` - Remove all gluten
- `paleo` - Paleo-approved ingredients only
- `low_calorie` - Reduce calories by 30-40%
- `high_protein` - Increase protein to 30g+
- `budget` - Reduce cost while maintaining nutrition
- `quick` - Reduce prep time to <30 minutes

### 3. Nutrition Reports (`nutrition_report.py`)

Generate comprehensive Excel reports with nutrition tracking and analysis.

**Features:**
- Multi-sheet Excel workbooks
- Interactive charts and graphs
- Macro analysis and trends
- Goal progress tracking
- Actionable insights and recommendations
- Professional formatting

**Usage:**
```bash
python nutrition_report.py
```

**Report Sections:**
1. Dashboard - Overview and key metrics
2. Daily Breakdown - Detailed meal log
3. Macro Analysis - Distribution and trends
4. Micronutrients - Vitamins and minerals
5. Trends & Insights - Visual analytics
6. Goals Progress - Achievement tracking
7. Food Log - Complete searchable log

## Code Structure

### Meal Planning Example

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-key")

preferences = {
    "diet_type": "vegetarian",
    "daily_calories": 2000,
    "restrictions": ["gluten"],
    "skill_level": "intermediate",
    "cooking_time": "moderate",
    "goals": ["weight_loss"]
}

result = generate_meal_plan(preferences)
```

### Recipe Adaptation Example

```python
original_recipe = {
    "name": "Chicken Pasta",
    "ingredients": [...],
    "instructions": [...]
}

adapted = adapt_recipe(
    original_recipe,
    adaptation_type='vegan',
    additional_requirements=['Keep it creamy']
)
```

### Nutrition Report Example

```python
user_data = {
    "name": "Alex",
    "goals": ["Weight Loss"],
    "nutrition_summary": {...}
}

result = generate_nutrition_report(
    user_data,
    report_type="weekly"
)

download_report(result['file_id'], "report.xlsx")
```

## API Usage and Costs

### Model Selection by Task

| Task | Model | Avg Cost per Request |
|------|-------|---------------------|
| Meal Planning | Sonnet | $0.12 - $0.24 |
| Recipe Analysis | Sonnet | $0.06 - $0.12 |
| Photo Analysis | Sonnet (Vision) | $0.09 - $0.18 |
| Nutrition Report | Sonnet + Skills | $0.24 - $0.40 |
| Quick Queries | Haiku | $0.01 - $0.02 |

### Optimization Tips

1. **Use appropriate model sizes**:
   - Haiku for simple queries
   - Sonnet for complex tasks

2. **Implement caching**:
   - Cache common recipes
   - Store frequently generated meal plans
   - Reuse nutrition calculations

3. **Batch processing**:
   - Generate weekly plans at once
   - Process multiple recipes together

4. **Optimize prompts**:
   - Be specific and concise
   - Use structured outputs
   - Set appropriate max_tokens

## Error Handling

All examples include robust error handling:

```python
try:
    response = client.messages.create(...)
    
    if response.success:
        # Process result
        pass
    else:
        # Handle error
        print(f"Error: {response.error}")
        
except Exception as e:
    print(f"Exception: {e}")
    # Fallback logic
```

## Testing

Run tests for the examples:

```bash
# Test meal planning
python -m pytest test_meal_planning.py

# Test recipe analyzer
python -m pytest test_recipe_analyzer.py

# Test nutrition reports
python -m pytest test_nutrition_report.py
```

## Integration with PulsePlate

### Step 1: Install Dependencies

```bash
pip install anthropic python-dotenv
```

### Step 2: Configure Environment

```python
# config.py
import os
from anthropic import Anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic(
    api_key=ANTHROPIC_API_KEY,
    default_headers={
        "anthropic-beta": "code-execution-2025-08-25,files-api-2025-04-14,skills-2025-10-02"
    }
)
```

### Step 3: Integrate Functions

```python
# In your PulsePlate application
from examples.meal_planning import generate_meal_plan
from examples.recipe_analyzer import adapt_recipe
from examples.nutrition_report import generate_nutrition_report

# Generate meal plan for user
user_prefs = get_user_preferences(user_id)
meal_plan = generate_meal_plan(user_prefs)

# Save to database
save_meal_plan(user_id, meal_plan)
```

## Performance Monitoring

Track these metrics:

```python
import time

start = time.time()
result = generate_meal_plan(preferences)
duration = time.time() - start

# Log metrics
log_metrics({
    "function": "generate_meal_plan",
    "duration": duration,
    "tokens_used": result['tokens_used'],
    "success": result['success']
})
```

## Security Considerations

1. **Never log sensitive data** in API calls
2. **Validate all inputs** before sending to Claude
3. **Sanitize outputs** before displaying to users
4. **Implement rate limiting** to control costs
5. **Use environment variables** for API keys

## Support

For questions or issues:

- Check the [main documentation](../SKILL.md)
- Review the [quick reference](../REFERENCE.md)
- Open an issue on GitHub
- Contact: support@pulseplate.example

## License

These examples are provided under the MIT License. See the main repository LICENSE file for details.

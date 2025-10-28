# PulsePlate Claude Integration - Quick Reference

## Quick Start Checklist

### Initial Setup
✅ Obtain Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
✅ Install Anthropic Python SDK: `pip install anthropic`
✅ Configure environment variables
✅ Set up beta headers for Skills feature
✅ Test basic API connectivity

### Essential Features to Implement
✅ Meal plan generation (Sonnet)
✅ Recipe queries (Haiku)
✅ Food photo analysis (Sonnet with Vision)
✅ Nutrition reports (Sonnet with Excel skill)
✅ Customer support chat (Sonnet)

## API Configuration Quick Reference

### Required Beta Headers
```python
from anthropic import Anthropic

client = Anthropic(
    api_key="your-api-key",
    default_headers={
        "anthropic-beta": "code-execution-2025-08-25,files-api-2025-04-14,skills-2025-10-02"
    }
)
```

### Model Selection Guide

| Task | Model | Avg Response Time | Cost per 1K tokens |
|------|-------|-------------------|-------------------|
| Quick recipe lookup | Haiku | <1s | $0.25 |
| Meal plan generation | Sonnet | 2-3s | $3.00 |
| Nutrition analysis | Sonnet | 2-4s | $3.00 |
| Food photo analysis | Sonnet | 3-5s | $3.00 |
| Report generation | Sonnet + Skills | 5-10s | $3.00 |

## Common Use Case Templates

### 1. Meal Plan Generation

```python
def generate_meal_plan(user_preferences):
    """Generate personalized weekly meal plan"""
    
    prompt = f"""Generate a 7-day meal plan with the following requirements:
    - Dietary preference: {user_preferences['diet_type']}
    - Daily calorie target: {user_preferences['calories']}
    - Restrictions: {', '.join(user_preferences['restrictions'])}
    - Cooking skill level: {user_preferences['skill_level']}
    
    For each day, provide:
    - Breakfast, Lunch, Dinner, 2 Snacks
    - Total calories and macros (protein, carbs, fats)
    - Prep time and difficulty
    
    Return as JSON with structure: {{"days": [{{"day": "Monday", "meals": [...]}}]}}
    """
    
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text
```

### 2. Food Photo Analysis

```python
import base64

def analyze_food_photo(image_path):
    """Extract nutrition info from food photo"""
    
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": """Analyze this food photo and provide:
                    1. Identified foods and ingredients
                    2. Estimated portion sizes
                    3. Approximate calories and macros
                    4. Suggestions for healthier alternatives"""
                }
            ]
        }]
    )
    
    return response.content[0].text
```

### 3. Recipe Adaptation

```python
def adapt_recipe(original_recipe, adaptation_type):
    """Adapt recipe for dietary needs"""
    
    adaptations = {
        'vegan': 'Remove all animal products and suggest plant-based alternatives',
        'low_carb': 'Reduce carbs to under 20g, increase protein and healthy fats',
        'gluten_free': 'Replace all gluten-containing ingredients',
        'budget': 'Use cost-effective alternatives while maintaining nutrition'
    }
    
    prompt = f"""Original Recipe:
    {original_recipe}
    
    Please adapt this recipe to be {adaptation_type}.
    {adaptations[adaptation_type]}
    
    Maintain similar:
    - Flavor profile
    - Preparation method
    - Cooking time
    
    Provide adapted recipe with:
    - Modified ingredient list with quantities
    - Updated instructions
    - New nutritional information
    - Cost comparison (if applicable)
    """
    
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text
```

### 4. Nutrition Report Generation

```python
def generate_nutrition_report(user_data, date_range):
    """Create Excel nutrition tracking report"""
    
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        container={
            "skills": [
                {"type": "anthropic", "skill_id": "xlsx", "version": "latest"}
            ]
        },
        tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
        messages=[{
            "role": "user",
            "content": f"""Create a comprehensive nutrition tracking report for:
            User: {user_data['name']}
            Period: {date_range['start']} to {date_range['end']}
            Data: {user_data['meals_log']}
            
            Include:
            1. Daily nutrition summary (calories, protein, carbs, fats)
            2. Charts showing macro distribution trends
            3. Comparison to RDA targets
            4. Goal progress tracker
            5. Top consumed foods
            6. Recommendations for improvement
            
            Format as professional Excel workbook with multiple sheets."""
        }]
    )
    
    # Extract and download file
    for block in response.content:
        if hasattr(block, 'output') and 'file_id' in str(block.output):
            file_id = extract_file_id(block.output)
            file_content = client.beta.files.download(file_id=file_id)
            
            with open(f"reports/nutrition_report_{user_data['id']}.xlsx", "wb") as f:
                f.write(file_content.read())
            
            return f"Report generated: nutrition_report_{user_data['id']}.xlsx"
```

### 5. Customer Support Chatbot

```python
def handle_support_query(user_message, conversation_history):
    """Process customer support interaction"""
    
    system_prompt = """You are a helpful nutrition and app support assistant for PulsePlate.
    
    Your capabilities:
    - Answer nutrition questions (evidence-based)
    - Help with app features and troubleshooting
    - Provide meal planning advice
    - Explain recipe modifications
    - Guide goal setting
    
    Guidelines:
    - Be friendly and supportive
    - Cite sources for nutrition claims
    - Suggest consulting healthcare providers for medical advice
    - Escalate complex technical issues
    - Keep responses concise but complete
    """
    
    messages = conversation_history + [
        {"role": "user", "content": user_message}
    ]
    
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=system_prompt,
        messages=messages
    )
    
    return response.content[0].text
```

## Prompt Engineering Best Practices

### For Meal Plans
✅ Specify calorie range (e.g., 1800-2000 cal/day)
✅ List all dietary restrictions clearly
✅ Include cooking skill level and time constraints
✅ Request structured output format (JSON)
✅ Ask for macronutrient breakdown

### For Recipe Queries
✅ Specify serving size
✅ Mention available ingredients
✅ Note cooking equipment/methods available
✅ Include time constraints
✅ Request difficulty rating

### For Nutrition Analysis
✅ Provide complete food descriptions
✅ Include preparation methods
✅ Specify portion sizes when known
✅ Ask for specific nutrients of interest
✅ Request comparison to RDA

### For Photo Analysis
✅ Use high-quality, well-lit images
✅ Include scale reference when possible
✅ Specify what information you need
✅ Ask for confidence levels
✅ Request suggestions or alternatives

## Cost Optimization Strategies

### 1. Model Selection
- Use **Haiku** for: Simple queries, recipe lookups, quick answers
- Use **Sonnet** for: Meal planning, analysis, complex tasks
- Use **Vision** only when needed: Food photos require Sonnet

### 2. Prompt Caching
```python
# Cache frequently used system prompts
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": nutrition_guidelines,  # Long, reusable content
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": query}]
)
```

### 3. Batch Processing
- Group similar requests together
- Process multiple recipes in one call
- Generate weekly meal plans at once

### 4. Response Caching
- Cache common recipes and meal plans
- Store frequently asked support answers
- Reuse nutrition calculations for same foods

## Error Handling Patterns

### API Errors
```python
from anthropic import APIError, RateLimitError

try:
    response = client.messages.create(...)
except RateLimitError:
    # Wait and retry
    time.sleep(60)
    response = client.messages.create(...)
except APIError as e:
    # Log error and use fallback
    logger.error(f"API Error: {e}")
    return fallback_response()
```

### Invalid Outputs
```python
import json

def validate_meal_plan(response_text):
    try:
        meal_plan = json.loads(response_text)
        assert 'days' in meal_plan
        assert len(meal_plan['days']) == 7
        return meal_plan
    except (json.JSONDecodeError, AssertionError):
        # Request regeneration with more specific format
        return None
```

## Performance Benchmarks

### Target Metrics
| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| Response Time | <2s | 2-5s | >5s |
| Error Rate | <0.5% | 0.5-2% | >2% |
| User Satisfaction | >4.5/5 | 4.0-4.5 | <4.0 |
| API Cost/User/Month | <$0.10 | $0.10-0.25 | >$0.25 |

### Optimization Checklist
- [ ] Implement response caching
- [ ] Use appropriate model for each task
- [ ] Batch similar requests
- [ ] Set reasonable max_tokens limits
- [ ] Monitor and log all API calls
- [ ] Track costs per feature
- [ ] A/B test prompt variations

## Safety and Compliance

### Medical Disclaimers
Always include:
- "Consult healthcare provider before dietary changes"
- "Not a substitute for professional medical advice"
- "Results may vary by individual"

### Data Privacy
- Never log sensitive health information
- Anonymize data before API calls
- Comply with HIPAA/GDPR requirements
- Implement data retention policies
- Encrypt data in transit and at rest

### Content Validation
- Verify nutrition data against USDA database
- Review AI-generated recipes for safety
- Flag potential allergen issues
- Validate calorie calculations
- Check macro calculations

## Troubleshooting Guide

### Common Issues

**Problem**: Meal plans don't match calorie targets
**Solution**: Be more specific in prompt about acceptable ranges

**Problem**: Recipes have unusual ingredient combinations
**Solution**: Add constraints about cuisine type and common pairings

**Problem**: Response times too slow
**Solution**: Reduce max_tokens, use Haiku for simpler tasks

**Problem**: High API costs
**Solution**: Implement caching, batch requests, optimize prompts

**Problem**: Inconsistent output formats
**Solution**: Use structured output with JSON schema validation

## Integration Patterns

### Asynchronous Processing
```python
import asyncio

async def process_meal_plans_async(user_ids):
    tasks = [generate_meal_plan_async(uid) for uid in user_ids]
    return await asyncio.gather(*tasks)
```

### Webhook Integration
```python
@app.route('/api/meal-plan-webhook', methods=['POST'])
def meal_plan_webhook():
    user_id = request.json['user_id']
    
    # Generate asynchronously
    task_id = queue_meal_plan_generation(user_id)
    
    return {"task_id": task_id, "status": "processing"}
```

### Real-time Chat
```python
@socketio.on('support_message')
def handle_support_message(data):
    user_id = data['user_id']
    message = data['message']
    
    # Get response from Claude
    response = handle_support_query(message, get_history(user_id))
    
    # Send back to user
    emit('support_response', {'message': response})
```

## Testing Recommendations

### Unit Tests
- Test prompt formatting
- Validate JSON parsing
- Check error handling
- Verify data anonymization

### Integration Tests
- Test full API flow
- Validate response formats
- Check file generation
- Test tool calling

### Performance Tests
- Load test with concurrent requests
- Measure response times
- Test caching effectiveness
- Monitor error rates

## Contact and Support

**PulsePlate Development Team**
- Email: dev@pulseplate.example
- Slack: #pulseplate-ai

**Anthropic Support**
- Documentation: https://docs.anthropic.com
- Discord: Anthropic community
- Email: support@anthropic.com

**Emergency Contacts**
- API issues: Check status.anthropic.com
- Production incidents: Follow incident response plan
- Security concerns: security@pulseplate.example

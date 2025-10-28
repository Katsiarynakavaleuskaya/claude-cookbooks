"""
PulsePlate - Recipe Analysis and Adaptation Example
Demonstrates how to analyze recipes and adapt them for different dietary needs.
"""

import os
import base64
from pathlib import Path
from anthropic import Anthropic

# Initialize the client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def analyze_recipe_from_photo(image_path):
    """
    Extract recipe information from a food photo.
    
    Args:
        image_path (str): Path to the image file
    
    Returns:
        dict: Extracted recipe information
    """
    
    # Read and encode the image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Determine media type
    suffix = Path(image_path).suffix.lower()
    media_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    media_type = media_type_map.get(suffix, 'image/jpeg')
    
    prompt = """Analyze this food photo and provide detailed information:

1. Identify all visible foods and ingredients
2. Estimate portion sizes (in common measurements)
3. Provide nutritional estimates:
   - Total calories
   - Protein (g)
   - Carbohydrates (g)
   - Fats (g)
   - Fiber (g)
4. Suggest the likely recipe or dish name
5. If it's a prepared meal, try to estimate the recipe
6. Provide suggestions for making it healthier

Format your response as JSON:
{
  "dish_name": "name",
  "identified_foods": ["food1", "food2"],
  "portion_estimates": {"food1": "amount", "food2": "amount"},
  "nutrition": {
    "calories": 0,
    "protein_g": 0,
    "carbs_g": 0,
    "fats_g": 0,
    "fiber_g": 0
  },
  "recipe_estimate": {
    "ingredients": [],
    "instructions": []
  },
  "health_suggestions": [],
  "confidence_level": "high/medium/low"
}
"""
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        )
        
        return {
            "success": True,
            "analysis": response.content[0].text,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def adapt_recipe(original_recipe, adaptation_type, additional_requirements=None):
    """
    Adapt a recipe for different dietary needs.
    
    Args:
        original_recipe (str or dict): Original recipe text or structured recipe
        adaptation_type (str): Type of adaptation (vegan, low_carb, gluten_free, etc.)
        additional_requirements (list): Optional additional requirements
    
    Returns:
        dict: Adapted recipe
    """
    
    # Recipe adaptation instructions for different types
    adaptation_instructions = {
        'vegan': {
            'description': 'Remove all animal products',
            'focus': 'Use plant-based alternatives for meat, dairy, eggs, and honey',
            'maintain': 'Similar protein content and flavor profile'
        },
        'low_carb': {
            'description': 'Reduce carbohydrates to under 20g per serving',
            'focus': 'Replace high-carb ingredients with low-carb alternatives',
            'maintain': 'Satiety and flavor while increasing protein/healthy fats'
        },
        'keto': {
            'description': 'Very low carb (<10g), high fat (70% calories from fat)',
            'focus': 'Maximize healthy fats, minimize carbs, moderate protein',
            'maintain': 'Ketogenic ratios while keeping it delicious'
        },
        'gluten_free': {
            'description': 'Remove all gluten-containing ingredients',
            'focus': 'Replace wheat, barley, rye with gluten-free alternatives',
            'maintain': 'Texture and taste as close as possible'
        },
        'paleo': {
            'description': 'Use only paleo-approved ingredients',
            'focus': 'No grains, legumes, dairy, processed foods',
            'maintain': 'Nutritional balance and satisfaction'
        },
        'low_calorie': {
            'description': 'Reduce calories by 30-40% while maintaining nutrition',
            'focus': 'Use lower-calorie cooking methods and ingredient swaps',
            'maintain': 'Protein content and feeling of fullness'
        },
        'high_protein': {
            'description': 'Increase protein content to 30g+ per serving',
            'focus': 'Add or increase protein sources',
            'maintain': 'Balanced meal with reasonable calories'
        },
        'budget': {
            'description': 'Reduce cost while maintaining nutrition',
            'focus': 'Use economical ingredients and seasonal produce',
            'maintain': 'Nutritional value and taste'
        },
        'quick': {
            'description': 'Reduce total time to under 30 minutes',
            'focus': 'Simplify steps, use pre-prep ingredients',
            'maintain': 'Flavor and nutritional value'
        }
    }
    
    adaptation = adaptation_instructions.get(adaptation_type, {
        'description': f'Adapt recipe for {adaptation_type}',
        'focus': 'Make appropriate ingredient substitutions',
        'maintain': 'Overall quality and nutrition'
    })
    
    # Format the original recipe
    if isinstance(original_recipe, dict):
        recipe_text = f"""
Name: {original_recipe.get('name', 'Unknown')}
Servings: {original_recipe.get('servings', 'N/A')}

Ingredients:
{chr(10).join(['- ' + ing for ing in original_recipe.get('ingredients', [])])}

Instructions:
{chr(10).join([f'{i+1}. {step}' for i, step in enumerate(original_recipe.get('instructions', []))])}

Nutrition (per serving):
{chr(10).join([f'- {k}: {v}' for k, v in original_recipe.get('nutrition', {}).items()])}
"""
    else:
        recipe_text = original_recipe
    
    additional_reqs = ""
    if additional_requirements:
        additional_reqs = "\n\nAdditional Requirements:\n" + "\n".join([f"- {req}" for req in additional_requirements])
    
    prompt = f"""Adapt the following recipe to be {adaptation_type}:

Original Recipe:
{recipe_text}

Adaptation Goal: {adaptation['description']}
Focus: {adaptation['focus']}
Maintain: {adaptation['maintain']}{additional_reqs}

Please provide:
1. Adapted ingredient list with exact quantities
2. Modified cooking instructions
3. Substitution explanations (why each swap was made)
4. New nutritional information per serving
5. Taste/texture comparison notes
6. Difficulty level (1-5)
7. Estimated cost change (if applicable)
8. Any additional tips for this adaptation

Format as JSON:
{{
  "adapted_recipe": {{
    "name": "adapted name",
    "servings": 0,
    "ingredients": [
      {{"item": "ingredient", "amount": "quantity", "original": "original ingredient if substituted"}}
    ],
    "instructions": [],
    "prep_time_min": 0,
    "cook_time_min": 0,
    "difficulty": 3
  }},
  "nutrition": {{
    "per_serving": {{
      "calories": 0,
      "protein_g": 0,
      "carbs_g": 0,
      "fats_g": 0,
      "fiber_g": 0
    }},
    "comparison_to_original": {{
      "calories_change": "+/- amount or %",
      "protein_change": "+/- amount",
      "carbs_change": "+/- amount"
    }}
  }},
  "substitutions": [
    {{"original": "item", "replacement": "item", "reason": "explanation"}}
  ],
  "notes": {{
    "taste_texture": "how it compares",
    "cost_change": "more/less expensive or similar",
    "tips": []
  }}
}}
"""
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3072,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return {
            "success": True,
            "adapted_recipe": response.content[0].text,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_recipe_variations(base_recipe, num_variations=3):
    """
    Generate multiple variations of a base recipe.
    
    Args:
        base_recipe (dict): Base recipe
        num_variations (int): Number of variations to generate
    
    Returns:
        list: List of recipe variations
    """
    
    prompt = f"""Based on this recipe:

{base_recipe}

Generate {num_variations} creative variations that:
1. Change the protein source (if applicable)
2. Modify the cuisine style
3. Adjust spice level or flavor profile
4. Use different cooking methods
5. Make it suitable for different occasions

Each variation should be significantly different but maintain the same difficulty level and approximate cooking time.

Return as JSON array of variations.
"""
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return {
            "success": True,
            "variations": response.content[0].text,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Example usage
if __name__ == "__main__":
    
    # Example 1: Adapt a recipe to vegan
    example_recipe = {
        "name": "Chicken Alfredo Pasta",
        "servings": 4,
        "ingredients": [
            "1 lb chicken breast, cubed",
            "12 oz fettuccine pasta",
            "2 cups heavy cream",
            "1 cup parmesan cheese, grated",
            "4 cloves garlic, minced",
            "3 tbsp butter",
            "Salt and pepper to taste",
            "Fresh parsley for garnish"
        ],
        "instructions": [
            "Cook pasta according to package directions",
            "Season and cook chicken in butter until golden",
            "Add garlic and cook until fragrant",
            "Add cream and simmer for 5 minutes",
            "Stir in parmesan until melted",
            "Toss with cooked pasta",
            "Garnish with parsley and serve"
        ],
        "nutrition": {
            "calories": 720,
            "protein_g": 42,
            "carbs_g": 58,
            "fats_g": 35,
            "fiber_g": 3
        }
    }
    
    print("="*60)
    print("🔄 Adapting Chicken Alfredo to Vegan")
    print("="*60)
    
    vegan_adaptation = adapt_recipe(
        example_recipe,
        'vegan',
        additional_requirements=['Keep it creamy', 'Use whole food ingredients']
    )
    
    if vegan_adaptation['success']:
        print("\n✅ Adaptation successful!")
        print(f"📊 Tokens used: {vegan_adaptation['tokens_used']}")
        print("\n" + vegan_adaptation['adapted_recipe'][:500] + "...")
    else:
        print(f"\n❌ Error: {vegan_adaptation['error']}")
    
    # Example 2: Make it low-carb
    print("\n" + "="*60)
    print("🔄 Adapting to Low-Carb Version")
    print("="*60)
    
    low_carb_adaptation = adapt_recipe(
        example_recipe,
        'low_carb',
        additional_requirements=['Keep it filling', 'Under 20g carbs per serving']
    )
    
    if low_carb_adaptation['success']:
        print("\n✅ Adaptation successful!")
        print(f"📊 Tokens used: {low_carb_adaptation['tokens_used']}")
        print("\n" + low_carb_adaptation['adapted_recipe'][:500] + "...")
    else:
        print(f"\n❌ Error: {low_carb_adaptation['error']}")
    
    # Example 3: Budget-friendly version
    print("\n" + "="*60)
    print("🔄 Creating Budget-Friendly Version")
    print("="*60)
    
    budget_adaptation = adapt_recipe(
        example_recipe,
        'budget',
        additional_requirements=['Feed a family of 4 for under $15']
    )
    
    if budget_adaptation['success']:
        print("\n✅ Adaptation successful!")
        print(f"📊 Tokens used: {budget_adaptation['tokens_used']}")
        print("\n" + budget_adaptation['adapted_recipe'][:500] + "...")
    else:
        print(f"\n❌ Error: {budget_adaptation['error']}")
    
    print("\n" + "="*60)
    print("✨ Recipe Adaptation Examples Complete")
    print("="*60)

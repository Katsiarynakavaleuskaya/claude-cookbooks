"""
PulsePlate - Meal Planning Example
Demonstrates how to generate personalized weekly meal plans using Claude.
"""

import os
import json
from anthropic import Anthropic

# Initialize the client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def generate_meal_plan(user_preferences):
    """
    Generate a personalized 7-day meal plan based on user preferences.
    
    Args:
        user_preferences (dict): User dietary preferences and constraints
            - diet_type: str (e.g., 'balanced', 'vegetarian', 'vegan', 'keto', 'paleo')
            - daily_calories: int (target daily calorie intake)
            - restrictions: list (food allergies/restrictions)
            - skill_level: str ('beginner', 'intermediate', 'advanced')
            - cooking_time: str ('quick', 'moderate', 'any')
            - goals: list (e.g., ['weight_loss', 'muscle_gain', 'maintenance'])
    
    Returns:
        dict: Structured meal plan with meals for each day
    """
    
    # Build the prompt
    prompt = f"""Generate a detailed 7-day meal plan based on the following requirements:

User Profile:
- Dietary Type: {user_preferences.get('diet_type', 'balanced')}
- Daily Calorie Target: {user_preferences.get('daily_calories', 2000)} calories
- Restrictions/Allergies: {', '.join(user_preferences.get('restrictions', ['none']))}
- Cooking Skill Level: {user_preferences.get('skill_level', 'intermediate')}
- Time Availability: {user_preferences.get('cooking_time', 'moderate')}
- Health Goals: {', '.join(user_preferences.get('goals', ['maintenance']))}

Requirements for the meal plan:
1. Include Breakfast, Lunch, Dinner, and 2 Snacks for each day
2. Ensure daily calorie total is within ±100 calories of target
3. Balance macronutrients appropriately for the diet type
4. Provide variety across the week (no recipe repeats)
5. Consider prep time and cooking skills
6. Include realistic portion sizes

For each meal, provide:
- Meal name
- Brief description
- Ingredients list with quantities
- Calories and macros (protein, carbs, fats in grams)
- Prep time and cook time (in minutes)
- Difficulty level (1-5)

Return the meal plan in the following JSON structure:
{{
  "summary": {{
    "total_weekly_calories": 0,
    "avg_daily_calories": 0,
    "avg_daily_protein": 0,
    "avg_daily_carbs": 0,
    "avg_daily_fats": 0
  }},
  "days": [
    {{
      "day": "Monday",
      "date": "YYYY-MM-DD",
      "total_calories": 0,
      "meals": [
        {{
          "meal_type": "Breakfast",
          "name": "Recipe Name",
          "description": "Brief description",
          "ingredients": ["ingredient 1", "ingredient 2"],
          "calories": 0,
          "protein_g": 0,
          "carbs_g": 0,
          "fats_g": 0,
          "prep_time_min": 0,
          "cook_time_min": 0,
          "difficulty": 3
        }}
      ]
    }}
  ],
  "shopping_list": {{
    "proteins": [],
    "vegetables": [],
    "fruits": [],
    "grains": [],
    "dairy": [],
    "pantry": [],
    "other": []
  }},
  "meal_prep_tips": []
}}

Ensure all JSON is valid and properly formatted.
"""
    
    try:
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract the text response
        response_text = response.content[0].text
        
        # Parse JSON from response
        # Sometimes Claude wraps JSON in markdown code blocks
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        meal_plan = json.loads(response_text)
        
        return {
            "success": True,
            "meal_plan": meal_plan,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse meal plan JSON: {str(e)}",
            "raw_response": response_text
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating meal plan: {str(e)}"
        }


def save_meal_plan(meal_plan, filename="meal_plan.json"):
    """Save meal plan to JSON file."""
    with open(filename, 'w') as f:
        json.dump(meal_plan, f, indent=2)
    print(f"✅ Meal plan saved to {filename}")


def print_meal_plan_summary(meal_plan_response):
    """Print a formatted summary of the meal plan."""
    if not meal_plan_response['success']:
        print(f"❌ Error: {meal_plan_response['error']}")
        return
    
    meal_plan = meal_plan_response['meal_plan']
    summary = meal_plan['summary']
    
    print("\n" + "="*60)
    print("🍽️  PULSEPLATE - YOUR PERSONALIZED MEAL PLAN")
    print("="*60)
    
    print(f"\n📊 Weekly Summary:")
    print(f"   Total Calories: {summary['total_weekly_calories']:,}")
    print(f"   Avg Daily: {summary['avg_daily_calories']} cal")
    print(f"   Avg Protein: {summary['avg_daily_protein']}g")
    print(f"   Avg Carbs: {summary['avg_daily_carbs']}g")
    print(f"   Avg Fats: {summary['avg_daily_fats']}g")
    
    print(f"\n📅 Daily Breakdown:")
    for day_plan in meal_plan['days']:
        print(f"\n   {day_plan['day']} - {day_plan['total_calories']} cal")
        for meal in day_plan['meals']:
            print(f"      • {meal['meal_type']}: {meal['name']}")
            print(f"        {meal['calories']} cal | P: {meal['protein_g']}g | "
                  f"C: {meal['carbs_g']}g | F: {meal['fats_g']}g")
    
    if 'meal_prep_tips' in meal_plan and meal_plan['meal_prep_tips']:
        print(f"\n💡 Meal Prep Tips:")
        for tip in meal_plan['meal_prep_tips'][:3]:
            print(f"   • {tip}")
    
    print(f"\n📈 API Usage: {meal_plan_response['tokens_used']} tokens")
    print("="*60 + "\n")


# Example usage
if __name__ == "__main__":
    # Example 1: Balanced diet for weight loss
    example_preferences_1 = {
        "diet_type": "balanced",
        "daily_calories": 1800,
        "restrictions": ["gluten"],
        "skill_level": "intermediate",
        "cooking_time": "moderate",
        "goals": ["weight_loss", "energy"]
    }
    
    print("Generating meal plan for Example 1: Balanced diet for weight loss...")
    result_1 = generate_meal_plan(example_preferences_1)
    print_meal_plan_summary(result_1)
    
    if result_1['success']:
        save_meal_plan(result_1['meal_plan'], "example_meal_plan_balanced.json")
    
    # Example 2: Vegetarian high-protein
    example_preferences_2 = {
        "diet_type": "vegetarian",
        "daily_calories": 2200,
        "restrictions": ["dairy", "eggs"],  # Vegan essentially
        "skill_level": "beginner",
        "cooking_time": "quick",
        "goals": ["muscle_gain", "high_protein"]
    }
    
    print("\nGenerating meal plan for Example 2: Vegan high-protein...")
    result_2 = generate_meal_plan(example_preferences_2)
    print_meal_plan_summary(result_2)
    
    if result_2['success']:
        save_meal_plan(result_2['meal_plan'], "example_meal_plan_vegan.json")
    
    # Example 3: Keto diet
    example_preferences_3 = {
        "diet_type": "keto",
        "daily_calories": 2000,
        "restrictions": ["soy"],
        "skill_level": "advanced",
        "cooking_time": "any",
        "goals": ["weight_loss", "mental_clarity"]
    }
    
    print("\nGenerating meal plan for Example 3: Keto diet...")
    result_3 = generate_meal_plan(example_preferences_3)
    print_meal_plan_summary(result_3)
    
    if result_3['success']:
        save_meal_plan(result_3['meal_plan'], "example_meal_plan_keto.json")

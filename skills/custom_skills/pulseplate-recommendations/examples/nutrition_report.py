"""
PulsePlate - Nutrition Report Generation Example
Demonstrates how to create comprehensive nutrition reports using Claude's Excel skill.
"""

import os
import json
from datetime import datetime, timedelta
from anthropic import Anthropic

# Initialize the client with beta headers for Skills
client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    default_headers={
        "anthropic-beta": "code-execution-2025-08-25,files-api-2025-04-14,skills-2025-10-02"
    }
)


def generate_nutrition_report(user_data, report_type="weekly"):
    """
    Generate a comprehensive nutrition tracking report.
    
    Args:
        user_data (dict): User nutrition data including meals log
        report_type (str): Type of report ('weekly', 'monthly', 'quarterly')
    
    Returns:
        dict: Report generation result with file_id
    """
    
    # Calculate date range based on report type
    end_date = datetime.now()
    if report_type == "weekly":
        start_date = end_date - timedelta(days=7)
        period_name = "Weekly"
    elif report_type == "monthly":
        start_date = end_date - timedelta(days=30)
        period_name = "Monthly"
    else:  # quarterly
        start_date = end_date - timedelta(days=90)
        period_name = "Quarterly"
    
    prompt = f"""Create a comprehensive nutrition tracking report as an Excel workbook for:

User Information:
- Name: {user_data.get('name', 'User')}
- Age: {user_data.get('age', 'N/A')}
- Goals: {', '.join(user_data.get('goals', ['General Health']))}
- Period: {period_name} ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})

Nutrition Data Summary:
{json.dumps(user_data.get('nutrition_summary', {}), indent=2)}

Target Daily Values:
- Calories: {user_data.get('target_calories', 2000)}
- Protein: {user_data.get('target_protein', 50)}g
- Carbs: {user_data.get('target_carbs', 250)}g
- Fats: {user_data.get('target_fats', 70)}g
- Fiber: {user_data.get('target_fiber', 25)}g

Create an Excel workbook with the following sheets:

1. **Dashboard** (Summary Sheet):
   - User profile and goals at the top
   - Key metrics cards (avg daily calories, protein, etc.)
   - Visual comparison: Actual vs Target (use bar charts)
   - Overall adherence percentage
   - Top 5 most consumed foods
   - Achievement badges (e.g., "Hit protein goal 5/7 days")
   - Use color coding: Green for on-target, Yellow for close, Red for off-target

2. **Daily Breakdown**:
   - Table with columns: Date, Meal Type, Food, Calories, Protein, Carbs, Fats, Fiber
   - Daily totals row after each day
   - Running averages
   - Color-coded cells based on targets
   - Conditional formatting

3. **Macro Analysis**:
   - Daily macro distribution (stacked bar chart)
   - Macro percentages (% of total calories from each macro)
   - Trend lines showing changes over time
   - Comparison to ideal ratios for user's goals

4. **Micronutrients** (if data available):
   - Vitamins and minerals tracking
   - RDA comparison
   - Deficiency warnings

5. **Trends & Insights**:
   - Line chart showing calorie intake over time
   - Weight trend (if available)
   - Hydration tracking
   - Sleep quality correlation (if available)
   - Weekly patterns (best/worst days)

6. **Goals Progress**:
   - Goal tracking with progress bars
   - Milestone achievements
   - Recommendations for next period

7. **Food Log**:
   - Complete detailed log of all meals
   - Searchable and filterable
   - Notes/comments column

Formatting Requirements:
- Use professional color scheme (blues and greens primarily)
- Bold headers with background color
- Alternating row colors for readability
- Freeze panes on header rows
- Add data validation where appropriate
- Include formulas for calculations
- Auto-fit column widths
- Add print settings for each sheet

Make it visually appealing, easy to read, and actionable.
"""
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,
            container={
                "skills": [
                    {"type": "anthropic", "skill_id": "xlsx", "version": "latest"}
                ]
            },
            tools=[
                {"type": "code_execution_20250825", "name": "code_execution"}
            ],
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Extract file_id from response
        file_id = None
        for block in response.content:
            if hasattr(block, 'type') and block.type == 'tool_result':
                if hasattr(block, 'output'):
                    output_str = str(block.output) if block.output else ""
                    if 'file_id' in output_str:
                        # Parse file_id from output
                        import re
                        match = re.search(r'file_[a-zA-Z0-9]+', output_str)
                        if match:
                            file_id = match.group(0)
                            break
        
        return {
            "success": True,
            "file_id": file_id,
            "response": response,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def download_report(file_id, output_filename):
    """
    Download the generated report file.
    
    Args:
        file_id (str): File ID from Claude API
        output_filename (str): Local filename to save
    
    Returns:
        bool: Success status
    """
    try:
        # Download the file
        file_content = client.beta.files.download(file_id=file_id)
        
        # Save to disk
        with open(output_filename, 'wb') as f:
            f.write(file_content.read())
        
        print(f"✅ Report downloaded: {output_filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading report: {e}")
        return False


def generate_quick_summary_text(user_data):
    """
    Generate a quick text summary of nutrition data using Claude.
    
    Args:
        user_data (dict): User nutrition data
    
    Returns:
        str: Text summary
    """
    
    prompt = f"""Analyze this nutrition data and provide a concise, actionable summary:

User: {user_data.get('name')}
Goals: {', '.join(user_data.get('goals', []))}

Weekly Averages:
- Calories: {user_data.get('avg_calories', 0)} (Target: {user_data.get('target_calories', 2000)})
- Protein: {user_data.get('avg_protein', 0)}g (Target: {user_data.get('target_protein', 50)}g)
- Carbs: {user_data.get('avg_carbs', 0)}g (Target: {user_data.get('target_carbs', 250)}g)
- Fats: {user_data.get('avg_fats', 0)}g (Target: {user_data.get('target_fats', 70)}g)

Provide:
1. Overall assessment (2-3 sentences)
2. Top 3 strengths
3. Top 3 areas for improvement
4. Specific actionable recommendations (3-5)
5. Motivation/encouragement

Keep it concise, positive, and actionable.
"""
    
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Use Haiku for quick summaries
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content[0].text
        
    except Exception as e:
        return f"Error generating summary: {e}"


# Example usage
if __name__ == "__main__":
    
    # Sample user data
    example_user_data = {
        "name": "Alex Johnson",
        "age": 32,
        "goals": ["Weight Loss", "Muscle Gain", "Better Energy"],
        "target_calories": 2000,
        "target_protein": 150,
        "target_carbs": 200,
        "target_fats": 65,
        "target_fiber": 30,
        "avg_calories": 1950,
        "avg_protein": 145,
        "avg_carbs": 195,
        "avg_fats": 68,
        "nutrition_summary": {
            "total_days_tracked": 7,
            "days_met_calorie_goal": 5,
            "days_met_protein_goal": 6,
            "days_met_carb_goal": 5,
            "days_met_fat_goal": 4,
            "top_foods": [
                {"name": "Chicken Breast", "frequency": 12},
                {"name": "Brown Rice", "frequency": 8},
                {"name": "Broccoli", "frequency": 7},
                {"name": "Eggs", "frequency": 6},
                {"name": "Greek Yogurt", "frequency": 5}
            ],
            "daily_data": [
                {
                    "date": "2025-01-20",
                    "total_calories": 2050,
                    "protein": 155,
                    "carbs": 198,
                    "fats": 70,
                    "meals": [
                        {"type": "Breakfast", "name": "Oatmeal with berries", "calories": 350},
                        {"type": "Lunch", "name": "Grilled chicken salad", "calories": 450},
                        {"type": "Dinner", "name": "Salmon with quinoa", "calories": 550},
                        {"type": "Snack", "name": "Greek yogurt", "calories": 150}
                    ]
                }
                # More days would be included in real data
            ]
        }
    }
    
    print("="*60)
    print("📊 PULSEPLATE NUTRITION REPORT GENERATOR")
    print("="*60)
    
    # Generate quick text summary
    print("\n📝 Generating quick summary...")
    summary = generate_quick_summary_text(example_user_data)
    print("\n" + summary)
    
    # Generate full Excel report
    print("\n\n📈 Generating comprehensive Excel report...")
    result = generate_nutrition_report(example_user_data, report_type="weekly")
    
    if result['success']:
        print(f"\n✅ Report generated successfully!")
        print(f"📊 Tokens used: {result['tokens_used']}")
        
        if result['file_id']:
            print(f"📎 File ID: {result['file_id']}")
            
            # Download the report
            output_filename = f"nutrition_report_{example_user_data['name'].replace(' ', '_')}.xlsx"
            download_report(result['file_id'], output_filename)
        else:
            print("⚠️  No file_id found in response")
            print("Response content:")
            for block in result['response'].content:
                print(f"  - {block.type}: {str(block)[:200]}")
    else:
        print(f"\n❌ Error: {result['error']}")
    
    print("\n" + "="*60)
    print("✨ Report generation complete!")
    print("="*60)
    
    # Additional example: Monthly report for different user
    print("\n\n" + "="*60)
    print("📊 Generating Monthly Report Example")
    print("="*60)
    
    monthly_user_data = {
        "name": "Sarah Martinez",
        "age": 28,
        "goals": ["Marathon Training", "Maintain Weight"],
        "target_calories": 2500,
        "target_protein": 120,
        "target_carbs": 350,
        "target_fats": 75,
        "target_fiber": 35,
        "avg_calories": 2480,
        "avg_protein": 118,
        "avg_carbs": 355,
        "avg_fats": 72,
        "nutrition_summary": {
            "total_days_tracked": 30,
            "days_met_calorie_goal": 25,
            "days_met_protein_goal": 22,
            "workout_days": 20,
            "rest_days": 10
        }
    }
    
    monthly_result = generate_nutrition_report(monthly_user_data, report_type="monthly")
    
    if monthly_result['success']:
        print(f"\n✅ Monthly report generated!")
        print(f"📊 Tokens used: {monthly_result['tokens_used']}")
        if monthly_result['file_id']:
            output_filename = f"nutrition_report_monthly_{monthly_user_data['name'].replace(' ', '_')}.xlsx"
            download_report(monthly_result['file_id'], output_filename)
    else:
        print(f"\n❌ Error: {monthly_result['error']}")

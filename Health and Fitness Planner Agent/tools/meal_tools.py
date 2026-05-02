"""Meal-planning and recipe helper tools.

These helpers are adapted from the uploaded AI Recipe Meal Planning Agent and kept
lightweight so the Health and Fitness Planner remains runnable without Agno or
external recipe APIs. Spoonacular support is optional and used only when an API key
is configured.
"""

from __future__ import annotations

import os
import random
from typing import Dict, Iterable, List, Optional

try:
    import requests
except ImportError:  # Optional until recipe search is used.
    requests = None  # type: ignore[assignment]


MEAL_LIBRARY: Dict[str, List[Dict[str, float | str]]] = {
    "breakfast": [
        {"name": "Overnight oats with berries", "calories": 320, "protein": 12, "cost": 2.50},
        {"name": "Vegetable egg scramble with toast", "calories": 280, "protein": 18, "cost": 3.20},
        {"name": "Greek yogurt fruit parfait", "calories": 250, "protein": 15, "cost": 2.80},
        {"name": "Peanut butter banana smoothie", "calories": 360, "protein": 16, "cost": 3.00},
    ],
    "lunch": [
        {"name": "Quinoa vegetable bowl", "calories": 420, "protein": 16, "cost": 4.50},
        {"name": "Chicken Caesar wrap", "calories": 380, "protein": 25, "cost": 5.20},
        {"name": "Lentil vegetable soup", "calories": 340, "protein": 18, "cost": 3.80},
        {"name": "Tuna rice salad bowl", "calories": 430, "protein": 28, "cost": 4.90},
    ],
    "dinner": [
        {"name": "Grilled salmon with vegetables", "calories": 520, "protein": 35, "cost": 8.90},
        {"name": "Chicken stir fry with brown rice", "calories": 480, "protein": 32, "cost": 6.50},
        {"name": "Vegetable curry with quinoa", "calories": 450, "protein": 15, "cost": 5.20},
        {"name": "Turkey chili with beans", "calories": 500, "protein": 34, "cost": 6.20},
    ],
    "snack": [
        {"name": "Fruit with mixed nuts", "calories": 220, "protein": 6, "cost": 2.20},
        {"name": "Cottage cheese with cucumber", "calories": 180, "protein": 18, "cost": 2.50},
        {"name": "Hummus with carrots", "calories": 210, "protein": 7, "cost": 2.10},
    ],
}


def _diet_filter(meal: Dict[str, float | str], dietary_preference: str) -> bool:
    """Return whether a meal is compatible with a broad dietary preference."""
    preference = dietary_preference.lower()
    name = str(meal["name"]).lower()
    if "vegan" in preference:
        return not any(term in name for term in ["chicken", "salmon", "turkey", "egg", "yogurt", "cottage", "tuna"])
    if "vegetarian" in preference:
        return not any(term in name for term in ["chicken", "salmon", "turkey", "tuna"])
    if "dairy" in preference:
        return not any(term in name for term in ["yogurt", "cottage", "caesar"])
    if "gluten" in preference:
        return "toast" not in name and "wrap" not in name
    return True


def _select_meal(meal_type: str, dietary_preference: str, seed: int) -> Dict[str, float | str]:
    compatible = [meal for meal in MEAL_LIBRARY[meal_type] if _diet_filter(meal, dietary_preference)]
    choices = compatible or MEAL_LIBRARY[meal_type]
    return choices[seed % len(choices)]


def create_meal_plan(
    dietary_preference: str = "balanced",
    people: int = 1,
    days: int = 7,
    budget: str = "moderate",
    include_snacks: bool = True,
) -> Dict[str, object]:
    """Create a weekly meal plan with estimated calories, protein, cost, and shopping list."""
    days = max(1, min(days, 7))
    people = max(1, people)
    budget_multipliers = {"low": 0.7, "moderate": 1.0, "high": 1.3}
    multiplier = budget_multipliers.get(budget.lower(), 1.0)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    weekly_plan: Dict[str, Dict[str, Dict[str, float | str]]] = {}
    shopping_list: set[str] = set()
    total_cost = 0.0
    total_calories = 0.0
    total_protein = 0.0
    meal_types = ["breakfast", "lunch", "dinner"] + (["snack"] if include_snacks else [])

    for day_index, day in enumerate(day_names[:days]):
        weekly_plan[day] = {}
        for meal_index, meal_type in enumerate(meal_types):
            selected = _select_meal(meal_type, dietary_preference, day_index + meal_index)
            calories = float(selected["calories"])
            protein = float(selected["protein"])
            cost = float(selected["cost"]) * people * multiplier
            weekly_plan[day][meal_type] = {
                "name": str(selected["name"]),
                "calories": round(calories),
                "protein_g": round(protein, 1),
                "estimated_cost": round(cost, 2),
            }
            total_calories += calories
            total_protein += protein
            total_cost += cost
            _add_meal_to_shopping_list(str(selected["name"]), shopping_list)

    avg_daily_calories = round(total_calories / days)
    avg_daily_protein = round(total_protein / days, 1)
    insights = build_meal_plan_insights(avg_daily_calories, avg_daily_protein, dietary_preference)

    return {
        "meal_plan": weekly_plan,
        "total_weekly_cost": round(total_cost, 2),
        "cost_per_person_per_day": round(total_cost / (people * days), 2),
        "avg_daily_calories": avg_daily_calories,
        "avg_daily_protein_g": avg_daily_protein,
        "dietary_preference": dietary_preference,
        "serves": people,
        "days": days,
        "shopping_list": sorted(shopping_list),
        "insights": insights,
    }


def _add_meal_to_shopping_list(meal_name: str, shopping_list: set[str]) -> None:
    name = meal_name.lower()
    if "chicken" in name:
        shopping_list.add("Chicken breast")
    if "salmon" in name:
        shopping_list.add("Salmon fillets")
    if "vegetable" in name or "stir fry" in name or "curry" in name:
        shopping_list.update(["Mixed vegetables", "Onions", "Garlic"])
    if "quinoa" in name:
        shopping_list.add("Quinoa")
    if "oats" in name:
        shopping_list.add("Rolled oats")
    if "yogurt" in name:
        shopping_list.add("Greek yogurt")
    if "lentil" in name:
        shopping_list.add("Lentils")
    if "rice" in name:
        shopping_list.add("Brown rice")
    if "beans" in name:
        shopping_list.add("Beans")
    if "fruit" in name or "berries" in name or "banana" in name:
        shopping_list.add("Fresh fruit")


def build_meal_plan_insights(avg_daily_calories: int, avg_daily_protein: float, dietary_preference: str) -> List[str]:
    """Create practical meal-plan insights from calculated totals."""
    insights: List[str] = []
    if avg_daily_calories < 1800:
        insights.append("Consider adding a healthy snack if energy, hunger, or training recovery is low.")
    elif avg_daily_calories > 2400:
        insights.append("This is a higher-energy template, useful for active users or muscle-gain goals.")
    else:
        insights.append("The meal template is moderate and can be adjusted through portion size.")

    if avg_daily_protein >= 80:
        insights.append("Protein intake is strong for general fitness and muscle maintenance.")
    elif avg_daily_protein < 60:
        insights.append("Add protein-rich foods such as lentils, eggs, yogurt, tofu, fish, or chicken as appropriate.")

    if "vegetarian" in dietary_preference.lower() or "vegan" in dietary_preference.lower():
        insights.append("Pay attention to protein variety, iron, B12, calcium, and omega-3 sources.")
    return insights


def estimate_costs(ingredients: Iterable[str], servings: int = 4) -> Dict[str, object]:
    """Estimate broad ingredient costs with budget tips."""
    price_reference = {
        "chicken breast": 6.99,
        "ground beef": 5.99,
        "salmon": 12.99,
        "rice": 2.99,
        "pasta": 1.99,
        "broccoli": 2.99,
        "tomatoes": 3.99,
        "cheese": 5.99,
        "onion": 1.49,
        "garlic": 2.99,
        "olive oil": 7.99,
        "quinoa": 4.99,
        "oats": 2.99,
        "lentils": 2.49,
        "beans": 1.99,
    }
    servings = max(1, servings)
    breakdown: List[Dict[str, float | str]] = []
    total_cost = 0.0
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower().strip()
        cost = 3.99
        for key, price in price_reference.items():
            if key in ingredient_lower or any(word in ingredient_lower for word in key.split()):
                cost = price
                break
        adjusted = (cost * servings) / 4
        total_cost += adjusted
        breakdown.append({"name": ingredient.title(), "cost": round(adjusted, 2)})

    tips = ["Shop local and compare bulk prices for staples."]
    if total_cost > 30:
        tips.append("Batch-cook grains, legumes, and proteins to reduce weekly cost.")
    if total_cost > 40:
        tips.append("Use seasonal produce and swap expensive proteins when needed.")
    return {
        "total_cost": round(total_cost, 2),
        "cost_per_serving": round(total_cost / servings, 2),
        "servings": servings,
        "breakdown": breakdown,
        "budget_tips": tips,
    }


def search_recipes(ingredients: str, diet_type: Optional[str] = None, number: int = 5) -> Dict[str, object]:
    """Search recipes through Spoonacular when configured; otherwise return a clear fallback."""
    api_key = os.getenv("SPOONACULAR_API_KEY")
    if not api_key:
        return {"status": "skipped", "message": "SPOONACULAR_API_KEY is not configured.", "recipes": []}
    if requests is None:
        return {"status": "error", "message": "requests is not installed.", "recipes": []}

    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": api_key,
        "ingredients": ingredients,
        "number": max(1, min(number, 10)),
        "ranking": 2,
        "ignorePantry": True,
    }
    if diet_type:
        params["diet"] = diet_type

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:  # type: ignore[union-attr]
        return {"status": "error", "message": f"Recipe search failed: {exc}", "recipes": []}

    recipes = []
    for recipe in data:
        recipes.append(
            {
                "id": recipe.get("id"),
                "title": recipe.get("title", "Untitled recipe"),
                "used_ingredients": [item.get("name", "") for item in recipe.get("usedIngredients", [])],
                "missing_ingredients": [item.get("name", "") for item in recipe.get("missedIngredients", [])],
            }
        )
    return {"status": "ok", "recipes": recipes, "total_found": len(data)}


def meal_plan_to_markdown(plan: Dict[str, object]) -> str:
    """Render a generated meal plan dictionary into readable Markdown."""
    lines = [
        f"- Dietary preference: {plan['dietary_preference']}",
        f"- Serves: {plan['serves']} person(s)",
        f"- Days planned: {plan['days']}",
        f"- Average daily calories: {plan['avg_daily_calories']}",
        f"- Average daily protein: {plan['avg_daily_protein_g']} g",
        f"- Estimated weekly cost: {plan['total_weekly_cost']}",
        f"- Cost per person per day: {plan['cost_per_person_per_day']}",
        "",
        "### Day-by-Day Meal Template",
    ]
    meal_plan = plan.get("meal_plan", {})
    if isinstance(meal_plan, dict):
        for day, meals in meal_plan.items():
            lines.append(f"\n**{day}**")
            if isinstance(meals, dict):
                for meal_type, meal in meals.items():
                    if isinstance(meal, dict):
                        lines.append(
                            f"- {meal_type.title()}: {meal['name']} "
                            f"({meal['calories']} kcal, {meal['protein_g']} g protein)"
                        )
    shopping = plan.get("shopping_list", [])
    if shopping:
        lines.append("\n### Shopping List")
        lines.extend(f"- {item}" for item in shopping)
    insights = plan.get("insights", [])
    if insights:
        lines.append("\n### Meal Planning Notes")
        lines.extend(f"- {item}" for item in insights)
    return "\n".join(lines).strip()

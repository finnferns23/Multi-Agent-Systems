"""Meal planning specialist agent."""

from __future__ import annotations

from .base import AgentResult, BaseAgent
from tools import UserProfile, create_meal_plan, meal_plan_to_markdown


class MealPlannerAgent(BaseAgent):
    """Creates practical meal templates, shopping lists, and budget-aware meal guidance."""

    name = "Meal Planning Agent"
    system_prompt = (
        "You are a practical meal planning agent. Give general wellness meal planning guidance, "
        "not medical nutrition therapy. Keep plans realistic, budget-aware, and preference-compatible."
    )

    def create_plan(self, profile: UserProfile) -> AgentResult:
        budget = "low" if "budget" in profile.constraints.lower() or "cheap" in profile.constraints.lower() else "moderate"
        deterministic_plan = create_meal_plan(
            dietary_preference=profile.dietary_preference,
            people=1,
            days=7,
            budget=budget,
            include_snacks=True,
        )
        structured_meal_plan = meal_plan_to_markdown(deterministic_plan)

        llm_context = (
            "Create a realistic meal plan section using this calculated meal template. "
            "Include meal timing, simple swaps, shopping guidance, and adherence tips. "
            "Do not claim medical treatment or exact clinical nutrition targets.\n\n"
            f"User profile:\n{profile.to_prompt()}\n\n"
            f"Calculated meal template:\n{structured_meal_plan}"
        )
        model_output = self.run(llm_context).content
        content = f"{structured_meal_plan}\n\n### Personalized Meal Guidance\n{model_output}"
        return AgentResult(agent_name=self.name, content=content)

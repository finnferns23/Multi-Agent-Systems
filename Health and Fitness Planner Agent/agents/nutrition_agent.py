"""Nutrition planning specialist agent."""

from __future__ import annotations

from .base import BaseAgent, AgentResult
from tools import UserProfile


class NutritionPlanningAgent(BaseAgent):
    name = "Nutrition Planning Agent"
    system_prompt = "You are a practical nutrition planning agent. Give general wellness guidance, not medical diet therapy."

    def create_plan(self, profile: UserProfile) -> AgentResult:
        return self.run(
            "Create a realistic nutrition plan. Include meal structure, protein, fiber, hydration, portions, "
            "preference alignment, budget-friendly swaps, and adherence tips.\n\n"
            f"{profile.to_prompt()}"
        )

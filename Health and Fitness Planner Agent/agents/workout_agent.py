"""Workout programming specialist agent."""

from __future__ import annotations

from .base import BaseAgent, AgentResult
from tools import UserProfile


class WorkoutProgrammingAgent(BaseAgent):
    name = "Workout Programming Agent"
    system_prompt = "You are a fitness programming agent focused on safe progression, form, recovery, and consistency."

    def create_plan(self, profile: UserProfile) -> AgentResult:
        return self.run(
            "Create a weekly workout plan. Include warm-up, strength, cardio, mobility, cool-down, rest days, "
            "progression, equipment alternatives, and modifications for constraints.\n\n"
            f"{profile.to_prompt()}"
        )

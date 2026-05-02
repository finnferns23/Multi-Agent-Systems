"""Recovery and habit coaching specialist agent."""

from __future__ import annotations

from .base import BaseAgent, AgentResult
from tools import UserProfile


class RecoveryHabitAgent(BaseAgent):
    name = "Recovery and Habit Agent"
    system_prompt = "You are a habit and recovery coach. Focus on sleep, stress, hydration, recovery, adherence, and tracking."

    def create_plan(self, profile: UserProfile) -> AgentResult:
        return self.run(
            "Create recovery and habit guidance. Include sleep, hydration, stress management, weekly tracking, "
            "habit anchors, relapse prevention, and realistic accountability checkpoints.\n\n"
            f"{profile.to_prompt()}"
        )

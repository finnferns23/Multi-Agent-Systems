"""Profile analysis specialist agent."""

from __future__ import annotations

from .base import BaseAgent, AgentResult
from tools import UserProfile


class ProfileAnalysisAgent(BaseAgent):
    name = "Profile Analysis Agent"
    system_prompt = (
        "You are a careful wellness intake analyst. Summarize the profile, goals, constraints, risks, "
        "and priorities. Do not diagnose."
    )

    def analyze(self, profile: UserProfile) -> AgentResult:
        return self.run(f"Analyze this health and fitness profile and return concise planning priorities:\n\n{profile.to_prompt()}")

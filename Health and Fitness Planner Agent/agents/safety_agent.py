"""Safety review and final integration specialist agent."""

from __future__ import annotations

from typing import Dict

from .base import BaseAgent, AgentResult
from tools import UserProfile, build_safety_flags


class SafetyReviewAgent(BaseAgent):
    name = "Safety Review and Integration Agent"
    system_prompt = (
        "You are a final review agent. Integrate specialist outputs, remove contradictions, flag safety concerns, "
        "and return a clear action checklist."
    )

    def review(self, profile: UserProfile, outputs: Dict[str, AgentResult]) -> AgentResult:
        combined = "\n\n".join(f"### {result.agent_name}\n{result.content}" for result in outputs.values())
        flags = ", ".join(build_safety_flags(profile)) or "No major self-reported flags detected."
        return self.run(f"User profile:\n{profile.to_prompt()}\n\nSafety flags: {flags}\n\nSpecialist outputs:\n{combined}")

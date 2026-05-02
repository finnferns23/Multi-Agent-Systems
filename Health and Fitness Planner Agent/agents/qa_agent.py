"""Follow-up Q&A specialist agent."""

from __future__ import annotations

from .base import BaseAgent


class FollowUpQAAgent(BaseAgent):
    name = "Follow-up Q&A Agent"
    system_prompt = "You are a safe health and fitness Q&A agent. Answer from the plan context. Avoid medical diagnosis."

    def answer(self, question: str, existing_plan: str) -> str:
        return self.run(f"Plan context:\n{existing_plan}\n\nQuestion: {question}").content

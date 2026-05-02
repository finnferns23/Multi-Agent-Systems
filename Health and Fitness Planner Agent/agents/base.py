"""Shared base classes and model-provider routing for specialist agents."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
SUPPORTED_PROVIDERS = {"demo", "gemini", "openai"}


@dataclass(frozen=True)
class AgentResult:
    """Normalized response returned by each specialist agent."""

    agent_name: str
    content: str


class BaseAgent:
    """Base agent with OpenAI, Gemini, and deterministic demo support."""

    name: str = "Base Agent"
    system_prompt: str = "You are a helpful planning agent."

    def __init__(self, provider: str = "demo", api_key: Optional[str] = None, model_id: Optional[str] = None) -> None:
        provider = provider.lower().strip()
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider '{provider}'. Use one of: {sorted(SUPPORTED_PROVIDERS)}")
        self.provider = provider
        self.api_key = api_key or self._read_provider_key(provider)
        self.model_id = model_id or self._default_model(provider)

    @staticmethod
    def _default_model(provider: str) -> str:
        if provider == "openai":
            return DEFAULT_OPENAI_MODEL
        if provider == "gemini":
            return DEFAULT_GEMINI_MODEL
        return "deterministic-demo"

    @staticmethod
    def _read_provider_key(provider: str) -> Optional[str]:
        if provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        if provider == "gemini":
            return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        return None

    def run(self, user_prompt: str) -> AgentResult:
        """Execute the specialist agent and return a normalized result."""
        return AgentResult(agent_name=self.name, content=self._run_llm(self.system_prompt, user_prompt))

    def _run_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Run selected provider or deterministic local output."""
        if self.provider == "demo" or not self.api_key:
            return self._deterministic_response(system_prompt, user_prompt)
        if self.provider == "openai":
            return self._run_openai(system_prompt, user_prompt)
        if self.provider == "gemini":
            return self._run_gemini(system_prompt, user_prompt)
        return self._deterministic_response(system_prompt, user_prompt)

    def _run_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Run OpenAI through the modern Responses API."""
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("OpenAI package is missing. Run: pip install -r requirements.txt") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model_id,
            instructions=system_prompt,
            input=user_prompt,
            temperature=0.3,
        )
        return getattr(response, "output_text", "").strip()

    def _run_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Run Gemini through the current Google Gen AI SDK."""
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError("Google Gen AI package is missing. Run: pip install -r requirements.txt") from exc

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model_id,
            contents=user_prompt,
            config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.3),
        )
        text = getattr(response, "text", "")
        return text.strip() if text else str(response).strip()

    def _deterministic_response(self, system_prompt: str, user_prompt: str) -> str:
        """Local fallback keeps GitHub review runnable without API keys."""
        text = f"{system_prompt}\n{user_prompt}".lower()
        if "review" in text or "integration" in text or "specialist outputs" in text:
            return (
                "- The specialist outputs are aligned into one practical plan.\n"
                "- Keep training progression gradual and avoid ignoring pain, dizziness, or unusual fatigue.\n"
                "- Weekly checklist: complete planned sessions, hydrate, sleep consistently, and review adherence."
            )
        if "intake analyst" in text or "profile" in text or "planning priorities" in text:
            return (
                "- The profile supports a realistic, moderate plan that balances training, food quality, recovery, and consistency.\n"
                "- Prioritize sustainable routines over aggressive changes.\n"
                "- Use constraints, available training days, sleep, and stress level to guide plan intensity."
            )
        if "nutrition" in text or "meal" in text:
            return (
                "- Build each main meal around protein, vegetables or fruit, and a controlled carbohydrate or healthy-fat portion.\n"
                "- Use preference-compatible meals and simple swaps to improve adherence.\n"
                "- Hydrate regularly and adjust portions gradually based on progress and energy."
            )
        if "workout" in text or "strength" in text or "cardio" in text:
            return (
                "- Train 3-5 days weekly depending on availability, alternating strength, cardio, and mobility.\n"
                "- Start sessions with a warm-up and end with cool-down breathing or mobility.\n"
                "- Progress by adding small amounts of volume, load, or time only when recovery is stable."
            )
        if "recovery" in text or "habit" in text or "sleep" in text:
            return (
                "- Keep a consistent sleep window and reduce late-day stimulants where possible.\n"
                "- Track workouts, hydration, sleep, and energy weekly.\n"
                "- Use small habit anchors such as preparing water, planning meals, and scheduling workouts in advance."
            )
        if "question" in text and "plan context" in text:
            return "Use the generated plan as the base, make one small adjustment at a time, and keep safety constraints first."
        return (
            "- The user profile suggests starting with a realistic, moderate plan.\n"
            "- Prioritize consistency, safety, sleep, hydration, and sustainable routines.\n"
            "- Adjust training and nutrition based on weekly feedback rather than daily fluctuations."
        )

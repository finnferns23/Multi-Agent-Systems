"""Specialist agents and model wrappers for the travel planning app."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

import requests
from icalendar import Calendar, Event
from openai import OpenAI

from tools import LocalMCPToolRegistry, build_mcp_registry, make_date_window, truncate_for_error


APP_TITLE = "Multi-Agent AI Travel Agent"


@dataclass(frozen=True)
class Settings:
    """Runtime settings collected from environment variables and UI overrides."""

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    serpapi_api_key: str = ""
    google_maps_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"


@dataclass(frozen=True)
class TripRequest:
    """Structured trip details provided by the user."""

    destination: str
    days: int
    start_date: date
    origin: str = ""
    budget: str = ""
    travelers: str = ""
    preferences: str = ""
    accessibility: str = ""
    pace: str = "Balanced"
    accommodation_style: str = "Flexible"


class ChatModel(Protocol):
    """Minimal protocol shared by OpenAI and Ollama wrappers."""

    def generate(self, system: str, user: str) -> str:
        """Generate a response from a chat-style model."""


class OpenAIResponsesModel:
    """OpenAI wrapper using the modern Responses API client."""

    def __init__(self, api_key: str, model: str) -> None:
        if not api_key.strip():
            raise ValueError("OpenAI API key is required when OpenAI mode is selected.")
        if not model.strip():
            raise ValueError("OpenAI model name cannot be empty.")
        self.client = OpenAI(api_key=api_key.strip())
        self.model = model.strip()

    def generate(self, system: str, user: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.35,
        )
        text = getattr(response, "output_text", "")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("OpenAI returned an empty response.")
        return text.strip()


class OllamaChatModel:
    """Local Ollama chat wrapper. Requires Ollama to be running separately."""

    def __init__(self, base_url: str, model: str) -> None:
        if not base_url.strip():
            raise ValueError("Ollama base URL cannot be empty.")
        if not model.strip():
            raise ValueError("Ollama model name cannot be empty.")
        self.base_url = base_url.rstrip("/")
        self.model = model.strip()

    def generate(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": 0.35},
        }
        response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(f"Ollama returned an empty response: {truncate_for_error(data)}")
        return content.strip()


class BaseAgent:
    """Base class for deterministic specialist agents."""

    name = "Base Agent"

    def __init__(self, tools: LocalMCPToolRegistry) -> None:
        self.tools = tools

    def run(self, request: TripRequest) -> str:
        raise NotImplementedError


class MCPPlannerAgent(BaseAgent):
    """Prepares the planning context and lists available MCP-style tools."""

    name = "MCP Planner Agent"

    def run(self, request: TripRequest) -> str:
        date_range = self.tools.call(
            "date_window",
            start_date=request.start_date.isoformat(),
            days=request.days,
        )
        return textwrap.dedent(
            f"""
            ### MCP Planner Agent
            Registered MCP-style tools:
{self.tools.describe()}

            Planning window: {date_range}
            Planning rule: live prices, opening hours, visa rules, booking availability, weather, and policies must be treated as changeable unless verified by a current source.
            """
        ).strip()


class DestinationResearchAgent(BaseAgent):
    """Researches destination context, attractions, food, and seasonality."""

    name = "Destination Research Agent"

    def run(self, request: TripRequest) -> str:
        queries = [
            f"{request.destination} top attractions current travel guide",
            f"{request.destination} food neighborhoods restaurants travel guide",
            f"{request.destination} weather best time visit travel",
        ]
        return "\n\n".join(self.tools.call("web_search", query=query, limit=4) for query in queries)


class AccommodationAgent(BaseAgent):
    """Suggests accommodation zones and stay strategy."""

    name = "Accommodation Agent"

    def run(self, request: TripRequest) -> str:
        budget_hint = request.budget or "general budget"
        style_hint = request.accommodation_style or "flexible accommodation"
        queries = [
            f"best areas to stay in {request.destination} tourists {style_hint}",
            f"{request.destination} hotels neighborhoods travel guide {budget_hint}",
        ]
        return "\n\n".join(self.tools.call("web_search", query=query, limit=4) for query in queries)


class TransportAgent(BaseAgent):
    """Builds movement and transfer notes."""

    name = "Transport Agent"

    def run(self, request: TripRequest) -> str:
        route = self.tools.call(
            "route_distance",
            origin=request.origin,
            destination=request.destination,
        )
        search = self.tools.call(
            "web_search",
            query=f"{request.destination} airport transfer public transport tourist tips current",
            limit=4,
        )
        return f"### Route and Movement Notes\n{route}\n\n{search}"


class SafetyBudgetAgent(BaseAgent):
    """Collects safety, money, and broad cost-planning context."""

    name = "Safety and Budget Agent"

    def run(self, request: TripRequest) -> str:
        queries = [
            f"{request.destination} travel safety tips tourists current",
            f"{request.destination} daily travel budget meals transport attractions",
        ]
        return "\n\n".join(self.tools.call("web_search", query=query, limit=4) for query in queries)


class AccessibilityAgent(BaseAgent):
    """Adds accessibility-aware planning context where requirements exist."""

    name = "Accessibility Agent"

    def run(self, request: TripRequest) -> str:
        if not request.accessibility.strip():
            return (
                "### Accessibility Agent\n"
                "No specific accessibility requirements were provided. Keep walking distances realistic, avoid overpacked days, and verify accessibility before booking."
            )
        query = f"{request.destination} accessibility travel guide {request.accessibility}"
        return self.tools.call("web_search", query=query, limit=4)


class ItineraryCoordinatorAgent:
    """Final model-based agent that converts specialist outputs into an itinerary."""

    def __init__(self, model: ChatModel) -> None:
        self.model = model

    def run(self, request: TripRequest, research_pack: str) -> str:
        system = (
            "You are a senior multi-agent travel coordinator. Build practical, safe, and clearly structured travel plans. "
            "Use only the trip details and specialist-agent research provided. Do not invent confirmed prices, opening hours, visa rules, weather, hotel availability, or booking policies. "
            "When information is likely to change, label it as an estimate or verification item."
        )
        user = f"""
Create a complete travel plan from the specialist-agent research.

Trip request:
- Destination: {request.destination}
- Date window: {make_date_window(request.start_date.isoformat(), request.days)}
- Origin: {request.origin or 'Not specified'}
- Budget: {request.budget or 'Not specified'}
- Travelers: {request.travelers or 'Not specified'}
- Preferences: {request.preferences or 'General sightseeing'}
- Pace: {request.pace}
- Accommodation style: {request.accommodation_style}
- Accessibility / special requirements: {request.accessibility or 'None specified'}

Specialist-agent research pack:
{research_pack}

Output format:
1. Executive trip summary.
2. Important assumptions and verification notes.
3. Best stay area / accommodation strategy.
4. Transport and movement plan.
5. Day-by-day itinerary from Day 1 to Day {request.days}. Include morning, afternoon, evening, food ideas, transport notes, and cost level.
6. Budget guide using broad categories, not fabricated exact prices.
7. Safety, accessibility, etiquette, and local practical notes.
8. Booking checklist.
9. What to verify before payment.

Write in clean markdown. Keep it useful, realistic, and honest about unverified details.
"""
        return self.model.generate(system=system, user=user)


def build_model(provider: str, settings: Settings) -> ChatModel:
    """Create the selected LLM wrapper."""
    if provider == "OpenAI":
        return OpenAIResponsesModel(api_key=settings.openai_api_key, model=settings.openai_model)
    return OllamaChatModel(base_url=settings.ollama_base_url, model=settings.ollama_model)


def run_specialist_agents(request: TripRequest, settings: Settings) -> str:
    """Run all deterministic specialist agents and return their research pack."""
    tools = build_mcp_registry(settings.serpapi_api_key, settings.google_maps_api_key)
    agents: list[BaseAgent] = [
        MCPPlannerAgent(tools),
        DestinationResearchAgent(tools),
        AccommodationAgent(tools),
        TransportAgent(tools),
        SafetyBudgetAgent(tools),
        AccessibilityAgent(tools),
    ]

    sections: list[str] = []
    for agent in agents:
        try:
            result = agent.run(request)
        except requests.RequestException as exc:
            result = f"Live API request failed for this agent: {exc}. Verify this area manually."
        except Exception as exc:
            result = f"Agent failed safely: {exc}. Verify this area manually."
        sections.append(f"## {agent.name}\n{result}")

    if not settings.serpapi_api_key.strip():
        sections.append(
            "## Live Research Notice\n"
            "SerpAPI key was not provided, so web-search tools returned verification placeholders. "
            "The final itinerary should be treated as a planning draft until checked against current sources."
        )
    return "\n\n".join(sections)


def generate_ics(itinerary_markdown: str, start_date: date, days: int) -> str:
    """Create a simple calendar file with one all-day event per trip day."""
    calendar = Calendar()
    calendar.add("prodid", "-//Multi-Agent AI Travel Agent//EN")
    calendar.add("version", "2.0")
    for offset in range(max(1, int(days))):
        event_date = start_date + timedelta(days=offset)
        event = Event()
        event.add("summary", f"Travel itinerary - Day {offset + 1}")
        event.add("dtstart", event_date)
        event.add("dtend", event_date + timedelta(days=1))
        event.add("description", itinerary_markdown[:4000])
        calendar.add_component(event)
    return calendar.to_ical().decode("utf-8")

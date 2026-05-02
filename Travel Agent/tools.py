"""MCP-style local tools for the multi-agent travel planner.

The project intentionally uses a lightweight local registry instead of a
remote MCP server so the app remains easy to run from a simple portfolio repo.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Iterable

import requests


@dataclass(frozen=True)
class SearchResult:
    """Normalized web-search result returned by the search tool."""

    title: str
    link: str
    snippet: str


class LocalMCPToolRegistry:
    """Small MCP-style tool registry used by the specialist agents.

    Each tool has a stable name, a short description, and a callable. Agents use
    this single interface instead of calling external services directly.
    """

    def __init__(self) -> None:
        self._tools: dict[str, tuple[str, Callable[..., str]]] = {}

    def register(self, name: str, description: str, func: Callable[..., str]) -> None:
        """Register a callable tool by name."""
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Tool name cannot be empty.")
        self._tools[clean_name] = (description.strip(), func)

    def call(self, name: str, **kwargs: Any) -> str:
        """Execute a registered tool and return text output."""
        if name not in self._tools:
            available = ", ".join(sorted(self._tools)) or "none"
            raise KeyError(f"Unknown tool '{name}'. Available tools: {available}")
        return self._tools[name][1](**kwargs)

    def describe(self) -> str:
        """Return a markdown list of registered tools."""
        if not self._tools:
            return "No MCP-style tools registered."
        return "\n".join(
            f"- {name}: {description}" for name, (description, _) in sorted(self._tools.items())
        )


def safe_text(value: Any, fallback: str = "") -> str:
    """Normalize unknown input into safe display text."""
    text = str(value).strip() if value is not None else ""
    return text or fallback


def serpapi_search(query: str, api_key: str, limit: int = 5) -> list[SearchResult]:
    """Search Google through SerpAPI.

    Returns an empty list when no API key is configured. This keeps the app
    runnable without live-search credentials while still being explicit about
    verification requirements in the UI and final output.
    """
    if not api_key.strip():
        return []

    bounded_limit = max(1, min(int(limit), 10))
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key.strip(),
        "num": bounded_limit,
    }
    response = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
    response.raise_for_status()
    data: dict[str, Any] = response.json()

    results: list[SearchResult] = []
    for item in (data.get("organic_results", []) or [])[:bounded_limit]:
        if not isinstance(item, dict):
            continue
        results.append(
            SearchResult(
                title=safe_text(item.get("title"), "Untitled result"),
                link=safe_text(item.get("link"), "No link returned"),
                snippet=safe_text(item.get("snippet"), "No snippet returned"),
            )
        )
    return results


def format_search_results(query: str, results: Iterable[SearchResult]) -> str:
    """Format search results as markdown for agent context."""
    rows = list(results)
    if not rows:
        return (
            f"### {query}\n"
            "No live source results available. Verify current details manually before booking."
        )

    lines = [f"### {query}"]
    for index, result in enumerate(rows, start=1):
        lines.append(
            f"{index}. **{result.title}**\n"
            f"   - {result.snippet}\n"
            f"   - Source: {result.link}"
        )
    return "\n".join(lines)


def google_distance(origin: str, destination: str, api_key: str) -> str:
    """Return a route estimate from Google Distance Matrix when configured."""
    if not api_key.strip() or not origin.strip() or not destination.strip():
        return "Google Maps route check skipped because the API key, origin, or destination was missing."

    params = {
        "origins": origin.strip(),
        "destinations": destination.strip(),
        "key": api_key.strip(),
        "mode": "transit",
        "units": "metric",
    }
    response = requests.get(
        "https://maps.googleapis.com/maps/api/distancematrix/json",
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    rows = data.get("rows", [])
    if not rows or not rows[0].get("elements"):
        return "Google Maps returned no route elements. Verify the route manually."

    element = rows[0]["elements"][0]
    if element.get("status") != "OK":
        status = element.get("status", "UNKNOWN")
        return f"Google Maps route status: {status}. Verify transport manually."

    distance = element.get("distance", {}).get("text", "unknown distance")
    duration = element.get("duration", {}).get("text", "unknown duration")
    return f"Approximate public-transit route from {origin} to {destination}: {distance}, {duration}."


def make_date_window(start_date: str, days: int) -> str:
    """Create a readable travel date range."""
    parsed = datetime.fromisoformat(start_date).date()
    safe_days = max(1, int(days))
    end = parsed + timedelta(days=safe_days - 1)
    return f"{parsed.isoformat()} to {end.isoformat()} ({safe_days} day(s))"


def build_mcp_registry(serpapi_api_key: str, google_maps_api_key: str) -> LocalMCPToolRegistry:
    """Build and return all local MCP-style tools used by the agents."""
    registry = LocalMCPToolRegistry()
    registry.register(
        "web_search",
        "Search current travel information through SerpAPI when a key is provided.",
        lambda query, limit=5: format_search_results(
            str(query), serpapi_search(str(query), serpapi_api_key, int(limit))
        ),
    )
    registry.register(
        "route_distance",
        "Estimate route distance and duration through Google Maps when a key is provided.",
        lambda origin, destination: google_distance(str(origin), str(destination), google_maps_api_key),
    )
    registry.register(
        "date_window",
        "Create the travel date range from a start date and trip length.",
        lambda start_date, days: make_date_window(str(start_date), int(days)),
    )
    return registry


def truncate_for_error(data: Any, limit: int = 500) -> str:
    """Return a compact string useful for API diagnostics."""
    return json.dumps(data, ensure_ascii=False)[:limit]

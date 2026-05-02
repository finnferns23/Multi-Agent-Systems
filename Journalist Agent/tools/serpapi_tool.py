"""SerpAPI tool factory for the research agent."""

from __future__ import annotations


def create_serpapi_tools(api_key: str):
    """Create Agno SerpAPI tools with a validated API key."""

    cleaned_key = (api_key or "").strip()
    if not cleaned_key:
        raise ValueError("SerpAPI key is required to create search tools.")

    from agno.tools.serpapi import SerpApiTools

    return SerpApiTools(api_key=cleaned_key)

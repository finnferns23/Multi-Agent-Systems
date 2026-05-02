"""Searcher agent definition."""

from __future__ import annotations

from textwrap import dedent

from config import AppConfig
from tools import create_serpapi_tools


def create_searcher_agent(config: AppConfig):
    """Create the agent that researches credible URLs for an article topic."""

    from agno.agent import Agent
    from agno.models.openai import OpenAIChat

    return Agent(
        name="Searcher",
        role="Researches credible, relevant, and current source URLs for article topics.",
        model=OpenAIChat(id=config.model_id, api_key=config.openai_api_key),
        description=dedent(
            """
            You are a research journalist. Given a topic, create focused search terms,
            search the web, inspect the results carefully, and return high quality URLs
            that can support a reliable article.
            """
        ).strip(),
        instructions=[
            "Generate three focused search terms for the topic before searching.",
            "Use the search tool for each term and compare result quality.",
            "Return up to ten source URLs with a one sentence reason for each URL.",
            "Prioritize primary sources, official reports, reputable journalism, research papers, and expert commentary.",
            "Avoid thin, duplicate, promotional, or unreliable sources.",
            "Do not invent URLs, facts, dates, names, or quotations.",
        ],
        tools=[create_serpapi_tools(config.serpapi_api_key)],
        add_datetime_to_context=True,
        markdown=True,
    )

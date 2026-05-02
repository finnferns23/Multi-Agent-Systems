"""Editor agent definition and team orchestration."""

from __future__ import annotations

from config import AppConfig
from agents.searcher_agent import create_searcher_agent
from agents.writer_agent import create_writer_agent


def create_editor_agent(config: AppConfig):
    """Create the editor agent that coordinates searcher and writer agents."""

    from agno.agent import Agent
    from agno.models.openai import OpenAIChat

    searcher = create_searcher_agent(config)
    writer = create_writer_agent(config)

    return Agent(
        name="Editor",
        role="Coordinates research and writing, then performs final editorial review.",
        model=OpenAIChat(id=config.model_id, api_key=config.openai_api_key),
        team=[searcher, writer],
        description="You are the final editor responsible for producing a reliable, polished article.",
        instructions=[
            "Ask the Searcher to find the most relevant source URLs for the requested topic.",
            "Give the topic and selected source URLs to the Writer for drafting.",
            "Review the draft for clarity, attribution, balance, structure, and factual caution.",
            "Remove unsupported claims or clearly mark them as analysis when appropriate.",
            "Return a clean final article in Markdown.",
        ],
        add_datetime_to_context=True,
        markdown=True,
    )

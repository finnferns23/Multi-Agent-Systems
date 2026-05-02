"""Writer agent definition."""

from __future__ import annotations

from textwrap import dedent

from config import AppConfig
from tools import create_newspaper_tools


def _length_guidance(article_length: str) -> str:
    """Return writing guidance for the selected article length."""

    guidance = {
        "short": "Write a concise article of around 700 to 900 words.",
        "balanced": "Write a polished article of around 1,000 to 1,400 words.",
        "long": "Write a detailed article of around 1,500 to 2,000 words.",
    }
    return guidance.get(article_length, guidance["balanced"])


def create_writer_agent(config: AppConfig):
    """Create the agent that drafts the article from researched sources."""

    from agno.agent import Agent
    from agno.models.openai import OpenAIChat

    return Agent(
        name="Writer",
        role="Reads source material and writes a clear, balanced, well attributed article.",
        model=OpenAIChat(id=config.model_id, api_key=config.openai_api_key),
        description=dedent(
            """
            You are a senior editorial writer. Given a topic and source URLs,
            read the available material and produce a structured article with
            attribution, context, analysis, and a strong editorial flow.
            """
        ).strip(),
        instructions=[
            "Read source URLs with the extraction tool where possible.",
            _length_guidance(config.article_length),
            "Use a headline, standfirst, section headings, and concise paragraphs.",
            "Attribute important facts naturally in the article body.",
            "Separate confirmed facts from analysis or interpretation.",
            "Do not plagiarize and do not fabricate quotes, statistics, sources, or events.",
            "End with a short source notes section listing the main source types used.",
        ],
        tools=[create_newspaper_tools()],
        add_datetime_to_context=True,
        markdown=True,
    )

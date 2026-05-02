"""Application workflow for generating researched articles."""

from __future__ import annotations

from agents import create_editor_agent
from config import build_config


def generate_article(
    topic: str,
    openai_api_key: str | None = None,
    serpapi_api_key: str | None = None,
    model_id: str | None = None,
    article_length: str | None = None,
) -> str:
    """Generate an article by running the editor led multi agent workflow."""

    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        raise ValueError("Topic cannot be empty.")

    config = build_config(
        openai_api_key=openai_api_key,
        serpapi_api_key=serpapi_api_key,
        model_id=model_id,
        article_length=article_length,
    )
    editor = create_editor_agent(config)
    response = editor.run(cleaned_topic, stream=False)
    content = getattr(response, "content", response)
    return str(content).strip()

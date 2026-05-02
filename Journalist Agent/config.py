"""Configuration helpers for AI Journalist Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

ArticleLength = Literal["short", "balanced", "long"]

DEFAULT_MODEL_ID = "gpt-4o"
DEFAULT_ARTICLE_LENGTH: ArticleLength = "balanced"


@dataclass(frozen=True)
class AppConfig:
    """Validated runtime settings for the journalist workflow."""

    openai_api_key: str
    serpapi_api_key: str
    model_id: str = DEFAULT_MODEL_ID
    article_length: ArticleLength = DEFAULT_ARTICLE_LENGTH


def _clean(value: str | None) -> str:
    """Return a stripped string for optional text input."""

    return (value or "").strip()


def env_value(name: str) -> str:
    """Read a stripped environment variable value."""

    return _clean(os.getenv(name))


def normalize_article_length(value: str | None) -> ArticleLength:
    """Normalize and validate the requested article length preset."""

    cleaned = _clean(value).lower()
    if cleaned in {"short", "balanced", "long"}:
        return cleaned  # type: ignore[return-value]
    return DEFAULT_ARTICLE_LENGTH


def build_config(
    openai_api_key: str | None = None,
    serpapi_api_key: str | None = None,
    model_id: str | None = None,
    article_length: str | None = None,
) -> AppConfig:
    """Build configuration from explicit values first, then environment variables."""

    resolved_openai_key = _clean(openai_api_key) or env_value("OPENAI_API_KEY")
    resolved_serpapi_key = _clean(serpapi_api_key) or env_value("SERPAPI_API_KEY")
    resolved_model_id = _clean(model_id) or DEFAULT_MODEL_ID

    if not resolved_openai_key:
        raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY or enter it in the app.")
    if not resolved_serpapi_key:
        raise ValueError("SerpAPI key is required. Set SERPAPI_API_KEY or enter it in the app.")

    return AppConfig(
        openai_api_key=resolved_openai_key,
        serpapi_api_key=resolved_serpapi_key,
        model_id=resolved_model_id,
        article_length=normalize_article_length(article_length),
    )

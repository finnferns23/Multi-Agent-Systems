"""Newspaper extraction tool factory for the writer agent."""

from __future__ import annotations


def create_newspaper_tools():
    """Create Agno Newspaper4k tools for extracting article text from URLs."""

    from agno.tools.newspaper4k import Newspaper4kTools

    return Newspaper4kTools()

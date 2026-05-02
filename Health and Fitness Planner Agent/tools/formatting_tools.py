"""Formatting helpers used by CLI and Streamlit outputs."""

from __future__ import annotations

from typing import Dict


def format_plan(title: str, sections: Dict[str, str]) -> str:
    """Create consistent Markdown output for CLI and Streamlit display."""
    output = [f"# {title}"]
    for heading, body in sections.items():
        output.append(f"\n## {heading}\n{body.strip()}")
    return "\n".join(output).strip() + "\n"

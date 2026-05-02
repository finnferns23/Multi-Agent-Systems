"""Tool factories used by AI Journalist Agent."""

from tools.newspaper_tool import create_newspaper_tools
from tools.serpapi_tool import create_serpapi_tools

__all__ = ["create_newspaper_tools", "create_serpapi_tools"]

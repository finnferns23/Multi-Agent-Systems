"""Command line entry point for AI Journalist Agent."""

from __future__ import annotations

import argparse
import sys

from workflows import generate_article


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description="Generate a researched article with AI Journalist Agent.")
    parser.add_argument("topic", nargs="+", help="Article topic to research and write about.")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model ID. Default: gpt-4o")
    parser.add_argument(
        "--length",
        choices=("short", "balanced", "long"),
        default="balanced",
        help="Article length preset. Default: balanced",
    )
    return parser.parse_args()


def main() -> int:
    """Run the command line application."""

    args = parse_args()
    topic = " ".join(args.topic)

    try:
        article = generate_article(topic=topic, model_id=args.model, article_length=args.length)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(article)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Command-line entry point for the Health and Fitness Planner Agent."""

from __future__ import annotations

import argparse

from agents import DEFAULT_GEMINI_MODEL, DEFAULT_OPENAI_MODEL, HealthFitnessOrchestrator
from tools import UserProfile, validate_profile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an end-to-end health and fitness plan.")
    parser.add_argument("--provider", choices=["demo", "gemini", "openai"], default="demo")
    parser.add_argument("--model", default=None, help=f"Defaults: Gemini={DEFAULT_GEMINI_MODEL}, OpenAI={DEFAULT_OPENAI_MODEL}")
    parser.add_argument("--age", type=int, default=30)
    parser.add_argument("--weight", type=float, default=70.0, help="Weight in kg")
    parser.add_argument("--height", type=float, default=170.0, help="Height in cm")
    parser.add_argument("--sex", default="Other")
    parser.add_argument("--activity", default="Moderately Active")
    parser.add_argument("--diet", default="Balanced")
    parser.add_argument("--goal", default="Stay Fit")
    parser.add_argument("--constraints", default="None provided")
    parser.add_argument("--experience", default="Beginner")
    parser.add_argument("--days", type=int, default=4)
    parser.add_argument("--minutes", type=int, default=45)
    parser.add_argument("--equipment", default="Bodyweight and basic gym equipment")
    parser.add_argument("--sleep", type=float, default=7.0)
    parser.add_argument("--stress", default="Moderate")
    return parser


def build_profile(args: argparse.Namespace) -> UserProfile:
    return UserProfile(
        age=args.age,
        weight_kg=args.weight,
        height_cm=args.height,
        sex=args.sex,
        activity_level=args.activity,
        dietary_preference=args.diet,
        fitness_goal=args.goal,
        constraints=args.constraints,
        experience_level=args.experience,
        available_days=args.days,
        session_minutes=args.minutes,
        equipment=args.equipment,
        sleep_hours=args.sleep,
        stress_level=args.stress,
    )


def main() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    args = build_parser().parse_args()
    profile = build_profile(args)
    errors = validate_profile(profile)
    if errors:
        raise SystemExit("Invalid profile: " + "; ".join(errors))

    orchestrator = HealthFitnessOrchestrator(provider=args.provider, model_id=args.model)
    print(orchestrator.generate_plan(profile))


if __name__ == "__main__":
    main()

"""Safety helpers for non-medical fitness planning."""

from __future__ import annotations

from typing import List

from .profile_tools import UserProfile


def build_safety_flags(profile: UserProfile) -> List[str]:
    """Create non-diagnostic safety flags for the final review agent."""
    notes = profile.constraints.lower()
    keywords = [
        "injury",
        "pain",
        "pregnant",
        "pregnancy",
        "diabetes",
        "heart",
        "blood pressure",
        "medication",
        "allergy",
        "eating disorder",
    ]
    flags = [word for word in keywords if word in notes]
    if profile.sleep_hours < 6:
        flags.append("low sleep")
    if profile.stress_level.lower() == "high":
        flags.append("high stress")
    return flags


def safety_notice() -> str:
    """Standard non-medical disclaimer for generated wellness guidance."""
    return (
        "This project provides educational wellness guidance only and is not medical advice. "
        "Consult a qualified healthcare professional before changing diet, exercise intensity, "
        "medication, rehabilitation, or recovery routines, especially if you have injuries, "
        "medical conditions, pregnancy-related concerns, eating-disorder history, or chronic pain."
    )

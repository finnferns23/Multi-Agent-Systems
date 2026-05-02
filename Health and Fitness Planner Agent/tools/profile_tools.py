"""Profile data model and validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class UserProfile:
    """Validated user profile collected from the CLI or Streamlit app."""

    age: int
    weight_kg: float
    height_cm: float
    sex: str
    activity_level: str
    dietary_preference: str
    fitness_goal: str
    constraints: str = "None provided"
    experience_level: str = "Beginner"
    available_days: int = 4
    session_minutes: int = 45
    equipment: str = "Bodyweight and basic gym equipment"
    sleep_hours: float = 7.0
    stress_level: str = "Moderate"

    def to_prompt(self) -> str:
        """Return a stable plain-text profile block for all agent prompts."""
        return (
            f"Age: {self.age}\n"
            f"Weight: {self.weight_kg:.1f} kg\n"
            f"Height: {self.height_cm:.1f} cm\n"
            f"Sex: {self.sex}\n"
            f"Activity level: {self.activity_level}\n"
            f"Dietary preference: {self.dietary_preference}\n"
            f"Fitness goal: {self.fitness_goal}\n"
            f"Experience level: {self.experience_level}\n"
            f"Training days available: {self.available_days}\n"
            f"Session length: {self.session_minutes} minutes\n"
            f"Equipment access: {self.equipment}\n"
            f"Typical sleep: {self.sleep_hours:.1f} hours\n"
            f"Stress level: {self.stress_level}\n"
            f"Constraints, injuries, allergies, or notes: {self.constraints}"
        )


def validate_profile(profile: UserProfile) -> List[str]:
    """Return validation errors without raising, so UI layers can display them cleanly."""
    errors: List[str] = []
    if not 10 <= profile.age <= 100:
        errors.append("Age must be between 10 and 100.")
    if not 20 <= profile.weight_kg <= 300:
        errors.append("Weight must be between 20 kg and 300 kg.")
    if not 100 <= profile.height_cm <= 250:
        errors.append("Height must be between 100 cm and 250 cm.")
    if not 1 <= profile.available_days <= 7:
        errors.append("Available training days must be between 1 and 7.")
    if not 10 <= profile.session_minutes <= 180:
        errors.append("Session length must be between 10 and 180 minutes.")
    if not 3 <= profile.sleep_hours <= 12:
        errors.append("Sleep hours must be between 3 and 12.")
    if not profile.activity_level.strip():
        errors.append("Activity level is required.")
    if not profile.fitness_goal.strip():
        errors.append("Fitness goal is required.")
    if not profile.dietary_preference.strip():
        errors.append("Dietary preference is required.")
    return errors

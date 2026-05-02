"""Fitness and wellness calculation helpers."""

from __future__ import annotations


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate body mass index using metric units."""
    height_m = height_cm / 100
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    return round(weight_kg / (height_m * height_m), 1)


def estimate_daily_water_liters(weight_kg: float, activity_level: str) -> float:
    """Simple non-medical hydration estimate for general wellness planning."""
    base = weight_kg * 0.033
    active_levels = {"very active", "extremely active"}
    extra = 0.4 if activity_level.lower().strip() in active_levels else 0.2
    return round(base + extra, 1)

"""Typography formatting and fitting helpers."""

from __future__ import annotations

import re


def has_chinese(text: str) -> bool:
    """Return whether text contains a CJK Unified Ideograph."""
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def format_coordinates(latitude: float, longitude: float) -> str:
    """Format signed coordinates with cardinal directions."""
    lat_direction = "N" if latitude >= 0 else "S"
    lon_direction = "E" if longitude >= 0 else "W"
    return f"{abs(latitude):.4f}° {lat_direction} / {abs(longitude):.4f}° {lon_direction}"


def apply_letter_spacing(text: str, spacing: float) -> str:
    """Approximate tracking for Latin text without altering CJK text."""
    if spacing <= 0 or has_chinese(text):
        return text
    gap = " " if spacing < 0.16 else "  "
    return gap.join(text.upper())


def safe_slug(value: str, fallback: str = "map-poster") -> str:
    """Create a readable Unicode-safe filename slug."""
    value = value.replace("_", "-")
    value = re.sub(r"[^\w\-]+", "-", value.strip().lower(), flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-_")
    return value[:80] or fallback


def fitted_font_size(text: str, requested: float, max_units: float, minimum: float = 18) -> float:
    """Return a deterministic first-pass title size for a bounded layout region."""
    if not text:
        return requested
    units = sum(1.0 if has_chinese(char) else 0.62 for char in text)
    if units <= max_units:
        return requested
    return max(minimum, requested * max_units / units)

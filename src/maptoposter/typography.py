"""Typography formatting and fitting helpers."""

from __future__ import annotations

import re


def resolve_text_positions(
    *,
    figure_height: float,
    text_rect_y: float,
    text_rect_height: float,
    title_y: float,
    subtitle_y: float,
    caption_y: float,
    coordinates_y: float,
    title_size: float,
    subtitle_size: float,
    caption_size: float,
    coordinate_size: float,
    has_title: bool,
    has_subtitle: bool,
    has_caption: bool,
    show_coordinates: bool,
) -> dict[str, float]:
    """Keep poster text boxes separated when the figure becomes short and wide.

    Layout coordinates are normalized to the figure. Font sizes are points, so
    their normalized height changes with the physical figure height. Computing
    the stack from those two units prevents the fixed portrait coordinates from
    causing overlap in landscape posters.
    """
    if figure_height <= 0:
        raise ValueError("Figure height must be greater than zero.")

    gap = 0.012

    def normalized_height(size: float) -> float:
        return size / 72 / figure_height

    heights = {
        "title": normalized_height(title_size),
        "subtitle": normalized_height(subtitle_size),
        "caption": normalized_height(caption_size),
        "coordinates": normalized_height(coordinate_size),
    }
    positions = {
        "title": title_y,
        "subtitle": subtitle_y,
        "caption": caption_y,
        "coordinates": coordinates_y,
    }
    active = [
        ("title", title_y, has_title),
        ("subtitle", subtitle_y, has_subtitle),
        ("caption", caption_y, has_caption),
        ("coordinates", coordinates_y, show_coordinates),
    ]

    previous_key: str | None = None
    for key, desired, enabled in active:
        if not enabled:
            continue
        if previous_key is not None:
            desired = min(
                desired,
                positions[previous_key]
                - heights[previous_key] / 2
                - gap
                - heights[key] / 2,
            )
        positions[key] = desired
        previous_key = key

    if has_title:
        top_limit = text_rect_y + text_rect_height - heights["title"] / 2
        positions["title"] = min(positions["title"], top_limit)

    if has_title and has_subtitle:
        title_bottom = positions["title"] - heights["title"] / 2
        subtitle_top = positions["subtitle"] + heights["subtitle"] / 2
        positions["divider"] = (title_bottom + subtitle_top) / 2
    elif has_title:
        positions["divider"] = positions["title"] - heights["title"] / 2 - gap / 2
    else:
        positions["divider"] = subtitle_y

    return positions


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

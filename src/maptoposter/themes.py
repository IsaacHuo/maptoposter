"""Theme discovery and loading helpers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .paths import THEMES_DIR


DEFAULT_THEME_NAME = "feature_based"

DEFAULT_THEME: dict[str, Any] = {
    "name": "Feature-Based Shading",
    "bg": "#FFFFFF",
    "text": "#000000",
    "gradient_color": "#FFFFFF",
    "water": "#C0C0C0",
    "parks": "#F0F0F0",
    "road_motorway": "#0A0A0A",
    "road_primary": "#1A1A1A",
    "road_secondary": "#2A2A2A",
    "road_tertiary": "#3A3A3A",
    "road_residential": "#4A4A4A",
    "road_default": "#3A3A3A",
}


def _theme_path(theme_name: str) -> Path:
    return THEMES_DIR / f"{theme_name}.json"


@lru_cache(maxsize=None)
def list_themes() -> tuple[str, ...]:
    """Return available theme names sorted by filename."""
    if not THEMES_DIR.exists():
        return ()
    return tuple(sorted(path.stem for path in THEMES_DIR.glob("*.json")))


@lru_cache(maxsize=None)
def _load_theme_cached(theme_name: str) -> tuple[tuple[str, Any], ...] | None:
    path = _theme_path(theme_name)
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as theme_file:
        theme = json.load(theme_file)
    return tuple(theme.items())


def load_theme_info(theme_name: str) -> dict[str, Any] | None:
    """Load a theme JSON file, returning None when it does not exist."""
    cached = _load_theme_cached(theme_name)
    if cached is None:
        return None
    return dict(cached)


def load_theme(theme_name: str = DEFAULT_THEME_NAME, *, verbose: bool = True) -> dict[str, Any]:
    """Load a theme with the embedded default as a fallback."""
    theme = load_theme_info(theme_name)
    if theme is None:
        if verbose:
            path = _theme_path(theme_name)
            print(f"⚠ Theme file '{path}' not found. Using default feature_based theme.")
        return DEFAULT_THEME.copy()

    if verbose:
        print(f"✓ Loaded theme: {theme.get('name', theme_name)}")
        if "description" in theme:
            print(f"  {theme['description']}")
    return theme


def get_theme_choices(lang: str = "en") -> list[tuple[str, str]]:
    """Return UI choices as (display name, internal theme name) tuples."""
    from cities_data import translate

    choices = []
    for internal_name in list_themes():
        theme_info = load_theme_info(internal_name)
        if theme_info:
            proper_name = theme_info.get("name", internal_name)
            display_name = translate(proper_name, lang)
            choices.append((display_name, internal_name))
        else:
            choices.append((internal_name, internal_name))
    return choices


"""Local Chinese administrative hierarchy and coordinate index."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from .models import Coordinate, Location
from .paths import CHINA_DATA_DIR


@lru_cache(maxsize=1)
def load_china_info() -> dict[str, dict[str, Any]]:
    """Load the compact hierarchy used by local place search."""
    path = CHINA_DATA_DIR / "info.json"
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def _walk_entries() -> list[tuple[dict[str, Any], dict[str, Any] | None]]:
    info = load_china_info()
    entries: list[tuple[dict[str, Any], dict[str, Any] | None]] = []
    for entry in info.values():
        for child in entry.get("children", []):
            entries.append((child, entry))
    return entries


@lru_cache(maxsize=256)
def search_china(query: str, limit: int = 8) -> tuple[Location, ...]:
    """Search local province/city/district names without an external request."""
    normalized = query.strip().lower()
    if not normalized:
        return ()
    matches: list[Location] = []
    for child, parent in _walk_entries():
        name = str(child.get("name", ""))
        center = child.get("center")
        if normalized not in name.lower() or not isinstance(center, list) or len(center) != 2:
            continue
        region = str(parent.get("name", "")) if parent else ""
        matches.append(
            Location(
                display_name=f"{name}, {region}, 中国" if region else f"{name}, 中国",
                coordinate=Coordinate(float(center[1]), float(center[0])),
                country="中国",
                region=region,
                country_code="cn",
                provider="china-local",
            )
        )
        if len(matches) >= limit:
            break
    return tuple(matches)

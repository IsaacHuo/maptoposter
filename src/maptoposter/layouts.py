"""Poster layout definitions in normalized figure coordinates."""

from __future__ import annotations

from dataclasses import dataclass

from .models import LayoutPreset


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class LayoutSpec:
    map_rect: Rect
    text_rect: Rect
    alignment: str
    title_y: float
    subtitle_y: float
    caption_y: float
    coordinates_y: float
    divider_y: float
    fade_top: bool = False
    fade_bottom: bool = True


LAYOUTS: dict[LayoutPreset, LayoutSpec] = {
    LayoutPreset.CLASSIC: LayoutSpec(
        Rect(0, 0, 1, 1), Rect(0.08, 0.045, 0.84, 0.18), "center", 0.145, 0.105, 0.082, 0.055, 0.128, True, True
    ),
    LayoutPreset.EDITORIAL: LayoutSpec(
        Rect(0.055, 0.285, 0.89, 0.66),
        Rect(0.08, 0.055, 0.84, 0.19),
        "left",
        0.195,
        0.147,
        0.105,
        0.072,
        0.168,
        False,
        False,
    ),
    LayoutPreset.MINIMAL: LayoutSpec(
        Rect(0.03, 0.17, 0.94, 0.79),
        Rect(0.055, 0.035, 0.48, 0.12),
        "left",
        0.125,
        0.09,
        0.063,
        0.038,
        0.103,
        False,
        False,
    ),
    LayoutPreset.BOTTOM_LEFT: LayoutSpec(
        Rect(0, 0, 1, 1), Rect(0.06, 0.04, 0.6, 0.2), "left", 0.175, 0.13, 0.09, 0.058, 0.148, False, True
    ),
    LayoutPreset.CENTERED: LayoutSpec(
        Rect(0.045, 0.045, 0.91, 0.91),
        Rect(0.15, 0.38, 0.7, 0.24),
        "center",
        0.56,
        0.505,
        0.455,
        0.415,
        0.532,
        True,
        True,
    ),
}


def get_layout(preset: LayoutPreset | str) -> LayoutSpec:
    """Return a normalized layout specification."""
    return LAYOUTS[LayoutPreset(preset)]

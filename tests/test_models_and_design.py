from __future__ import annotations

import pytest

from maptoposter.layouts import LAYOUTS, get_layout
from maptoposter.models import Coordinate, LayoutPreset, PosterSize, SizePreset, TypographyConfig
from maptoposter.themes import list_themes, load_style
from maptoposter.typography import apply_letter_spacing, fitted_font_size, format_coordinates, safe_slug
from maptoposter.viewport import create_viewport


def test_coordinate_and_viewport_validation() -> None:
    with pytest.raises(ValueError, match="Latitude"):
        Coordinate(91, 0)
    viewport = create_viewport(Coordinate(39.9042, 116.4074), 10_000, 12, 16)
    assert viewport.bbox.west < 116.4074 < viewport.bbox.east
    assert viewport.bbox.south < 39.9042 < viewport.bbox.north
    with pytest.raises(ValueError, match="89"):
        create_viewport(Coordinate(89.2, 0), 10_000, 12, 16)


def test_sizes_and_layouts_are_distinct() -> None:
    assert PosterSize(SizePreset.THREE_FOUR).dimensions == (12.0, 16.0)
    assert PosterSize(SizePreset.SQUARE).dimensions == (12.0, 12.0)
    with pytest.raises(ValueError, match="requires"):
        PosterSize(SizePreset.CUSTOM)
    assert len(LAYOUTS) == 5
    assert len({get_layout(item).map_rect for item in LayoutPreset}) >= 3


def test_theme_loading_and_custom_colors() -> None:
    names = list_themes()
    assert len(names) >= 5
    style = load_style("japanese_ink")
    changed = style.with_colors(background="#123456", road_primary="#654321")
    assert changed.background == "#123456"
    assert style.background != changed.background
    with pytest.raises(ValueError, match="Unknown"):
        style.with_colors(not_a_color="#000000")


def test_typography_helpers() -> None:
    assert format_coordinates(-12.3, -45.6) == "12.3000° S / 45.6000° W"
    assert apply_letter_spacing("ABC", 0.08) == "A B C"
    assert apply_letter_spacing("北京", 0.2) == "北京"
    assert fitted_font_size("A VERY LONG POSTER TITLE", 54, 5) < 54
    assert safe_slug("Where We Met / 北京") == "where-we-met-北京"
    with pytest.raises(ValueError, match="alignment"):
        TypographyConfig(alignment="middle")

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pytest
from shapely.geometry import LineString, Polygon

from maptoposter.map_data import classify_road, split_features
from maptoposter.models import (
    ExportConfig,
    LayoutConfig,
    LayoutPreset,
    OutputFormat,
    PosterSize,
    PreviewConfig,
    SizePreset,
    TypographyConfig,
)
from maptoposter.renderer import PosterRenderer
from maptoposter.themes import list_themes, load_style


@pytest.mark.parametrize(
    ("value", "expected"),
    [("motorway", "motorway"), ("primary_link", "primary"), ("tertiary", "secondary"), (["service"], "residential")],
)
def test_road_classification(value, expected) -> None:
    assert classify_road(value) == expected


def test_feature_splitting() -> None:
    features = gpd.GeoDataFrame(
        {
            "natural": ["water", None, None],
            "leisure": [None, "park", None],
            "waterway": [None, None, "river"],
            "geometry": [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),
                LineString([(0, 2), (2, 2)]),
            ],
        },
        crs="EPSG:4326",
    )
    water_polygons, water_lines, parks = split_features(features)
    assert len(water_polygons) == len(water_lines) == len(parks) == 1


def test_renderer_supports_preview_and_vector_exports(map_data, poster_config) -> None:
    renderer = PosterRenderer()
    preview = renderer.render_preview(map_data, poster_config, PreviewConfig(dpi=72, max_dimension_px=480))
    svg = renderer.export(map_data, poster_config, ExportConfig(OutputFormat.SVG, dpi=72))
    pdf = renderer.export(
        map_data,
        replace_layout(poster_config, LayoutPreset.EDITORIAL),
        ExportConfig(OutputFormat.PDF, dpi=72),
    )
    assert preview.startswith(b"\x89PNG")
    assert b"<svg" in svg[:500]
    assert pdf.startswith(b"%PDF")
    assert plt.get_fignums() == []


def test_renderer_selects_bundled_font_for_chinese_text() -> None:
    fonts = PosterRenderer._fonts("广州")

    assert fonts["is_cjk"] is True
    assert Path(fonts["bold"].get_file()).name == "HYWenRunSongYunU.ttf"
    assert Path(fonts["regular"].get_file()).name == "HYWenRunSongYunU.ttf"


def replace_layout(config, layout: LayoutPreset):
    from dataclasses import replace

    return replace(config, layout=LayoutConfig(layout))


def test_renderer_rejects_invalid_roads(map_data, poster_config) -> None:
    map_data.roads = []
    with pytest.raises(TypeError, match="GeoDataFrame"):
        PosterRenderer().render_preview(map_data, poster_config, PreviewConfig(dpi=72, max_dimension_px=200))
    assert plt.get_fignums() == []


def test_renderer_design_matrix(map_data, poster_config) -> None:
    renderer = PosterRenderer()
    for style_name in list_themes()[:5]:
        for layout in list(LayoutPreset):
            config = replace_layout(poster_config, layout)
            config = config.__class__(
                location=config.location,
                map=config.map,
                style=load_style(style_name),
                typography=TypographyConfig(title="北京林业大学", subtitle="北京", caption="2024"),
                layout=config.layout,
                layers=config.layers,
                size=config.size,
            )
            assert renderer.render_preview(map_data, config, PreviewConfig(dpi=48, max_dimension_px=220)).startswith(
                b"\x89PNG"
            )
    for preset in (SizePreset.THREE_FOUR, SizePreset.FOUR_FIVE, SizePreset.SQUARE, SizePreset.A4):
        config = poster_config.__class__(
            location=poster_config.location,
            map=poster_config.map,
            style=poster_config.style,
            typography=poster_config.typography,
            layout=poster_config.layout,
            layers=poster_config.layers,
            size=PosterSize(preset),
        )
        assert renderer.render_preview(map_data, config, PreviewConfig(dpi=48, max_dimension_px=220)).startswith(
            b"\x89PNG"
        )
    assert plt.get_fignums() == []

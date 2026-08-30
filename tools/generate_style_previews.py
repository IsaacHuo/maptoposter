"""Generate small, renderer-backed style thumbnails for the web editor."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
from PIL import Image
from shapely.geometry import LineString, Polygon

from maptoposter.models import (
    BBox,
    Coordinate,
    Location,
    MapConfig,
    MapData,
    MapViewport,
    PosterConfig,
    PreviewConfig,
    TypographyConfig,
)
from maptoposter.renderer import PosterRenderer
from maptoposter.themes import list_themes, load_style


def build_fixture() -> MapData:
    roads = gpd.GeoDataFrame(
        {
            "road_class": ["motorway", "primary", "secondary", "residential"] * 2,
            "geometry": [
                LineString([(116.28, 39.96), (116.40, 40.05)]),
                LineString([(116.28, 40.05), (116.40, 39.96)]),
                LineString([(116.25, 40.00), (116.42, 40.00)]),
                LineString([(116.33, 39.94), (116.33, 40.07)]),
                LineString([(116.25, 39.98), (116.42, 40.04)]),
                LineString([(116.27, 40.03), (116.41, 39.97)]),
                LineString([(116.29, 39.95), (116.39, 40.06)]),
                LineString([(116.38, 39.95), (116.30, 40.06)]),
            ],
        },
        crs="EPSG:4326",
    )
    water = gpd.GeoDataFrame(
        {"geometry": [Polygon([(116.27, 39.97), (116.31, 39.96), (116.33, 39.99), (116.30, 40.01), (116.27, 39.97)])]},
        crs="EPSG:4326",
    )
    parks = gpd.GeoDataFrame(
        {"geometry": [Polygon([(116.35, 40.01), (116.39, 40.01), (116.40, 40.05), (116.36, 40.06), (116.35, 40.01)])]},
        crs="EPSG:4326",
    )
    return MapData(BBox(116.25, 39.94, 116.42, 40.07), roads, water_polygons=water, parks=parks)


def main() -> None:
    output = Path("frontend/public/style-previews")
    output.mkdir(parents=True, exist_ok=True)
    location = Location("Beijing", Coordinate(40.0, 116.335), "China", "Beijing")
    viewport = MapViewport(location.coordinate, BBox(116.25, 39.94, 116.42, 40.07), 11, 10_000)
    data = build_fixture()
    renderer = PosterRenderer()
    for name in list_themes():
        config = PosterConfig(
            location=location,
            map=MapConfig(viewport),
            style=load_style(name),
            typography=TypographyConfig(title="BEIJING", subtitle="CHINA", caption="MAPTOPOSTER"),
        )
        preview = renderer.render_preview(data, config, PreviewConfig(dpi=72, max_dimension_px=420))
        image = Image.open(__import__("io").BytesIO(preview))
        image.save(output / f"{name}.webp", "WEBP", quality=82, method=6)


if __name__ == "__main__":
    main()

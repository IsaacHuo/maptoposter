from __future__ import annotations

import geopandas as gpd
import pytest
from shapely.geometry import LineString, Polygon

from maptoposter.models import (
    BBox,
    Coordinate,
    Location,
    MapConfig,
    MapData,
    MapViewport,
    PosterConfig,
    TypographyConfig,
)
from maptoposter.themes import load_style


@pytest.fixture
def poster_config() -> PosterConfig:
    location = Location("Test Place", Coordinate(40.0, 116.3), "China", "Beijing")
    bbox = BBox(116.25, 39.95, 116.35, 40.05)
    return PosterConfig(
        location=location,
        map=MapConfig(MapViewport(location.coordinate, bbox, 11, 10_000)),
        style=load_style("japanese_ink"),
        typography=TypographyConfig(title="TEST PLACE", subtitle="BEIJING", caption="2024"),
    )


@pytest.fixture
def map_data() -> MapData:
    roads = gpd.GeoDataFrame(
        {
            "road_class": ["motorway", "primary", "secondary", "residential"],
            "geometry": [
                LineString([(116.25, 39.96), (116.35, 40.04)]),
                LineString([(116.26, 40.04), (116.34, 39.96)]),
                LineString([(116.25, 40.0), (116.35, 40.0)]),
                LineString([(116.3, 39.95), (116.3, 40.05)]),
            ],
        },
        crs="EPSG:4326",
    )
    water = gpd.GeoDataFrame(
        {"geometry": [Polygon([(116.26, 39.97), (116.28, 39.97), (116.28, 39.99), (116.26, 39.99)])]},
        crs="EPSG:4326",
    )
    parks = gpd.GeoDataFrame(
        {"geometry": [Polygon([(116.31, 40.01), (116.33, 40.01), (116.33, 40.03), (116.31, 40.03)])]},
        crs="EPSG:4326",
    )
    return MapData(BBox(116.25, 39.95, 116.35, 40.05), roads, water_polygons=water, parks=parks)

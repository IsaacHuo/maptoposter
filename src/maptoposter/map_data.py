"""OSM acquisition and persistent prepared-geometry cache."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, cast

import geopandas as gpd
import osmnx as ox
import pandas as pd

from .cache import CACHE_SCHEMA_VERSION, DiskCache, map_cache_key
from .models import BBox, MapConfig, MapData, MapDataRef

LOGGER = logging.getLogger(__name__)

FEATURE_TAGS: dict[str, bool | str | list[str]] = {
    "natural": ["water", "wood", "scrub"],
    "waterway": ["riverbank", "river", "stream", "canal", "dock"],
    "leisure": ["park", "garden", "nature_reserve"],
    "landuse": ["forest", "grass", "cemetery", "recreation_ground", "village_green"],
}


class MapDataError(RuntimeError):
    """Raised when map data cannot be prepared."""


def _first_highway(value: Any) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else "unclassified"
    return str(value or "unclassified")


def classify_road(value: Any) -> str:
    """Map an OSM highway value to a stable poster road class."""
    highway = _first_highway(value)
    if highway in {"motorway", "motorway_link"}:
        return "motorway"
    if highway in {"trunk", "trunk_link", "primary", "primary_link"}:
        return "primary"
    if highway in {"secondary", "secondary_link", "tertiary", "tertiary_link"}:
        return "secondary"
    return "residential"


def split_features(
    features: gpd.GeoDataFrame | None,
) -> tuple[gpd.GeoDataFrame | None, gpd.GeoDataFrame | None, gpd.GeoDataFrame | None]:
    """Split OSM features into water polygons, water lines, and park polygons."""
    if features is None or features.empty:
        return None, None, None
    geometry_types = features.geometry.geom_type
    water_mask = pd.Series(False, index=features.index)
    if "natural" in features:
        water_mask |= features["natural"].eq("water")
    if "waterway" in features:
        water_mask |= features["waterway"].notna()
    park_mask = pd.Series(False, index=features.index)
    if "leisure" in features:
        park_mask |= features["leisure"].notna()
    if "landuse" in features:
        park_mask |= features["landuse"].isin(cast(list[str], FEATURE_TAGS["landuse"]))
    if "natural" in features:
        park_mask |= features["natural"].isin(["wood", "scrub"])

    water_polygons = gpd.GeoDataFrame(
        features.loc[water_mask & geometry_types.isin(["Polygon", "MultiPolygon"])].copy(),
        geometry="geometry",
        crs=features.crs,
    )
    water_lines = gpd.GeoDataFrame(
        features.loc[water_mask & geometry_types.isin(["LineString", "MultiLineString"])].copy(),
        geometry="geometry",
        crs=features.crs,
    )
    parks = gpd.GeoDataFrame(
        features.loc[park_mask & geometry_types.isin(["Polygon", "MultiPolygon"])].copy(),
        geometry="geometry",
        crs=features.crs,
    )
    return (
        water_polygons if not water_polygons.empty else None,
        water_lines if not water_lines.empty else None,
        parks if not parks.empty else None,
    )


class MapDataService:
    """Download OSM data once and expose reusable, projected map geometry."""

    def __init__(self, cache: DiskCache | None = None) -> None:
        self.cache = cache or DiskCache()
        ox.settings.use_cache = True
        ox.settings.cache_folder = str(self.cache.root / "osmnx")

    def prepare(self, config: MapConfig) -> MapDataRef:
        key = map_cache_key(config)
        destination = self.cache.map_path(key)
        if self._is_complete(destination):
            return MapDataRef(key, destination, True)

        with self.cache.lock("map_data", key):
            if self._is_complete(destination):
                return MapDataRef(key, destination, True)
            data = self._download(config)
            with self.cache.atomic_directory(destination) as temporary:
                self._write(temporary, data, key)
        return MapDataRef(key, destination, False)

    def load(self, reference: MapDataRef | str) -> MapData:
        key = reference if isinstance(reference, str) else reference.cache_key
        path = self.cache.map_path(key)
        metadata = self.cache.read_json(path / "metadata.json")
        if not metadata:
            raise MapDataError(f"Map data cache entry does not exist: {key}")
        bbox_values = metadata.get("bbox")
        if not isinstance(bbox_values, list) or len(bbox_values) != 4:
            raise MapDataError("Map data cache metadata is invalid.")
        bbox = BBox(*(float(value) for value in bbox_values))
        roads = gpd.read_file(path / "roads.gpkg", layer="roads")
        return MapData(
            bbox=bbox,
            roads=roads,
            water_polygons=self._read_optional(path / "water_polygons.gpkg", "water_polygons"),
            water_lines=self._read_optional(path / "water_lines.gpkg", "water_lines"),
            parks=self._read_optional(path / "parks.gpkg", "parks"),
            crs=str(metadata.get("crs", roads.crs)),
            metadata=metadata,
        )

    @staticmethod
    def _is_complete(path: Path) -> bool:
        return (path / "metadata.json").is_file() and (path / "roads.gpkg").is_file()

    @staticmethod
    def _read_optional(path: Path, layer: str) -> gpd.GeoDataFrame | None:
        if not path.exists():
            return None
        data = gpd.read_file(path, layer=layer)
        return data if not data.empty else None

    def _download(self, config: MapConfig) -> MapData:
        bbox = config.viewport.bbox
        distance = config.viewport.distance_m or 0
        try:
            if distance > 50_000:
                graph = ox.graph_from_bbox(
                    bbox.as_tuple(),
                    network_type="drive",
                    custom_filter='["highway"~"motorway|trunk|primary|secondary"]',
                )
            else:
                graph = ox.graph_from_bbox(bbox.as_tuple(), network_type=config.network_type)
        except Exception as exc:
            raise MapDataError(f"Unable to download the road network: {exc}") from exc

        try:
            roads = ox.graph_to_gdfs(graph, nodes=False, fill_edge_geometry=True).reset_index(drop=True)
        except Exception as exc:
            raise MapDataError(f"Unable to prepare the road network: {exc}") from exc
        if roads.empty:
            raise MapDataError("OpenStreetMap returned no roads for this viewport.")
        highway = roads["highway"] if "highway" in roads else pd.Series("unclassified", index=roads.index)
        roads["road_class"] = highway.map(classify_road)

        try:
            features = ox.features_from_bbox(bbox.as_tuple(), tags=FEATURE_TAGS)
        except Exception as exc:
            LOGGER.warning("Optional map features are unavailable: %s", exc)
            features = None
        water_polygons, water_lines, parks = split_features(features)

        target_crs = roads.estimate_utm_crs() or "EPSG:3857"
        roads = roads.to_crs(target_crs)
        projected: list[gpd.GeoDataFrame | None] = []
        for item in (water_polygons, water_lines, parks):
            projected.append(item.to_crs(target_crs) if item is not None else None)
        return MapData(
            bbox=bbox,
            roads=roads,
            water_polygons=projected[0],
            water_lines=projected[1],
            parks=projected[2],
            crs=str(target_crs),
            metadata={"network_type": config.network_type, "distance_m": distance},
        )

    @staticmethod
    def _write(path: Path, data: MapData, key: str) -> None:
        roads = data.roads
        if not isinstance(roads, gpd.GeoDataFrame):
            raise MapDataError("Prepared road data must be a GeoDataFrame.")
        roads.to_file(path / "roads.gpkg", layer="roads", driver="GPKG", index=False)
        optional = {
            "water_polygons": data.water_polygons,
            "water_lines": data.water_lines,
            "parks": data.parks,
        }
        for name, frame in optional.items():
            if isinstance(frame, gpd.GeoDataFrame) and not frame.empty:
                frame.to_file(path / f"{name}.gpkg", layer=name, driver="GPKG", index=False)
        metadata = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "cache_key": key,
            "bbox": list(data.bbox.as_tuple()),
            "crs": data.crs,
            **data.metadata,
        }
        (path / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, sort_keys=True), encoding="utf-8")

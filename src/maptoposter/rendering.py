"""Core map poster rendering logic."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import matplotlib.colors as mcolors
import numpy as np
import osmnx as ox
import pandas as pd
from matplotlib.font_manager import FontProperties

from .fonts import load_fonts
from .geocoding import GeocodingService
from .map_data import MapDataService
from .models import (
    Coordinate,
    ExportConfig,
    LayerConfig,
    LayoutConfig,
    Location,
    MapConfig,
    OutputFormat,
    PosterConfig,
    PosterSize,
    SizePreset,
    StyleConfig,
    TypographyConfig,
)
from .paths import POSTERS_DIR
from .renderer import PosterRenderer
from .themes import load_style
from .viewport import create_bbox_tuple, create_viewport

ox.settings.use_cache = True

FEATURE_TAGS: dict[str, bool | str | list[str]] = {
    "natural": ["water", "wood", "scrub"],
    "waterway": ["riverbank", "dock"],
    "leisure": ["park", "garden", "nature_reserve"],
    "landuse": [
        "forest",
        "grass",
        "cemetery",
        "recreation_ground",
        "village_green",
    ],
}

POLYGON_TYPES = ["Polygon", "MultiPolygon"]
LINE_TYPES = ["LineString", "MultiLineString"]


def generate_output_filename(
    city: str,
    theme_name: str,
    output_format: str,
    directory: str | Path = POSTERS_DIR,
) -> str:
    """Generate unique output filename with city, theme, and datetime."""
    from .export import generate_output_filename as build_filename

    return build_filename(city, theme_name, output_format, directory)


def create_bbox(
    point: tuple[float, float], dist: float, width: float, height: float
) -> tuple[float, float, float, float]:
    """Create an OSMnx bbox tuple matching the poster aspect ratio."""
    return create_bbox_tuple(point, dist, width, height)


def create_gradient_fade(ax, color: str, location: str = "bottom", zorder: int = 10) -> None:
    """Create a fade effect at the top or bottom of the map."""
    vals = np.linspace(0, 1, 256).reshape(-1, 1)
    gradient = np.hstack((vals, vals))

    rgb = mcolors.to_rgb(color)
    my_colors = np.zeros((256, 4))
    my_colors[:, 0] = rgb[0]
    my_colors[:, 1] = rgb[1]
    my_colors[:, 2] = rgb[2]

    if location == "bottom":
        my_colors[:, 3] = np.linspace(1, 0, 256)
        extent_y_start = 0
        extent_y_end = 0.25
    else:
        my_colors[:, 3] = np.linspace(0, 1, 256)
        extent_y_start = 0.75
        extent_y_end = 1.0

    custom_cmap = mcolors.ListedColormap(my_colors)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    y_range = ylim[1] - ylim[0]
    y_bottom = ylim[0] + y_range * extent_y_start
    y_top = ylim[0] + y_range * extent_y_end

    ax.imshow(
        gradient,
        extent=[xlim[0], xlim[1], y_bottom, y_top],
        aspect="auto",
        cmap=custom_cmap,
        zorder=zorder,
        origin="lower",
    )


def _first_highway_type(data: dict[str, Any]) -> str:
    highway = data.get("highway", "unclassified")
    if isinstance(highway, list):
        return highway[0] if highway else "unclassified"
    return highway


def get_edge_colors_by_type(
    graph,
    theme: dict[str, Any],
    show_motorway: bool = True,
    show_primary: bool = True,
    show_secondary: bool = True,
) -> list[str]:
    """Assign colors to graph edges by OSM highway type."""
    edge_colors = []

    for _, _, data in graph.edges(data=True):
        highway = _first_highway_type(data)

        if highway in ["motorway", "motorway_link"]:
            color = theme["road_motorway"] if show_motorway else "none"
        elif highway in ["trunk", "trunk_link", "primary", "primary_link"]:
            color = theme["road_primary"] if show_primary else "none"
        elif highway in ["secondary", "secondary_link"]:
            color = theme["road_secondary"] if show_secondary else "none"
        elif highway in ["tertiary", "tertiary_link"]:
            color = theme["road_tertiary"] if show_secondary else "none"
        elif highway in [
            "residential",
            "living_street",
            "unclassified",
            "service",
            "road",
        ] or highway in ["path", "footway", "track", "cycleway", "pedestrian"]:
            color = theme["road_residential"]
        else:
            color = theme["road_default"]

        edge_colors.append(color)

    return edge_colors


def get_edge_widths_by_type(graph) -> list[float]:
    """Assign line widths to graph edges by OSM highway type."""
    edge_widths = []

    for _, _, data in graph.edges(data=True):
        highway = _first_highway_type(data)

        if highway in ["motorway", "motorway_link"]:
            width = 1.6
        elif highway in ["trunk", "trunk_link", "primary", "primary_link"]:
            width = 1.3
        elif highway in ["secondary", "secondary_link"]:
            width = 1.0
        elif highway in ["tertiary", "tertiary_link"] or highway in [
            "residential",
            "living_street",
            "unclassified",
            "service",
            "road",
        ]:
            width = 0.8
        elif highway in ["path", "footway", "track", "cycleway", "pedestrian"]:
            width = 0.5
        else:
            width = 0.6

        edge_widths.append(width)

    return edge_widths


def has_chinese(text: str) -> bool:
    """Check if a string contains any Chinese characters."""
    if not text:
        return False
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def get_coordinates(city: str, country: str, parent: str | None = None) -> tuple[float, float]:
    """Fetch coordinates from local overrides first, then Nominatim."""
    from cities_data import get_china_adcode, get_manual_coordinates

    if country == "中国":
        parent_adcode = None
        if parent:
            parent_adcode = get_china_adcode(parent)
            if not parent_adcode:
                parent_adcode = get_china_adcode(parent, 100000)

        manual_coords = get_manual_coordinates(city, parent_adcode)
        if manual_coords:
            print(f"✓ Using local coordinate data for {city}: {manual_coords}")
            return manual_coords

        manual_coords = get_manual_coordinates(city, 100000)
        if manual_coords:
            return manual_coords

    results = GeocodingService().search(f"{city}, {country}", limit=1)
    if results:
        coordinate = results[0].coordinate
        return (coordinate.latitude, coordinate.longitude)
    raise ValueError(f"Could not find coordinates for {city}, {country}")


def _simplify_polygons(features):
    simplified = features.copy()
    simplified.loc[:, "geometry"] = simplified.geometry.apply(
        lambda geometry: geometry.buffer(0) if not geometry.is_valid else geometry
    )
    simplified.loc[:, "geometry"] = simplified.geometry.simplify(
        tolerance=0.00001,
        preserve_topology=True,
    )
    return simplified[~simplified.geometry.is_empty]


def split_features(features):
    """Split OSM features into water polygons, water lines, and park polygons."""
    if features is None or features.empty:
        return None, None, None

    water_mask = pd.Series(False, index=features.index)
    if "natural" in features.columns:
        water_mask |= features["natural"].isin(["water"])
    if "waterway" in features.columns:
        water_mask |= features["waterway"].notna()

    water = features[water_mask]
    if not water.empty:
        water_polys = water[water.geometry.type.isin(POLYGON_TYPES)].copy()
        if not water_polys.empty:
            water_polys = _simplify_polygons(water_polys)

        water_lines = water[water.geometry.type.isin(LINE_TYPES)].copy()
    else:
        water_polys = None
        water_lines = None

    park_mask = pd.Series(False, index=features.index)
    if "leisure" in features.columns:
        park_mask |= features["leisure"].notna()
    if "landuse" in features.columns:
        park_mask |= features["landuse"].isin(["forest", "grass", "cemetery", "recreation_ground", "village_green"])
    if "natural" in features.columns:
        park_mask |= features["natural"].isin(["wood", "scrub"])

    parks = features[park_mask]
    if not parks.empty:
        parks = parks[parks.geometry.type.isin(POLYGON_TYPES)].copy()
        parks = _simplify_polygons(parks) if not parks.empty else None
    else:
        parks = None

    if water_polys is not None and water_polys.empty:
        water_polys = None
    if water_lines is not None and water_lines.empty:
        water_lines = None
    if parks is not None and parks.empty:
        parks = None
    return water_polys, water_lines, parks


def _load_map_data(bbox: tuple[float, float, float, float], is_large_area: bool):
    if is_large_area:
        custom_filter = '["highway"~"motorway|trunk|primary|secondary"]'
        graph = ox.graph_from_bbox(bbox, custom_filter=custom_filter, network_type="drive")
    else:
        graph = ox.graph_from_bbox(bbox, network_type="all")
    return graph


def _load_features(bbox: tuple[float, float, float, float]):
    try:
        return ox.features_from_bbox(bbox, tags=FEATURE_TAGS)
    except Exception as exc:
        print(f"Warning: Could not fetch features: {exc}")
        return None


def _build_font_properties(city: str):
    fonts = load_fonts()
    is_chinese = has_chinese(city)

    if fonts:
        if is_chinese:
            font_path = fonts.get("cn") or fonts.get("en_bold")
            font_main_base = FontProperties(fname=font_path)
            font_sub_base = FontProperties(fname=font_path)
            font_coords = FontProperties(fname=font_path, size=14)
        else:
            font_path_bold = fonts.get("en_bold")
            font_path_reg = fonts.get("en_regular")
            font_main_base = FontProperties(fname=font_path_bold)
            font_sub_base = FontProperties(fname=font_path_reg)
            font_coords = FontProperties(fname=font_path_reg, size=14)
    else:
        font_main_base = FontProperties(family="serif", weight="bold")
        font_sub_base = FontProperties(family="serif")
        font_coords = FontProperties(family="monospace", size=14)

    base_font_size = 60 if not is_chinese else 54
    city_char_count = len(city)
    if not is_chinese and city_char_count > 10:
        scale_factor = 10 / city_char_count
        adjusted_font_size = max(base_font_size * scale_factor, 24)
    elif is_chinese and city_char_count > 6:
        scale_factor = 6 / city_char_count
        adjusted_font_size = max(base_font_size * scale_factor, 32)
    else:
        adjusted_font_size = base_font_size

    font_main = font_main_base.copy()
    font_main.set_size(adjusted_font_size)

    font_sub = font_sub_base.copy()
    font_sub.set_size(22)

    attr_font = font_sub_base.copy()
    attr_font.set_size(8)

    return is_chinese, font_main, font_sub, font_coords, attr_font


def _format_display_text(city: str, country: str, is_chinese: bool) -> tuple[str, str]:
    if is_chinese:
        return city, country
    return "  ".join(list(city.upper())), country.upper()


def _format_coordinates(point: tuple[float, float]) -> str:
    lat, lon = point
    coords_text = f"{lat:.4f}° N / {lon:.4f}° E" if lat >= 0 else f"{abs(lat):.4f}° S / {lon:.4f}° E"
    if lon < 0:
        coords_text = coords_text.replace("E", "W")
    return coords_text


def create_poster(
    city: str,
    country: str,
    point: tuple[float, float],
    dist: float,
    output_file: str,
    output_format: str,
    *,
    theme: dict[str, Any] | None = None,
    theme_name: str = "feature_based",
    width: float = 12,
    height: float = 16,
    no_crop: bool = False,
    show_text: bool = True,
    show_motorway: bool = True,
    show_primary: bool = True,
    show_secondary: bool = True,
    show_water: bool = True,
    show_parks: bool = True,
):
    """Generate a map poster and yield user-facing progress strings."""
    del no_crop  # Exact poster dimensions are now always preserved.
    yield f"Generating map for {city}, {country}..."
    coordinate = Coordinate(*point)
    viewport = create_viewport(coordinate, dist, width, height)
    typed_style = _legacy_style(theme, theme_name)
    poster = PosterConfig(
        location=Location(city or "Custom location", coordinate, country=country),
        map=MapConfig(viewport=viewport, network_type="drive" if dist > 50_000 else "all"),
        style=typed_style,
        typography=TypographyConfig(
            title=city if show_text else "",
            subtitle=country if show_text else "",
            show_coordinates=show_text,
            show_divider=show_text,
        ),
        layout=LayoutConfig(),
        layers=LayerConfig(
            motorway=show_motorway,
            primary=show_primary,
            secondary=show_secondary,
            residential=True,
            water=show_water,
            parks=show_parks,
        ),
        size=PosterSize(SizePreset.CUSTOM, width, height),
    )
    map_service = MapDataService()
    yield "Downloading street network and features..."
    reference = map_service.prepare(poster.map)
    yield "Data cache hit. Rendering map..." if reference.cache_hit else "Data downloaded. Rendering map..."
    content = PosterRenderer().export(
        map_service.load(reference),
        poster,
        ExportConfig(OutputFormat(output_format.lower()), dpi=300),
    )
    yield f"Saving to {output_file}..."
    target = Path(output_file)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    temporary.write_bytes(content)
    os.replace(temporary, target)
    yield "Done!"


def _legacy_style(theme: dict[str, Any] | None, theme_name: str) -> StyleConfig:
    if theme is None:
        return load_style(theme_name)
    return StyleConfig(
        id=theme_name,
        name=str(theme.get("name", theme_name)),
        description=str(theme.get("description", "")),
        background=str(theme.get("bg", "#FFFFFF")),
        text=str(theme.get("text", "#000000")),
        water=str(theme.get("water", "#C0C0C0")),
        parks=str(theme.get("parks", "#F0F0F0")),
        road_motorway=str(theme.get("road_motorway", "#0A0A0A")),
        road_primary=str(theme.get("road_primary", "#1A1A1A")),
        road_secondary=str(theme.get("road_secondary", "#2A2A2A")),
        road_tertiary=str(theme.get("road_tertiary", "#3A3A3A")),
        road_residential=str(theme.get("road_residential", "#4A4A4A")),
        road_default=str(theme.get("road_default", "#3A3A3A")),
        gradient=str(theme.get("gradient_color", theme.get("bg", "#FFFFFF"))),
    )

"""Core map poster rendering logic."""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
import pandas as pd
from geopy.geocoders import Nominatim
from matplotlib.font_manager import FontProperties

from .fonts import load_fonts
from .paths import POSTERS_DIR
from .themes import load_theme


ox.settings.use_cache = True

FEATURE_TAGS = {
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
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    city_slug = city.lower().replace(" ", "_")
    ext = output_format.lower()
    filename = f"{city_slug}_{theme_name}_{timestamp}.{ext}"
    return str(output_dir / filename)


def create_bbox(point: tuple[float, float], dist: float, width: float, height: float) -> tuple[float, float, float, float]:
    """Create an OSMnx bbox tuple matching the poster aspect ratio."""
    if height == 0:
        raise ValueError("Poster height must be greater than 0.")

    lat, lon = point
    cos_lat = math.cos(math.radians(lat))
    if abs(cos_lat) < 1e-6:
        raise ValueError("Cannot calculate bounding box at this latitude.")

    dist_ns = dist
    dist_ew = dist * (width / height)

    delta_lat = dist_ns / 111320.0
    delta_lon = dist_ew / (111320.0 * cos_lat)

    north = max(lat + delta_lat, lat - delta_lat)
    south = min(lat + delta_lat, lat - delta_lat)
    west = min(lon - delta_lon, lon + delta_lon)
    east = max(lon - delta_lon, lon + delta_lon)
    return (west, south, east, north)


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
        ]:
            color = theme["road_residential"]
        elif highway in ["path", "footway", "track", "cycleway", "pedestrian"]:
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
        elif highway in ["tertiary", "tertiary_link"]:
            width = 0.8
        elif highway in [
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

    print(f"Looking up coordinates for {city}, {country} via Nominatim...")
    geolocator = Nominatim(user_agent="city_map_poster", timeout=10)

    import time

    time.sleep(1)
    location = geolocator.geocode(f"{city}, {country}")

    if location:
        print(f"✓ Found: {location.address}")
        print(f"✓ Coordinates: {location.latitude}, {location.longitude}")
        return (location.latitude, location.longitude)
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
        park_mask |= features["landuse"].isin(
            ["forest", "grass", "cemetery", "recreation_ground", "village_green"]
        )
    if "natural" in features.columns:
        park_mask |= features["natural"].isin(["wood", "scrub"])

    parks = features[park_mask]
    if not parks.empty:
        parks = parks[parks.geometry.type.isin(POLYGON_TYPES)].copy()
        if not parks.empty:
            parks = _simplify_polygons(parks)
        else:
            parks = None
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
    coords_text = (
        f"{lat:.4f}° N / {lon:.4f}° E"
        if lat >= 0
        else f"{abs(lat):.4f}° S / {lon:.4f}° E"
    )
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
    active_theme = theme if theme is not None else load_theme(theme_name)

    msg = f"Generating map for {city}, {country}..."
    print(f"\n{msg}")
    yield msg

    is_large_area = dist > 50000
    if is_large_area:
        print(f"Large area detected (dist={dist}m). Fetching major roads only.")
        yield "Large region detected. Fetching major roads only to avoid timeout..."

    bbox = create_bbox(point, dist, width, height)
    west, south, east, north = bbox

    if is_large_area:
        yield "Downloading major road network..."
    else:
        yield "Downloading street network..."
    graph = _load_map_data(bbox, is_large_area)

    yield "Downloading features (water, parks)..."
    features = _load_features(bbox)
    water_polys, water_lines, parks = split_features(features)

    print("✓ All data downloaded successfully!")
    yield "Data downloaded. Rendering map..."

    print("Rendering map...")
    fig, ax = plt.subplots(figsize=(width, height), facecolor=active_theme["bg"])
    ax.set_facecolor(active_theme["bg"])
    ax.set_position([0, 0, 1, 1])

    if show_water:
        if water_polys is not None and not water_polys.empty:
            water_polys.plot(
                ax=ax, facecolor=active_theme["water"], edgecolor="none", zorder=1
            )

        if water_lines is not None and not water_lines.empty:
            water_lines.plot(ax=ax, color=active_theme["water"], linewidth=2.0, zorder=1)

    if show_parks and parks is not None and not parks.empty:
        parks_polys = parks[parks.geometry.type.isin(POLYGON_TYPES)]
        if not parks_polys.empty:
            parks_polys.plot(
                ax=ax, facecolor=active_theme["parks"], edgecolor="none", zorder=2
            )

    print("Applying road hierarchy colors...")
    yield "Applying road styles..."
    edge_colors = get_edge_colors_by_type(
        graph,
        active_theme,
        show_motorway=show_motorway,
        show_primary=show_primary,
        show_secondary=show_secondary,
    )
    edge_widths = get_edge_widths_by_type(graph)

    ox.plot_graph(
        graph,
        ax=ax,
        bgcolor=active_theme["bg"],
        node_size=0,
        edge_color=edge_colors,
        edge_linewidth=edge_widths,
        show=False,
        close=False,
    )

    ax.set_aspect("equal")
    ax.set_xlim(west, east)
    ax.set_ylim(south, north)

    create_gradient_fade(ax, active_theme["gradient_color"], location="bottom", zorder=10)
    create_gradient_fade(ax, active_theme["gradient_color"], location="top", zorder=10)

    is_chinese, font_main, font_sub, font_coords, attr_font = _build_font_properties(city)
    display_city, display_country = _format_display_text(city, country, is_chinese)

    if show_text:
        if display_city:
            ax.text(
                0.5,
                0.14,
                display_city,
                transform=ax.transAxes,
                color=active_theme["text"],
                ha="center",
                fontproperties=font_main,
                zorder=11,
            )

        if display_country:
            ax.text(
                0.5,
                0.10,
                display_country,
                transform=ax.transAxes,
                color=active_theme["text"],
                ha="center",
                fontproperties=font_sub,
                zorder=11,
            )

        if display_city and display_country:
            ax.plot(
                [0.4, 0.6],
                [0.125, 0.125],
                transform=ax.transAxes,
                color=active_theme["text"],
                linewidth=1,
                zorder=11,
            )

        if display_city or display_country:
            ax.text(
                0.5,
                0.07,
                _format_coordinates(point),
                transform=ax.transAxes,
                color=active_theme["text"],
                alpha=0.7,
                ha="center",
                fontproperties=font_coords,
                zorder=11,
            )

    ax.text(
        0.98,
        0.02,
        "© OpenStreetMap contributors",
        transform=ax.transAxes,
        color=active_theme["text"],
        alpha=0.5,
        ha="right",
        va="bottom",
        fontproperties=attr_font,
        zorder=11,
    )

    print(f"Saving to {output_file}...")
    yield f"Saving to {output_file}..."

    fmt = output_format.lower()
    save_kwargs = dict(facecolor=active_theme["bg"], pad_inches=0.05)
    if not no_crop:
        save_kwargs["bbox_inches"] = "tight"
    if fmt == "png":
        save_kwargs["dpi"] = 300

    plt.savefig(output_file, format=fmt, **save_kwargs)
    plt.close(fig)
    print(f"✓ Done! Poster saved as {output_file}")
    yield "Done!"


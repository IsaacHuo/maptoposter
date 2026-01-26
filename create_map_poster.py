import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.colors as mcolors
import numpy as np
from geopy.geocoders import Nominatim
import time
import json
import os
from datetime import datetime
import argparse

# Explicitly enable caching
ox.settings.use_cache = True

THEMES_DIR = "themes"
FONTS_DIR = "fonts"
POSTERS_DIR = "posters"


def load_fonts():
    """
    Load fonts for both English (Goudy Old Style) and Chinese (HYWenRunSongYunU).
    """
    fonts = {
        "en_bold": os.path.join(FONTS_DIR, "GoudyOldStyle-Bold.ttf"),
        "en_regular": os.path.join(FONTS_DIR, "GoudyOldStyle-Regular.ttf"),
        "cn": os.path.join(FONTS_DIR, "HYWenRunSongYunU.ttf"),
    }

    # Verify fonts exist
    available_fonts = {}
    for key, path in fonts.items():
        if os.path.exists(path):
            available_fonts[key] = path
        else:
            print(f"⚠ Font not found: {path}")

    return available_fonts if available_fonts else None


FONTS = load_fonts()


def generate_output_filename(city, theme_name, output_format, directory=POSTERS_DIR):
    """
    Generate unique output filename with city, theme, and datetime.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    city_slug = city.lower().replace(" ", "_")
    ext = output_format.lower()
    filename = f"{city_slug}_{theme_name}_{timestamp}.{ext}"
    return os.path.join(directory, filename)


def get_available_themes():
    """
    Scans the themes directory and returns a list of available theme names.
    """
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR)
        return []

    themes = []
    for file in sorted(os.listdir(THEMES_DIR)):
        if file.endswith(".json"):
            theme_name = file[:-5]  # Remove .json extension
            themes.append(theme_name)
    return themes


def load_theme(theme_name="feature_based"):
    """
    Load theme from JSON file in themes directory.
    """
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")

    if not os.path.exists(theme_file):
        print(
            f"⚠ Theme file '{theme_file}' not found. Using default feature_based theme."
        )
        # Fallback to embedded default theme
        return {
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

    with open(theme_file, "r") as f:
        theme = json.load(f)
        print(f"✓ Loaded theme: {theme.get('name', theme_name)}")
        if "description" in theme:
            print(f"  {theme['description']}")
        return theme


# Load theme (can be changed via command line or input)
THEME = None  # Will be loaded later


def create_gradient_fade(ax, color, location="bottom", zorder=10):
    """
    Creates a fade effect at the top or bottom of the map.
    """
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


def get_edge_colors_by_type(
    G, show_motorway=True, show_primary=True, show_secondary=True
):
    """
    Assigns colors to edges based on road type hierarchy.
    Returns a list of colors corresponding to each edge in the graph.
    If a layer is hidden, returns 'none' for that edge.
    """
    edge_colors = []

    for u, v, data in G.edges(data=True):
        # Get the highway type (can be a list or string)
        highway = data.get("highway", "unclassified")

        # Handle list of highway types (take the first one)
        if isinstance(highway, list):
            highway = highway[0] if highway else "unclassified"

        # Assign color based on road type
        if highway in ["motorway", "motorway_link"]:
            color = THEME["road_motorway"] if show_motorway else "none"
        elif highway in ["trunk", "trunk_link", "primary", "primary_link"]:
            color = THEME["road_primary"] if show_primary else "none"
        elif highway in ["secondary", "secondary_link"]:
            color = THEME["road_secondary"] if show_secondary else "none"
        elif highway in ["tertiary", "tertiary_link"]:
            color = (
                THEME["road_tertiary"] if show_secondary else "none"
            )  # Group tertiary with secondary
        elif highway in [
            "residential",
            "living_street",
            "unclassified",
            "service",
            "road",
        ]:
            color = THEME["road_residential"]
        elif highway in ["path", "footway", "track", "cycleway", "pedestrian"]:
            # Use residential color or a lighter version if defined, for now residential
            color = THEME["road_residential"]
        else:
            color = THEME["road_default"]

        edge_colors.append(color)

    return edge_colors


def get_edge_widths_by_type(G):
    """
    Assigns line widths to edges based on road type.
    Major roads get thicker lines.
    """
    edge_widths = []

    for u, v, data in G.edges(data=True):
        highway = data.get("highway", "unclassified")

        if isinstance(highway, list):
            highway = highway[0] if highway else "unclassified"

        # Assign width based on road importance (increased for visibility)
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


def has_chinese(text):
    """Check if a string contains any Chinese characters."""
    if not text:
        return False
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            return True
    return False


def get_coordinates(city, country, parent=None):
    """
    Fetches coordinates for a given city and country.
    First checks for manual overrides in cities_data, then falls back to geopy.
    """
    from cities_data import get_manual_coordinates, get_china_adcode

    # For China, try local data first
    if country == "中国":
        parent_adcode = None
        if parent:
            parent_adcode = get_china_adcode(parent)

            # Fallback if parent is already a city/province name and get_china_adcode failed
            # (though it shouldn't for these inputs)
            if not parent_adcode:
                # Try looking up parent as a direct child of China
                parent_adcode = get_china_adcode(parent, 100000)

        # Try finding city in province
        manual_coords = get_manual_coordinates(city, parent_adcode)
        if manual_coords:
            print(f"✓ Using local coordinate data for {city}: {manual_coords}")
            return manual_coords

        # Fallback: if city has its own children (like districts), it might be a city level entry
        # but manual_coordinates requires a parent.
        # Actually, get_manual_coordinates handles hardcoded ones too.
        # Let's try looking it up as a province if parent_adcode is 100000
        manual_coords = get_manual_coordinates(city, 100000)
        if manual_coords:
            return manual_coords

    print(f"Looking up coordinates for {city}, {country} via Nominatim...")
    geolocator = Nominatim(user_agent="city_map_poster", timeout=10)

    # Add a small delay to respect Nominatim's usage policy
    time.sleep(1)

    location = geolocator.geocode(f"{city}, {country}")

    if location:
        print(f"✓ Found: {location.address}")
        print(f"✓ Coordinates: {location.latitude}, {location.longitude}")
        return (location.latitude, location.longitude)
    else:
        raise ValueError(f"Could not find coordinates for {city}, {country}")


def create_poster(
    city,
    country,
    point,
    dist,
    output_file,
    output_format,
    width=12,
    height=16,
    no_crop=False,
    show_motorway=True,
    show_primary=True,
    show_secondary=True,
    show_water=True,
    show_parks=True,
):
    msg = f"Generating map for {city}, {country}..."
    print(f"\n{msg}")
    yield msg

    # Calculate non-square distances to match figure aspect ratio
    # dist is the vertical (North-South) half-distance
    dist_ns = dist
    dist_ew = dist * (width / height)

    # Progress bar for data fetching
    # Note: tqdm writes to stderr, we will just yield status updates for the UI

    # 1. Fetch Street Network
    # Detect if we are doing a "Whole Province" (large area)
    # If the bounding box is very large, we should limit the road types to avoid timeouts
    is_large_area = False
    if dist > 50000: # Over 50km half-width is likely a province or large region
        is_large_area = True
        print(f"Large area detected (dist={dist}m). Fetching major roads only.")
        yield "Large region detected. Fetching major roads only to avoid timeout..."

    import math

    lat, lon = point
    delta_lat = dist_ns / 111320.0
    delta_lon = dist_ew / (111320.0 * math.cos(math.radians(lat)))

    north, south = lat + delta_lat, lat - delta_lat
    west, east = lon - delta_lon, lon + delta_lon

    bbox = (west, south, east, north)
    
    if is_large_area:
        # Use custom filter for major roads only
        custom_filter = (
            '["highway"~"motorway|trunk|primary|secondary"]'
        )
        yield "Downloading major road network..."
        G = ox.graph_from_bbox(bbox, custom_filter=custom_filter, network_type="drive")
    else:
        yield "Downloading street network..."
        G = ox.graph_from_bbox(bbox, network_type="all")

    # 2. Fetch Water and Parks in one request
    yield "Downloading features (water, parks)..."
    tags = {
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

    water_polys = None
    water_lines = None
    parks = None

    try:
        features = ox.features_from_bbox(bbox, tags=tags)

        # Separate features and simplify geometries for faster rendering
        if features is not None and not features.empty:
            # Safe mask creation for Water
            water_mask = pd.Series(False, index=features.index)
            if "natural" in features.columns:
                water_mask |= features["natural"].isin(["water"])
            if "waterway" in features.columns:
                water_mask |= features["waterway"].notna()

            water = features[water_mask]

            if not water.empty:
                # Water Polygons (Lakes, Wide Rivers)
                water_polys = water[
                    water.geometry.type.isin(["Polygon", "MultiPolygon"])
                ]
                if not water_polys.empty:
                    water_polys.geometry = water_polys.geometry.simplify(
                        tolerance=0.00001, preserve_topology=True
                    )

                # Water Lines (Rivers, Streams represented as lines)
                water_lines = water[
                    water.geometry.type.isin(["LineString", "MultiLineString"])
                ]
            else:
                water_polys, water_lines = None, None  # No water features found

            # Green space/Parks features
            park_mask = pd.Series(False, index=features.index)
            if "leisure" in features.columns:
                park_mask |= features["leisure"].notna()
            if "landuse" in features.columns:
                park_mask |= features["landuse"].isin(
                    [
                        "forest",
                        "grass",
                        "cemetery",
                        "recreation_ground",
                        "village_green",
                    ]
                )
            if "natural" in features.columns:
                park_mask |= features["natural"].isin(["wood", "scrub"])

            parks = features[park_mask]
            if not parks.empty:
                parks = parks[parks.geometry.type.isin(["Polygon", "MultiPolygon"])]
                # Simplify geometries
                parks.geometry = parks.geometry.simplify(
                    tolerance=0.00001, preserve_topology=True
                )
            else:
                parks = None  # No park features found
        else:
            water_polys, water_lines, parks = None, None, None
    except Exception as e:
        print(f"Warning: Could not fetch features: {e}")
        water_polys, water_lines, parks = None, None, None

    print("✓ All data downloaded successfully!")
    yield "Data downloaded. Rendering map..."

    # 2. Setup Plot
    print("Rendering map...")
    fig, ax = plt.subplots(figsize=(width, height), facecolor=THEME["bg"])
    ax.set_facecolor(THEME["bg"])
    ax.set_position([0, 0, 1, 1])

    # 3. Plot Layers
    # Layer 1: Polygons (filter to only plot polygon/multipolygon geometries, not points)
    # Layer 1: Water (Polygons and Lines)
    if show_water:
        if water_polys is not None and not water_polys.empty:
            water_polys.plot(
                ax=ax, facecolor=THEME["water"], edgecolor="none", zorder=1
            )

        if water_lines is not None and not water_lines.empty:
            # Plot water lines (rivers) with some thickness
            water_lines.plot(ax=ax, color=THEME["water"], linewidth=2.0, zorder=1)

    if show_parks and parks is not None and not parks.empty:
        # Filter to only polygon/multipolygon geometries to avoid point features showing as dots
        parks_polys = parks[parks.geometry.type.isin(["Polygon", "MultiPolygon"])]
        if not parks_polys.empty:
            parks_polys.plot(
                ax=ax, facecolor=THEME["parks"], edgecolor="none", zorder=2
            )

    # Layer 2: Roads with hierarchy coloring
    print("Applying road hierarchy colors...")
    yield "Applying road styles..."
    edge_colors = get_edge_colors_by_type(
        G,
        show_motorway=show_motorway,
        show_primary=show_primary,
        show_secondary=show_secondary,
    )
    edge_widths = get_edge_widths_by_type(G)

    ox.plot_graph(
        G,
        ax=ax,
        bgcolor=THEME["bg"],
        node_size=0,
        edge_color=edge_colors,
        edge_linewidth=edge_widths,
        show=False,
        close=False,
    )

    # Layer 3: Gradients (Top and Bottom)
    create_gradient_fade(ax, THEME["gradient_color"], location="bottom", zorder=10)
    create_gradient_fade(ax, THEME["gradient_color"], location="top", zorder=10)

    # 4. Typography
    is_chinese = has_chinese(city)

    if FONTS:
        if is_chinese:
            # Chinese styling
            font_path = FONTS.get("cn") or FONTS.get("en_bold")
            font_main_base = FontProperties(fname=font_path)
            font_sub_base = FontProperties(fname=font_path)
            font_coords = FontProperties(fname=font_path, size=14)

            display_city = city
            display_country = country
        else:
            # English styling (Original)
            font_path_bold = FONTS.get("en_bold")
            font_path_reg = FONTS.get("en_regular")
            font_main_base = FontProperties(fname=font_path_bold)
            font_sub_base = FontProperties(fname=font_path_reg)
            font_coords = FontProperties(fname=font_path_reg, size=14)

            # Spaced and uppercase for English
            display_city = "  ".join(list(city.upper()))
            display_country = country.upper()
    else:
        # Fallback to system fonts
        font_main_base = FontProperties(family="serif", weight="bold")
        font_sub_base = FontProperties(family="serif")
        font_coords = FontProperties(family="monospace", size=14)

        if is_chinese:
            display_city = city
            display_country = country
        else:
            display_city = "  ".join(list(city.upper()))
            display_country = country.upper()

    # Dynamically adjust font size
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

    # --- BOTTOM TEXT ---
    ax.text(
        0.5,
        0.14,
        display_city,
        transform=ax.transAxes,
        color=THEME["text"],
        ha="center",
        fontproperties=font_main,
        zorder=11,
    )

    ax.text(
        0.5,
        0.10,
        display_country,
        transform=ax.transAxes,
        color=THEME["text"],
        ha="center",
        fontproperties=font_sub,
        zorder=11,
    )

    lat, lon = point
    coords_text = (
        f"{lat:.4f}° N / {lon:.4f}° E"
        if lat >= 0
        else f"{abs(lat):.4f}° S / {lon:.4f}° E"
    )
    if lon < 0:
        coords_text = coords_text.replace("E", "W")

    ax.text(
        0.5,
        0.07,
        coords_text,
        transform=ax.transAxes,
        color=THEME["text"],
        alpha=0.7,
        ha="center",
        fontproperties=font_coords,
        zorder=11,
    )

    ax.plot(
        [0.4, 0.6],
        [0.125, 0.125],
        transform=ax.transAxes,
        color=THEME["text"],
        linewidth=1,
        zorder=11,
    )

    # --- ATTRIBUTION (bottom right) ---
    attr_font = font_sub_base.copy()
    attr_font.set_size(8)

    ax.text(
        0.98,
        0.02,
        "© OpenStreetMap contributors",
        transform=ax.transAxes,
        color=THEME["text"],
        alpha=0.5,
        ha="right",
        va="bottom",
        fontproperties=attr_font,
        zorder=11,
    )

    # 5. Save
    print(f"Saving to {output_file}...")
    yield f"Saving to {output_file}..."

    fmt = output_format.lower()
    save_kwargs = dict(facecolor=THEME["bg"], pad_inches=0.05)

    if not no_crop:
        save_kwargs["bbox_inches"] = "tight"

    # DPI matters mainly for raster formats
    if fmt == "png":
        save_kwargs["dpi"] = 300

    plt.savefig(output_file, format=fmt, **save_kwargs)

    plt.close()
    print(f"✓ Done! Poster saved as {output_file}")
    yield "Done!"


def print_examples():
    """Print usage examples."""
    print("""
City Map Poster Generator
=========================

Usage:
  python create_map_poster.py --city <city> --country <country> [options]

Examples:
  # Iconic grid patterns
  python create_map_poster.py -c "New York" -C "USA" -t noir -d 12000           # Manhattan grid
  python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000   # Eixample district grid
  
  # Waterfront & canals
  python create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000       # Canal network
  python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t ocean -d 6000  # Concentric canals
  python create_map_poster.py -c "Dubai" -C "UAE" -t midnight_blue -d 15000     # Palm & coastline
  
  # Radial patterns
  python create_map_poster.py -c "Paris" -C "France" -t pastel_dream -d 10000   # Haussmann boulevards
  python create_map_poster.py -c "Moscow" -C "Russia" -t noir -d 12000          # Ring roads
  
  # Organic old cities
  python create_map_poster.py -c "Tokyo" -C "Japan" -t japanese_ink -d 15000    # Dense organic streets
  python create_map_poster.py -c "Marrakech" -C "Morocco" -t terracotta -d 5000 # Medina maze
  python create_map_poster.py -c "Rome" -C "Italy" -t warm_beige -d 8000        # Ancient street layout
  
  # Coastal cities
  python create_map_poster.py -c "San Francisco" -C "USA" -t sunset -d 10000    # Peninsula grid
  python create_map_poster.py -c "Sydney" -C "Australia" -t ocean -d 12000      # Harbor city
  python create_map_poster.py -c "Mumbai" -C "India" -t contrast_zones -d 18000 # Coastal peninsula
  
  # River cities
  python create_map_poster.py -c "London" -C "UK" -t noir -d 15000              # Thames curves
  python create_map_poster.py -c "Budapest" -C "Hungary" -t copper_patina -d 8000  # Danube split
  
  # List themes
  python create_map_poster.py --list-themes

Options:
  --city, -c        City name (required)
  --country, -C     Country name (required)
  --theme, -t       Theme name (default: feature_based)
  --distance, -d    Map radius in meters (default: 29000)
  --list-themes     List all available themes

Distance guide:
  4000-6000m   Small/dense cities (Venice, Amsterdam old center)
  8000-12000m  Medium cities, focused downtown (Paris, Barcelona)
  15000-20000m Large metros, full city view (Tokyo, Mumbai)

Available themes can be found in the 'themes/' directory.
Generated posters are saved to 'posters/' directory.
""")


def list_themes():
    """List all available themes with descriptions."""
    available_themes = get_available_themes()
    if not available_themes:
        print("No themes found in 'themes/' directory.")
        return

    print("\nAvailable Themes:")
    print("-" * 60)
    for theme_name in available_themes:
        theme_path = os.path.join(THEMES_DIR, f"{theme_name}.json")
        try:
            with open(theme_path, "r") as f:
                theme_data = json.load(f)
                display_name = theme_data.get("name", theme_name)
                description = theme_data.get("description", "")
        except Exception:
            display_name = theme_name
            description = ""
        print(f"  {theme_name}")
        print(f"    {display_name}")
        if description:
            print(f"    {description}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate beautiful map posters for any city",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_map_poster.py --city "New York" --country "USA"
  python create_map_poster.py --city Tokyo --country Japan --theme midnight_blue
  python create_map_poster.py --city Paris --country France --theme noir --distance 15000
  python create_map_poster.py --list-themes
        """,
    )

    parser.add_argument("--city", "-c", type=str, help="City name")
    parser.add_argument("--country", "-C", type=str, help="Country name")
    parser.add_argument(
        "--theme",
        "-t",
        type=str,
        default="feature_based",
        help="Theme name (default: feature_based)",
    )
    parser.add_argument(
        "--distance",
        "-d",
        type=int,
        default=10000,
        help="Map radius in meters (default: 10000)",
    )
    parser.add_argument(
        "--width",
        "-W",
        type=float,
        default=12.0,
        help="Poster width in inches (default: 12.0)",
    )
    parser.add_argument(
        "--height",
        "-H",
        type=float,
        default=16.0,
        help="Poster height in inches (default: 16.0)",
    )
    parser.add_argument(
        "--no-crop",
        action="store_true",
        help="Do not crop the image to the data extent (keeps background)",
    )
    parser.add_argument(
        "--list-themes", action="store_true", help="List all available themes"
    )
    parser.add_argument(
        "--format",
        "-f",
        default="png",
        choices=["png", "svg", "pdf"],
        help="Output format for the poster (default: png)",
    )

    args = parser.parse_args()

    # If no arguments provided, show examples
    if len(os.sys.argv) == 1:
        print_examples()
        os.sys.exit(0)

    # List themes if requested
    if args.list_themes:
        list_themes()
        os.sys.exit(0)

    # Validate required arguments
    if not args.city or not args.country:
        print("Error: --city and --country are required.\n")
        print_examples()
        os.sys.exit(1)

    # Validate theme exists
    available_themes = get_available_themes()
    if args.theme not in available_themes:
        print(f"Error: Theme '{args.theme}' not found.")
        print(f"Available themes: {', '.join(available_themes)}")
        os.sys.exit(1)

    print("=" * 50)
    print("City Map Poster Generator")
    print("=" * 50)

    # Load theme
    THEME = load_theme(args.theme)

    # Get coordinates and generate poster
    try:
        coords = get_coordinates(args.city, args.country)
        output_file = generate_output_filename(args.city, args.theme, args.format)

        # Iterate over the generator to execute it
        for status in create_poster(
            args.city,
            args.country,
            coords,
            args.distance,
            output_file,
            args.format,
            width=args.width,
            height=args.height,
            no_crop=args.no_crop,
        ):
            # We already print inside the function, but we act as a consumer here
            pass

        print("\n" + "=" * 50)
        print("✓ Poster generation complete!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        os.sys.exit(1)

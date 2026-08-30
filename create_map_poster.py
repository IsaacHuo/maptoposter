"""CLI and backward-compatible façade for map poster generation."""

import argparse
import os

from maptoposter.fonts import load_fonts
from maptoposter.rendering import (
    create_poster as _create_poster,
)
from maptoposter.rendering import (
    generate_output_filename,
    get_coordinates,
)
from maptoposter.rendering import (
    get_edge_colors_by_type as _get_edge_colors_by_type,
)
from maptoposter.themes import list_themes as _list_theme_names
from maptoposter.themes import load_theme

THEME = None
FONTS = load_fonts()


def get_available_themes():
    """Scans the themes directory and returns a list of available theme names."""
    return list(_list_theme_names())


def get_edge_colors_by_type(G, show_motorway=True, show_primary=True, show_secondary=True):
    """Backward-compatible wrapper using the active global theme."""
    active_theme = THEME if THEME is not None else load_theme()
    return _get_edge_colors_by_type(
        G,
        active_theme,
        show_motorway=show_motorway,
        show_primary=show_primary,
        show_secondary=show_secondary,
    )


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
    show_text=True,
    show_motorway=True,
    show_primary=True,
    show_secondary=True,
    show_water=True,
    show_parks=True,
    theme=None,
    theme_name="feature_based",
):
    """Create a poster while preserving the historical function signature."""
    active_theme = theme if theme is not None else THEME
    yield from _create_poster(
        city,
        country,
        point,
        dist,
        output_file,
        output_format,
        theme=active_theme,
        theme_name=theme_name,
        width=width,
        height=height,
        no_crop=no_crop,
        show_text=show_text,
        show_motorway=show_motorway,
        show_primary=show_primary,
        show_secondary=show_secondary,
        show_water=show_water,
        show_parks=show_parks,
    )


def print_examples():
    """Print usage examples."""
    print("""
City Map Poster Generator
=========================

Usage:
  python create_map_poster.py --city <city> --country <country> [options]

Examples:
  python create_map_poster.py -c "New York" -C "USA" -t noir -d 12000
  python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000
  python create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000
  python create_map_poster.py -c "Tokyo" -C "Japan" -t japanese_ink -d 15000
  python create_map_poster.py --list-themes

Options:
  --city, -c        City name (required)
  --country, -C     Country name (required)
  --theme, -t       Theme name (default: feature_based)
  --distance, -d    Map radius in meters (default: 10000)
  --list-themes     List all available themes

Distance guide:
  4000-6000m   Small/dense cities
  8000-12000m  Medium cities, focused downtown
  15000-20000m Large metros, full city view

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
        theme_data = load_theme(theme_name, verbose=False)
        display_name = theme_data.get("name", theme_name)
        description = theme_data.get("description", "")
        print(f"  {theme_name}")
        print(f"    {display_name}")
        if description:
            print(f"    {description}")
        print()


def main():
    """Run the command-line poster generator."""
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
    parser.add_argument("--list-themes", action="store_true", help="List all available themes")
    parser.add_argument(
        "--format",
        "-f",
        default="png",
        choices=["png", "svg", "pdf"],
        help="Output format for the poster (default: png)",
    )

    args = parser.parse_args()

    if len(os.sys.argv) == 1:
        print_examples()
        os.sys.exit(0)

    if args.list_themes:
        list_themes()
        os.sys.exit(0)

    if not args.city or not args.country:
        print("Error: --city and --country are required.\n")
        print_examples()
        os.sys.exit(1)

    available_themes = get_available_themes()
    if args.theme not in available_themes:
        print(f"Error: Theme '{args.theme}' not found.")
        print(f"Available themes: {', '.join(available_themes)}")
        os.sys.exit(1)

    print("=" * 50)
    print("City Map Poster Generator")
    print("=" * 50)

    theme = load_theme(args.theme)

    try:
        coords = get_coordinates(args.city, args.country)
        output_file = generate_output_filename(args.city, args.theme, args.format)

        for _ in create_poster(
            args.city,
            args.country,
            coords,
            args.distance,
            output_file,
            args.format,
            width=args.width,
            height=args.height,
            no_crop=args.no_crop,
            theme=theme,
            theme_name=args.theme,
        ):
            pass

        print("\n" + "=" * 50)
        print("✓ Poster generation complete!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        os.sys.exit(1)


if __name__ == "__main__":
    main()

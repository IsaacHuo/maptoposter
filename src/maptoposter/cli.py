"""MapToPoster command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .export import generate_output_filename
from .geocoding import GeocodingService
from .models import (
    ExportConfig,
    LayoutConfig,
    LayoutPreset,
    MapConfig,
    OutputFormat,
    PosterConfig,
    PosterSize,
    SizePreset,
    TypographyConfig,
)
from .service import PosterService
from .themes import list_themes, load_style
from .viewport import create_viewport


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Turn any place into a map poster.")
    parser.add_argument("--city", "-c")
    parser.add_argument("--country", "-C", default="")
    parser.add_argument("--theme", "-t", default="feature_based", choices=list_themes())
    parser.add_argument("--distance", "-d", type=float, default=10_000)
    parser.add_argument("--format", "-f", choices=[item.value for item in OutputFormat], default="png")
    parser.add_argument("--layout", choices=[item.value for item in LayoutPreset], default="classic")
    parser.add_argument("--list-themes", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.list_themes:
        print("\n".join(list_themes()))
        return
    if not args.city:
        raise SystemExit("--city is required unless --list-themes is used")

    query = f"{args.city}, {args.country}" if args.country else args.city
    results = GeocodingService().search(query, limit=1)
    if not results:
        raise SystemExit(f"Location not found: {query}")
    location = results[0]
    size = PosterSize(SizePreset.THREE_FOUR)
    width, height = size.dimensions
    config = PosterConfig(
        location=location,
        map=MapConfig(create_viewport(location.coordinate, args.distance, width, height)),
        style=load_style(args.theme),
        typography=TypographyConfig(title=args.city, subtitle=args.country),
        layout=LayoutConfig(LayoutPreset(args.layout)),
        size=size,
    )
    service = PosterService()
    reference = service.prepare_map(config)
    output = args.output or Path(generate_output_filename(args.city, args.theme, OutputFormat(args.format)))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(service.export_poster(reference, config, ExportConfig(OutputFormat(args.format))))
    print(output)


if __name__ == "__main__":
    main()

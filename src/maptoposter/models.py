"""Typed configuration and data models for MapToPoster."""

from __future__ import annotations

import math
from dataclasses import dataclass, field, fields, replace
from enum import StrEnum
from pathlib import Path


class LayoutPreset(StrEnum):
    CLASSIC = "classic"
    EDITORIAL = "editorial"
    MINIMAL = "minimal"
    BOTTOM_LEFT = "bottom_left"
    CENTERED = "centered"


class SizePreset(StrEnum):
    THREE_FOUR = "3:4"
    FOUR_FIVE = "4:5"
    TWO_THREE = "2:3"
    FOUR_THREE = "4:3"
    FIVE_FOUR = "5:4"
    THREE_TWO = "3:2"
    SQUARE = "1:1"
    NINE_SIXTEEN = "9:16"
    SIXTEEN_NINE = "16:9"
    A4 = "A4"
    A3 = "A3"
    A4_LANDSCAPE = "A4-landscape"
    A3_LANDSCAPE = "A3-landscape"
    CUSTOM = "custom"


class OutputFormat(StrEnum):
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.latitude) or not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be a finite value between -90 and 90.")
        if not math.isfinite(self.longitude) or not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be a finite value between -180 and 180.")


@dataclass(frozen=True)
class BBox:
    west: float
    south: float
    east: float
    north: float

    def __post_init__(self) -> None:
        values = (self.west, self.south, self.east, self.north)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Bounding box values must be finite.")
        if not -90 <= self.south < self.north <= 90:
            raise ValueError("Bounding box latitude values are invalid.")
        if not -180 <= self.west < self.east <= 180:
            raise ValueError("Bounding boxes crossing the antimeridian are not supported.")

    def as_tuple(self) -> tuple[float, float, float, float]:
        """Return the OSMnx 2.x bbox order: west, south, east, north."""
        return (self.west, self.south, self.east, self.north)


@dataclass(frozen=True)
class Location:
    display_name: str
    coordinate: Coordinate
    country: str = ""
    region: str = ""
    country_code: str = ""
    provider: str = "manual"


@dataclass(frozen=True)
class MapViewport:
    center: Coordinate
    bbox: BBox
    zoom: float | None = None
    distance_m: float | None = None


@dataclass(frozen=True)
class MapConfig:
    viewport: MapViewport
    network_type: str = "all"
    data_layers: tuple[str, ...] = ("roads", "water", "parks")

    def __post_init__(self) -> None:
        if self.network_type not in {"all", "drive", "walk", "bike"}:
            raise ValueError(f"Unsupported network type: {self.network_type}")


@dataclass(frozen=True)
class LayerConfig:
    motorway: bool = True
    primary: bool = True
    secondary: bool = True
    residential: bool = True
    water: bool = True
    parks: bool = True


@dataclass(frozen=True)
class StyleConfig:
    id: str
    name: str
    description: str = ""
    preview: str = ""
    background: str = "#FFFFFF"
    text: str = "#000000"
    water: str = "#C0C0C0"
    parks: str = "#F0F0F0"
    road_motorway: str = "#0A0A0A"
    road_primary: str = "#1A1A1A"
    road_secondary: str = "#2A2A2A"
    road_tertiary: str = "#3A3A3A"
    road_residential: str = "#4A4A4A"
    road_default: str = "#3A3A3A"
    gradient: str = "#FFFFFF"

    def with_colors(self, **colors: str) -> StyleConfig:
        """Return a customized style without mutating its preset."""
        allowed = {item.name for item in fields(self)} - {"id", "name", "description", "preview"}
        unknown = set(colors) - allowed
        if unknown:
            raise ValueError(f"Unknown style colors: {', '.join(sorted(unknown))}")
        return replace(self, **colors)


@dataclass(frozen=True)
class TypographyConfig:
    title: str = ""
    subtitle: str = ""
    caption: str = ""
    coordinates: str = ""
    font_family: str = "auto"
    title_size: float = 54
    subtitle_size: float = 22
    caption_size: float = 14
    coordinate_size: float = 12
    letter_spacing: float = 0.08
    line_height: float = 1.15
    alignment: str = "center"
    show_coordinates: bool = True
    show_divider: bool = True

    def __post_init__(self) -> None:
        if self.alignment not in {"left", "center", "right"}:
            raise ValueError("Typography alignment must be left, center, or right.")
        sizes = (self.title_size, self.subtitle_size, self.caption_size, self.coordinate_size)
        if not all(6 <= size <= 240 for size in sizes):
            raise ValueError("Typography sizes must be between 6 and 240 points.")


SIZE_PRESETS: dict[SizePreset, tuple[float, float]] = {
    SizePreset.THREE_FOUR: (12.0, 16.0),
    SizePreset.FOUR_FIVE: (12.0, 15.0),
    SizePreset.TWO_THREE: (12.0, 18.0),
    SizePreset.FOUR_THREE: (16.0, 12.0),
    SizePreset.FIVE_FOUR: (15.0, 12.0),
    SizePreset.THREE_TWO: (18.0, 12.0),
    SizePreset.SQUARE: (12.0, 12.0),
    SizePreset.NINE_SIXTEEN: (9.0, 16.0),
    SizePreset.SIXTEEN_NINE: (16.0, 9.0),
    SizePreset.A4: (8.2677, 11.6929),
    SizePreset.A3: (11.6929, 16.5354),
    SizePreset.A4_LANDSCAPE: (11.6929, 8.2677),
    SizePreset.A3_LANDSCAPE: (16.5354, 11.6929),
}


@dataclass(frozen=True)
class PosterSize:
    preset: SizePreset = SizePreset.THREE_FOUR
    width_in: float | None = None
    height_in: float | None = None

    def __post_init__(self) -> None:
        if self.preset is SizePreset.CUSTOM:
            if self.width_in is None or self.height_in is None:
                raise ValueError("Custom poster size requires width and height.")
            if not 4 <= self.width_in <= 40 or not 4 <= self.height_in <= 40:
                raise ValueError("Custom poster dimensions must be between 4 and 40 inches.")

    @property
    def dimensions(self) -> tuple[float, float]:
        if self.preset is SizePreset.CUSTOM:
            assert self.width_in is not None and self.height_in is not None
            return self.width_in, self.height_in
        return SIZE_PRESETS[self.preset]


@dataclass(frozen=True)
class LayoutConfig:
    preset: LayoutPreset = LayoutPreset.CLASSIC


@dataclass(frozen=True)
class PosterConfig:
    location: Location
    map: MapConfig
    style: StyleConfig
    typography: TypographyConfig = field(default_factory=TypographyConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    layers: LayerConfig = field(default_factory=LayerConfig)
    size: PosterSize = field(default_factory=PosterSize)


@dataclass(frozen=True)
class PreviewConfig:
    dpi: int = 120
    max_dimension_px: int = 1200


@dataclass(frozen=True)
class ExportConfig:
    output_format: OutputFormat = OutputFormat.PNG
    dpi: int = 300
    output_path: Path | None = None

    def __post_init__(self) -> None:
        if not 72 <= self.dpi <= 600:
            raise ValueError("Export DPI must be between 72 and 600.")


@dataclass(frozen=True)
class MapDataRef:
    cache_key: str
    cache_path: Path
    cache_hit: bool


@dataclass
class MapData:
    bbox: BBox
    roads: object
    water_polygons: object | None = None
    water_lines: object | None = None
    parks: object | None = None
    crs: str = "EPSG:4326"
    metadata: dict[str, object] = field(default_factory=dict)

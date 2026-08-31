"""Public API schemas and conversion to the Python core."""

from __future__ import annotations

from pydantic import BaseModel, Field

from maptoposter.models import (
    BBox,
    Coordinate,
    LayerConfig,
    LayoutConfig,
    LayoutPreset,
    Location,
    MapConfig,
    MapViewport,
    PosterConfig,
    PosterSize,
    SizePreset,
    TypographyConfig,
)
from maptoposter.themes import load_style


class LocationSchema(BaseModel):
    display_name: str
    latitude: float
    longitude: float
    country: str = ""
    region: str = ""
    country_code: str = ""
    provider: str = "manual"

    @classmethod
    def from_core(cls, location: Location) -> LocationSchema:
        return cls(
            display_name=location.display_name,
            latitude=location.coordinate.latitude,
            longitude=location.coordinate.longitude,
            country=location.country,
            region=location.region,
            country_code=location.country_code,
            provider=location.provider,
        )

    def to_core(self) -> Location:
        return Location(
            self.display_name,
            Coordinate(self.latitude, self.longitude),
            self.country,
            self.region,
            self.country_code,
            self.provider,
        )


class BBoxSchema(BaseModel):
    west: float
    south: float
    east: float
    north: float


class TypographySchema(BaseModel):
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


class LayerSchema(BaseModel):
    motorway: bool = True
    primary: bool = True
    secondary: bool = True
    residential: bool = True
    water: bool = True
    parks: bool = True


class SizeSchema(BaseModel):
    preset: SizePreset = SizePreset.THREE_FOUR
    width_in: float | None = None
    height_in: float | None = None


class PosterRequest(BaseModel):
    location: LocationSchema
    bbox: BBoxSchema
    distance_m: float = Field(default=10_000, ge=100, le=250_000)
    zoom: float | None = None
    network_type: str = "all"
    style_id: str = "japanese_ink"
    colors: dict[str, str] = Field(default_factory=dict)
    typography: TypographySchema = Field(default_factory=TypographySchema)
    layout: LayoutPreset = LayoutPreset.CLASSIC
    layers: LayerSchema = Field(default_factory=LayerSchema)
    size: SizeSchema = Field(default_factory=SizeSchema)

    def to_core(self) -> PosterConfig:
        location = self.location.to_core()
        bbox = BBox(**self.bbox.model_dump())
        size = PosterSize(**self.size.model_dump())
        layout = LayoutConfig(self.layout)
        style = load_style(self.style_id).with_colors(**self.colors)
        return PosterConfig(
            location=location,
            map=MapConfig(
                MapViewport(location.coordinate, bbox, self.zoom, self.distance_m),
                network_type=self.network_type,
            ),
            style=style,
            typography=TypographyConfig(**self.typography.model_dump()),
            layout=layout,
            layers=LayerConfig(**self.layers.model_dump()),
            size=size,
        )


class PreviewRequest(BaseModel):
    map_data_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    poster: PosterRequest


class ExportRequest(PreviewRequest):
    format: str = Field(default="png", pattern=r"^(png|svg|pdf)$")
    dpi: int = Field(default=300, ge=72, le=600)

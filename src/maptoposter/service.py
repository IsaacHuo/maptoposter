"""Application layer shared by the web API and CLI."""

from __future__ import annotations

from .geocoding import GeocodingService
from .map_data import MapDataService
from .models import ExportConfig, MapDataRef, PosterConfig, PreviewConfig
from .renderer import PosterRenderer


class PosterService:
    """Coordinate place search, reusable map data, preview, and export."""

    def __init__(
        self,
        geocoding: GeocodingService | None = None,
        map_data: MapDataService | None = None,
        renderer: PosterRenderer | None = None,
    ) -> None:
        self.geocoding = geocoding or GeocodingService()
        self.map_data = map_data or MapDataService()
        self.renderer = renderer or PosterRenderer()

    def search_places(self, query: str, language: str = "en"):
        """Search after an explicit user submission."""
        return self.geocoding.search(query, language)

    def prepare_map(self, config: PosterConfig) -> MapDataRef:
        return self.map_data.prepare(config.map)

    def render_preview(
        self, reference: MapDataRef | str, config: PosterConfig, preview: PreviewConfig | None = None
    ) -> bytes:
        return self.renderer.render_preview(self.map_data.load(reference), config, preview)

    def export_poster(self, reference: MapDataRef | str, config: PosterConfig, export: ExportConfig) -> bytes:
        return self.renderer.export(self.map_data.load(reference), config, export)

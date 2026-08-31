"""Network-free poster renderer for prepared MapData."""

# Backend selection must happen before pyplot import for headless/threaded servers.
# ruff: noqa: I001

from __future__ import annotations

import io
import threading
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from pyproj import Transformer

from .fonts import load_fonts
from .layouts import LayoutSpec, get_layout
from .models import ExportConfig, LayoutPreset, MapData, OutputFormat, PosterConfig, PreviewConfig
from .typography import apply_letter_spacing, fitted_font_size, format_coordinates, resolve_text_positions

RENDER_LOCK = threading.RLock()
ROAD_WIDTHS = {"motorway": 1.5, "primary": 1.15, "secondary": 0.75, "residential": 0.38}



class PosterRenderer:
    """Render preview and export artifacts without making network requests."""

    def render_preview(self, data: MapData, config: PosterConfig, preview: PreviewConfig | None = None) -> bytes:
        preview = preview or PreviewConfig()
        width, height = config.size.dimensions
        scale = preview.max_dimension_px / (max(width, height) * preview.dpi)
        figure_size = (width * scale, height * scale)
        return self._render_bytes(data, config, OutputFormat.PNG, preview.dpi, figure_size)

    def export(self, data: MapData, config: PosterConfig, export: ExportConfig) -> bytes:
        return self._render_bytes(
            data,
            config,
            export.output_format,
            export.dpi,
            config.size.dimensions,
        )

    def export_to_path(self, data: MapData, config: PosterConfig, export: ExportConfig) -> Path:
        if export.output_path is None:
            raise ValueError("An output path is required.")
        content = self.export(data, config, export)
        export.output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = export.output_path.with_name(f".{export.output_path.name}.tmp")
        temporary.write_bytes(content)
        temporary.replace(export.output_path)
        return export.output_path

    def _render_bytes(
        self,
        data: MapData,
        config: PosterConfig,
        output_format: OutputFormat,
        dpi: int,
        figure_size: tuple[float, float],
    ) -> bytes:
        with RENDER_LOCK:
            fig = None
            try:
                fig = plt.figure(figsize=figure_size, dpi=dpi, facecolor=config.style.background)
                layout = get_layout(config.layout.preset)
                self._render_map(fig, data, config, layout)
                self._render_typography(fig, config, layout)
                fig.text(
                    0.985,
                    0.012,
                    "© OpenStreetMap contributors",
                    ha="right",
                    va="bottom",
                    fontsize=5.5,
                    color=config.style.text,
                    alpha=0.55,
                )
                stream = io.BytesIO()
                fig.savefig(
                    stream,
                    format=output_format.value,
                    dpi=dpi,
                    facecolor=config.style.background,
                    edgecolor="none",
                    bbox_inches=None,
                    pad_inches=0,
                    metadata={"Creator": "MapToPoster"},
                )
                return stream.getvalue()
            finally:
                if fig is not None:
                    plt.close(fig)

    def _render_map(self, fig, data: MapData, config: PosterConfig, layout: LayoutSpec) -> None:
        rect = layout.map_rect
        ax = fig.add_axes([rect.x, rect.y, rect.width, rect.height], facecolor=config.style.background)
        ax.set_axis_off()

        self._plot_optional(ax, data.water_polygons, config.style.water, 1, config.layers.water)
        if config.layers.water and isinstance(data.water_lines, gpd.GeoDataFrame) and not data.water_lines.empty:
            data.water_lines.plot(ax=ax, color=config.style.water, linewidth=1.2, zorder=1)
        self._plot_optional(ax, data.parks, config.style.parks, 2, config.layers.parks)

        roads = data.roads
        if not isinstance(roads, gpd.GeoDataFrame):
            raise TypeError("MapData.roads must be a GeoDataFrame.")
        visible = {
            "motorway": config.layers.motorway,
            "primary": config.layers.primary,
            "secondary": config.layers.secondary,
            "residential": config.layers.residential,
        }
        colors = {
            "motorway": config.style.road_motorway,
            "primary": config.style.road_primary,
            "secondary": config.style.road_secondary,
            "residential": config.style.road_residential,
        }
        for road_class in ("residential", "secondary", "primary", "motorway"):
            if not visible[road_class]:
                continue
            subset = roads[roads["road_class"] == road_class]
            if not subset.empty:
                subset.plot(
                    ax=ax,
                    color=colors[road_class],
                    linewidth=ROAD_WIDTHS[road_class],
                    zorder=3,
                )

        west, south, east, north = data.bbox.as_tuple()
        transformer = Transformer.from_crs("EPSG:4326", data.crs, always_xy=True)
        corners = [
            transformer.transform(west, south),
            transformer.transform(west, north),
            transformer.transform(east, south),
            transformer.transform(east, north),
        ]
        xs, ys = zip(*corners, strict=True)
        ax.set_xlim(min(xs), max(xs))
        ax.set_ylim(min(ys), max(ys))
        ax.set_aspect("equal", adjustable="box")

        if layout.fade_bottom:
            self._add_fade(ax, config.style.gradient, "bottom")
        if layout.fade_top:
            self._add_fade(ax, config.style.gradient, "top")

    @staticmethod
    def _plot_optional(ax, frame: object | None, color: str, zorder: int, visible: bool) -> None:
        if visible and isinstance(frame, gpd.GeoDataFrame) and not frame.empty:
            frame.plot(ax=ax, facecolor=color, edgecolor="none", zorder=zorder)

    @staticmethod
    def _add_fade(ax, color: str, location: str) -> None:
        bands = 48
        height = 0.26
        for index in range(bands):
            ratio = index / bands
            alpha = (1 - ratio) * 0.92
            y = ratio * height if location == "bottom" else 1 - height + ratio * height
            if location == "top":
                alpha = ratio * 0.92
            ax.add_patch(
                Rectangle(
                    (0, y),
                    1,
                    height / bands + 0.002,
                    transform=ax.transAxes,
                    facecolor=color,
                    edgecolor="none",
                    alpha=alpha,
                    zorder=9,
                )
            )

    def _render_typography(self, fig, config: PosterConfig, layout: LayoutSpec) -> None:
        typography = config.typography
        style = config.style
        fonts = self._fonts(typography.title)
        alignment = typography.alignment if config.layout.preset is LayoutPreset.CLASSIC else layout.alignment
        x = {
            "left": layout.text_rect.x,
            "center": layout.text_rect.x + layout.text_rect.width / 2,
            "right": layout.text_rect.x + layout.text_rect.width,
        }[alignment]

        if config.layout.preset in {LayoutPreset.EDITORIAL, LayoutPreset.CENTERED}:
            rect = layout.text_rect
            fig.patches.append(
                Rectangle(
                    (rect.x, rect.y),
                    rect.width,
                    rect.height,
                    transform=fig.transFigure,
                    facecolor=style.background,
                    edgecolor="none",
                    alpha=0.94,
                    zorder=10,
                )
            )

        title = typography.title or config.location.display_name.split(",")[0]
        title_size = fitted_font_size(title, typography.title_size, max_units=layout.text_rect.width * 29)
        positions = resolve_text_positions(
            figure_height=fig.get_figheight(),
            text_rect_y=layout.text_rect.y,
            text_rect_height=layout.text_rect.height,
            title_y=layout.title_y,
            subtitle_y=layout.subtitle_y,
            caption_y=layout.caption_y,
            coordinates_y=layout.coordinates_y,
            title_size=title_size,
            subtitle_size=typography.subtitle_size,
            caption_size=typography.caption_size,
            coordinate_size=typography.coordinate_size,
            has_title=bool(title),
            has_subtitle=bool(typography.subtitle),
            has_caption=bool(typography.caption),
            show_coordinates=typography.show_coordinates,
        )
        if title:
            fig.text(
                x,
                positions["title"],
                title if fonts["is_cjk"] else apply_letter_spacing(title, typography.letter_spacing),
                ha=alignment,
                va="center",
                color=style.text,
                fontproperties=fonts["bold"],
                fontsize=title_size,
                linespacing=typography.line_height,
                zorder=11,
            )
        if typography.show_divider and title:
            half_width = min(0.13, layout.text_rect.width * 0.22)
            center = layout.text_rect.x + layout.text_rect.width / 2
            fig.lines.append(
                Line2D(
                    [center - half_width, center + half_width],
                    [positions["divider"], positions["divider"]],
                    transform=fig.transFigure,
                    color=style.text,
                    linewidth=0.75,
                    alpha=0.65,
                    zorder=11,
                )
            )
        if typography.subtitle:
            fig.text(
                x,
                positions["subtitle"],
                apply_letter_spacing(typography.subtitle, typography.letter_spacing),
                ha=alignment,
                va="center",
                color=style.text,
                fontproperties=fonts["regular"],
                fontsize=typography.subtitle_size,
                zorder=11,
            )
        if typography.caption:
            fig.text(
                x,
                positions["caption"],
                typography.caption,
                ha=alignment,
                va="center",
                color=style.text,
                fontproperties=fonts["regular"],
                fontsize=typography.caption_size,
                zorder=11,
            )
        if typography.show_coordinates:
            coordinate_text = typography.coordinates or format_coordinates(
                config.location.coordinate.latitude, config.location.coordinate.longitude
            )
            fig.text(
                x,
                positions["coordinates"],
                coordinate_text,
                ha=alignment,
                color=style.text,
                alpha=0.72,
                fontproperties=fonts["regular"],
                fontsize=typography.coordinate_size,
                zorder=11,
            )

    @staticmethod
    def _fonts(title: str) -> dict[str, object]:
        available = load_fonts() or {}
        is_cjk = any("\u4e00" <= char <= "\u9fff" for char in title)
        if is_cjk and available.get("cn"):
            path = available["cn"]
            return {
                "bold": FontProperties(fname=path, weight="bold"),
                "regular": FontProperties(fname=path),
                "is_cjk": True,
            }
        return {
            "bold": FontProperties(
                fname=available.get("en_bold") if available.get("en_bold") else None,
                family=None if available.get("en_bold") else "serif",
                weight="bold",
            ),
            "regular": FontProperties(
                fname=available.get("en_regular") if available.get("en_regular") else None,
                family=None if available.get("en_regular") else "serif",
            ),
            "is_cjk": False,
        }

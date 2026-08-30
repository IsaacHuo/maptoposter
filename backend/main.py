"""FastAPI product backend for MapToPoster."""

from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from maptoposter import __version__
from maptoposter.export import generate_output_filename
from maptoposter.geocoding import GeocodingError
from maptoposter.layouts import LAYOUTS
from maptoposter.map_data import MapDataError
from maptoposter.models import SIZE_PRESETS, ExportConfig, OutputFormat
from maptoposter.service import PosterService
from maptoposter.themes import list_themes, load_style

from .schemas import ExportRequest, LocationSchema, PosterRequest, PreviewRequest

app = FastAPI(title="MapToPoster API", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("MAPTOPOSTER_CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
service = PosterService()


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/api/v1/styles")
def styles() -> list[dict[str, object]]:
    return [asdict(load_style(name)) for name in list_themes()]


@app.get("/api/v1/layouts")
def layouts() -> list[dict[str, str]]:
    return [{"id": preset.value, "name": preset.value.replace("_", " ").title()} for preset in LAYOUTS]


@app.get("/api/v1/sizes")
def sizes() -> list[dict[str, object]]:
    return [
        {"id": preset.value, "width_in": dimensions[0], "height_in": dimensions[1]}
        for preset, dimensions in SIZE_PRESETS.items()
    ]


@app.get("/api/v1/locations/search", response_model=list[LocationSchema])
def search_locations(q: str = Query(min_length=1, max_length=200), lang: str = "en"):
    try:
        return [LocationSchema.from_core(item) for item in service.search_places(q, lang)]
    except (ValueError, GeocodingError) as exc:
        raise HTTPException(status_code=502 if isinstance(exc, GeocodingError) else 400, detail=str(exc)) from exc


@app.post("/api/v1/map-data/prepare")
def prepare_map(request: PosterRequest) -> dict[str, object]:
    try:
        reference = service.prepare_map(request.to_core())
        return {"map_data_id": reference.cache_key, "cache_hit": reference.cache_hit}
    except (ValueError, MapDataError) as exc:
        raise HTTPException(status_code=502 if isinstance(exc, MapDataError) else 400, detail=str(exc)) from exc


@app.post("/api/v1/posters/preview")
def preview(request: PreviewRequest) -> Response:
    try:
        content = service.render_preview(request.map_data_id, request.poster.to_core())
        return Response(content, media_type="image/png", headers={"Cache-Control": "no-store"})
    except (ValueError, MapDataError) as exc:
        raise HTTPException(status_code=404 if isinstance(exc, MapDataError) else 400, detail=str(exc)) from exc


@app.post("/api/v1/posters/export")
def export(request: ExportRequest) -> Response:
    try:
        poster = request.poster.to_core()
        output_format = OutputFormat(request.format)
        content = service.export_poster(
            request.map_data_id,
            poster,
            ExportConfig(output_format=output_format, dpi=request.dpi),
        )
        filename = Path(
            generate_output_filename(
                poster.typography.title or poster.location.display_name,
                poster.style.id,
                output_format,
                directory=Path("."),
                include_time=False,
            )
        ).name
        return Response(
            content,
            media_type={"png": "image/png", "svg": "image/svg+xml", "pdf": "application/pdf"}[request.format],
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except (ValueError, MapDataError) as exc:
        raise HTTPException(status_code=404 if isinstance(exc, MapDataError) else 400, detail=str(exc)) from exc


def run() -> None:
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=7860, reload=False)


_frontend_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if _frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=_frontend_dist, html=True), name="frontend")

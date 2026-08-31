from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app, service
from maptoposter.models import MapDataRef

client = TestClient(app)


def poster_payload() -> dict[str, object]:
    return {
        "location": {"display_name": "Beijing", "latitude": 39.9042, "longitude": 116.4074, "country": "China"},
        "bbox": {"west": 116.3, "south": 39.8, "east": 116.5, "north": 40.0},
        "style_id": "japanese_ink",
        "typography": {"title": "BEIJING"},
        "layout": "classic",
        "layers": {},
        "size": {"preset": "3:4"},
    }


def test_catalog_endpoints() -> None:
    assert client.get("/api/v1/health").json()["status"] == "ok"
    assert len(client.get("/api/v1/styles").json()) >= 5
    assert len(client.get("/api/v1/layouts").json()) == 5
    assert {item["id"] for item in client.get("/api/v1/sizes").json()} >= {
        "3:4",
        "4:3",
        "16:9",
        "1:1",
        "A4",
        "A4-landscape",
    }


def test_prepare_preview_and_export_contract(monkeypatch, tmp_path) -> None:
    key = "a" * 64
    monkeypatch.setattr(service, "prepare_map", lambda config: MapDataRef(key, Path(tmp_path), True))
    monkeypatch.setattr(service, "render_preview", lambda reference, config: b"\x89PNG\r\n")
    monkeypatch.setattr(service, "export_poster", lambda reference, config, export: b"%PDF-test")

    prepared = client.post("/api/v1/map-data/prepare", json=poster_payload())
    assert prepared.status_code == 200 and prepared.json()["cache_hit"] is True
    preview = client.post("/api/v1/posters/preview", json={"map_data_id": key, "poster": poster_payload()})
    assert preview.status_code == 200 and preview.headers["content-type"] == "image/png"
    exported = client.post(
        "/api/v1/posters/export",
        json={"map_data_id": key, "poster": poster_payload(), "format": "pdf", "dpi": 300},
    )
    assert exported.status_code == 200
    assert "beijing-japanese-ink" in exported.headers["content-disposition"]


def test_invalid_coordinate_returns_clear_error(monkeypatch) -> None:
    response = client.post(
        "/api/v1/map-data/prepare",
        json={**poster_payload(), "location": {"display_name": "Invalid", "latitude": 95, "longitude": 0}},
    )
    assert response.status_code == 400
    assert "Latitude" in response.json()["detail"]

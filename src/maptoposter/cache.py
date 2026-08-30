"""Atomic, versioned disk caches for geocoding and prepared map data."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from filelock import FileLock

from .models import MapConfig
from .paths import CACHE_DIR

CACHE_SCHEMA_VERSION = 1


def map_cache_key(config: MapConfig) -> str:
    """Build a stable key from data-affecting map parameters only."""
    bbox = config.viewport.bbox
    payload = {
        "schema": CACHE_SCHEMA_VERSION,
        "center": [round(config.viewport.center.latitude, 5), round(config.viewport.center.longitude, 5)],
        "bbox": [round(value, 5) for value in bbox.as_tuple()],
        "distance_m": round(config.viewport.distance_m or 0, 1),
        "network_type": config.network_type,
        "layers": sorted(config.data_layers),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class DiskCache:
    """Small filesystem cache with per-key locking and atomic directories."""

    def __init__(self, root: Path = CACHE_DIR) -> None:
        self.root = Path(root)
        self.map_root = self.root / "map_data"
        self.geocoding_root = self.root / "geocoding"

    def map_path(self, key: str) -> Path:
        return self.map_root / key

    def geocoding_path(self, key: str) -> Path:
        return self.geocoding_root / f"{key}.json"

    @contextmanager
    def lock(self, namespace: str, key: str) -> Iterator[None]:
        lock_dir = self.root / "locks" / namespace
        lock_dir.mkdir(parents=True, exist_ok=True)
        with FileLock(str(lock_dir / f"{key}.lock"), timeout=180):
            yield

    @contextmanager
    def atomic_directory(self, destination: Path) -> Iterator[Path]:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{destination.name}-", dir=destination.parent))
        try:
            yield temporary
            if destination.exists():
                shutil.rmtree(destination)
            os.replace(temporary, destination)
        except Exception:
            shutil.rmtree(temporary, ignore_errors=True)
            raise

    def read_json(self, path: Path) -> dict[str, object] | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None

    def write_json(self, path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        handle, name = tempfile.mkstemp(prefix=f".{path.stem}-", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, ensure_ascii=False, sort_keys=True)
            os.replace(name, path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

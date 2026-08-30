"""Location search with local China data, Nominatim, rate limiting, and cache."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict
from typing import Any, Protocol, cast

from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

from .cache import DiskCache
from .china import search_china
from .models import Coordinate, Location

COORDINATE_QUERY = re.compile(r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*[,/ ]\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*$")


class GeocodingError(RuntimeError):
    """Raised when a place search cannot be completed."""


class GeocoderProvider(Protocol):
    def search(self, query: str, language: str, limit: int) -> list[Location]: ...


def parse_coordinate_query(query: str) -> Location | None:
    """Parse a latitude/longitude search query."""
    match = COORDINATE_QUERY.match(query)
    if match is None:
        return None
    coordinate = Coordinate(float(match.group(1)), float(match.group(2)))
    return Location(
        display_name=f"{coordinate.latitude:.5f}, {coordinate.longitude:.5f}",
        coordinate=coordinate,
        provider="coordinates",
    )


class NominatimProvider:
    """Thin Nominatim provider. Call only after an explicit user submission."""

    def __init__(self) -> None:
        user_agent = os.getenv(
            "MAPTOPOSTER_USER_AGENT",
            "MapToPoster/0.2 (+https://github.com/IsaacHuo/maptoposter)",
        )
        endpoint = os.getenv("MAPTOPOSTER_NOMINATIM_DOMAIN", "nominatim.openstreetmap.org")
        geocoder = cast(Any, Nominatim)(user_agent=user_agent, domain=endpoint, timeout=15)
        self._geocode = RateLimiter(
            geocoder.geocode,
            min_delay_seconds=1.0,
            max_retries=2,
            error_wait_seconds=2.0,
            swallow_exceptions=False,
        )

    def search(self, query: str, language: str = "en", limit: int = 5) -> list[Location]:
        try:
            results = self._geocode(
                query,
                exactly_one=False,
                limit=limit,
                addressdetails=True,
                language="zh-CN" if language == "cn" else "en",
            )
        except Exception as exc:
            raise GeocodingError(f"Location service is unavailable: {exc}") from exc

        locations: list[Location] = []
        for result in results or []:
            raw = getattr(result, "raw", {}) or {}
            address = raw.get("address", {}) or {}
            locations.append(
                Location(
                    display_name=str(getattr(result, "address", query)),
                    coordinate=Coordinate(float(result.latitude), float(result.longitude)),
                    country=str(address.get("country", "")),
                    region=str(address.get("state") or address.get("region") or ""),
                    country_code=str(address.get("country_code", "")),
                    provider="nominatim",
                )
            )
        return locations


class GeocodingService:
    """Search places in priority order and persist external results."""

    def __init__(self, cache: DiskCache | None = None, provider: GeocoderProvider | None = None) -> None:
        self.cache = cache or DiskCache()
        self.provider = provider or NominatimProvider()

    def search(self, query: str, language: str = "en", limit: int = 5) -> list[Location]:
        query = query.strip()
        if not query:
            raise ValueError("Search query cannot be empty.")

        coordinate = parse_coordinate_query(query)
        if coordinate is not None:
            return [coordinate]

        local = list(search_china(query, limit=limit))
        if local:
            return local[:limit]

        key_payload = json.dumps([query.casefold(), language, limit], ensure_ascii=False)
        key = hashlib.sha256(key_payload.encode("utf-8")).hexdigest()
        cache_path = self.cache.geocoding_path(key)
        cached = self.cache.read_json(cache_path)
        cached_results = cached.get("results") if cached else None
        if isinstance(cached_results, list):
            external = [self._from_dict(item) for item in cached_results if isinstance(item, dict)]
        else:
            with self.cache.lock("geocoding", key):
                cached = self.cache.read_json(cache_path)
                cached_results = cached.get("results") if cached else None
                if isinstance(cached_results, list):
                    external = [self._from_dict(item) for item in cached_results if isinstance(item, dict)]
                else:
                    external = self.provider.search(query, language, limit)
                    self.cache.write_json(
                        cache_path,
                        {"query": query, "results": [self._to_dict(item) for item in external]},
                    )

        combined: list[Location] = []
        seen: set[tuple[float, float]] = set()
        for result in [*local, *external]:
            coordinate_key = (
                round(result.coordinate.latitude, 5),
                round(result.coordinate.longitude, 5),
            )
            if coordinate_key not in seen:
                combined.append(result)
                seen.add(coordinate_key)
            if len(combined) >= limit:
                break
        return combined

    @staticmethod
    def _to_dict(location: Location) -> dict[str, object]:
        payload = asdict(location)
        payload["coordinate"] = asdict(location.coordinate)
        return payload

    @staticmethod
    def _from_dict(payload: dict[str, object]) -> Location:
        coordinate = payload.get("coordinate")
        if not isinstance(coordinate, dict):
            raise GeocodingError("Invalid cached coordinate.")
        return Location(
            display_name=str(payload.get("display_name", "")),
            coordinate=Coordinate(
                float(coordinate["latitude"]),
                float(coordinate["longitude"]),
            ),
            country=str(payload.get("country", "")),
            region=str(payload.get("region", "")),
            country_code=str(payload.get("country_code", "")),
            provider=str(payload.get("provider", "cache")),
        )

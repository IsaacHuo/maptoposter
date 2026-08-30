from __future__ import annotations

from dataclasses import replace

from maptoposter.cache import DiskCache, map_cache_key
from maptoposter.china import search_china
from maptoposter.geocoding import GeocodingService, parse_coordinate_query
from maptoposter.models import Coordinate, Location


class FakeProvider:
    def __init__(self) -> None:
        self.calls = 0

    def search(self, query: str, language: str, limit: int) -> list[Location]:
        self.calls += 1
        return [Location(query, Coordinate(1.25, 2.5), "Testland", provider="fake")]


def test_map_cache_key_uses_rounded_data_parameters(poster_config) -> None:
    original = map_cache_key(poster_config.map)
    viewport = replace(
        poster_config.map.viewport,
        center=Coordinate(40.0000001, 116.3000001),
    )
    assert map_cache_key(replace(poster_config.map, viewport=viewport)) == original
    assert map_cache_key(replace(poster_config.map, network_type="drive")) != original


def test_disk_json_cache_is_atomic(tmp_path) -> None:
    cache = DiskCache(tmp_path)
    path = cache.geocoding_path("abc")
    cache.write_json(path, {"value": "北京"})
    assert cache.read_json(path) == {"value": "北京"}


def test_coordinate_and_china_local_search_do_not_call_network(tmp_path) -> None:
    coordinate = parse_coordinate_query("39.9042, 116.4074")
    assert coordinate is not None and coordinate.provider == "coordinates"
    assert search_china("北京")[0].provider == "china-local"
    provider = FakeProvider()
    service = GeocodingService(DiskCache(tmp_path), provider)
    assert service.search("北京")[0].provider == "china-local"
    assert provider.calls == 0


def test_external_geocoder_result_is_cached(tmp_path) -> None:
    provider = FakeProvider()
    service = GeocodingService(DiskCache(tmp_path), provider)
    assert service.search("Atlantis")[0].provider == "fake"
    assert service.search("Atlantis")[0].provider == "fake"
    assert provider.calls == 1

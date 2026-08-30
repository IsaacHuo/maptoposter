"""Compatibility pytest module for the original data helpers.

The detailed product tests live under ``tests/``; these checks stay at the
historical path so existing contributors can still run ``uv run pytest``.
"""

from __future__ import annotations

import os
import tempfile

from cities_data import get_china_adcode, get_cities, get_districts, get_manual_coordinates, get_provinces
from maptoposter.layers import keys_to_labels, selected_labels_to_keys, selected_layer_flags
from maptoposter.rendering import create_bbox, generate_output_filename
from maptoposter.themes import list_themes, load_theme


def test_china_hierarchy() -> None:
    provinces = get_provinces("中国", lang="cn")
    assert len(provinces) > 30
    assert any(province[1] == "广东省" for province in provinces)

    cities = get_cities("中国", "广东省", lang="cn")
    assert len(cities) > 10
    assert cities[0] == ("整个省", "广东省_WHOLE")
    assert any(city[1] == "广州市" for city in cities)

    districts = get_districts("中国", "广东省", "广州市", lang="cn")
    assert len(districts) > 5
    assert districts[0][0] == "整个城市"
    assert any(district[1] == "天河区" for district in districts)

    assert get_cities("中国", "上海市", lang="cn") == [("上海市", "上海市")]
    shanghai_districts = get_districts("中国", "上海市", "上海市", lang="cn")
    assert len(shanghai_districts) > 10
    assert any(district[1] == "浦东新区" for district in shanghai_districts)


def test_manual_coordinates() -> None:
    guangdong = get_china_adcode("广东省")
    guangzhou = get_china_adcode("广州市", guangdong)
    assert get_manual_coordinates("广州市", guangdong) is not None
    assert get_manual_coordinates("天河区", guangzhou) is not None
    shanghai = get_china_adcode("上海市")
    assert get_manual_coordinates("浦东新区", shanghai) is not None


def test_theme_helpers() -> None:
    themes = list_themes()
    assert "feature_based" in themes
    assert load_theme("feature_based", verbose=False)["name"] == "Feature-Based Shading"
    assert load_theme("__missing_theme__", verbose=False)["name"] == "Feature-Based Shading"


def test_layer_helpers() -> None:
    keys = selected_labels_to_keys(["Motorway", "主干道", "Water"])
    assert keys == ["motorway", "primary", "water"]
    assert keys_to_labels(keys, "cn") == ["高速公路", "主干道", "水域"]
    assert selected_layer_flags(["Motorway", "水域"]) == {
        "show_motorway": True,
        "show_primary": False,
        "show_secondary": False,
        "show_water": True,
        "show_parks": False,
    }


def test_rendering_helpers() -> None:
    west, south, east, north = create_bbox((30.0, 120.0), 10_000, 12, 16)
    assert west < east and south < north
    assert (east - west) < (north - south)
    with tempfile.TemporaryDirectory() as temp_dir:
        filename = generate_output_filename("New York", "noir", "png", directory=temp_dir)
        assert filename.startswith(temp_dir)
        assert filename.endswith(".png")
        assert "new-york-noir-" in os.path.basename(filename)

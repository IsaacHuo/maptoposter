import os
import sys
import tempfile

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cities_data import get_provinces, get_cities, get_districts, get_manual_coordinates
from maptoposter.layers import (
    keys_to_labels,
    selected_labels_to_keys,
    selected_layer_flags,
)
from maptoposter.rendering import create_bbox, generate_output_filename
from maptoposter.themes import load_theme, list_themes


def test_china_hierarchy():
    print("Testing China Hierarchy...")

    # 1. Test Provinces
    provinces = get_provinces("中国", lang="cn")
    print(f"Found {len(provinces)} provinces.")
    assert len(provinces) > 30, f"Expected >30 provinces, found {len(provinces)}"
    assert any(p[1] == "广东省" for p in provinces), "广东省 not found"

    # 2. Test Cities
    cities = get_cities("中国", "广东省", lang="cn")
    print(f"Found {len(cities)} cities in 广东省.")
    assert len(cities) > 10, f"Expected >10 cities in GD, found {len(cities)}"
    assert cities[0] == ("整个省", "广东省_WHOLE"), "Whole province option missing"
    assert any(c[1] == "广州市" for c in cities), "广州市 not found"

    # 3. Test Districts
    districts = get_districts("中国", "广东省", "广州市", lang="cn")
    print(f"Found {len(districts)} districts in 广州市.")
    assert len(districts) > 5, f"Expected >5 districts in GZ, found {len(districts)}"
    assert districts[0][0] == "整个城市", "First option should be '整个城市'"
    assert any(d[1] == "天河区" for d in districts), "天河区 not found"

    # 4. Test Municipality
    sh_cities = get_cities("中国", "上海市", lang="cn")
    print(f"Cities in 上海市: {sh_cities}")
    assert sh_cities == [("上海市", "上海市")], (
        "Shanghai municipality should return itself as city"
    )

    sh_districts = get_districts("中国", "上海市", "上海市", lang="cn")
    print(f"Found {len(sh_districts)} districts in 上海市.")
    assert len(sh_districts) > 10, (
        f"Expected >10 districts in SH, found {len(sh_districts)}"
    )
    assert any(d[1] == "浦东新区" for d in sh_districts), "浦东新区 not found"


def test_manual_coordinates():
    print("\nTesting Coordinate Data Retrieval...")

    # 1. Test Province Lookup (should find City if parent is 100000)
    from cities_data import get_china_adcode

    gd_adcode = get_china_adcode("广东省")
    gz_adcode = get_china_adcode("广州市", gd_adcode)

    # 2. Test City Lookup
    coords = get_manual_coordinates("广州市", gd_adcode)
    print(f"广州市 coords: {coords}")
    assert coords is not None, "Could not find GZ coords"

    # 3. Test District Lookup
    coords = get_manual_coordinates("天河区", gz_adcode)
    print(f"天河区 coords: {coords}")
    assert coords is not None, "Could not find Tianhe coords"

    # 4. Test Municipality District
    sh_adcode = get_china_adcode("上海市")
    coords = get_manual_coordinates("浦东新区", sh_adcode)
    print(f"浦东新区 coords: {coords}")
    assert coords is not None, "Could not find Pudong coords"


def test_theme_helpers():
    print("\nTesting Theme Helpers...")

    themes = list_themes()
    print(f"Found {len(themes)} themes.")
    assert "feature_based" in themes, "feature_based theme not found"

    theme = load_theme("feature_based", verbose=False)
    assert theme["name"] == "Feature-Based Shading"

    fallback = load_theme("__missing_theme__", verbose=False)
    assert fallback["name"] == "Feature-Based Shading"


def test_layer_helpers():
    print("\nTesting Layer Helpers...")

    keys = selected_labels_to_keys(["Motorway", "主干道", "Water"])
    assert keys == ["motorway", "primary", "water"]

    labels = keys_to_labels(keys, "cn")
    assert labels == ["高速公路", "主干道", "水域"]

    flags = selected_layer_flags(["Motorway", "水域"])
    assert flags == {
        "show_motorway": True,
        "show_primary": False,
        "show_secondary": False,
        "show_water": True,
        "show_parks": False,
    }


def test_rendering_helpers():
    print("\nTesting Rendering Helpers...")

    west, south, east, north = create_bbox((30.0, 120.0), 10000, 12, 16)
    assert west < east
    assert south < north
    assert (east - west) < (north - south), "Portrait bbox should be narrower than tall"

    with tempfile.TemporaryDirectory() as temp_dir:
        filename = generate_output_filename("New York", "noir", "png", directory=temp_dir)
        assert filename.startswith(temp_dir)
        assert filename.endswith(".png")
        assert "new_york_noir_" in os.path.basename(filename)


if __name__ == "__main__":
    try:
        test_china_hierarchy()
        test_manual_coordinates()
        test_theme_helpers()
        test_layer_helpers()
        test_rendering_helpers()
        print("\n✅ Data logic tests passed!")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

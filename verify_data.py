import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cities_data import get_provinces, get_cities, get_districts
import create_map_poster as cmp


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


def test_coordinate_lookup():
    print("\nTesting Coordinate Lookup...")

    # 1. Test Province Lookup
    coords = cmp.get_coordinates("广东省", "中国", parent="中国")
    print(f"广东省 coords: {coords}")
    assert coords is not None, "Could not find GD coords"

    # 2. Test City Lookup
    coords = cmp.get_coordinates("广州市", "中国", parent="广东省")
    print(f"广州市 coords: {coords}")
    assert coords is not None, "Could not find GZ coords"

    # 3. Test District Lookup
    coords = cmp.get_coordinates("天河区", "中国", parent="广州市")
    print(f"天河区 coords: {coords}")
    assert coords is not None, "Could not find Tianhe coords"

    # 4. Test Municipality District
    coords = cmp.get_coordinates("浦东新区", "中国", parent="上海市")
    print(f"浦东新区 coords: {coords}")
    assert coords is not None, "Could not find Pudong coords"


if __name__ == "__main__":
    try:
        test_china_hierarchy()
        test_coordinate_lookup()
        print("\n✅ All integration tests passed!")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

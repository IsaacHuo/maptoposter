"""Geodesic viewport construction."""

from __future__ import annotations

from pyproj import Geod

from .models import BBox, Coordinate, MapViewport

GEOD = Geod(ellps="WGS84")


def create_viewport(
    center: Coordinate, distance_m: float, width: float, height: float, zoom: float | None = None
) -> MapViewport:
    """Create a geodesic bbox whose geographic coverage follows the poster ratio."""
    if not 100 <= distance_m <= 250_000:
        raise ValueError("Map distance must be between 100 m and 250 km.")
    if width <= 0 or height <= 0:
        raise ValueError("Poster dimensions must be greater than zero.")
    if abs(center.latitude) >= 89:
        raise ValueError("Map viewports above 89° latitude are not supported.")

    east_west = distance_m * width / height
    west, _, _ = GEOD.fwd(center.longitude, center.latitude, 270, east_west)
    east, _, _ = GEOD.fwd(center.longitude, center.latitude, 90, east_west)
    _, south, _ = GEOD.fwd(center.longitude, center.latitude, 180, distance_m)
    _, north, _ = GEOD.fwd(center.longitude, center.latitude, 0, distance_m)
    if west >= east:
        raise ValueError("Viewports crossing the antimeridian are not supported yet.")
    return MapViewport(
        center=center,
        bbox=BBox(west=west, south=south, east=east, north=north),
        zoom=zoom,
        distance_m=distance_m,
    )


def create_bbox_tuple(
    point: tuple[float, float], distance_m: float, width: float, height: float
) -> tuple[float, float, float, float]:
    """Backward-compatible bbox helper."""
    return create_viewport(Coordinate(*point), distance_m, width, height).bbox.as_tuple()


def expand_bbox_to_aspect(bbox: BBox, target_aspect: float) -> BBox:
    """Expand a bbox to an aspect ratio without cropping its original coverage."""
    if target_aspect <= 0:
        raise ValueError("Target aspect ratio must be greater than zero.")

    center_lon = (bbox.west + bbox.east) / 2
    center_lat = (bbox.south + bbox.north) / 2
    _, _, width_m = GEOD.inv(bbox.west, center_lat, bbox.east, center_lat)
    _, _, height_m = GEOD.inv(center_lon, bbox.south, center_lon, bbox.north)
    if width_m <= 0 or height_m <= 0:
        raise ValueError("Bounding box dimensions must be greater than zero.")

    current_aspect = width_m / height_m
    if abs(current_aspect - target_aspect) < 0.005:
        return bbox
    if current_aspect > target_aspect:
        extra_m = (width_m / target_aspect - height_m) / 2
        _, south, _ = GEOD.fwd(center_lon, bbox.south, 180, extra_m)
        _, north, _ = GEOD.fwd(center_lon, bbox.north, 0, extra_m)
        return BBox(bbox.west, south, bbox.east, north)

    extra_m = (height_m * target_aspect - width_m) / 2
    west, _, _ = GEOD.fwd(bbox.west, center_lat, 270, extra_m)
    east, _, _ = GEOD.fwd(bbox.east, center_lat, 90, extra_m)
    if west >= east:
        raise ValueError("Aspect fitting would cross the antimeridian.")
    return BBox(west, bbox.south, east, bbox.north)

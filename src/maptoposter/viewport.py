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

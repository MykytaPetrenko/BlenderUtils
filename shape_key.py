from __future__ import annotations

from typing import Iterable, List, Sequence

import bpy
from mathutils import Vector


def shape_key_coordinates_flat(shape_key: bpy.types.ShapeKey) -> List[float]:
    coordinates = [0.0] * (len(shape_key.data) * 3)
    shape_key.data.foreach_get("co", coordinates)
    return coordinates


def write_shape_key_coordinates_flat(
    shape_key: bpy.types.ShapeKey,
    coordinates: Sequence[float],
) -> None:
    if getattr(shape_key, "lock_shape", False):
        raise RuntimeError(f"Shape key is locked: {shape_key.name}")

    shape_key.data.foreach_set("co", coordinates)


def write_shape_key_coordinates(
    shape_key: bpy.types.ShapeKey,
    coordinates: Iterable[Vector],
) -> None:
    """Batch write coordinates to a shape key."""
    flat_coordinates = [
        component
        for coordinate in coordinates
        for component in (coordinate.x, coordinate.y, coordinate.z)
    ]
    write_shape_key_coordinates_flat(shape_key, flat_coordinates)

from __future__ import annotations

from typing import Iterable

import bpy
from mathutils import Vector


def write_shape_key_coordinates(
    shape_key: bpy.types.ShapeKey,
    coordinates: Iterable[Vector],
) -> None:
    """Batch write coordinates to a shape key."""
    if getattr(shape_key, "lock_shape", False):
        raise RuntimeError(f"Shape key is locked: {shape_key.name}")

    flat_coordinates = [
        component
        for coordinate in coordinates
        for component in (coordinate.x, coordinate.y, coordinate.z)
    ]
    shape_key.data.foreach_set("co", flat_coordinates)

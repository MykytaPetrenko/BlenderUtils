import bpy
from mathutils import Vector
from typing import List


def get_basis_coordinates(obj: bpy.types.Object) -> List[Vector]:
    """Get basis vertex coordinates from the mesh or Basis shape key.

    Args:
        obj: Mesh object to read coordinates from.

    Returns:
        Vertex coordinates representing the basis shape.
    """
    shape_keys = obj.data.shape_keys
    if shape_keys and shape_keys.key_blocks:
        return [point.co.copy() for point in shape_keys.key_blocks[0].data]
    return [vertex.co.copy() for vertex in obj.data.vertices]


def write_basis_coordinates(obj: bpy.types.Object, new_coordinates: List[Vector]) -> None:
    """Write coordinates to the mesh and Basis shape key.

    Args:
        obj: Mesh object to update.
        new_coordinates: Coordinates to assign to basis vertices.

    Returns:
        None.
    """
    mesh = obj.data
    shape_keys = mesh.shape_keys
    if shape_keys and shape_keys.key_blocks:
        basis = shape_keys.key_blocks[0]
        for i, coordinate in enumerate(new_coordinates):
            basis.data[i].co = coordinate
    for i, coordinate in enumerate(new_coordinates):
        mesh.vertices[i].co = coordinate
    mesh.update()


def save_shape_key(
    obj: bpy.types.Object,
    original_coordinates: List[Vector],
    shape_key_name: str,
) -> None:
    """Create a shape key from vertex coordinates.

    Args:
        obj: Mesh object that receives the shape key.
        original_coordinates: Coordinates stored in the new shape key.
        shape_key_name: Name of the shape key.

    Returns:
        None.
    """
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis").interpolation = "KEY_LINEAR"
    shape_key = obj.shape_key_add(name=shape_key_name)
    shape_key.interpolation = "KEY_LINEAR"
    shape_key.value = 0.0
    for i, coordinate in enumerate(original_coordinates):
        shape_key.data[i].co = coordinate

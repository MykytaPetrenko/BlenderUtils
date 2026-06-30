import bpy
from mathutils import Vector
from typing import List, Sequence


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


def apply_basis_shape(
    obj: bpy.types.Object,
    new_coordinates: Sequence[Vector],
    recompute_shape_keys: bool = True,
) -> None:
    """Apply a new Basis shape to a mesh object.

    Args:
        obj: Mesh object to update.
        new_coordinates: Coordinates to assign to basis vertices.
        recompute_shape_keys: Move every non-Basis shape key by the Basis
            displacement so its original deltas are preserved.

    Returns:
        None.
    """
    mesh = obj.data
    vertex_count = len(mesh.vertices)
    if len(new_coordinates) != vertex_count:
        raise ValueError(
            f"Expected {vertex_count} basis coordinates, got {len(new_coordinates)}."
        )

    flat_coordinates = [
        component
        for coordinate in new_coordinates
        for component in (coordinate.x, coordinate.y, coordinate.z)
    ]
    shape_keys = mesh.shape_keys
    if shape_keys and shape_keys.key_blocks:
        basis = shape_keys.key_blocks[0]
        if recompute_shape_keys:
            old_basis_coordinates = [0.0] * (vertex_count * 3)
            basis.data.foreach_get("co", old_basis_coordinates)
            basis_displacement = [
                new_value - old_value
                for new_value, old_value in zip(flat_coordinates, old_basis_coordinates)
            ]

            for shape_key in shape_keys.key_blocks[1:]:
                shape_key_coordinates = [0.0] * (vertex_count * 3)
                shape_key.data.foreach_get("co", shape_key_coordinates)
                shape_key.data.foreach_set(
                    "co",
                    [
                        value + displacement
                        for value, displacement in zip(
                            shape_key_coordinates,
                            basis_displacement,
                        )
                    ],
                )

        basis.data.foreach_set("co", flat_coordinates)

    mesh.vertices.foreach_set("co", flat_coordinates)
    mesh.update()


def write_basis_coordinates(obj: bpy.types.Object, new_coordinates: List[Vector]) -> None:
    """Write coordinates to the mesh and Basis without adjusting shape keys.

    This compatibility wrapper preserves the behavior of the original helper.
    Use :func:`apply_basis_shape` for optional shape-key recomputation.
    """
    apply_basis_shape(obj, new_coordinates, recompute_shape_keys=False)


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

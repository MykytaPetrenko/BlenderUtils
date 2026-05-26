from typing import List, Tuple
from mathutils import Vector
import math


def normalize_half_turn(angle: float) -> float:
    while angle > math.pi * 0.5:
        angle -= math.pi
    while angle < math.pi * -0.5:
        angle += math.pi
    return angle

def centroid(points: List[Vector]) -> Vector:
    n = len(points)
    result = Vector(
        (
            sum(v.x for v in points),
            sum(v.y for v in points),
            sum(v.z for v in points)
        )
    )
    return result / n


def centroid_2d(points: List[Vector]) -> Vector:
    n = len(points)
    result = Vector(
        (
            sum(v.x for v in points),
            sum(v.y for v in points)
        )
    )
    return result / n


def principal_angle_2d(points: List[Vector]) -> float:
    if len(points) < 2:
        return 0.0
    mean_x = sum(point.x for point in points) / len(points)
    mean_y = sum(point.y for point in points) / len(points)
    cov_xx = 0.0
    cov_xy = 0.0
    cov_yy = 0.0
    for point in points:
        dx = point.x - mean_x
        dy = point.y - mean_y
        cov_xx += dx * dx
        cov_xy += dx * dy
        cov_yy += dy * dy
    if math.sqrt(cov_xx * cov_xx + cov_yy * cov_yy + cov_xy * cov_xy) <= 0.0:
        return 0.0
    return 0.5 * math.atan2(2.0 * cov_xy, cov_xx - cov_yy)


def rotate_point_2d(point: Vector, origin: Vector, angle: float) -> Vector:
    c = math.cos(angle)
    s = math.sin(angle)
    x = point.x - origin.x
    y = point.y - origin.y
    return Vector((origin.x + c * x - s * y, origin.y + s * x + c * y))


def mirror_point(
    co: Vector,
    axis_index: int,
    axis_position: float = 0.0
) -> Vector:
    """Mirror a 3D/2D point across a plane/axis.

    Args:
        co: Source coordinate.
        axis_index: Plane normal axis.
        axis_position: Position of the mirror plane.

    Returns:
        Mirrored coordinate.
    """
    result = co.copy()
    result[axis_index] = 2.0 * axis_position - result[axis_index]
    return result


def average_symmetric_pair(
    first: Vector,
    second: Vector,
    axis_index: int,
    axis_position: float = 0.0,
) -> Tuple[Vector, Vector]:
    """Average a mirrored point pair.

    Produces a symmetric pair whose midpoint lies on the mirror
    axis or plane.

    Args:
        first: First coordinate.
        second: Second coordinate.
        axis_index: Mirror axis index.
        axis_position: Position of the mirror axis or plane.

    Returns:
        Averaged symmetric coordinate pair.
    """
    second_mirrored = mirror_point(
        second,
        axis_index,
        axis_position,
    )

    first_average = (first + second_mirrored) * 0.5

    second_average = mirror_point(
        first_average,
        axis_index,
        axis_position,
    )

    return first_average, second_average


def transform_2d(uv: Vector, translation: Vector, angle: float, scale: float = 1.0) -> Vector:
    """
    Apply 2D rotation, scale, and translation.

    Args:
        uv: Source coordinate.
        translation: Translation offset.
        angle: Rotation angle in radians.
        scale: Uniform scale factor.

    Returns:
        Transformed coordinate.
    """
    origin = Vector((0.0, 0.0))
    rotated = rotate_point_2d(uv.copy(), origin, angle)
    return rotated * scale + translation

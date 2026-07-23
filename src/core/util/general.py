from math import floor, hypot
from typing import Iterable
from pathlib import Path
from .vector import Vec
from enum import Enum
import weakref
import pygame
import sys
import os

VecLike = tuple[float, float] | Vec

BUNDLE_DIR = getattr(
    sys, "_MEIPASS",
    Path(os.path.abspath(os.path.dirname(__file__))).parent
)

def pathof(file: str) -> str:
    """Gets the path to the given file that will work with exes.

    Args:
        file: The original path to go to

    Returns:
        The bundled exe-compatible file path
    """

    abspath = os.path.abspath(os.path.join(BUNDLE_DIR, file))
    if not os.path.exists(abspath):
        abspath = file
    return abspath

def ref_proxy[T](obj: T) -> T:
    """Create a weak reference proxy to an object if it isn"t already one.

    Args:
        obj: The object to create a weak reference proxy to.

    Returns:
        The weak reference proxy.
    """
    if isinstance(obj, weakref.ProxyTypes):
        return obj
    return weakref.proxy(obj)

def read_file(path: str | Path) -> str:
    """Opens a file, read the contents of the file, then closes it.

    Args:
        path: The path of the file to read from.

    Returns:
        The full contents of the file.
    """
    with open(path, "r") as file:
        return file.read()

def inttup(tup: VecLike) -> tuple[int, int]:
    """Convert a tuple of 2 numbers to a tuple of 2 ints.

    This uses the floor function to convert the numbers to ints.

    Args:
        tup: The tuple to convert.

    Returns:
        The integer tuple.
    """
    return (int(floor(tup[0])), int(floor(tup[1])))

def sign(x: float) -> int:
    """Get the sign of a number.

    Args:
        x: The number to get the sign of.

    Returns:
        The sign of the number.
    """
    return (x > 0) - (x < 0)

def iter_rect(left: int, right: int,
              top: int, bottom: int) -> Iterable[tuple[int, int]]:
    """Iterate over the coordinates of a rectangle.

    Args:
        left: The leftmost x-coordinate (inclusive).
        right: The rightmost x-coordinate (inclusive).
        top: The topmost y-coordinate (inclusive).
        bottom: The bottommost y-coordinate (inclusive).

    Yields:
        The coordinates of the rectangle.
    """
    for x in range(int(left), int(right) + 1):
        for y in range(int(top), int(bottom) + 1):
            yield (x, y)

def point_in_polygon(point: VecLike, polygon: list[VecLike]) -> bool:
    """Check whether a point lies within a polygon.

    Uses the ray casting algorithm, so it works for concave polygons too.

    Args:
        point: The point to check.
        polygon: The vertices of the polygon, in order.

    Returns:
        Whether the point lies within the polygon.
    """
    x, y = point
    inside = False
    n = len(polygon)
    x1, y1 = polygon[-1]
    for i in range(n):
        x2, y2 = polygon[i]
        if (y1 > y) != (y2 > y):
            x_intersect = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < x_intersect:
                inside = not inside
        x1, y1 = x2, y2
    return inside

def point_segment_distance(point: VecLike, a: VecLike, b: VecLike) -> float:
    """Compute the shortest distance from a point to a line segment.

    Args:
        point: The point to measure from.
        a: One endpoint of the segment.
        b: The other endpoint of the segment.

    Returns:
        The shortest distance between the point and the segment.
    """
    px, py = point
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return hypot(px - ax, py - ay)
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    closest_x = ax + t * dx
    closest_y = ay + t * dy
    return hypot(px - closest_x, py - closest_y)

def distance_to_polygon_edges(point: VecLike, polygon: list[VecLike]) -> float:
    """Compute the shortest distance from a point to a polygon's edges.

    Args:
        point: The point to measure from.
        polygon: The vertices of the polygon, in order.

    Returns:
        The shortest distance between the point and any edge of the polygon.
    """
    n = len(polygon)
    return min(
        point_segment_distance(point, polygon[i], polygon[(i + 1) % n])
        for i in range(n)
    )

def iter_square(size: int) -> Iterable[tuple[int, int]]:
    """Iterate over the coordinates of a square.

    Args:
        size: The size of the square.

    Yields:
        The coordinates of the square.
    """
    yield from iter_rect(0, size - 1, 0, size - 1)

class Anchor(Enum):
    """Anchor points for blitting surfaces."""
    TOPLEFT = Vec(0, 0)
    TOPRIGHT = Vec(1, 0)
    BOTTOMLEFT = Vec(0, 1)
    BOTTOMRIGHT = Vec(1, 1)
    TOP = Vec(0.5, 0)
    BOTTOM = Vec(0.5, 1)
    LEFT = Vec(0, 0.5)
    RIGHT = Vec(1, 0.5)
    CENTER = Vec(0.5, 0.5)

    def offset(self, offset: VecLike) -> OffsetAnchor:
        """Apply an offset to this anchor. Returns a new OffsetAnchor instance.

        Args:
            offset: The offset to apply to the anchor.

        Returns:
            A new OffsetAnchor with the offset applied.
        """
        return OffsetAnchor(self, offset)

    def apply_to(self, size: VecLike) -> Vec:
        """Get the offset vector for this anchor and the given size.

        Args:
            size: The size to get the offset for.

        Returns:
            The offset vector.
        """
        return self.value.elementwise() * Vec(size)

class OffsetAnchor:
    def __init__(self, anchor: Anchor, offset: VecLike) -> None:
        self.anchor = anchor
        self._offset = Vec(offset)

    def apply_to(self, size: VecLike) -> Vec:
        """Get the offset vector for this anchor and the given size.

        Args:
            size: The size to get the offset for.

        Returns:
            The offset vector.
        """
        return self.anchor.value.elementwise() * Vec(size) + self._offset

AnchorType = Anchor | OffsetAnchor

def anchored_blit(target: pygame.Surface, source: pygame.Surface, pos: VecLike,
                  anchor: AnchorType | VecLike) -> None:
    """Blit a surface onto another surface with an anchor point.

    Args:
        target: The target surface to blit onto.
        source: The source surface to blit.
        pos: The position to blit at.
        anchor: The anchor point to use. This can either be an Anchor enum, or a
            Vec representing the offset from the top-left corner of the source
            surface.
    """

    if isinstance(anchor, (Anchor, OffsetAnchor)):
        blit_pos = Vec(pos) - anchor.apply_to(source.size)
    else:
        blit_pos = Vec(pos) - anchor
    target.blit(source, blit_pos)

def rotate(surface: pygame.Surface, angle: float) -> pygame.Surface:
    """Rotate a surface by a given angle. This differs from
    `pygame.transform.rotate` in that it rotates clockwise instead of
    counter-clockwise. This makes it consistent with the rest of the engine.

    Args:
        surface: The surface to rotate.
        angle: The angle to rotate by, in degrees.

    Returns:
        The rotated surface.
    """
    return pygame.transform.rotate(surface, -angle)

def rotate_around(surface: pygame.Surface, angle: float,
                  pivot: AnchorType | Vec) -> tuple[pygame.Surface, Vec]:
    """Rotate a surface around a pivot point.

    Args:
        surface: The surface to rotate.
        angle: The angle to rotate by, in degrees.
        pivot: The pivot point to rotate around. This can either be an Anchor
            enum, or a Vec representing the offset from the top-left corner of
            the surface.

    Returns:
        A tuple of the rotated surface and the offset to blit at in order to
        maintain the pivot point's position.
    """
    if isinstance(pivot, (Anchor, OffsetAnchor)):
        pivot_vec = pivot.apply_to(surface.size)
    else:
        pivot_vec = pivot
    center = Vec(surface.size) / 2
    offset_from_center = pivot_vec - center
    rotated_image = rotate(surface, angle)
    new_center = Vec(rotated_image.size) / 2
    rotated_offset = offset_from_center.rotate(angle)
    blit_offset = new_center + rotated_offset
    return rotated_image, -blit_offset

def dropshadow(surface: pygame.Surface, darkness: int) -> pygame.Surface:
    """Create a drop shadow surface from the given surface.

    Blit the returned surface using the BLEND_SUB flag.

    Args:
        surface: The surface to create a drop shadow from.
        darkness: The darkness of the shadow, from 0 (invisible) to 255 (black).

    Returns:
        The drop shadow surface.
    """
    return pygame.mask.from_surface(surface).to_surface(
        setcolor = (darkness,) * 3,
        unsetcolor = (0, 0, 0),
    )

__all__ = [
    "VecLike",
    "pathof",
    "ref_proxy",
    "read_file",
    "inttup",
    "sign",
    "point_in_polygon",
    "point_segment_distance",
    "distance_to_polygon_edges",
    "iter_rect",
    "iter_square",
    "Anchor",
    "AnchorType",
    "anchored_blit",
    "rotate",
    "rotate_around",
    "dropshadow",
]

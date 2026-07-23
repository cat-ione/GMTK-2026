from abc import ABC as AbstractClass, abstractmethod
from .general import Vec, VecLike, AnchorType
import pygame

class Hitbox(AbstractClass):
    pos: Vec

    @abstractmethod
    def set_pos(self, pos: VecLike) -> None:
        pass

    @abstractmethod
    def collides(self, other: Hitbox) -> bool:
        pass

    def _not_implemented(self) -> NotImplementedError:
        return NotImplementedError(
            "Collision detection not implemented for this hitbox type.")

class RectHitbox(Hitbox):
    @classmethod
    def copy(
        cls, other: RectHitbox,
        pos: VecLike | None = None
    ) -> RectHitbox:
        return cls(
            pos if pos is not None else other.pos,
            other.size, other.anchor
        )

    def __init__(self, pos: VecLike, size: VecLike, anchor: AnchorType) -> None:
        self.anchor = anchor
        self._offset = anchor.apply_to(size)
        self.pos = Vec(pos)
        self.size = Vec(size)

    def set_pos(self, pos: VecLike) -> None:
        self.pos = Vec(pos)

    def collides(self, other: Hitbox) -> bool:
        if isinstance(other, RectHitbox):
            return self._collides_rect(other)

        raise self._not_implemented()

    def _collides_rect(self, other: RectHitbox) -> bool:
        return (
            self.topleft.x < other.topleft.x + other.size.x and
            self.topleft.x + self.size.x > other.topleft.x and
            self.topleft.y < other.topleft.y + other.size.y and
            self.topleft.y + self.size.y > other.topleft.y
        )

    def collides_point(self, point: VecLike, margin: float = 0) -> bool:
        return self.topleft.x - margin < point[0] < self.bottomright.x + margin \
            and self.topleft.y - margin < point[1] < self.bottomright.y + margin

    @property
    def topleft(self) -> Vec:
        return self.pos - self._offset

    @property
    def topright(self) -> Vec:
        return self.topleft + Vec(self.size.x, 0)

    @property
    def bottomright(self) -> Vec:
        return self.topleft + self.size

    @property
    def bottomleft(self) -> Vec:
        return self.topleft + Vec(0, self.size.y)

    @property
    def topcenter(self) -> Vec:
        return self.topleft + Vec(self.size.x / 2, 0)

    @property
    def bottomcenter(self) -> Vec:
        return self.topleft + Vec(self.size.x / 2, self.size.y)

    @property
    def leftcenter(self) -> Vec:
        return self.topleft + Vec(0, self.size.y / 2)

    @property
    def rightcenter(self) -> Vec:
        return self.topleft + Vec(self.size.x, self.size.y / 2)

    @property
    def center(self) -> Vec:
        return self.topleft + self.size / 2

    def get_rect(self, rel: VecLike = (0, 0)) -> tuple[VecLike, VecLike]:
        return (self.topleft + rel, self.size)

    def draw(
        self, screen: pygame.Surface,
        color: tuple[int, int, int],
        rel: VecLike = (0, 0), width: int = 1
    ) -> None:
        pygame.draw.rect(screen, color, self.get_rect(rel), width)

__all__ = [
    "Hitbox",
    "RectHitbox",
]

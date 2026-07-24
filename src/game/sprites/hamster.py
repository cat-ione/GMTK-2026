from src.core import *

from .interaction_target import InteractionTarget
from .item import Item

if TYPE_CHECKING:
    from .furniture import Furniture

class HamsterItem(Item):
    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(scene, pos, Image.get("hamster_front"))

    def drop(self) -> None:
        self.scene.remove_item(self)
        hamster = Hamster(self.scene, self.pos)

        targets = [
            furniture for furniture in self.scene.furnitures
            if furniture.hitbox is not None and furniture.hitbox.size != Vec(0, 0)
        ]
        if targets:
            hamster.go_to(choice(targets), 90)

        self.scene.add(hamster)

class Hamster(Sprite["Room"]):
    update_group = UGroup.MAIN
    draw_group = DGroup.ROOM

    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)
        self.vel = Vec(0, 0)
        self.image = Image.get("hamster_side")
        self.hitbox = RectHitbox(self.pos, (6, 6), Anchor.CENTER)

        self.target_furniture = None
        self.speed = 0
        # The cardinal direction currently being walked in
        self.direction = Vec(0, 0)
        # Whether we're currently detouring around an obstacle, and (if so)
        # the direction we're actually trying to get back to
        self.detouring = False
        self.detour_target = Vec(0, 0)

        self.interaction_target = InteractionTarget(self.scene, self.pos, self)
        self.scene.interaction_targets.add(self.interaction_target)
        self.selected = False

    def update(self) -> None:
        if self.target_furniture is not None:
            self._move_towards_target()
        self.hitbox.set_pos(self.pos)
        self.interaction_target.pos = self.pos.copy()

        if self.vel.x < 0:
            self.image = Image.get("hamster_side")
        elif self.vel.x > 0:
            self.image = pygame.transform.flip(Image.get("hamster_side"), True, False)

    def select(self) -> None:
        self.selected = True

    def deselect(self) -> None:
        self.selected = False

    def interact(self) -> None:
        self.remove()
        self.scene.player.gain_item(HamsterItem(self.scene, self.pos))

    def remove(self) -> None:
        self.scene.remove(self)
        self.scene.interaction_targets.remove(self.interaction_target)

    def go_to(self, furniture: Furniture, speed: float) -> None:
        self.target_furniture = furniture
        self.speed = speed
        self.direction = Vec(0, 0)
        self.detouring = False

    def draw(self, screen: pygame.Surface) -> None:
        draw_pos = self.screen_pos - Vec(self.image.size) / 2
        if self.selected:
            screen.blit(outline(self.image, (255, 255, 255)), draw_pos - (1, 1))
        screen.blit(self.image, draw_pos)

    def _move_towards_target(self) -> None:
        assert self.target_furniture is not None

        target_pos = self.target_furniture.get_pos()
        delta = target_pos - self.pos
        step = self.speed * self.game.dt

        if delta.length() <= step:
            self.pos = target_pos
            self.vel = Vec(0, 0)
            self.target_furniture = None
            self.direction = Vec(0, 0)
            self.detouring = False
            return

        if self.detouring:
            self._update_detour(delta)
        else:
            self._update_direct(delta)

        if self.direction == Vec(0, 0):
            # Boxed in on all sides so dont move
            self.vel = Vec(0, 0)
            return

        self.vel = self.direction * self.speed
        self.pos += self.vel * self.game.dt

    def _update_direct(self, delta: Vec) -> None:
        # Commit to the dominant axis until it stops making progress, so
        # movement happens in long segments instead of zigzagging
        if self.direction == Vec(0, 0) or self.direction.dot(delta) <= 0:
            self.direction = self._dominant_direction(delta)

        if self._blocked(self.direction):
            self.detour_target = self.direction
            self.detouring = True
            self.direction = self._pick_perpendicular(self.detour_target, delta)

    def _update_detour(self, delta: Vec) -> None:
        # Resume the original direction once it's clear; otherwise keep
        # going, turning again only if the detour itself gets blocked
        if not self._blocked(self.detour_target):
            self.direction = self.detour_target
            self.detouring = False
        elif self.direction == Vec(0, 0) or self._blocked(self.direction):
            self.direction = self._pick_perpendicular(self.detour_target, delta)

    def _dominant_direction(self, delta: Vec) -> Vec:
        if abs(delta.x) >= abs(delta.y):
            return Vec(sign(delta.x), 0)
        return Vec(0, sign(delta.y))

    def _pick_perpendicular(self, primary: Vec, delta: Vec) -> Vec:
        # Turn 90 degrees from the blocked direction, preferring the side
        # that also moves towards the target on the other axis
        if primary.x != 0:
            preferred = Vec(0, sign(delta.y)) if delta.y != 0 else Vec(0, 1)
        else:
            preferred = Vec(sign(delta.x), 0) if delta.x != 0 else Vec(1, 0)

        for direction in (preferred, -preferred, -primary):
            if direction == Vec(0, 0):
                continue
            if not self._blocked(direction):
                return direction
        return Vec(0, 0)

    def _blocked(self, direction: Vec) -> bool:
        step = self.speed * self.game.dt
        test_hitbox = RectHitbox.copy(self.hitbox, self.pos + direction * step)

        if not self._within_boundary(test_hitbox):
            return True

        for furniture in self.scene.furnitures:
            if furniture is self.target_furniture: continue
            if furniture.hitbox is None: continue
            if furniture.hitbox.size == Vec(0, 0): continue
            if test_hitbox.collides(furniture.hitbox):
                return True
        return False

    def _within_boundary(self, hitbox: RectHitbox) -> bool:
        corners = (
            hitbox.topleft, hitbox.topright,
            hitbox.bottomleft, hitbox.bottomright,
        )
        return all(
            point_in_polygon(corner, self.scene.boundary)
            for corner in corners
        )

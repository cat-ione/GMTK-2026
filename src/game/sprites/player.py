from src.core import *

from pygame.constants import K_a, K_d, K_w, K_s, K_e

if TYPE_CHECKING:
    from .item import Item
    from .interaction_target import InteractionTarget

SPEED = 50 # px/s
ITEM_RANGE = 25

class Player(Sprite["Room"]):
    update_group = UGroup.MAIN
    draw_group = DGroup.ROOM

    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)

        # Direction the player was most recently walking towards
        # (used for calculating the item to select) (8-directional)
        self.ordinal_direction = Vec(0, 1)
        # 4-directional
        self.cardinal_direction = Vec(0, 1)
        self.direction_text = "down"
        self.key_queue = []

        self._define_animations()
        self.image = self.animation.frame
        self.drawbox = RectHitbox(self.pos, self.image.size,
            Anchor.BOTTOM.offset((0, -3)))
        self.hitbox = RectHitbox(self.pos, (6, 4), Anchor.CENTER.offset((0, -1)))

        self.selected: InteractionTarget | None = None
        self.held_item: Item | None = None
        # How much to offset the held item relative to the topleft
        self.held_item_offsets = {
            "left": Vec(2, 17),
            "right": Vec(11, 17),
            "up": Vec(3, 15),
            "down": Vec(10, 17),
        }

    def update(self) -> None:
        self.vel = Vec(
            self.game.keys[K_d] - self.game.keys[K_a],
            self.game.keys[K_s] - self.game.keys[K_w],
        ).normalize() * SPEED

        # Boundary collisions
        self.pos.x += self.vel.x * self.game.dt
        self.hitbox.set_pos(self.pos)
        if not self._within_boundary():
            self.pos.x -= self.vel.x * self.game.dt
            self.hitbox.set_pos(self.pos)
        self.pos.y += self.vel.y * self.game.dt
        self.hitbox.set_pos(self.pos)
        if not self._within_boundary():
            self.pos.y -= self.vel.y * self.game.dt
            self.hitbox.set_pos(self.pos)

        self.drawbox.set_pos(self.pos)
        self.hitbox.set_pos(self.pos)

        if self.vel != Vec(0, 0):
            self.ordinal_direction = self.vel.normalize()

        for furniture in self.scene.furnitures:
            if furniture.hitbox is None: continue
            if furniture.hitbox.size == Vec(0, 0): continue
            if self.hitbox.collides(furniture.hitbox):
                self._resolve_collision(furniture.hitbox)

        self._update_animation()

        self._select()
        if self.game.keydown == K_e:
            # If selecting something, interact with it
            if self.selected is not None:
                self.selected.interact()
            # If holding an item, drop it
            elif self.held_item is not None:
                self.drop_item()

        if self.held_item is not None:
            self.held_item.update_when_held()

        watch("pos", self.pos)
        watch("vel", self.vel)
        watch("animation", self.animation.current_name)
        watch("held_item", self.held_item)
        watch("ordinal_direction", self.ordinal_direction)
        watch("cardinal_direction", self.cardinal_direction)
        watch("direction_text", self.direction_text)

    def draw(self, screen: pygame.Surface) -> None:
        # If facing up, left, or right, draw the item behind the player
        if self.ordinal_direction.y <= 0:
            self._draw_held_item(screen)

        self.image = self.animation.frame

        if self.cardinal_direction.y != 0:
            shadow = pygame.Surface((12, 8), flags=pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 40), (0, 0, 12, 8), border_radius=3)
            anchored_blit(screen, shadow, self.pos, Anchor.CENTER.offset((0, -2)))
        else:
            shadow = pygame.Surface((10, 10), flags=pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 40), (0, 0, 10, 10), border_radius=3)
            anchored_blit(screen, shadow, self.pos, Anchor.CENTER.offset((0, -1)))

        screen.blit(self.image, self.drawbox.get_rect())

        # If facing down, draw the item in front of the player
        if self.ordinal_direction.y > 0:
            self._draw_held_item(screen)

    def draw_hitbox(self, screen: pygame.Surface) -> None:
        screen.set_at(self.pos, (255, 0, 0))
        pygame.draw.rect(screen, (0, 255, 0), self.hitbox.get_rect(), 1)

    def _draw_held_item(self, screen: pygame.Surface) -> None:
        if self.held_item is None: return

        image = self.held_item.held_images[self.direction_text]
        offset = self.held_item_offsets[self.direction_text]
        anchor = self.held_item.held_anchors[self.direction_text]
        anchored_blit(screen, image, self.drawbox.topleft + offset, anchor)

    def _within_boundary(self) -> bool:
        corners = (
            self.hitbox.topleft, self.hitbox.topright,
            self.hitbox.bottomleft, self.hitbox.bottomright,
        )
        return all(
            point_in_polygon(corner, self.scene.boundary)
            for corner in corners
        )

    def _resolve_collision(self, other: RectHitbox) -> None:
        overlap_x = floor(min(self.hitbox.bottomright.x, other.bottomright.x)
            - max(self.hitbox.topleft.x, other.topleft.x))
        overlap_y = floor(min(self.hitbox.bottomright.y, other.bottomright.y)
            - max(self.hitbox.topleft.y, other.topleft.y))

        # Push out along the axis with the smaller overlap
        if overlap_x < overlap_y:
            if self.hitbox.center.x < other.center.x:
                self.pos.x -= overlap_x
            else:
                self.pos.x += overlap_x
        else:
            if self.hitbox.center.y < other.center.y:
                self.pos.y -= overlap_y
            else:
                self.pos.y += overlap_y

        self.hitbox.set_pos(self.pos)
        self.drawbox.set_pos(self.pos)

    def _select(self) -> None:
        pos = self.drawbox.center
        max_dot = -1
        closest = None
        for target in self.scene.interaction_targets:
            if target.pos.distance_to(pos) > ITEM_RANGE: continue
            # vector to the target
            facing = (target.pos - pos).normalize()
            # find the vector that's the most "straight ahead"
            dot = self.ordinal_direction.dot(facing)
            if dot < 0.8: continue # not directly in front of player
            if dot > max_dot:
                max_dot = dot
                closest = target
        self.change_selection(closest)

    def change_selection(self, new: InteractionTarget | None) -> None:
        if self.selected is not None:
            self.selected.deselect()
        self.selected = new
        if self.selected is not None:
            self.selected.select()

    def gain_item(self, new: Item) -> None:
        """Giving an item to the player out of thin air."""
        self.drop_item()
        self.held_item = new

    def pickup_item(self, new: Item) -> None:
        """Pick up an item from the ground"""
        if self.held_item is not None:
            self.held_item.set_pos(new.pos)
            self.scene.add_item(self.held_item)
        self.held_item = new
        self.scene.remove_item(new)
        self.change_selection(None)

    def drop_item(self) -> None:
        """Drop the currently held item."""
        if self.held_item is not None:
            self.held_item.set_pos(self.pos + self.ordinal_direction * 8)
            self.scene.add_item(self.held_item)
            self.held_item = None

    def _define_animations(self) -> None:
        stand_up = Animation(Spritesheet.get("player_walk_back")[:1], -1)
        stand_down = Animation(Spritesheet.get("player_walk_front")[:1], -1)
        stand_left = Animation(Spritesheet.get("player_walk_side")[:1], -1)
        stand_right = Animation(
            [pygame.transform.flip(
                Spritesheet.get("player_walk_side")[0], True, False)], -1)

        walk_up = Animation(Spritesheet.get("player_walk_back"), 0.15)
        walk_down = Animation(Spritesheet.get("player_walk_front"), 0.15)
        walk_left = Animation(Spritesheet.get("player_walk_side"), 0.15)
        walk_right = Animation(
            [pygame.transform.flip(frame, True, False)
                for frame in Spritesheet.get("player_walk_side")], 0.15)

        stand_hold_up = Animation(Spritesheet.get("player_walk_hold_back")[:1], -1)
        stand_hold_down = Animation(Spritesheet.get("player_walk_hold_front")[:1], -1)
        stand_hold_left = Animation(Spritesheet.get("player_walk_hold_side")[:1], -1)
        stand_hold_right = Animation(
            [pygame.transform.flip(
                Spritesheet.get("player_walk_hold_side")[0], True, False)], -1)

        walk_hold_up = Animation(Spritesheet.get("player_walk_hold_back"), 0.15)
        walk_hold_down = Animation(Spritesheet.get("player_walk_hold_front"), 0.15)
        walk_hold_left = Animation(Spritesheet.get("player_walk_hold_side"), 0.15)
        walk_hold_right = Animation(
            [pygame.transform.flip(frame, True, False)
                for frame in Spritesheet.get("player_walk_hold_side")], 0.15)

        self.animation = AnimationManager({
            "stand_up": stand_up,
            "stand_down": stand_down,
            "stand_left": stand_left,
            "stand_right": stand_right,
            "walk_up": walk_up,
            "walk_down": walk_down,
            "walk_left": walk_left,
            "walk_right": walk_right,
            "stand_hold_up": stand_hold_up,
            "stand_hold_down": stand_hold_down,
            "stand_hold_left": stand_hold_left,
            "stand_hold_right": stand_hold_right,
            "walk_hold_up": walk_hold_up,
            "walk_hold_down": walk_hold_down,
            "walk_hold_left": walk_hold_left,
            "walk_hold_right": walk_hold_right,
        }, "stand_down")

        self.anim_vec_mapping = {
            Vec(0, -1): "up",
            Vec(0, 1): "down",
            Vec(-1, 0): "left",
            Vec(1, 0): "right",
        }
        self.anim_key_mapping = {
            K_w: "up",
            K_s: "down",
            K_a: "left",
            K_d: "right",
        }

    def _update_animation(self) -> None:
        # This is fucking horrible
        if self.game.keys[K_a] and K_a not in self.key_queue:
            self.key_queue.append(K_a)
        elif not self.game.keys[K_a] and K_a in self.key_queue:
            self.key_queue.remove(K_a)
        if self.game.keys[K_d] and K_d not in self.key_queue:
            self.key_queue.append(K_d)
        elif not self.game.keys[K_d] and K_d in self.key_queue:
            self.key_queue.remove(K_d)
        if self.game.keys[K_w] and K_w not in self.key_queue:
            self.key_queue.append(K_w)
        elif not self.game.keys[K_w] and K_w in self.key_queue:
            self.key_queue.remove(K_w)
        if self.game.keys[K_s] and K_s not in self.key_queue:
            self.key_queue.append(K_s)
        elif not self.game.keys[K_s] and K_s in self.key_queue:
            self.key_queue.remove(K_s)

        # If the direction is one of the four cardinal directions
        if self.ordinal_direction in self.anim_vec_mapping:
            self.direction_text = self.anim_vec_mapping[self.ordinal_direction]
            self.cardinal_direction = self.ordinal_direction.copy()
        # Otherwise it's on a diagonal, in which case we find the key that was
        # first pressed sitting in the key queue
        elif self.key_queue:
            self.direction_text = self.anim_key_mapping[self.key_queue[0]]

        holding_text = "_hold" if self.held_item is not None else ""
        if self.vel == Vec(0, 0):
            self.animation.loop(f"stand{holding_text}_{self.direction_text}")
        else:
            self.animation.loop(f"walk{holding_text}_{self.direction_text}")

        self.animation.update()

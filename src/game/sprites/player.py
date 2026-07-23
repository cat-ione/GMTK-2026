from src.core import *

from pygame.constants import K_a, K_d, K_w, K_s, K_e

if TYPE_CHECKING:
    from .item import Item

SPEED = 50 # px/s
ITEM_RANGE = 15

class Player(Sprite["MainScene"]):
    update_group = UGroup.MAIN
    draw_group = DGroup.PLAYER

    def __init__(self, scene: MainScene) -> None:
        super().__init__(scene)

        self.pos = Vec(SIZE) / 2

        # Direction the player was most recently walking towards
        # (used for calculating the item to select) (8-directional)
        self.direction = Vec(0, 1)
        # 4-directional
        self.direction_text = "down"
        self.key_queue = []

        self._define_animations()
        self.image = self.animation.frame
        self.hitbox = RectHitbox(self.pos, self.image.size,
            Anchor.BOTTOM.offset((0, -3)))

        self.selected_item: Item | None = None
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
        self.pos += self.vel * self.game.dt
        self.hitbox.set_pos(self.pos)

        if self.vel != Vec(0, 0):
            self.direction = self.vel.normalize()

        self._update_animation()

        self._select_item()
        if self.game.keydown == K_e:
            # If selecting an item
            if self.selected_item is not None:
                # If selecting an item and also holding one, swap places
                if self.held_item is not None:
                    self.held_item.pos = self.selected_item.pos.copy()
                    self.scene.add_item(self.held_item)
                self.held_item = self.selected_item
                self.scene.remove_item(self.selected_item)
                self.selected_item = None
            # If holding an item, drop it in front
            elif self.held_item is not None:
                self.held_item.pos = self.pos + self.direction * 8
                self.scene.add_item(self.held_item)
                self.held_item = None

        watch("vel", self.vel)
        watch("animation", self.animation.current_name)
        watch("held_item", self.held_item)
        watch("direction", self.direction)
        watch("direction_text", self.direction_text)

    def draw(self, screen: pygame.Surface) -> None:
        # If facing up, left, or right, draw the item behind the player
        if self.direction.y <= 0:
            self._draw_held_item(screen)

        self.image = self.animation.frame
        screen.blit(self.image, self.hitbox.get_rect())

        # If facing down, draw the item in front of the player
        if self.direction.y > 0:
            self._draw_held_item(screen)

    def draw_hitbox(self, screen: pygame.Surface) -> None:
        screen.set_at(self.pos, (255, 0, 0))
        pygame.draw.rect(screen, (0, 255, 0), self.hitbox.get_rect(), 1)

    def _draw_held_item(self, screen: pygame.Surface) -> None:
        if self.held_item is None: return

        image = self.held_item.held_images[self.direction_text]
        offset = self.held_item_offsets[self.direction_text]
        anchor = self.held_item.held_anchors[self.direction_text]
        anchored_blit(screen, image, self.hitbox.topleft + offset, anchor)

    def _select_item(self) -> None:
        pos = self.hitbox.center
        max_dot = -1
        closest_item = None
        for item in self.scene.items:
            if item.pos.distance_to(pos) > ITEM_RANGE + item.image.width: continue
            item_facing = (item.pos - pos).normalize()
            dot = self.direction.dot(item_facing)
            if dot < 0.7: continue # not directly in front of player
            if dot > max_dot:
                max_dot = dot
                closest_item = item
        self.selected_item = closest_item

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

        stand_hold_up = Animation(Spritesheet.get("player_walk_back")[:1], -1)
        stand_hold_down = Animation(Spritesheet.get("player_walk_hold_front")[:1], -1)
        stand_hold_left = Animation(Spritesheet.get("player_walk_hold_side")[:1], -1)
        stand_hold_right = Animation(
            [pygame.transform.flip(
                Spritesheet.get("player_walk_hold_side")[0], True, False)], -1)

        walk_hold_up = Animation(Spritesheet.get("player_walk_back"), 0.15)
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
        if self.direction in self.anim_vec_mapping:
            self.direction_text = self.anim_vec_mapping[self.direction]
        elif self.key_queue:
            self.direction_text = self.anim_key_mapping[self.key_queue[0]]

        holding_text = "_hold" if self.held_item is not None else ""
        if self.vel == Vec(0, 0):
            self.animation.loop(f"stand{holding_text}_{self.direction_text}")
        else:
            self.animation.loop(f"walk{holding_text}_{self.direction_text}")

        self.animation.update()

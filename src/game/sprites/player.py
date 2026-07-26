from src.core import *

from pygame.constants import K_a, K_d, K_w, K_s, K_e
from .item import Chicken
from .furniture import Microwave, Fridge
from .speech_bubble import GameSpeechBubble

if TYPE_CHECKING:
    from .item import Item
    from .interaction_target import InteractionTarget

SPEED = 50 # px/s
ITEM_RANGE = 25
# angle tolerance for selecting an item, at close range vs at ITEM_RANGE
ITEM_SELECT_DOT_NEAR = 0.3
ITEM_SELECT_DOT_FAR = 0.8
# how much being close counts towards priority, relative to being lined up
# (angle contributes in [-1, 1], closeness in [0, 1] * this weight)
ITEM_SELECT_DISTANCE_WEIGHT = 1.5

class Player(Sprite["Room"]):
    update_group = UGroup.MAIN
    draw_group = DGroup.ROOM

    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)
        self.speed = SPEED

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

        # Lock movement
        self.locked = False
        self.keys = {K_a: False, K_d: False, K_w: False, K_s: False}
        self.disable_collision = False

        self.speech_bubble = None
        self.speech_timer = Timer(0)

    def update(self) -> None:
        if self.scene.cutscene is None and not self.locked:
            self.keys = {key: self.game.keys[key] for key in self.keys}
        else:
            self.keys = {K_a: False, K_d: False, K_w: False, K_s: False}
        self._move()

        if not self.disable_collision:
            for furniture in self.scene.furnitures:
                if furniture.hitbox is None: continue
                if furniture.hitbox.size == Vec(0, 0): continue
                if self.hitbox.collides(furniture.hitbox):
                    self._resolve_collision(furniture.hitbox)

        self.drawbox.set_pos(self.pos)

        if self.scene.cutscene is None:
            self._update_animation()
        self.animation.update()

        if self.scene.cutscene is None:
            self._select()
        if self.game.keydown == K_e and self.scene.cutscene is None:
            # Disallow all interactions when holding a chicken except microwave and fridge
            holding_chicken = isinstance(self.held_item, Chicken)
            is_microwave = self.selected is not None and isinstance(self.selected.owner, Microwave)
            is_fridge = self.selected is not None and isinstance(self.selected.owner, Fridge)
            if is_microwave or is_fridge or not holding_chicken:
                # If selecting something, interact with it
                if self.selected is not None:
                    self.selected.interact()
                # If holding an item, drop it
                elif self.held_item is not None:
                    self.drop_item()

        if self.held_item is not None:
            self.held_item.update_when_held()

        if self.speech_bubble is not None:
            self.speech_bubble.pos = self.pos - (0, 25)
            if self.speech_timer.done:
                self.scene.remove(self.speech_bubble)
                self.speech_bubble = None

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

        if self.animation.current_name != "sleeping":
            if self.cardinal_direction.y != 0:
                shadow = pygame.Surface((12, 8), flags=pygame.SRCALPHA)
                pygame.draw.rect(shadow, (0, 0, 0, 40), (0, 0, 12, 8), border_radius=3)
                anchored_blit(screen, shadow, self.screen_pos, Anchor.CENTER.offset((0, -2)))
            else:
                shadow = pygame.Surface((10, 10), flags=pygame.SRCALPHA)
                pygame.draw.rect(shadow, (0, 0, 0, 40), (0, 0, 10, 10), border_radius=3)
                anchored_blit(screen, shadow, self.screen_pos, Anchor.CENTER.offset((0, -1)))

        screen.blit(self.image, self.drawbox.topleft - self.scene.camera.pos)

        # If facing down, draw the item in front of the player
        if self.ordinal_direction.y > 0:
            self._draw_held_item(screen)

    def draw_hitbox(self, screen: pygame.Surface) -> None:
        screen.set_at(self.screen_pos, (255, 0, 0))
        pygame.draw.rect(screen, (0, 255, 0), self.hitbox.get_rect(-self.scene.camera.pos), 1)

    def _draw_held_item(self, screen: pygame.Surface) -> None:
        if self.held_item is None: return

        image = self.held_item.held_images[self.direction_text]
        offset = self.held_item_offsets[self.direction_text]
        anchor = self.held_item.held_anchors[self.direction_text]
        anchored_blit(screen, image, (self.drawbox.topleft + offset - self.scene.camera.pos) // 1, anchor)

    def _move(self) -> None:
        self.vel = Vec(
            self.keys[K_d] - self.keys[K_a],
            self.keys[K_s] - self.keys[K_w],
        ).normalize() * self.speed

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

        if self.vel != Vec(0, 0):
            self.ordinal_direction = self.vel.normalize()

        self.hitbox.set_pos(self.pos)

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
        overlap_x = (min(self.hitbox.bottomright.x, other.bottomright.x)
            - max(self.hitbox.topleft.x, other.topleft.x))
        overlap_y = (min(self.hitbox.bottomright.y, other.bottomright.y)
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
        best_score = None
        best = None
        for target in self.scene.interaction_targets:
            distance = target.pos.distance_to(self.pos)
            if distance > ITEM_RANGE: continue
            # vector to the target
            facing = (target.pos - self.pos).normalize()
            # find the vector that's the most "straight ahead"
            dot = self.cardinal_direction.dot(facing)
            # closer items get a more lenient angle tolerance
            t = distance / ITEM_RANGE
            min_dot = ITEM_SELECT_DOT_NEAR + (ITEM_SELECT_DOT_FAR - ITEM_SELECT_DOT_NEAR) * t
            if dot < min_dot: continue # not enough in front of player
            # combine angle and closeness into one score, so a target that's
            # very close but at a bad angle can outrank one that's further
            # away but better lined up
            closeness = 1 - distance / ITEM_RANGE
            score = dot + closeness * ITEM_SELECT_DISTANCE_WEIGHT
            if best_score is None or score > best_score:
                best_score = score
                best = target
        self.change_selection(best)

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

    def delete_item(self) -> None:
        """Simply remove the item in the player's hand."""
        self.held_item = None

    def pickup_item(self, new: Item) -> None:
        """Pick up an item from the ground"""
        if self.held_item is not None:
            self.held_item.set_pos(new.pos)
            self.scene.add_item(self.held_item)
        self.held_item = new
        self.scene.remove_item(new)
        self.change_selection(None)

    def drop_item(self, pos: VecLike | None = None) -> None:
        """Drop the currently held item."""
        if self.held_item is not None:
            if pos is None:
                pos = self.pos + self.ordinal_direction * 8
            self.held_item.set_pos(pos)
            self.scene.add_item(self.held_item)
            self.held_item.drop()
            self.held_item = None

    def say(self, text: str, anchor: Anchor = Anchor.BOTTOM) -> GameSpeechBubble:
        if self.speech_bubble is not None:
            self.scene.remove(self.speech_bubble)
        self.speech_bubble = GameSpeechBubble(self.scene, self.pos - (0, 25), text, 80, anchor)
        self.scene.add(self.speech_bubble)
        self.speech_timer.reset(3 + len(text.split()) * 0.3)
        return self.speech_bubble

    def _define_animations(self) -> None:
        still_up = Animation(Spritesheet.get("player_idle_back")[:1], -1)
        still_down = Animation(Spritesheet.get("player_idle_front")[:1], -1)
        still_left = Animation(Spritesheet.get("player_idle_side")[:1], -1)
        still_right = Animation(
            [pygame.transform.flip(
                Spritesheet.get("player_idle_side")[0], True, False)], -1)

        idle_up = Animation(Spritesheet.get("player_idle_back"), 0.5)
        idle_down = Animation(Spritesheet.get("player_idle_front"), 0.5)
        idle_left = Animation(Spritesheet.get("player_idle_side"), 0.5)
        idle_right = Animation(
            [pygame.transform.flip(frame, True, False)
                for frame in Spritesheet.get("player_idle_side")], 0.5)

        walk_up = Animation(Spritesheet.get("player_walk_back"), 0.15)
        walk_down = Animation(Spritesheet.get("player_walk_front"), 0.15)
        walk_left = Animation(Spritesheet.get("player_walk_side"), 0.15)
        walk_right = Animation(
            [pygame.transform.flip(frame, True, False)
                for frame in Spritesheet.get("player_walk_side")], 0.15)

        idle_hold_up = Animation(Spritesheet.get("player_walk_hold_back")[:1], -1)
        idle_hold_down = Animation(Spritesheet.get("player_walk_hold_front")[:1], -1)
        idle_hold_left = Animation(Spritesheet.get("player_walk_hold_side")[:1], -1)
        idle_hold_right = Animation(
            [pygame.transform.flip(
                Spritesheet.get("player_walk_hold_side")[0], True, False)], -1)

        walk_hold_up = Animation(Spritesheet.get("player_walk_hold_back"), 0.15)
        walk_hold_down = Animation(Spritesheet.get("player_walk_hold_front"), 0.15)
        walk_hold_left = Animation(Spritesheet.get("player_walk_hold_side"), 0.15)
        walk_hold_right = Animation(
            [pygame.transform.flip(frame, True, False)
                for frame in Spritesheet.get("player_walk_hold_side")], 0.15)

        sleeping = Animation(Spritesheet.get("player_sleeping"), 0.25)
        phone_1 = Animation(Spritesheet.get("player_phone")[:1], 4)
        phone_2 = Animation(Spritesheet.get("player_phone")[1:], -1)

        self.animation = AnimationManager({
            "still_up": still_up,
            "still_down": still_down,
            "still_left": still_left,
            "still_right": still_right,
            "idle_up": idle_up,
            "idle_down": idle_down,
            "idle_left": idle_left,
            "idle_right": idle_right,
            "walk_up": walk_up,
            "walk_down": walk_down,
            "walk_left": walk_left,
            "walk_right": walk_right,
            "idle_hold_up": idle_hold_up,
            "idle_hold_down": idle_hold_down,
            "idle_hold_left": idle_hold_left,
            "idle_hold_right": idle_hold_right,
            "walk_hold_up": walk_hold_up,
            "walk_hold_down": walk_hold_down,
            "walk_hold_left": walk_hold_left,
            "walk_hold_right": walk_hold_right,
            "sleeping": sleeping,
            "phone_1": phone_1,
            "phone_2": phone_2,
        }, "idle_down")

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
        if self.keys[K_a] and K_a not in self.key_queue:
            self.key_queue.append(K_a)
        elif not self.keys[K_a] and K_a in self.key_queue:
            self.key_queue.remove(K_a)
        if self.keys[K_d] and K_d not in self.key_queue:
            self.key_queue.append(K_d)
        elif not self.keys[K_d] and K_d in self.key_queue:
            self.key_queue.remove(K_d)
        if self.keys[K_w] and K_w not in self.key_queue:
            self.key_queue.append(K_w)
        elif not self.keys[K_w] and K_w in self.key_queue:
            self.key_queue.remove(K_w)
        if self.keys[K_s] and K_s not in self.key_queue:
            self.key_queue.append(K_s)
        elif not self.keys[K_s] and K_s in self.key_queue:
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
            self.animation.loop(f"idle{holding_text}_{self.direction_text}")
        else:
            self.animation.loop(f"walk{holding_text}_{self.direction_text}")

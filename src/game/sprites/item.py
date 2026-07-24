from src.core import *

from .interaction_target import InteractionTarget

class Item(Sprite["Room"]):
    update_group = UGroup.MAIN
    draw_group = DGroup.ROOM

    def __init__(self,
        scene: Room,
        pos: VecLike,
        world_image: pygame.Surface,
        held_image_front: pygame.Surface | None = None,
        held_image_back: pygame.Surface | None = None,
        held_image_side: pygame.Surface | None = None,
        held_front_anchor: AnchorType | None = None,
        held_back_anchor: AnchorType | None = None,
        held_left_anchor: AnchorType | None = None,
        held_right_anchor: AnchorType | None = None,
    ) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)

        self._process_images_and_anchors(
            world_image,
            held_image_front, held_image_back, held_image_side,
            held_front_anchor, held_back_anchor,
            held_left_anchor, held_right_anchor,
        )
        self.image = world_image

        self.outline = self._get_outline()

        self.interaction_target = InteractionTarget(scene, self.pos, self)
        self.selected = False

    def update(self) -> None:
        pass

    def select(self) -> None:
        self.selected = True

    def deselect(self) -> None:
        self.selected = False

    def interact(self) -> None:
        self.scene.player.pickup_item(self)

    def update_when_held(self) -> None:
        pass

    def set_pos(self, new: VecLike) -> None:
        self.pos = Vec(new)
        self.interaction_target.pos = Vec(new)

    def draw(self, screen: pygame.Surface) -> None:
        draw_pos = self.pos - Vec(self.image.size) / 2

        # Draw outline behind the actual sprite
        if self.selected:
            screen.blit(self.outline, draw_pos - (1, 1))

        screen.blit(self.image, draw_pos)

    def draw_hitbox(self, screen: pygame.Surface) -> None:
        screen.set_at(self.pos, (255, 0, 0))

    def _get_outline(self) -> pygame.Surface:
        mask = pygame.mask.from_surface(self.image)
        mask_surf = mask.to_surface(
            setcolor=(255, 255, 255),
            unsetcolor=(0, 0, 0)
        )
        mask_surf.set_colorkey((0, 0, 0))
        surface = pygame.Surface(Vec(mask_surf.size) + (2, 2))
        surface.blit(mask_surf, (0, 1))
        surface.blit(mask_surf, (1, 0))
        surface.blit(mask_surf, (1, 2))
        surface.blit(mask_surf, (2, 1))
        surface.set_colorkey((0, 0, 0))
        return surface

    def _process_images_and_anchors(self,
        world_image: pygame.Surface,
        held_image_front: pygame.Surface | None,
        held_image_back: pygame.Surface | None,
        held_image_side: pygame.Surface | None,
        held_front_anchor: AnchorType | None,
        held_back_anchor: AnchorType | None,
        held_left_anchor: AnchorType | None,
        held_right_anchor: AnchorType | None,
    ) -> None:
        self.world_image = world_image

        if held_image_front is None:
            self.held_image_front = self.world_image
        else:
            self.held_image_front = held_image_front
        if held_image_back is None:
            self.held_image_back = self.held_image_front
        else:
            self.held_image_back = held_image_back
        if held_image_side is None:
            self.held_image_left = self.held_image_front
        else:
            self.held_image_left = held_image_side
        self.held_image_right = pygame.transform.flip(self.held_image_left, True, False)

        if held_front_anchor is None:
            self.held_front_anchor = Anchor.CENTER
        else:
            self.held_front_anchor = held_front_anchor
        if held_back_anchor is None:
            self.held_back_anchor = self.held_front_anchor
        else:
            self.held_back_anchor = held_back_anchor
        if held_left_anchor is None:
            self.held_left_anchor = self.held_front_anchor
        else:
            self.held_left_anchor = held_left_anchor
        if held_right_anchor is None:
            self.held_right_anchor = self.held_left_anchor
        else:
            self.held_right_anchor = held_right_anchor

        self.held_images = {
            "left": self.held_image_left,
            "right": self.held_image_right,
            "up": self.held_image_back,
            "down": self.held_image_front,
        }
        self.held_anchors = {
            "left": self.held_left_anchor,
            "right": self.held_right_anchor,
            "up": self.held_back_anchor,
            "down": self.held_front_anchor,
        }

class TestItem(Item):
    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(scene, pos, Image.get("test_item"))

class Vacuum(Item):
    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(
            scene, pos,
            Image.get("vacuum_world"),
            held_image_front=Image.get("vacuum_front"),
            held_image_side=Image.get("vacuum_side"),
            held_front_anchor=Anchor.TOP,
            held_left_anchor=Anchor.TOPLEFT.offset((8, 2)),
            held_right_anchor=Anchor.TOPLEFT.offset((0, 2)),
        )
        self.offsets = {
            "left": Vec(-13, 2),
            "right": Vec(12, 2),
            "up": Vec(-3, -8),
            "down": Vec(2, 3),
        }

    def update_when_held(self) -> None:
        player = self.scene.player
        for dust in self.scene.dusts.copy():
            pos = player.pos + self.offsets[player.direction_text]
            if pos.distance_to(dust.pos) < 4:
                self.scene.remove_dust(dust)

class Plate(Item):
    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(
            scene, pos,
            Image.get("plate"),
        )

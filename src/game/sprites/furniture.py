from src.core import *

from .interaction_target import InteractionTarget
from .item import Plate

class Furniture(Sprite["Room"]):
    draw_group = DGroup.ROOM

    def __init__(self,
        scene: Room,
        pos: VecLike,
        image: pygame.Surface,
        hitbox: list[int] | None
    ) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)
        self.image = image
        if hitbox is not None:
            self.hitbox = RectHitbox(
                self.pos + hitbox[:2],
                (hitbox[2], hitbox[3]),
                Anchor.TOPLEFT,
            )
        else:
            self.hitbox = None
        self.drawbox = RectHitbox(self.pos, self.image.size, Anchor.TOPLEFT)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.screen_pos)

    def draw_hitbox(self, screen: pygame.Surface) -> None:
        if self.hitbox is None: return
        pygame.draw.rect(screen, (0, 255, 255), self.hitbox.get_rect(-self.scene.camera.pos), 1)

class InteractableFurniture(Furniture):
    def __init__(self,
        scene: Room,
        pos: VecLike,
        image: pygame.Surface,
        hitbox: list[int] | None
    ) -> None:
        super().__init__(scene, pos, image, hitbox)

        pos = self.hitbox.center if self.hitbox is not None else self.pos + Vec(self.image.size) / 2
        self.interaction_target = InteractionTarget(scene, pos, self)
        self.selected = False
        self.outline = self._get_outline()

    def select(self) -> None:
        self.selected = True

    def deselect(self) -> None:
        self.selected = False

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

    def draw(self, screen: pygame.Surface) -> None:
        if self.selected:
            screen.blit(self.outline, self.screen_pos - (1, 1))

        super().draw(screen)

    def interact(self) -> None:
        # Implement in subclass
        pass

class StackOfPlates(InteractableFurniture):
    def __init__(self, scene: Room, pos: VecLike, image: pygame.Surface, hitbox: list[int] | None) -> None:
        super().__init__(scene, pos, image, hitbox)
        self.remaining_plates = 6

    def interact(self) -> None:
        plate = Plate(self.scene, (0, 0))
        self.scene.player.gain_item(plate)
        self.remaining_plates -= 1
        if self.remaining_plates == 0:
            self.scene.remove_furniture(self)
        else:
            self.image = Image.get(f"stack_of_plates_{self.remaining_plates}")
            self.outline = self._get_outline()

class BedroomDoor(InteractableFurniture):
    def interact(self) -> None:
        new_scene = self.scene.game_data.bedroom
        self.scene.player.scene = new_scene
        self.scene.camera.scene = new_scene

        rel_pos = self.scene.camera.pos - self.scene.player.pos
        self.scene.player.pos = Vec(36, 30)
        self.scene.camera.pos = self.scene.player.pos + rel_pos

        self.game.set_scene(new_scene)

class LivingRoomDoor(InteractableFurniture):
    def interact(self) -> None:
        new_scene = self.scene.game_data.living_room
        self.scene.player.scene = new_scene
        self.scene.camera.scene = new_scene

        rel_pos = self.scene.camera.pos - self.scene.player.pos
        self.scene.player.pos = Vec(36, 82)
        self.scene.camera.pos = self.scene.player.pos + rel_pos

        self.game.set_scene(new_scene)

class BathroomDoor(InteractableFurniture):
    def interact(self) -> None:
        new_scene = self.scene.game_data.bathroom
        self.scene.player.scene = new_scene
        self.scene.camera.scene = new_scene

        rel_pos = self.scene.camera.pos - self.scene.player.pos
        self.scene.player.pos = Vec(10, 68)
        self.scene.camera.pos = self.scene.player.pos + rel_pos

        self.game.set_scene(new_scene)

class BedroomDoor2(InteractableFurniture):
    def interact(self) -> None:
        new_scene = self.scene.game_data.bedroom
        self.scene.player.scene = new_scene
        self.scene.camera.scene = new_scene

        rel_pos = self.scene.camera.pos - self.scene.player.pos
        self.scene.player.pos = Vec(67, 55)
        self.scene.camera.pos = self.scene.player.pos + rel_pos

        self.game.set_scene(new_scene)

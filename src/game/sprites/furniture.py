from src.core import *

from .interaction_target import InteractionTarget
from .item import Plate
from .hamster import HamsterItem
from .item import Chicken

class Furniture(Sprite["Room"]):
    draw_group = DGroup.ROOM

    def __init__(self,
        scene: Room,
        name: str,
        pos: VecLike,
        image: pygame.Surface,
        hitbox: list[int] | None
    ) -> None:
        super().__init__(scene)
        self.name = name

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

    def get_pos(self) -> Vec:
        """Get hitbox position if has hitbox, otherwise just center pos"""
        if self.hitbox is not None:
            return self.hitbox.center
        else:
            return self.pos + Vec(self.image.size) / 2

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.screen_pos)

    def draw_hitbox(self, screen: pygame.Surface) -> None:
        if self.hitbox is None: return
        pygame.draw.rect(screen, (0, 255, 255), self.hitbox.get_rect(-self.scene.camera.pos), 1)

class InteractableFurniture(Furniture):
    def __init__(self,
        scene: Room,
        name: str,
        pos: VecLike,
        image: pygame.Surface,
        hitbox: list[int] | None
    ) -> None:
        super().__init__(scene, name, pos, image, hitbox)

        pos = self.get_pos()
        self.interaction_target = InteractionTarget(scene, pos, self)
        self.selected = False
        self.outline = outline(self.image, (255, 255, 255))

    def select(self) -> None:
        self.selected = True

    def deselect(self) -> None:
        self.selected = False

    def draw(self, screen: pygame.Surface) -> None:
        if self.selected:
            screen.blit(self.outline, self.screen_pos - (1, 1))

        super().draw(screen)

    def interact(self) -> None:
        # Implement in subclass
        pass

class StackOfPlates(InteractableFurniture):
    def __init__(self, scene: Room, name: str, pos: VecLike, image: pygame.Surface, hitbox: list[int] | None) -> None:
        super().__init__(scene, name, pos, image, hitbox)
        self.remaining_plates = 6

    def interact(self) -> None:
        plate = Plate(self.scene, (0, 0))
        self.scene.player.gain_item(plate)
        self.remaining_plates -= 1
        if self.remaining_plates == 0:
            self.scene.remove_furniture(self)
        else:
            self.image = Image.get(f"stack_of_plates_{self.remaining_plates}")
            self.outline = outline(self.image, (255, 255, 255))

class Door(InteractableFurniture):
    room: str
    target_pos: VecLike

    def interact(self) -> None:
        new_scene = getattr(self.scene.game_data, self.room)
        self.scene.player.scene = new_scene
        self.scene.camera.scene = new_scene
        if self.scene.player.held_item is not None:
            self.scene.player.held_item.scene = new_scene

        rel_pos = self.scene.camera.pos - self.scene.player.pos
        self.scene.player.pos = Vec(self.target_pos)
        self.scene.camera.pos = self.scene.player.pos + rel_pos

        self.game.set_scene(new_scene)

class BedroomDoor(Door):
    room = "bedroom"
    target_pos = (36, 30)

class LivingRoomDoor(Door):
    room = "living_room"
    target_pos = (36, 82)

class BathroomDoor(Door):
    room = "bathroom"
    target_pos = (10, 68)

class BedroomDoor2(Door):
    room = "bedroom"
    target_pos = (67, 55)

class Fridge(InteractableFurniture):
    update_group = UGroup.MAIN

    def __init__(self, scene: Room, name: str, pos: VecLike, image: pygame.Surface, hitbox: list[int] | None) -> None:
        super().__init__(scene, name, pos, image, hitbox)
        self.chicken = Chicken(self.scene, pos)
        self.open_timer = Timer(1, True)
        self.freeze_timer = LoopTimer(6, True)

    def update(self) -> None:
        if self.open_timer.done:
            self.image = Image.get("fridge_closed")
            self.open_timer.reset()
            self.open_timer.pause()
            self.scene.player.locked = False

            if self.chicken is not None:
                self.scene.player.gain_item(self.chicken)
                self.chicken = None
            elif isinstance(self.scene.player.held_item, Chicken):
                self.chicken = self.scene.player.held_item
                self.scene.player.delete_item()
                self.freeze_timer.reset()

        if self.chicken is not None:
            if self.freeze_timer.done:
                if self.chicken.temperature > -18:
                    self.chicken.temperature -= 1
            watch("chicken_temp", self.chicken.temperature)

    def interact(self) -> None:
        self.image = Image.get("fridge_opened")
        self.open_timer.reset()
        self.scene.player.locked = True

class Microwave(InteractableFurniture):
    update_group = UGroup.MAIN

    def __init__(self, scene: Room, name: str, pos: VecLike, image: pygame.Surface, hitbox: list[int] | None) -> None:
        super().__init__(scene, name, pos, image, hitbox)
        self.chicken = None
        self.open_timer = Timer(1, True)
        self.heat_timer = LoopTimer(4, True)

    def update(self) -> None:
        if self.open_timer.done:
            self.image = Image.get("microwave_closed")
            self.open_timer.reset()
            self.open_timer.pause()
            self.scene.player.locked = False

            if self.chicken is not None:
                self.scene.player.gain_item(self.chicken)
                self.chicken = None
            elif isinstance(self.scene.player.held_item, Chicken):
                self.chicken = self.scene.player.held_item
                self.scene.player.delete_item()
                self.heat_timer.reset()

        if self.chicken is not None:
            if self.heat_timer.done:
                self.chicken.temperature += 1
            watch("chicken_temp", self.chicken.temperature)

    def interact(self) -> None:
        self.image = Image.get("microwave_opened")
        self.open_timer.reset()
        self.scene.player.locked = True

class RiceCooker(InteractableFurniture):
    def interact(self) -> None:
        info("interacted with rice cooker")

class Tablecloth(InteractableFurniture):
    def __init__(self, scene: Room, name: str, pos: VecLike, image: pygame.Surface, hitbox: list[int] | None) -> None:
        super().__init__(scene, name, pos, image, hitbox)
        self.item = None

    def interact(self) -> None:
        if self.item is not None:
            item = self.item
            self.item = self.scene.player.held_item
            self.scene.player.pickup_item(item)
        elif self.scene.player.held_item is not None:
            self.item = self.scene.player.held_item
            self.scene.player.drop_item(self.get_pos())

    def has_plate(self) -> bool:
        return isinstance(self.item, Plate)

class HamsterCage(InteractableFurniture):
    def interact(self) -> None:
        if isinstance(self.scene.player.held_item, HamsterItem):
            self.scene.player.delete_item()

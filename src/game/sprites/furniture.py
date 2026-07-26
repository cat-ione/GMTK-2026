from src.core import *

from .interaction_target import InteractionTarget
from .item import Plate
from .hamster import HamsterItem
from .item import Chicken
from .thermometer import Thermometer, ThermometerIcons
from .bathtub_handle import BathtubHandle

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

        if self.scene.game_data.first_play and self.selected:
            screen.blit(Image.get("key_hint_e"), self.screen_pos + (self.image.width - 3, -5))

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
        self.scene.clipboard.scene = new_scene
        self.scene.mom_slider.scene = new_scene
        if self.scene.player.speech_bubble is not None:
            self.scene.remove(self.scene.player.speech_bubble)
            new_scene.add(self.scene.player.speech_bubble)

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

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)
        screen.blit(Image.get("door_icon"), self.screen_pos + (7, 3))

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
                self.chicken.spawn_thermometer()
                self.chicken = None
            elif isinstance(self.scene.player.held_item, Chicken):
                self.chicken = self.scene.player.held_item
                self.scene.player.delete_item()
                self.chicken.remove_thermometer()
                self.freeze_timer.reset()

            if self.scene.game_data.first_play and not self.scene.have_done_chicken: # type: ignore
                self.scene.player.say("Into the microwave it goes!")
                self.scene.have_done_chicken = True # type: ignore

        if self.chicken is not None:
            if self.freeze_timer.done:
                if self.chicken.temperature > -18:
                    self.chicken.temperature -= 1
                    perc = 1 - abs(self.chicken.temperature - 22) / 40
                    self.scene.game_data.scores["chicken"] = int(perc * self.scene.game_data.max_scores["chicken"])
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
                self.chicken.spawn_thermometer()
                if self.scene.game_data.first_play and not self.scene.have_done_chicken_3: # type: ignore
                    if self.chicken.temperature < 22:
                        self.scene.player.say("Still cold... better put it back in.")
                    else:
                        self.scene.player.say("Too warm! Let's throw it back into the freezer to cool it down.")
                        self.scene.have_done_chicken_3 = True # type: ignore
                self.chicken = None
            elif isinstance(self.scene.player.held_item, Chicken):
                self.chicken = self.scene.player.held_item
                self.scene.player.delete_item()
                self.chicken.remove_thermometer()
                self.heat_timer.reset()
                if self.scene.game_data.first_play and not self.scene.have_done_chicken_2: # type: ignore
                    self.scene.player.say("Gotta make sure I don't over-defrost it... I should check on it soon.")
                    self.scene.have_done_chicken_2 = True # type: ignore

        if self.chicken is not None:
            if self.heat_timer.done:
                if self.chicken.temperature < 40:
                    self.chicken.temperature += 1
                    perc = 1 - abs(self.chicken.temperature - 22) / 40
                    self.scene.game_data.scores["chicken"] = int(perc * self.scene.game_data.max_scores["chicken"])
            watch("chicken_temp", self.chicken.temperature)

    def interact(self) -> None:
        self.image = Image.get("microwave_opened")
        self.open_timer.reset()
        self.scene.player.locked = True

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
            if isinstance(self.item, Plate):
                self.item.on_table = True

    def has_plate(self) -> bool:
        return isinstance(self.item, Plate)

class HamsterCage(InteractableFurniture):
    def interact(self) -> None:
        if isinstance(self.scene.player.held_item, HamsterItem):
            self.scene.player.delete_item()
            self.scene.game_data.scores["hamsters"] += 4

class Bathtub(InteractableFurniture):
    update_group = UGroup.MAIN

    def __init__(self, scene: Room, name: str, pos: VecLike, image: pygame.Surface, hitbox: list[int] | None) -> None:
        super().__init__(scene, name, pos, image, hitbox)
        self.current_temp = 18
        self.new_temp = 18
        self.fullness = 0
        self.on = False
        self.full = False
        self.fill_timer = LoopTimer(1.5)
        self.stop_timer = Timer(30, True)
        self.locked = False
        self.animation = None

    def update(self) -> None:
        if self.fill_timer.done and self.on and not self.full:
            _sum = self.current_temp * self.fullness + self.new_temp
            self.fullness += 1
            self.current_temp = _sum / self.fullness
            if self.fullness == 33:
                self.animation = Animation(Spritesheet.get("bathtub_medium"), 0.1)
            elif self.fullness == 67:
                self.animation = Animation(Spritesheet.get("bathtub_full"), 0.1)
            elif self.fullness == 100:
                self.image = Image.get("bathtub_full")
                self.on = False
                self.full = True
                self.animation = None
                perc = 1 - abs(self.current_temp - 36) / 26
                self.scene.game_data.scores["bathtub"] = int(perc * self.scene.game_data.max_scores["bathtub"])

        if self.stop_timer.done:
            self.on = False
            self.animation = None
            if self.fullness < 33:
                self.image = Image.get("bathtub_shallow")
            elif self.fullness < 67:
                self.image = Image.get("bathtub_medium")
            else:
                self.image = Image.get("bathtub_full")

        if self.animation is not None:
            self.animation.update()
            if self.animation.done:
                self.animation.reset()
            self.image = self.animation.frame

        watch("bath_fullness", self.fullness)
        watch("bath_current_temp", self.current_temp)
        watch("bath_new_temp", self.new_temp)

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)

        screen.blit(Image.get("bathtub_indicator"), self.screen_pos + (11, 53))
        h = int(self.fullness / 100 * 6)
        pygame.draw.rect(screen, COLOR3, (self.screen_pos + (12, 60 - h), (1, h)))

    def select(self) -> None:
        super().select()
        self.spawn_thermometer()

    def deselect(self) -> None:
        super().deselect()
        self.remove_thermometer()

    def interact(self) -> None:
        if not self.locked:
            if self.full:
                self.scene.player.say("It's full!")
            if not self.on and not self.full:
                self.scene.player.locked = True
                self.handle = BathtubHandle(self.scene, self.pos + (13, 5))
                self.scene.add(self.handle)
                self.locked = True
                if self.scene.game_data.first_play and self.scene.first_bath_interaction: # type: ignore
                    self.scene.player.say("Now... gotta get this funky faucet to just the right temperature.", Anchor.BOTTOMRIGHT)
                    self.scene.first_bath_interaction = False # type: ignore
        else:
            if self.game.keydown == pygame.K_e:
                # Range from 10 to 62, 36 in the middle
                self.new_temp = round(10 + self.handle.progress * 52)
            self.scene.player.locked = False
            self.scene.remove(self.handle)
            if self.fullness < 33:
                self.animation = Animation(Spritesheet.get("bathtub_shallow"), 0.1)
            elif self.fullness < 67:
                self.animation = Animation(Spritesheet.get("bathtub_medium"), 0.1)
            elif self.fullness < 100:
                self.animation = Animation(Spritesheet.get("bathtub_full"), 0.1)
            self.on = True
            self.stop_timer.reset()
            self.locked = False
            if self.scene.game_data.first_play and self.scene.first_bath_interaction_2: # type: ignore
                if self.new_temp > 36:
                    self.scene.player.say("WOW! First try! I will come back later to fill it up more since the faucet stops after 30 seconds.", Anchor.BOTTOMRIGHT)
                elif self.new_temp > 36:
                    self.scene.player.say("Too hot. I can come back later to add some cold water when the faucet stops in 30 seconds.", Anchor.BOTTOMRIGHT)
                elif self.new_temp < 36:
                    self.scene.player.say("Too cold. I can come back later to add some hot water when the faucet stops in 30 seconds.", Anchor.BOTTOMRIGHT)
                self.scene.first_bath_interaction_2 = False # type: ignore

    def spawn_thermometer(self) -> None:
        img = Image.get("thermometer")
        self.current_thermometer = Thermometer(self.scene, (WIDTH - img.width - 4, HEIGHT - img.height - 4), self.current_temp, 36)
        self.scene.add(self.current_thermometer)
        self.new_thermometer = Thermometer(self.scene, (WIDTH - img.width * 2 - 4, HEIGHT - img.height - 4), self.new_temp, 36)
        self.scene.add(self.new_thermometer)
        self.icons = ThermometerIcons(self.scene)
        self.scene.add(self.icons)

    def remove_thermometer(self) -> None:
        self.scene.remove(self.current_thermometer)
        self.scene.remove(self.new_thermometer)
        self.scene.remove(self.icons)

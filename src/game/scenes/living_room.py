from src.core import *

from .room import Room
from src.game.sprites.furniture import StackOfPlates, BedroomDoor, Fridge, Microwave, RiceCooker, Tablecloth
from src.game.sprites.dust import Dust
from src.game.sprites.player import Player
from src.game.sprites.vacuum import Vacuum
from .game_data import GameData
from src.game.sprites.camera import Camera
from src.game.cutscenes.hamster_cutscene import HamsterCutscene
from src.game.cutscenes.opening_cutscene import OpeningCutscene
from src.game.sprites.clipboard import Clipboard
from src.game.sprites.item import Chicken
from src.game.sprites.mom_slider import MomSlider

class LivingRoom(Room):
    def __init__(self, game: Game) -> None:
        super().__init__(game, None, "living_room")

        self.set_boundary([(0, 29), (212, 29), (212, 139), (138, 139), (138, 86), (0, 86)])
        self.set_interactable_furniture({
            "stack_of_plates_6": StackOfPlates,
            "door": BedroomDoor,
            "fridge": Fridge,
            "microwave": Microwave,
            "rice_cooker": RiceCooker,
            "tablecloth": Tablecloth,
        })
        self.load_furniture()

        self.microwave = cast(Microwave, self.find_furniture("microwave"))
        self.fridge = cast(Fridge, self.find_furniture("fridge"))
        self.chicken = cast(Chicken, self.fridge.chicken)
        self.tablecloths = cast(list[Tablecloth], self.find_all_furniture("tablecloth"))

        self._spawn_dust()

        vacuum = Vacuum(self, (21, 30))
        self.add_item(vacuum)

        self.player = Player(self, (98, 37))
        self.add(self.player)
        self.camera = Camera(self)
        self.add(self.camera)
        self.camera.center_on(self.player.pos)

        self.clipboard = Clipboard(self)
        self.mom_slider = MomSlider(self)
        self.add(self.mom_slider)

        self.game_data = GameData(game, self)

        self.fade_opacity = 255
        self.fading = True
        self.fade_overlay = pygame.Surface(SIZE)
        self.opening_cutscene = OpeningCutscene(self)
        self.zooming = False
        self.start_cutscene(self.opening_cutscene)

        self.hamster_cs_timer = Timer(30, True)
        self.hamster_cutscene = HamsterCutscene(self)

        # Tutorial specific vars
        self.have_done_plate = False
        self.have_done_chicken = False # pulling out of the fridge
        self.have_done_chicken_2 = False # putting into the microwave
        self.have_done_chicken_3 = False # pulling out of microwave

    def update(self) -> None:
        super().update()

        if self.hamster_cs_timer.done \
            and 70 < self.player.pos.x < 130 \
            and 43 < self.player.pos.y < 75 \
            and not isinstance(self.player.held_item, Chicken):
            self.hamster_cs_timer.reset()
            self.hamster_cs_timer.pause()
            self.start_cutscene(self.hamster_cutscene)

        if len(self.dusts) == 0:
            self.clipboard.cross_out("vacuum")
        else:
            self.clipboard.uncross("vacuum")

        if all((tablecloth.has_plate() for tablecloth in self.tablecloths)):
            self.clipboard.cross_out("plates")
            if not self.have_done_plate and self.game_data.first_play and not self.have_done_chicken:
                self.player.say("Whew! That was quick... Time to defrost the chicken in the fridge!")
                self.have_done_plate = True
        else:
            self.clipboard.uncross("plates")

        self.game_data.bathroom.bathtub.update()

        self.game_data.game_time = time.time() - self.game_data.start_time
        if self.game_data.first_play:
            if int(self.game_data.game_time) == 1:
                self.player.say("We only have a few minutes! Lets get going by setting the dining table with plates first!")

    def _spawn_dust(self) -> None:
        min_x = int(min(x for x, _ in self.boundary))
        max_x = int(max(x for x, _ in self.boundary))
        min_y = int(min(y for _, y in self.boundary))
        max_y = int(max(y for _, y in self.boundary))

        for _ in range(200):
            valid = False
            pos = Vec(0, 0)
            while not valid:
                pos = Vec(randint(min_x, max_x), randint(min_y, max_y))
                if not self.contains_point(pos, margin=2): continue
                for furniture in self.furnitures:
                    if furniture.drawbox is None: continue
                    if furniture.drawbox.collides_point(pos, margin=2):
                        break
                else:
                    valid = True
            self.add_dust(Dust(self, pos))

    def go_to_bedroom(self) -> None:
        self.game.set_scene(self.game_data.bedroom)

    def draw(self, screen: pygame.Surface) -> None:
        if self.zooming:
            ss = pygame.transform.scale_by(self._screenshot, self._scale)
            screen.blit(ss, self._pos)
            self._call_animation.update()
            if self._call_animation.done:
                self._call_animation.reset()
            screen.blit(self._call_animation.frame, self._anim_pos)
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, 8))
            pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT - 8, WIDTH, 8))

            self.sprite_manager.d_groups[DGroup.HUD].draw(screen)
        else:
            super().draw(screen)

        self.fade_overlay.set_alpha(int(self.fade_opacity))
        screen.blit(self.fade_overlay)
        if self.fading and self.fade_opacity > 0:
            self.fade_opacity -= 0.6

    def fade_in(self) -> None:
        self.fade_opacity = 255
        self.fading = True

    def start_zoom_in(self) -> None:
        self.zooming = True
        self._screenshot = pygame.Surface(SIZE)
        self._screenshot.blit(self.game.px_screen)
        self._scale = 1
        self._pos = Vec(0, 0)
        self._call_animation = Animation(Spritesheet.get("call_animation_mom"), 0.1)
        self._anim_pos = Vec(WIDTH, 8)

    def zoom_in(self, pos: Vec, scale: int, progress: float) -> None:
        p1 = tween.easeOutElastic(progress, 0.6, 0.3)
        self._pos = -pos * self._scale * p1
        self._scale = 1 + (scale - 1) * p1
        p2 = tween.easeInBounce(1 - min(1, progress * 3))
        self._anim_pos.x = (WIDTH / 2 + 10) + (WIDTH / 2 - 10) * p2

    def zoom_out(self, pos: Vec, scale: int, progress: float) -> None:
        p1 = tween.easeInOutQuint(progress)
        self._pos = -pos * self._scale * p1
        self._scale = 1 + (scale - 1) * p1
        p2 = tween.easeInOutQuint(1 - progress)
        self._anim_pos.x = (WIDTH / 2 + 10) + (WIDTH / 2 - 10) * p2

    def end_zoom_out(self) -> None:
        self.zooming = False
        self.hamster_cs_timer.resume()

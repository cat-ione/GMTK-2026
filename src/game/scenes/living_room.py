from src.core import *

from .room import Room
from src.game.sprites.furniture import StackOfPlates, BedroomDoor, Fridge, Microwave, RiceCooker, Tablecloth
from src.game.sprites.dust import Dust
from src.game.sprites.player import Player
from src.game.sprites.vacuum import Vacuum
from .game_data import GameData
from src.game.sprites.camera import Camera
from src.game.cutscenes.hamster_cutscene import HamsterCutscene
from src.game.sprites.clipboard import Clipboard

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

        self.microwave = self.find_furniture("microwave")
        self.fridge = self.find_furniture("fridge")
        self.tablecloths = cast(list[Tablecloth], self.find_all_furniture("tablecloth"))

        self._spawn_dust()

        vacuum = Vacuum(self, (21, 30))
        self.add_item(vacuum)

        self.player = Player(self, (105, 42))
        self.add(self.player)
        self.camera = Camera(self)
        self.add(self.camera)
        self.camera.center_on(self.player.pos)

        self.clipboard = Clipboard(self)

        self.game_data = GameData(game, self)

        self.hamster_cs_timer = Timer(8)
        self.hamster_cutscene = HamsterCutscene(self)

    def update(self) -> None:
        super().update()

        if self.hamster_cs_timer.done:
            self.hamster_cs_timer.reset()
            self.hamster_cs_timer.pause()
            self.start_cutscene(self.hamster_cutscene)

        if len(self.dusts) == 0:
            self.clipboard.cross_out("vacuum")
        else:
            self.clipboard.uncross("vacuum")

        if all((tablecloth.has_plate() for tablecloth in self.tablecloths)):
            self.clipboard.cross_out("plates")
        else:
            self.clipboard.uncross("plates")

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

from src.core import *

from .room import Room
from src.game.sprites.item import Vacuum
from src.game.sprites.furniture import StackOfPlates
from src.game.sprites.dust import Dust

class LivingRoom(Room):
    def __init__(self, game: Game) -> None:
        super().__init__(game, "living_room")

        self.set_boundary([(0, 29), (212, 29), (212, 139), (138, 139), (138, 86), (0, 86)])
        self.set_interactable_furniture({
            "stack_of_plates_6": StackOfPlates,
        })
        self.load_furniture()

        self._spawn_dust()

        self.spawn_player((32, 42))

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

from src.core import *

from .room import Room
from src.game.sprites.item import Vacuum
from src.game.sprites.dust import Dust

class Bathroom(Room):
    def __init__(self, game: Game) -> None:
        super().__init__(game, "bathroom")

        self.set_boundary([(71, 29), (139, 29), (139, 86), (71, 86)])
        self.load_furniture()

        self.spawn_player((87, 46))

from src.core import *

from .room import Room
from src.game.sprites.item import Vacuum
from src.game.sprites.dust import Dust

class Entrance(Room):
    def __init__(self, game: Game) -> None:
        super().__init__(game, "entrance")

        self.set_boundary([(0, 29), (139, 29), (139, 139), (65, 139), (65, 86), (0, 86)])
        self.load_furniture()

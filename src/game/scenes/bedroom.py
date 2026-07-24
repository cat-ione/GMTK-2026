from src.core import *

from .room import Room
from src.game.sprites.item import Vacuum
from src.game.sprites.dust import Dust

class Bedroom(Room):
    def __init__(self, game: Game) -> None:
        super().__init__(game, "bedroom")

        self.set_boundary([(0, 29), (140, 140), (71, 85), (139, 85), (139, 139), (0, 139)])
        self.load_furniture()

from src.core import *
from .bedroom import Bedroom
from .bathroom import Bathroom

class GameData:
    def __init__(self, game: Game, living_room: LivingRoom) -> None:
        self.player = living_room.player
        self.camera = living_room.camera
        self.living_room = living_room
        self.bedroom = Bedroom(game, self)
        self.bathroom = Bathroom(game, self)

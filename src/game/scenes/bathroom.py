from src.core import *

from .room import Room
from src.game.sprites.furniture import BedroomDoor2

class Bathroom(Room):
    def __init__(self, game: Game, game_data: GameData) -> None:
        super().__init__(game, game_data, "bathroom")

        self.set_boundary([(6, 29), (72, 29), (72, 86), (6, 86)])
        self.set_interactable_furniture({
            "door": BedroomDoor2,
        })
        self.load_furniture()

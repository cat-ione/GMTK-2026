from src.core import *

from .room import Room
from src.game.sprites.item import Vacuum
from src.game.sprites.dust import Dust
from src.game.sprites.furniture import LivingRoomDoor, BathroomDoor

class Bedroom(Room):
    def __init__(self, game: Game, game_data: GameData) -> None:
        super().__init__(game, game_data, "bedroom")

        self.set_boundary([(0, 29), (71, 29), (71, 85), (139, 85), (139, 139), (0, 139)])
        self.set_interactable_furniture({
            "door_living_room": LivingRoomDoor,
            "door_bathroom": BathroomDoor,
        })
        self.load_furniture()

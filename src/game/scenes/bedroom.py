from src.core import *

from .room import Room
from src.game.sprites.furniture import LivingRoomDoor, BathroomDoor, HamsterCage

class Bedroom(Room):
    def __init__(self, game: Game, game_data: GameData) -> None:
        super().__init__(game, game_data, "bedroom")

        self.set_boundary([(0, 29), (71, 29), (71, 85), (139, 85), (139, 139), (0, 139)])
        self.set_interactable_furniture({
            "door_living_room": LivingRoomDoor,
            "door_bathroom": BathroomDoor,
            "hamster_cage": HamsterCage,
        })
        self.load_furniture()

        self.on_hamster_cutscene = False

    def update(self) -> None:
        super().update()

        self.game_data.living_room.microwave.update()
        self.game_data.living_room.fridge.update()
        self.game_data.bathroom.bathtub.update()

        if self.on_hamster_cutscene:
            self.player.say("Oh my goodness! All my hamsters escaped. I have to round them up into their cage!")
            self.flash_clipboard = True
            self.on_hamster_cutscene = False

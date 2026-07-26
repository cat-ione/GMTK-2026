from src.core import *

from .room import Room
from src.game.sprites.furniture import BedroomDoor2, Bathtub

class Bathroom(Room):
    def __init__(self, game: Game, game_data: GameData) -> None:
        super().__init__(game, game_data, "bathroom")

        self.set_boundary([(6, 29), (72, 29), (72, 86), (6, 86)])
        self.set_interactable_furniture({
            "door": BedroomDoor2,
            "bathtub": Bathtub,
        })
        self.load_furniture()
        self.bathtub = cast(Bathtub, self.find_furniture("bathtub"))

        # Tutorial stuffs
        self.first_time_here = True
        self.first_bath_interaction = True
        self.first_bath_interaction_2 = True

    def update(self) -> None:
        super().update()

        self.game_data.living_room.microwave.update()
        self.game_data.living_room.fridge.update()

        if self.game_data.first_play and self.first_time_here:
            self.bubble = self.player.say("Mom likes her bath temperature to be perfect, I better get this just right...", Anchor.BOTTOMRIGHT)
            self.first_time_here = False

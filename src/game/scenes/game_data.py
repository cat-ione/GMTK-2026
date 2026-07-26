from src.core import *
from .bedroom import Bedroom
from .bathroom import Bathroom

class GameData:
    def __init__(self, game: Game, living_room: LivingRoom, first_play: bool = True) -> None:
        self.player = living_room.player
        self.camera = living_room.camera
        self.clipboard = living_room.clipboard
        self.mom_slider = living_room.mom_slider
        self.living_room = living_room
        self.bedroom = Bedroom(game, self)
        self.bathroom = Bathroom(game, self)

        self.first_play = first_play
        self.start_time = 0.0
        self.game_time = 0.0

        self.scores = {
            "chicken": 0,
            "plates": 0,
            "vacuum": 0,
            "bathtub": 0,
            "hamsters": 0,
        }
        self.max_scores = {
            "chicken": 62,
            "plates": 30, # 5 points per plate
            "vacuum": 40,
            "bathtub": 60,
            "hamsters": 48, # 4 points per hamster
        }

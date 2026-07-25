from src.core import *
from .bedroom import Bedroom
from .bathroom import Bathroom

class GameData:
    def __init__(self, game: Game, living_room: LivingRoom) -> None:
        self.player = living_room.player
        self.camera = living_room.camera
        self.clipboard = living_room.clipboard
        self.living_room = living_room
        self.bedroom = Bedroom(game, self)
        self.bathroom = Bathroom(game, self)

        self.first_play = True
        self.start_time = 0.0
        self.game_time = 0.0

        self.scores = {
            "chicken": 0,
            "plates": 0,
            "rice": 0,
            "vacuum": 0,
            "bathtub": 0,
            "hamsters": 0,
        }
        self.max_scores = {
            "chicken": 62,
            "plates": 30, # 5 points per plate
            "rice": 60,
            "vacuum": 40,
            "bathtub": 60,
            "hamsters": 48, # 4 points per hamster
        }

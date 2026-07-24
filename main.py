# /// script
# dependencies = [
#     "pygame-ce",
#     "pytweening",
# ]
# ///

from src.game.scenes.living_room import LivingRoom
from src.game.scenes.bedroom import Bedroom
from src.game.scenes.bathroom import Bathroom
from src.core.engine.game import Game
import asyncio

if __name__ == "__main__":
    game = Game(LivingRoom)
    asyncio.run(game.run())

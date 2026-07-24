# /// script
# dependencies = [
#     "pygame-ce",
#     "pytweening",
# ]
# ///

from src.game.scenes.entrance import Entrance
from src.game.scenes.living_room import LivingRoom
from src.game.scenes.bedroom import Bedroom
from src.core.engine.game import Game
import asyncio

if __name__ == "__main__":
    game = Game(Bedroom)
    asyncio.run(game.run())

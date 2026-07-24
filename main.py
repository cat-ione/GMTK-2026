# /// script
# dependencies = [
#     "pygame-ce",
#     "pytweening",
# ]
# ///

from src.game.scenes.titlescreen import Titlescreen
from src.core.engine.game import Game
import asyncio

if __name__ == "__main__":
    game = Game(Titlescreen)
    asyncio.run(game.run())

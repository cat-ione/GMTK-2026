# /// script
# dependencies = [
#     "pygame-ce",
#     "pytweening",
# ]
# ///

from src.game.scenes.main_scene import MainScene
from src.core.engine.game import Game
import asyncio

if __name__ == "__main__":
    game = Game(MainScene)
    asyncio.run(game.run())

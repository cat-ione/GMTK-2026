from src.core import *

from .room import Room
from src.game.sprites.player import Player
from src.game.sprites.item import Item, TestItem, Vacuum
from src.game.sprites.dust import Dust

class LivingRoom(Room):
    def __init__(self, game: Game) -> None:
        super().__init__(game, "living_room")

        # test_item = TestItem(self, (50, 50))
        # self.add_item(test_item)
        # test_item = TestItem(self, (40, 45))
        # self.add_item(test_item)
        # vacuum = Vacuum(self, (100, 100))
        # self.add_item(vacuum)

        for _ in range(0):
            pos = Vec(randint(0, WIDTH - 2), randint(0, HEIGHT - 2))
            self.add_dust(Dust(self, pos))

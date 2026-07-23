from src.core import *

from .room import Room
from src.game.sprites.item import Vacuum
from src.game.sprites.dust import Dust

class LivingRoom(Room):
    def __init__(self, game: Game) -> None:
        super().__init__(game, "living_room")

        self.set_boundary([(0, 29), (139, 29), (139, 139), (65, 139), (65, 86), (0, 86)])

        # test_item = TestItem(self, (50, 50))
        # self.add_item(test_item)
        # test_item = TestItem(self, (40, 45))
        # self.add_item(test_item)
        vacuum = Vacuum(self, (60, 75))
        self.add_item(vacuum)

        min_x = int(min(x for x, _ in self.boundary))
        max_x = int(max(x for x, _ in self.boundary))
        min_y = int(min(y for _, y in self.boundary))
        max_y = int(max(y for _, y in self.boundary))

        for _ in range(200):
            valid = False
            pos = Vec(0, 0)
            while not valid:
                pos = Vec(randint(min_x, max_x), randint(min_y, max_y))
                if not self.contains_point(pos, margin=2): continue
                for furniture in self.furnitures:
                    if furniture.drawbox is None: continue
                    if furniture.drawbox.collides_point(pos, margin=2):
                        break
                else:
                    valid = True
            self.add_dust(Dust(self, pos))

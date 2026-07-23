from src.core import *

from src.game.sprites.player import Player
from src.game.sprites.item import Item, TestItem, Vacuum
from src.game.sprites.dust import Dust

class MainScene(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.items: set[Item] = set()
        self.dusts: set[Dust] = set()

        self.player = Player(self)
        self.add(self.player)

        test_item = TestItem(self, (50, 50))
        self.add_item(test_item)
        test_item = TestItem(self, (40, 45))
        self.add_item(test_item)
        vacuum = Vacuum(self, (100, 100))
        self.add_item(vacuum)

        for _ in range(20):
            pos = Vec(randint(0, WIDTH - 2), randint(0, HEIGHT - 2))
            self.add_dust(Dust(self, pos))

    def update(self) -> None:
        self.sprite_manager.update()

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((0, 0, 0))

        self.sprite_manager.draw(screen)

    def add_item(self, item: Item) -> None:
        self.items.add(item)
        self.add(item)

    def remove_item(self, item: Item) -> None:
        self.items.remove(item)
        self.remove(item)

    def add_dust(self, dust: Dust) -> None:
        self.dusts.add(dust)
        self.add(dust)

    def remove_dust(self, dust: Dust) -> None:
        self.dusts.remove(dust)
        self.remove(dust)

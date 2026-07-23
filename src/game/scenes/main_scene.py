from src.core import *

from src.game.sprites.player import Player
from src.game.sprites.item import Item, TestItem, Vacuum

class MainScene(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.items: set[Item] = set()

        self.player = Player(self)
        self.add(self.player)

        test_item = TestItem(self, (50, 50))
        self.add_item(test_item)
        test_item = TestItem(self, (40, 45))
        self.add_item(test_item)
        vacuum = Vacuum(self, (100, 100))
        self.add_item(vacuum)

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

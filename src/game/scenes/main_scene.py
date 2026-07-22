from src.core import *

class MainScene(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

    def update(self) -> None:
        self.sprite_manager.update()

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((0, 0, 0))

        self.sprite_manager.draw(screen)

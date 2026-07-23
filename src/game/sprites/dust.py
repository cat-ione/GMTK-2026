from src.core import *

class Dust(Sprite["MainScene"]):
    draw_group = DGroup.ITEM

    def __init__(self, scene: MainScene, pos: VecLike) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, COLOR1, (self.pos, (2, 1)))

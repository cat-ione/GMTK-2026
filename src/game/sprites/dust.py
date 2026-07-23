from src.core import *

class Dust(Sprite["LivingRoom"]):
    draw_group = DGroup.ROOM

    def __init__(self, scene: LivingRoom, pos: VecLike) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, COLOR1, (self.pos, (2, 1)))

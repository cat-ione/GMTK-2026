from src.core import *

if TYPE_CHECKING:
    from .furniture import Furniture

class Hamster(Sprite["Room"]):
    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)
        self.vel = Vec(0, 0)
        self.image = Image.get("hamster_side")

        self.target_furniture = None
        self.go_to_duration = 0

    def update(self) -> None:
        if self.target_furniture is not None:
            # pathfind

    def go_to(self, furniture: Furniture, duration: float) -> None:
        self.target_furniture = furniture
        self.go_to_duration = duration

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.screen_pos)

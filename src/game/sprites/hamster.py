from src.core import *

if TYPE_CHECKING:
    from .furniture import Furniture

class Hamster(Sprite["Room"]):
    update_group = UGroup.MAIN
    draw_group = DGroup.ROOM

    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)
        self.vel = Vec(0, 0)
        self.image = Image.get("hamster_side")

        self.target_furniture = None
        self.speed = 0

    def update(self) -> None:
        if self.target_furniture is not None:
            direction = (self.target_furniture.get_pos() - self.pos).normalize()
            self.vel = direction * self.speed
        self.pos += self.vel * self.game.dt

    def go_to(self, furniture: Furniture, speed: float) -> None:
        self.target_furniture = furniture
        self.speed = speed

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.screen_pos)

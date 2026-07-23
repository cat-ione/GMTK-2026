from src.core import *

class Furniture(Sprite["Room"]):
    draw_group = DGroup.ROOM

    def __init__(self,
        scene: Room,
        pos: VecLike,
        image: pygame.Surface,
        hitbox: list[int] | None
    ) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)
        self.image = image
        if hitbox is not None:
            self.hitbox = RectHitbox(
                self.pos + hitbox[:2],
                (hitbox[2], hitbox[3]),
                Anchor.TOPLEFT,
            )
        else:
            self.hitbox = None
        self.drawbox = RectHitbox(self.pos, self.image.size, Anchor.TOPLEFT)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.pos)

    def draw_hitbox(self, screen: pygame.Surface) -> None:
        if self.hitbox is None: return
        pygame.draw.rect(screen, (0, 255, 255), self.hitbox.get_rect(), 1)

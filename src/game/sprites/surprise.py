from src.core import *

class Surprise(Sprite["Room"]):
    update_group = UGroup.MAIN
    draw_group = DGroup.OVERLAY

    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(scene)
        self.pos = Vec(pos)
        self.animation = Animation(Spritesheet.get("surprise"), 0.4)

    def update(self) -> None:
        self.animation.update()
        if self.animation.done:
            self.scene.remove(self)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.animation.frame, self.screen_pos)

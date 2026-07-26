from src.core import *

class BathtubHandle(Sprite["Room"]):
    update_group = UGroup.MAIN
    draw_group = DGroup.OVERLAY

    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(scene)

        self.image = Image.get("bathtub_handle_base")

        self.pos = Vec(pos)
        self.timer = LoopTimer(0.4)
        self.increasing = True
        self.progress = 0

    def update(self) -> None:
        if self.timer.done:
            self.increasing = not self.increasing
        if self.increasing:
            self.progress = tween.easeInOutSine(self.timer.progress)
        else:
            self.progress = tween.easeInOutSine(self.timer.progress_remaining)

    def draw(self, screen: pygame.Surface) -> None:
        anchored_blit(screen, self.image, self.screen_pos, Anchor.CENTER)
        screen.set_at(self.screen_pos + (-9 + round(self.progress * 16), 0), COLOR4)

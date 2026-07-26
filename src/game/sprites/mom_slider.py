from src.core import *

from src.game.scenes.summary import Summary
from src.game.cutscenes.ending_cutscene import EndingCutscene

class MomSlider(Sprite["Room"]):
    update_group = UGroup.HUD
    draw_group = DGroup.HUD

    def __init__(self, scene: Room) -> None:
        super().__init__(scene)
        self.timer = Timer(10, True)
        self.animation = Animation(Spritesheet.get("mom_slider"), 0.15)
        self.flash_timer = LoopTimer(0.3)
        self.flashing_white = False

    def update(self) -> None:
        self.animation.update()
        if self.animation.done:
            self.animation.reset()
        if self.timer.done:
            self.scene.start_cutscene(EndingCutscene(self.scene))

    def start(self) -> None:
        self.timer.resume()

    def draw(self, screen: pygame.Surface) -> None:
        if self.scene.cutscene is not None: return
        base_image = self.animation.frame
        pos = Vec(6, HEIGHT / 2 - base_image.height / 2)
        screen.blit(base_image, pos)

        knob_image = Image.get("mom_slider_knob")
        pos = pos - Vec(knob_image.size) / 2 + (5, 15 + self.timer.progress * 54)
        if self.timer.progress > 0.9:
            if self.flash_timer.done:
                self.flashing_white = not self.flashing_white
            if self.flashing_white:
                screen.blit(outline(knob_image, (255, 255, 255)), pos - (1, 1))
        screen.blit(knob_image, pos)

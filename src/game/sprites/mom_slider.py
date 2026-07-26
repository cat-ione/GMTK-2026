from src.core import *

from src.game.scenes.summary import Summary

class MomSlider(Sprite["Room"]):
    update_group = UGroup.HUD
    draw_group = DGroup.HUD

    def __init__(self, scene: Room) -> None:
        super().__init__(scene)
        self.timer = Timer(300, True)
        self.animation = Animation(Spritesheet.get("mom_slider"), 0.15)

    def update(self) -> None:
        self.animation.update()
        if self.animation.done:
            self.animation.reset()
        if self.timer.done:
            summary = Summary(self.game, self.scene.game_data)
            self.game.set_scene(summary)

    def start(self) -> None:
        self.timer.resume()

    def draw(self, screen: pygame.Surface) -> None:
        if self.scene.cutscene is not None: return
        base_image = self.animation.frame
        pos = Vec(6, HEIGHT / 2 - base_image.height / 2)
        screen.blit(base_image, pos)
        knob_image = Image.get("mom_slider_knob")
        screen.blit(knob_image, pos - Vec(knob_image.size) / 2 + (5, 15 + self.timer.progress * 54))

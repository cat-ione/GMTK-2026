from src.core import *

from .cutscene import Cutscene
from src.game.sprites.surprise import Surprise

class OpeningCutscene(Cutscene["LivingRoom"]):
    def __init__(self, scene: LivingRoom) -> None:
        super().__init__(scene)

        self.phase = 0
        self.timer = Timer(6, True)

    def start(self) -> None:
        self.scene.player.disable_collision = True
        self.scene.player.animation.loop("sleeping")
        self.timer.reset()

    def update(self) -> None:
        self.skip_if_pressed()

        player = self.scene.player

        if self.phase == 0:
            if self.timer.done:
                self.phase = 1
        elif self.phase == 1:
            self.scene.player.pos = Vec(105, 41)
            self.scene.player.animation.loop("phone_2")
            self.scene.player.animation.one_shot("phone_1")
            self.surprise = Surprise(self.scene, player.pos + (5, -30))
            self.scene.add(self.surprise)
            self.timer.reset(4.5)
            self.phase = 2
        elif self.phase == 2:
            if self.timer.done:
                self.scene.start_zoom_in()
                self.timer.reset(2.5)
                self.phase = 3
        elif self.phase == 3:
            self.scene.zoom_in(Vec(72, 20), 2, self.timer.progress)
            if self.timer.done:
                self.timer.reset(3)
                self.phase = 4
        elif self.phase == 4:
            # Dialogue and stuffs
            if self.timer.done:
                self.timer.reset(2.5)
                self.phase = 5
        elif self.phase == 5:
            self.scene.zoom_out(Vec(72, 20), 2, self.timer.progress_remaining)
            if self.timer.done:
                self.scene.end_zoom_out()
                self.scene.player.animation.loop("idle_down")
                self.timer.reset(1)
                self.phase = 6
        elif self.phase == 6:
            if self.timer.done:
                self.scene.player.disable_collision = False
                self.scene.player.pos.y += 2
                self.scene.cutscene = None

    def cleanup(self) -> None:
        self.scene.player.disable_collision = False
        self.scene.hamster_cs_timer.resume()

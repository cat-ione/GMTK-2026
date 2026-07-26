from src.core import *

from .cutscene import Cutscene
from src.game.sprites.speech_bubble import GameSpeechBubble

class EndingCutscene(Cutscene):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene)
        self.phase = 0
        self.timer = Timer(1)

    def start(self) -> None:
        if self.scene.__class__.__name__ == "LivingRoom":
            self.scene.camera.lerp_to_centered((40, 40))
        elif self.scene.__class__.__name__ == "Bedroom":
            self.scene.camera.lerp_to_centered((40, 5))
        else:
            self.scene.camera.lerp_to_centered((0, 0))

        self.timer.reset()

    def update(self) -> None:
        if self.phase == 0:
            if self.timer.done:
                if self.scene.__class__.__name__ == "LivingRoom":
                    bubble = GameSpeechBubble(self.scene, (38, 20), "Honey, I'm home!", 100, Anchor.TOPLEFT)
                    self.scene.add(bubble)
                elif self.scene.__class__.__name__ == "Bedroom":
                    bubble = GameSpeechBubble(self.scene, (38, -35), "Honey, I'm home!", 100, Anchor.TOPLEFT)
                    self.scene.add(bubble)
                else:
                    bubble = GameSpeechBubble(self.scene, (-38, -35), "Honey, I'm home!", 100, Anchor.TOPLEFT)
                    self.scene.add(bubble)

                Sound.get("knock").play()
                pygame.mixer.music.fadeout(6000)

                self.timer.reset(3)
                self.phase = 1
        elif self.phase == 1:
            if self.timer.done:
                self.scene.fadeout()

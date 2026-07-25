from src.core import *

class Cutscene[S: Scene](Sprite[S]):
    def __init__(self, scene: S) -> None:
        super().__init__(scene)

    def start(self) -> None:
        pass

    def skip_if_pressed(self) -> None:
        if not __debug__: return
        if self.game.keydown == pygame.K_ESCAPE:
            self.scene.cutscene = None # type: ignore
            self.cleanup()

    def cleanup(self) -> None:
        pass

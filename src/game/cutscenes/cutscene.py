from src.core import *

class Cutscene[S: Scene](Sprite[S]):
    def __init__(self, scene: S) -> None:
        super().__init__(scene)

    def start(self) -> None:
        pass

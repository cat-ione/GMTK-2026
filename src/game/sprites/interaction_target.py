from src.core import *

class Interactable(Protocol):
    def select(self) -> None: ...
    def deselect(self) -> None: ...
    def interact(self) -> None: ...

class InteractionTarget(Sprite["Room"]):
    def __init__(self, scene: Room, pos: VecLike, owner: Interactable) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)
        self.owner = owner

    def select(self) -> None:
        self.owner.select()

    def deselect(self) -> None:
        self.owner.deselect()

    def interact(self) -> None:
        self.owner.interact()

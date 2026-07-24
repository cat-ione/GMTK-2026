from src.core import *

from .item import Item

class Vacuum(Item):
    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(
            scene, pos,
            Image.get("vacuum_world"),
            held_image_front=Image.get("vacuum_front"),
            held_image_side=Image.get("vacuum_side"),
            held_front_anchor=Anchor.TOP,
            held_left_anchor=Anchor.TOPLEFT.offset((8, 2)),
            held_right_anchor=Anchor.TOPLEFT.offset((0, 2)),
        )
        self.offsets = {
            "left": Vec(-13, 2),
            "right": Vec(12, 2),
            "up": Vec(-3, -8),
            "down": Vec(2, 3),
        }

    def update_when_held(self) -> None:
        player = self.scene.player
        for dust in self.scene.dusts.copy():
            pos = player.pos + self.offsets[player.direction_text]
            if pos.distance_to(dust.pos) < 4:
                self.scene.remove_dust(dust)

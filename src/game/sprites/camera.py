from src.core import *
from math import exp

FOLLOW_SPEED = 40
LERP_RATE = 6

class Camera(Sprite["Room"]):
    update_group = UGroup.CAMERA

    def __init__(self, scene: Room) -> None:
        super().__init__(scene)
        self.pos = Vec(0, 0)
        self.target = Vec(0, 0)
        self.lerping = False
        self.lerp_once = False

    def update(self) -> None:
        if self.lerping:
            self.pos += (self.target - self.pos) * (1 - exp(-LERP_RATE * self.game.dt))
            if self.lerp_once and self.pos.distance_to(self.target) < 1:
                self.pos = self.target.copy()
                self.lerping = False
            return

        player = self.scene.player
        if player.screen_pos.x < 50:
            self.pos.x -= FOLLOW_SPEED * self.game.dt
        elif player.screen_pos.x > WIDTH - 50:
            self.pos.x += FOLLOW_SPEED * self.game.dt
        if player.screen_pos.y < 50:
            self.pos.y -= FOLLOW_SPEED * self.game.dt
        elif player.screen_pos.y > HEIGHT - 50:
            self.pos.y += FOLLOW_SPEED * self.game.dt

    def center_on(self, pos: VecLike) -> None:
        self.pos = Vec(pos) - Vec(SIZE) / 2

    def lerp_to_centered(self, pos: VecLike) -> None:
        self.target = Vec(pos) - Vec(SIZE) / 2
        self.lerping = True
        self.lerp_once = False

    def lerp_to_centered_once(self, pos: VecLike) -> None:
        self.lerp_to_centered(pos)
        self.lerp_once = True

    def stop_lerp(self) -> None:
        self.lerping = False

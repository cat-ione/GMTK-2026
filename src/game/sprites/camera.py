from src.core import *

FOLLOW_SPEED = 40

class Camera(Sprite["Room"]):
    update_group = UGroup.CAMERA

    def __init__(self, scene: Room) -> None:
        super().__init__(scene)
        self.pos = Vec(0, 0)

    def update(self) -> None:
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

from src.core import *

class Button(Sprite):
    update_group = UGroup.HUD
    draw_group = DGroup.HUD

    def __init__(self,
        scene: Scene,
        pos: VecLike,
        image: pygame.Surface,
        func: Callable
    ) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)
        self.image = image
        self.hitbox = RectHitbox(self.pos, self.image.size, Anchor.TOPLEFT)
        self.func = func

        # Whether mouse button down happened inside the button
        self.down_in_me = False

    def update(self) -> None:
        if self.game.mouse_just_pressed[0]:
            if self.hitbox.collides_point(self.game.mouse_pos // PX):
                self.down_in_me = True
                self.press()
        if self.game.mouse_just_released[0]:
            if self.down_in_me:
                self.down_in_me = False
                self.release()
                if self.hitbox.collides_point(self.game.mouse_pos // PX):
                    self.func()

    def press(self) -> None:
        self.pos.x -= 1

    def release(self) -> None:
        self.pos.x += 1

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.pos)

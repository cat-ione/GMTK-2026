from src.core import *

class Button(Sprite):
    update_group = UGroup.HUD
    draw_group = DGroup.HUD

    def __init__(self,
        scene: Scene,
        pos: VecLike,
        image: pygame.Surface,
        text: str,
        func: Callable,
        sound: pygame.Sound | None = None
    ) -> None:
        super().__init__(scene)

        self.font = Font("font_small", 1, COLOR1)

        self.pos = Vec(pos)
        self.image = self.generate_image(image, text)
        self.hitbox = RectHitbox(self.pos, self.image.size, Anchor.TOPLEFT)
        self.func = func
        self.sound = sound

        # Whether mouse button down happened inside the button
        self.down_in_me = False

    def generate_image(self, image: pygame.Surface, text: str) -> pygame.Surface:
        image = image.copy()
        text_image = self.font.render(text)
        image.blit(text_image, Vec(image.size) / 2 - Vec(text_image.size) / 2)
        return image

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
        if self.sound is not None:
            self.sound.play()

    def release(self) -> None:
        self.pos.x += 1

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.pos)

from src.core import *

START_X = 20
START_Y = 31

class Clipboard(Sprite["Room"]):
    update_group = UGroup.HUD
    draw_group = DGroup.HUD

    def __init__(self, scene: Room) -> None:
        super().__init__(scene)

        self.font = Font("font_small", 1, COLOR1)

        self.items = {
            "chicken": "Defrost chicken",
            "plates": "Set table",
            "rice": "Cook rice",
            "vacuum": "Vacuum rooms",
            "bathtub": "Prepare bathtub",
            "hamsters": "Return hamsters",
        }
        self.done: set[str] = set()
        self._generate_image()

        self.animation_timer = Timer(0.3)
        self.appearing = True
        self.in_pos = Vec(SIZE) / 2 - Vec(self.image.size) / 2
        self.out_pos = self.in_pos + (0, 150)
        self.pos = self.out_pos.copy()

    def _generate_image(self) -> None:
        self.image = Image.get("clipboard").copy()
        for i, (name, text) in enumerate(self.items.items()):
            text_surf = self.font.render(text)
            self.image.blit(text_surf, (START_X, START_Y + i * 14))
            if name in self.done:
                pygame.draw.line(
                    self.image, COLOR1,
                    (START_X - 1, START_Y + i * 14 + 2),
                    (START_X + text_surf.width + 1, START_Y + i * 14 + 2)
                )

    def cross_out(self, item: str) -> None:
        if item in self.done: return
        self.done.add(item)
        self._generate_image()

    def uncross(self, item: str) -> None:
        if item not in self.done: return
        self.done.remove(item)
        self._generate_image()

    def slide_in(self) -> None:
        self.scene.player.locked = True
        self.scene.add(self)
        self.appearing = True
        self.animation_timer.reset()

    def slide_out(self) -> None:
        self.scene.player.locked = False
        self.appearing = False
        self.animation_timer.reset()

    def update(self) -> None:
        if self.animation_timer.done:
            # Sliding out
            if not self.appearing:
                self.scene.remove(self)
        if self.appearing:
            self.pos = self.out_pos + (self.in_pos - self.out_pos) * self.animation_timer.progress
        else:
            self.pos = self.in_pos + (self.out_pos - self.in_pos) * self.animation_timer.progress

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.pos)

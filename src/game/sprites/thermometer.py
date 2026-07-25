from src.core import *

from math import tanh

class Thermometer(Sprite["Room"]):
    draw_group = DGroup.HUD

    def __init__(self, scene: Room, pos: VecLike, temp: float, center_temp: float, spread: float = 1) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)

        self.temperature = temp
        self.center_temp = center_temp
        self.spread = spread

    def generate_image(self) -> None:
        self.image = Image.get("thermometer").copy()
        x, top_y, center_y, bottom_y = 9, 4, 14, 26
        extent_up, extent_down = (center_y - top_y) * self.spread, (bottom_y - center_y) * self.spread

        delta = self.temperature - self.center_temp
        if delta >= 0:
            level_y = center_y - extent_up * tanh(delta / extent_up)
        else:
            level_y = center_y + extent_down * tanh(-delta / extent_down)
        level_y = min(max(level_y, top_y), bottom_y)

        pygame.draw.line(self.image, COLOR6, (x, bottom_y), (x, round(level_y)))

    def update(self) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        self.generate_image()
        screen.blit(self.image, self.pos)

class ThermometerIcons(Sprite["Room"]):
    draw_group = DGroup.HUD

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(Image.get("thermometer_icons"), (146, 82))

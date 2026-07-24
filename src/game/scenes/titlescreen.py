from src.core import *

from src.game.sprites.button import Button
from .living_room import LivingRoom

class Titlescreen(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.text_scroll = Animation(Spritesheet.get("title_text_scroll"), 0.3)

        self.add_button((116, 49), Image.get("button_medium"), lambda: 0)
        self.add_button((145, 49), Image.get("button_medium"), lambda: 0)

        self.add_button((116, 65), Image.get("button_small"), lambda: 0)
        self.add_button((135, 65), Image.get("button_small"), lambda: 0)
        self.add_button((154, 65), Image.get("button_small"), lambda: 0)
        self.add_button((116, 81), Image.get("button_small"), lambda: 0)
        self.add_button((135, 81), Image.get("button_small"), lambda: 0)
        self.add_button((154, 81), Image.get("button_small"), lambda: 0)
        self.add_button((116, 97), Image.get("button_small"), lambda: 0)
        self.add_button((135, 97), Image.get("button_small"), lambda: 0)
        self.add_button((154, 97), Image.get("button_small"), lambda: 0)

        self.add_button((116, 113), Image.get("button_large"), self.start_game)

    def update(self) -> None:
        self.text_scroll.update()
        self.sprite_manager.update()

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(Image.get("titlescreen_bg"))
        screen.blit(self.text_scroll.frame, (115, 31))
        self.sprite_manager.draw(screen)

    def start_game(self) -> None:
        living_room = LivingRoom(self.game)
        self.game.set_scene(living_room)

    def add_button(self, pos: VecLike, image: pygame.Surface, func: Callable) -> None:
        button = Button(self, pos, image, func)
        self.add(button)

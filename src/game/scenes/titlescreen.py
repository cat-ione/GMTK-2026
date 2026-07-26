from src.core import *

from src.game.sprites.button import Button
from .living_room import LivingRoom

class Titlescreen(Scene):
    def __init__(self, game: Game, first_play: bool = True) -> None:
        super().__init__(game)
        self.first_play = first_play

        pygame.mixer.music.load("res/sounds/microwave.ogg")
        pygame.mixer.music.play(loops=-1, fade_ms=2500)

        self.text_scroll = Animation(Spritesheet.get("title_text_scroll"), 0.3)

        self.add_button((116, 49), Image.get("button_medium"), " ", lambda: 0, Sound.get("beep"))
        self.add_button((145, 49), Image.get("button_medium"), " ", lambda: 0, Sound.get("beep"))

        self.add_button((116, 65), Image.get("button_small"), " ", lambda: 0, Sound.get("beep"))
        self.add_button((135, 65), Image.get("button_small"), " ", lambda: 0, Sound.get("beep"))
        self.add_button((154, 65), Image.get("button_small"), " ", lambda: 0, Sound.get("beep"))
        self.add_button((116, 81), Image.get("button_small"), " ", lambda: 0, Sound.get("beep"))
        self.add_button((135, 81), Image.get("button_small"), " ", lambda: 0, Sound.get("beep"))
        self.add_button((154, 81), Image.get("button_small"), " ", lambda: 0, Sound.get("beep"))
        self.add_button((116, 97), Image.get("button_small"), " ", lambda: 0, Sound.get("beep"))
        self.add_button((135, 97), Image.get("button_small"), " ", lambda: 0, Sound.get("beep"))
        self.add_button((154, 97), Image.get("button_small"), " ", lambda: 0, Sound.get("beep"))

        self.add_button((116, 113), Image.get("button_large"), "Start", self.start_game)

        self.fade_timer = Timer(2, True)
        self.fading = False
        self.fade_surf = pygame.Surface(SIZE)
        self.fade_surf.fill((0, 0, 0))

    def update(self) -> None:
        self.text_scroll.update()
        if self.text_scroll.done:
            self.text_scroll.reset()
        self.sprite_manager.update()

        if self.fading and self.fade_timer.done:
            living_room = LivingRoom(self.game, self.first_play)
            self.game.set_scene(living_room)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(Image.get("titlescreen_bg"))
        screen.blit(self.text_scroll.frame, (115, 31))
        self.sprite_manager.draw(screen)

        if self.fading:
            self.fade_surf.set_alpha(int(self.fade_timer.progress * 255))
            screen.blit(self.fade_surf)

    def start_game(self) -> None:
        if self.fading: return
        self.fade_timer.reset()
        self.fading = True
        Sound.get("microwave_open_title").play()
        pygame.mixer.music.fadeout(2000)

    def add_button(self, pos: VecLike, image: pygame.Surface, text: str, func: Callable, sound: pygame.Sound | None = None) -> None:
        button = Button(self, pos, image, text, func, sound)
        self.add(button)

from src.core import *

from src.game.sprites.button import Button

START_X = 33
START_Y = 31

class Summary(Scene):
    def __init__(self, game: Game, game_data: GameData) -> None:
        super().__init__(game)

        pygame.mixer.music.fadeout(2500)
        self.font = Font("font_small", 1, COLOR1)

        self.scores = game_data.scores
        self.max_scores = game_data.max_scores
        info(self.scores)
        self.total_score = sum(self.scores.values())
        self.max_total_score = sum(self.max_scores.values())

        hamsters_captured = game_data.scores["hamsters"] // 4
        total_hamsters = game_data.max_scores["hamsters"] // 4
        plates = game_data.scores["plates"] // 5
        dust_percentage = int((1 - len(game_data.living_room.dusts) / 200) * 100)
        chicken_temp = game_data.living_room.chicken.temperature
        bath_full = game_data.bathroom.bathtub.full
        bath_temp = round(game_data.bathroom.bathtub.current_temp)
        self.text = [
            "Chicken:",
            f"   {chicken_temp}C/22C",
            "Bathtub:",
            f"   {bath_temp}C/36C" if bath_full else "   not filled!",
            f"Plates: {plates}/6",
            f"Vacuum: {dust_percentage}%",
            f"Hamsters: {hamsters_captured}/{total_hamsters}",
            " ",
            f"Final score:",
            f"   {self.total_score}/{self.max_total_score}"
        ]

        if self.total_score < self.max_total_score * 0.6:
            self.mood = 1
        elif self.total_score < self.max_total_score * 0.9:
            self.mood = 2
        else:
            self.mood = 3

        if self.mood == 1 or self.mood == 2:
            pygame.mixer.music.load("res/sounds/sad.mp3")
            pygame.mixer.music.play(loops=-1, fade_ms=2500)
        else:
            pygame.mixer.music.load("res/sounds/happy.mp3")
            pygame.mixer.music.play(loops=-1, fade_ms=2500)

        self.timer = Timer(2.5)

    def update(self) -> None:
        self.sprite_manager.update()

        if self.timer.done:
            self.timer.reset()
            self.timer.pause()
            button = Button(self, (70, HEIGHT - 35), Image.get("button_medium"), "Back", self.back_to_title)
            self.add(button)

    def back_to_title(self) -> None:
        pygame.mixer.music.fadeout(2500)
        from .titlescreen import Titlescreen
        self.game.set_scene(Titlescreen(self.game, False))

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(Image.get("ending_background"))
        screen.blit(Image.get(f"ending_characters_{self.mood}"), (121, 80))
        screen.blit(Image.get("ending_border"))

        for i, text in enumerate(self.text):
            text_surf = self.font.render(text)
            screen.blit(text_surf, (START_X, START_Y + i * 7))

        self.sprite_manager.draw(screen)

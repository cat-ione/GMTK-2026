from src.core import *

START_X = 33
START_Y = 31

class Summary(Scene):
    def __init__(self, game: Game, game_data: GameData) -> None:
        super().__init__(game)

        self.font = Font("font_small", 1, COLOR1)

        self.scores = game_data.scores
        self.max_scores = game_data.max_scores
        self.total_score = sum(self.scores.values())
        self.max_total_score = sum(self.max_scores.values())

        hamsters_captured = game_data.scores["hamsters"] // 4
        total_hamsters = game_data.max_scores["hamsters"] // 4
        plates = game_data.scores["plates"] // 5
        dust_percentage = int(len(game_data.living_room.dusts) / 200 * 100)
        chicken_temp = game_data.living_room.chicken.temperature
        self.text = [
            "Chicken:",
            f"   {chicken_temp}C / 22C",
            f"Bathtub:",
            f"   0 / 36C",
            f"Plates: {plates} / 6",
            f"Rice: 0 / 0",
            f"Vacuum: {dust_percentage}%",
            f"Hamsters: {hamsters_captured} / {total_hamsters}",
            " ",
            f"Final score:",
            f"   {self.total_score} / {self.max_total_score}"
        ]

        if self.total_score < self.max_total_score * 0.6:
            self.mood = 1
        elif self.total_score < self.max_total_score * 0.9:
            self.mood = 2
        else:
            self.mood = 3

    def update(self) -> None:
        self.sprite_manager.update()

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(Image.get("ending_background"))
        screen.blit(Image.get(f"ending_characters_{self.mood}"), (121, 80))
        screen.blit(Image.get("ending_border"))

        for i, text in enumerate(self.text):
            text_surf = self.font.render(text)
            screen.blit(text_surf, (START_X, START_Y + i * 7))

        self.sprite_manager.draw(screen)

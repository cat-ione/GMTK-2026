from src.core import *

class SpeechBubble(Sprite):
    update_group = UGroup.HUD
    draw_group = DGroup.HUD

    def __init__(self, scene: Scene, pos: VecLike, text: str, wrap: int, corner: Anchor,
                 typewriter: bool = False, letter_delay: float = 0.05, voice: str | None = None) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)
        self.text = text
        self.wrap = wrap # Length of each line in pixels before wrap
        self.anchor = corner

        self.font = Font("font_small", 1, COLOR1)
        self.corner = Image.get("speech_bubble_corner")
        self.lines = self.font.wrap_text(self.text, self.wrap)

        self.typewriter = typewriter
        self.reveal_timer = LoopTimer(letter_delay) if typewriter else None
        self.total_chars = sum(len(line) for line in self.lines)
        self.revealed_chars = 0 if typewriter else self.total_chars

        self.voice = voice

        self.image = self.generate_image()

    @property
    def done(self) -> bool:
        return self.revealed_chars >= self.total_chars

    def generate_image(self) -> pygame.Surface:
        full_lines = [self.font.render(line) for line in self.lines]
        width = max(line.width for line in full_lines)
        height = sum((line.height + 1 for line in full_lines)) - 1
        image = pygame.Surface((width + 6, height + 6), flags=pygame.SRCALPHA)
        pygame.draw.rect(image, COLOR4, ((0, 0), image.size), border_radius=3)
        pygame.draw.rect(image, COLOR1, ((0, 0), image.size), 1, 3)

        remaining = self.revealed_chars
        for i, line in enumerate(self.lines):
            if self.typewriter:
                visible = line[:max(0, remaining)]
                remaining -= len(line)
                if not visible: continue
                image.blit(self.font.render(visible), (3, 3 + i * 6))
            else:
                image.blit(full_lines[i], (3, 3 + i * 6))

        if self.anchor == Anchor.BOTTOM:
            expanded = pygame.Surface(Vec(image.size) + (0, 4), flags=pygame.SRCALPHA)
            expanded.blit(image)
            expanded.blit(Image.get("speech_bubble_side"), (image.width / 2 - 2, image.height - 1))
            return expanded

        expanded = pygame.Surface(Vec(image.size) + (3, 3), flags=pygame.SRCALPHA)
        main_offset = ((1, 1) - self.anchor.value) * 3
        expanded.blit(image, main_offset)
        corner_offset = self.anchor.value * 3
        corner = pygame.transform.flip(self.corner, bool(self.anchor.value.x), bool(self.anchor.value.y))
        expanded.blit(corner, Vec(image.size).elementwise() * self.anchor.value - corner_offset)

        return expanded

    def update(self) -> None:
        if self.typewriter and not self.done and self.reveal_timer is not None and self.reveal_timer.done:
            self.revealed_chars += 1
            self.image = self.generate_image()
            if self.voice is not None and self.revealed_chars % 2 == 0:
                Sound.get(f"{self.voice}_{randint(1, 8)}").play()

    def draw(self, screen: pygame.Surface) -> None:
        anchored_blit(screen, self.image, self.pos, self.anchor)

class GameSpeechBubble(SpeechBubble):
    def draw(self, screen: pygame.Surface) -> None:
        anchored_blit(screen, self.image, self.screen_pos, self.anchor)

from src.core import *

class SpeechBubble(Sprite):
    draw_group = DGroup.HUD

    def __init__(self, scene: Scene, pos: VecLike, text: str, wrap: int, corner: Anchor) -> None:
        super().__init__(scene)

        self.pos = Vec(pos)
        self.text = text
        self.wrap = wrap # Length of each line in pixels before wrap
        self.anchor = corner

        self.font = Font("font_small", 1, COLOR1)
        self.corner = Image.get("speech_bubble_corner")
        self.image = self.generate_image()

    def generate_image(self) -> pygame.Surface:
        lines = self.font.render_wrapped(self.text, self.wrap)
        width = max(line.width for line in lines)
        height = sum((line.height + 1 for line in lines)) - 1
        image = pygame.Surface((width + 6, height + 6), flags=pygame.SRCALPHA)
        pygame.draw.rect(image, COLOR4, ((0, 0), image.size), border_radius=3)
        pygame.draw.rect(image, COLOR1, ((0, 0), image.size), 1, 3)
        for i, line in enumerate(lines):
            image.blit(line, (3, 3 + i * 6))

        expanded = pygame.Surface(Vec(image.size) + (3, 3), flags=pygame.SRCALPHA)
        main_offset = ((1, 1) - self.anchor.value) * 3
        expanded.blit(image, main_offset)
        corner_offset = self.anchor.value * 3
        corner = pygame.transform.flip(self.corner, bool(self.anchor.value.x), bool(self.anchor.value.y))
        expanded.blit(corner, Vec(image.size).elementwise() * self.anchor.value - corner_offset)

        return expanded

    def update(self) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        anchored_blit(screen, self.image, self.pos, self.anchor)

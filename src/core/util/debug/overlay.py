from .watcher import Watcher
from src.settings import *
import pygame

class Overlay:
    """A debug overlay that displays watched variables on the screen."""

    _surface: pygame.Surface | None = None
    _font: pygame.font.Font | None = None

    visible = True

    @staticmethod
    def init() -> None:
        """Initialize the overlay.

        This method must be called before the overlay can be drawn.
        """
        Overlay._surface = pygame.Surface((WIDTH * PX, HEIGHT * PX))
        Overlay._surface.set_colorkey(CYAN)
        Overlay._surface.set_alpha(OVERLAY_ALPHA)

        Overlay._font = pygame.font.SysFont("monospace", 16)

    @staticmethod
    def draw(target: pygame.Surface) -> None:
        """Draw the overlay onto the target surface.

        Args:
            target: The surface to draw the overlay onto.
        """

        if not Overlay.visible: return

        assert Overlay._surface is not None and Overlay._font is not None, \
            "Overlay not initialized. Call Overlay.init() first."

        Overlay._surface.fill(CYAN)

        for i, (name, value) in enumerate(Watcher.values.items()):
            text = Overlay._font.render(
                f"{name}: {value}", False, OVERLAY_FG, OVERLAY_BG)
            Overlay._surface.blit(text, (0, 16 * i))

        target.blit(Overlay._surface, (0, 0))

    @staticmethod
    def toggle() -> None:
        """Toggle the visibility of the overlay."""
        Overlay.visible = not Overlay.visible

__all__ = ["Overlay"]

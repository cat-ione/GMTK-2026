from .general import read_file
from pathlib import Path
from .debug import *
import pygame
import json

FONT_DIR = Path("res/fonts/")

class Font:
    """A sprite sheet based font that has custom rendering features and
    configuration in a JSON file."""

    def __init__(self, name: str, scale: int,
                 color: tuple[int, int, int] | None = None) -> None:
        """Initializes the font.

        Args:
            name: The name of the font (corresponds to a JSON file in the font
                directory), without the .json extension.
            scale: The scale factor to apply to the rendered text.
            color: An optional color to replace the base color in the font.
        """
        self.name = name
        self.scale = scale
        self.data = json.loads(read_file(FONT_DIR / f"{name}.json"))
        image_path = FONT_DIR / self.data["file"]
        self.sprite_sheet = pygame.image.load(image_path).convert_alpha()
        self.base_color = tuple(self.data["base_color"])
        if color is not None:
            self._replace_color(color)
        self.images, self.advances = self._parse()
        self.gap = self.data["gap"]
        self._height = self.data["grid_size"][1]

    def _replace_color(self, color: tuple[int, int, int]) -> None:
        arr = pygame.surfarray.pixels3d(self.sprite_sheet)
        r1, g1, b1 = self.base_color
        r2, g2, b2 = color
        # Create a mask where the color matches the base color
        # arr[:, :, i] extracts one of the RGB channels from each pixel
        # compare each element of the entire channel array to the corresponding
        # base color component, producing boolean arrays where True indicates
        # a match for that channel. AND them together to find which pixels match
        # all three channels (the base color).
        mask = (  (arr[:, :, 0] == r1)
                & (arr[:, :, 1] == g1)
                & (arr[:, :, 2] == b1))
        # Apparently this [mask] syntax filters the array to only the elements
        # that are True in the mask and only allows the assignment to affect
        # those elements.
        arr[:, :, 0][mask] = r2
        arr[:, :, 1][mask] = g2
        arr[:, :, 2][mask] = b2
        # Deleting the array unlocks the surface
        # Seems that pixel3d automatically locks the surface
        del arr

    def _parse(self) -> tuple[dict[str, pygame.Surface], dict[str, int]]:
        # Size of each character area
        grid_w, grid_h = self.data["grid_size"]
        # Full pixel-width of the sprite sheet
        full_w = self.sprite_sheet.width
        images, advances = {}, {}
        for i, (char, info) in enumerate(self.data["chars"].items()):
            x = (i * grid_w) % full_w
            y = (i * grid_w) // full_w * grid_h
            width = info["width"] # Guaranteed to be present
            advance = info.get("advance", width) # Default to width
            image = self.sprite_sheet.subsurface((x, y, width, grid_h))
            images[char] = image
            advances[char] = advance
        return images, advances

    def __getitem__(self, char: str) -> pygame.Surface:
        """Get the image of the given character.

        Args:
            char: The character to get the image for.

        Returns:
            The image of the character.
        """
        return self.images[char.upper()]

    def advance(self, char: str) -> int:
        """Get the advance width of the given character.

        The advance width is the amount to move the cursor forward after
        rendering the character. Note that this is not necessarily the same as
        the character's width, as some characters may need extra spacing or
        can be closer together.

        Args:
            char: The character to get the advance width for.

        Returns:
            The advance width of the character.
        """
        return self.advances[char.upper()]

    def render(self, text: str) -> pygame.Surface:
        """Produce a surface with the given text rendered.

        Args:
            text: The text to render.

        Returns:
            A surface with the rendered text.
        """
        width = sum(self.advance(c) + self.gap for c in text) - self.gap
        surface = pygame.Surface((width, self._height), pygame.SRCALPHA)
        x = 0
        for char in text:
            surface.blit(self[char], (x, 0))
            x += self.advance(char) + self.gap
        return pygame.transform.scale_by(surface, self.scale)

    @property
    def height(self) -> int:
        """The actual rendered height of the font after scaling."""
        return self._height * self.scale

class Text:
    """A text object that uses a Font to render text surfaces."""

    def __init__(self, font: Font, *contents: str) -> None:
        """Initializes the text object.

        Args:
            font: The font to use for rendering the text.
            contents: The initial text contents.
        """
        self.font = font
        self.contents = contents
        self.image_cache = {}
        self._surfaces = [self._get_surface(content) for content in contents]
        self._surface = pygame.Surface((0, 0))

        self.modified = True

    def set(self, *contents: str) -> None:
        """Sets the text contents.

        This will only re-render the text if the contents have changed. So it is
        perfectly fine to call this every frame.

        Args:
            contents: The text contents to set.
        """
        if contents == self.contents: return
        self.contents = contents
        self._surfaces = [self._get_surface(content) for content in contents]
        self.modified = True

    def cache(self, content: str) -> pygame.Surface:
        """Pre-renders and caches a text surface for the given content.

        If the text is set with one of the arguments matching this content, it
        will use the cached surface instead of rendering it again.

        Args:
            content: The text content to cache.

        Returns:
            The cached surface.
        """
        self.image_cache[content] = self.font.render(content)
        return self.image_cache[content]

    def clear_cache(self) -> None:
        """Clears the cached text surfaces."""
        self.image_cache.clear()

    def _get_surface(self, content: str) -> pygame.Surface:
        if content in self.image_cache:
            return self.image_cache[content]
        return self.font.render(content)

    @property
    def surface(self) -> pygame.Surface:
        """The combined surface of all text contents."""
        if self.modified:
            self.modified = False
            total_width = (
                sum(surface.width + self.font.gap for surface in self._surfaces)
                - self.font.gap
            )
            height = self.font.height
            combined = pygame.Surface((total_width, height), pygame.SRCALPHA)
            x = 0
            for surface in self._surfaces:
                combined.blit(surface, (x, 0))
                x += surface.width + self.font.gap
            self._surface = combined
        return self._surface

__all__ = [
    "Font",
    "Text",
]

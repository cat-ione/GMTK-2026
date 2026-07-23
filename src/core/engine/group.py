from typing import Generator, Callable, Any
from src.settings import UGroup, DGroup
from .sprite import Sprite
import pygame

class UpdateGroup:
    """A group of sprites that are updated together."""

    def __init__(self, group: UGroup) -> None:
        """Initialize the update group.

        Args:
            group: The update group enum value.
        """
        self.group = group
        self.sprites: set[Sprite] = set()

    def update(self) -> None:
        """Update all sprites in the group."""
        for sprite in self.sprites.copy():
            sprite.update()

    def add(self, sprite: Sprite) -> None:
        """Add a sprite to the update group.

        Args:
            sprite: The sprite to add.
        """
        self.sprites.add(sprite)

    def remove(self, sprite: Sprite) -> None:
        """Remove a sprite from the update group.

        Args:
            sprite: The sprite to remove.
        """
        self.sprites.remove(sprite)

    def get_sprites(self) -> Generator[Sprite, None, None]:
        """Get all sprites in the update group.

        This method is intended to be used to manually manage sprites.

        Yields:
            The sprites in the update group.
        """
        yield from self.sprites

    def __len__(self) -> int:
        return len(self.sprites)

class DrawGroup:
    """A group of sprites that are drawn together."""

    def __init__(self, group: DGroup) -> None:
        """Initialize the draw group.

        Args:
            group: The draw group enum value.
        """
        self.group = group
        self.sprites: dict[int, Sprite] = {}

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all sprites in the group.

        Args:
            screen: The surface to draw the sprites on.
        """
        for sprite in self.sprites.values():
            sprite.draw(screen)
            sprite._draw_hitbox_wrapper(screen)

    def add(self, sprite: Sprite) -> None:
        """Add a sprite to the draw group.

        Args:
            sprite: The sprite to add.
        """
        self.sprites[sprite.uuid] = sprite

    def remove(self, sprite: Sprite) -> None:
        """Remove a sprite from the draw group.

        Args:
            sprite: The sprite to remove.
        """
        self.sprites.pop(sprite.uuid)

    def get_sprites(self) -> Generator[Sprite, None, None]:
        """Get all sprites in the draw group.

        This method is intended to be used to manually manage sprites.

        Yields:
            The sprites in the draw group.
        """
        yield from self.sprites.values()

    def sort(self, key: Callable[[tuple[int, Sprite]], Any]) -> None:
        self.sprites = dict(sorted(self.sprites.items(), key=key))

    def __len__(self) -> int:
        return len(self.sprites)

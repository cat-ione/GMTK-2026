from .group import DrawGroup, UpdateGroup
from typing import Generator
from .sprite import Sprite
from src.settings import *
import pygame

class SpriteManager:
    """Manages all sprites in a scene, organizing them into update and draw
    groups.

    The groups are defined in `game.settings.UGroups` and
    `game.settings.DGroups`.
    """

    def __init__(self) -> None:
        """Initialize the sprite manager."""
        self.sprites_registry = {}
        self.u_groups = {group: UpdateGroup(group) for group in UGroup}
        self.d_groups = {group: DrawGroup(group) for group in DGroup}
        self.current_uuid = 0

    def update(self) -> None:
        """Update all sprites in the sprite manager."""
        for group in self.u_groups.values():
            group.update()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all sprites in the sprite manager.

        Args:
            screen: The surface to draw the sprites on.
        """
        for group in self.d_groups.values():
            group.draw(screen)

    def add(self, sprite: Sprite) -> None:
        """Add a sprite to the sprite manager. The sprite will be added to both
        its update and draw groups (if it has one).

        Args:
            sprite: The sprite to add.
        """
        self.sprites_registry[sprite.uuid] = sprite
        if sprite.update_group:
            self.u_groups[sprite.update_group].add(sprite)
        if sprite.draw_group:
            self.d_groups[sprite.draw_group].add(sprite)

    def remove(self, sprite: Sprite) -> None:
        """Remove a sprite from the sprite manager. The sprite will be removed
        from both its update and draw groups (if it has one).

        Args:
            sprite: The sprite to remove.
        """
        self.sprites_registry.pop(sprite.uuid)
        if sprite.update_group:
            self.u_groups[sprite.update_group].remove(sprite)
        if sprite.draw_group:
            self.d_groups[sprite.draw_group].remove(sprite)
        sprite.cleanup()

    def get_update_groups(self) -> Generator[UpdateGroup, None, None]:
        """Get all update groups in the sprite manager.

        This method is intended to be used to manually manage update groups.

        Yields:
            The update groups.
        """
        yield from self.u_groups.values()

    def get_draw_groups(self) -> Generator[DrawGroup, None, None]:
        """Get all draw groups in the sprite manager.

        This method is intended to be used to manually manage draw groups.

        Yields:
            The draw groups.
        """
        yield from self.d_groups.values()

    def get_update_sprites(self) -> Generator[Sprite, None, None]:
        """Get all update sprites in the sprite manager.

        This method is intended to be used to manually manage update sprites.

        Yields:
            The update sprites.
        """
        for group in self.u_groups.values():
            yield from group.get_sprites()

    def get_draw_sprites(self) -> Generator[Sprite, None, None]:
        """Get all draw sprites in the sprite manager.

        This method is intended to be used to manually manage draw sprites.

        Yields:
            The draw sprites.
        """
        for group in self.d_groups.values():
            yield from group.get_sprites()

    def get_sprite(self, uuid: int) -> Sprite:
        """Get a sprite by its UUID.

        Args:
            uuid: The UUID of the sprite to get.

        Returns:
            The sprite with the given UUID.

        Raises:
            KeyError: If no sprite with the given UUID is found.
        """
        return self.sprites_registry[uuid]

    def exists(self, uuid: int) -> bool:
        """Check if a sprite with the given UUID exists in the sprite manager.

        Args:
            uuid: The UUID of the sprite to check.

        Returns:
            True if the sprite exists, False otherwise.
        """
        return uuid in self.sprites_registry

    def get_next_uuid(self) -> int:
        """Get the next UUID to give to a sprite, which is one larger than the
        previous UUID.

        Returns:
            The next uuid.
        """
        self.current_uuid += 1
        return self.current_uuid

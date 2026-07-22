from abc import ABC as AbstractClass, abstractmethod
from .sprite_manager import SpriteManager
from .sprite import Sprite
from src.core.util import *
import pygame

if TYPE_CHECKING:
    from .game import Game

class Scene(AbstractClass):
    """Base class for all scenes in the game.

    A scene represents a self-contained part of the game, such as a level,
    menu, or cutscene. Each scene manages its own sprites and handles updating
    and drawing them.
    """

    def __init__(self, game: Game) -> None:
        """Initialize the scene.

        Args:
            game: The game instance that owns the scene.
        """
        self.game = ref_proxy(game)
        self.sprite_manager = SpriteManager()

    @abstractmethod
    def update(self) -> None:
        """Override to update the scene."""
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Override to draw the scene.

        Args:
            screen: The surface to draw the scene on.
        """
        pass

    def add(self, sprite: Sprite) -> None:
        """Add a sprite to the scene.

        Args:
            sprite: The sprite to add.
        """
        self.sprite_manager.add(sprite)

    def remove(self, sprite: Sprite) -> None:
        """Remove a sprite from the scene.

        This method will log a warning if the sprite is not found in the scene.

        Args:
            sprite: The sprite to remove.
        """
        try:
            self.sprite_manager.remove(sprite)
        except KeyError:
            warn(f"Attempted to remove sprite {sprite} from scene {self}, "
                 "but it was not found in the sprite manager.")

    def get(self, uuid: int) -> Sprite:
        """Get a sprite by its UUID.

        Args:
            uuid: The UUID of the sprite to get.

        Returns:
            The sprite with the given UUID.

        Raises:
            KeyError: If no sprite with the given UUID is found.
        """
        return self.sprite_manager.get_sprite(uuid)

    def has(self, uuid: int) -> bool:
        """Check if a sprite with the given UUID exists in the scene.

        Args:
            uuid: The UUID of the sprite to check.

        Returns:
            True if the sprite exists, False otherwise.
        """
        return self.sprite_manager.exists(uuid)

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

    _fade_timer: Timer | None = None
    _fade_start_volume: float = 1.0
    _fade_end_volume: float = 1.0
    _fade_stop_on_done: bool = False

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

    def fade_music_out(self, duration_ms: int) -> None:
        """Fade the currently playing music out, then stop it.

        Replacement for `pygame.mixer.music.fadeout()`, which does not work
        under pygbag web builds.

        Args:
            duration_ms: The duration of the fade in milliseconds.
        """
        Scene._fade_start_volume = pygame.mixer.music.get_volume()
        Scene._fade_end_volume = 0.0
        Scene._fade_stop_on_done = True
        Scene._fade_timer = Timer(duration_ms / 1000)

    def load_music_fade_in(self, path: str, duration_ms: int, loops: int = -1) -> None:
        """Load and play a music track, fading in from silence.

        Replacement for `pygame.mixer.music.load()` followed by
        `pygame.mixer.music.play(fade_ms=...)`, which does not work under
        pygbag web builds.

        Args:
            path: The path to the music file to load.
            duration_ms: The duration of the fade in milliseconds.
            loops: The number of times to loop the music (-1 loops forever).
        """
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0)
        pygame.mixer.music.play(loops=loops)
        Scene._fade_start_volume = 0.0
        Scene._fade_end_volume = 1.0
        Scene._fade_stop_on_done = False
        Scene._fade_timer = Timer(duration_ms / 1000)

    @classmethod
    def update_music_fade(cls) -> None:
        """Advance the in-progress music fade, if any.

        Called once per frame from the main game loop, independent of which
        scene is active, since a fade started just before a scene change
        (e.g. a title screen fading out its music) must keep playing after
        control moves to the new scene.
        """
        if cls._fade_timer is None:
            return
        progress = cls._fade_timer.progress
        volume = cls._fade_start_volume + (cls._fade_end_volume - cls._fade_start_volume) * progress
        pygame.mixer.music.set_volume(volume)
        if cls._fade_timer.done:
            if cls._fade_stop_on_done:
                pygame.mixer.music.stop()
            cls._fade_timer = None

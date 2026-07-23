from src.settings import UGroup, DGroup
from src.core.util import *
import pygame

if TYPE_CHECKING:
    from .scene import Scene

class Sprite[S: Scene](AbstractClass):
    """A base class for all sprites in the game.

    A sprite represents any object that can be updated and drawn.

    Optional hook methods:
    - `update`: Called every frame to update the sprite (default: no-op).
    - `draw`: Called every frame to render the sprite (default: no-op).
    - `draw_hitbox`: Called every frame to render the sprite's hitbox
      (default: no-op).
    - `cleanup`: Called when the sprite is removed from the scene
      (default: no-op).

    Define class variables `update_group` and `draw_group` to specify
    which update and draw groups this sprite belongs to. If either is undefined,
    the sprite will not be updated or drawn respectively.
    """

    update_group: UGroup | None = None
    draw_group: DGroup | None = None

    def __init__(self, scene: S) -> None:
        """Initialize the sprite.

        Args:
            scene: The scene the sprite belongs to.
        """
        self.uuid = scene.sprite_manager.get_next_uuid()
        self.game = ref_proxy(scene.game)
        self.scene: S = ref_proxy(scene)
        self.pos = Vec()
        self.size = Vec()

    def update(self) -> None:
        """Override to update the sprite.

        Called every frame to update the sprite's state. This method can be
        overridden by subclasses to define the sprite's behavior.
        """
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Override to draw the sprite.

        Called every frame to render the sprite to the screen. This method can
        be overridden by subclasses to define the sprite's visuals.

        Args:
            screen: The pygame surface to draw the sprite on.
        """
        pass

    def cleanup(self) -> None:
        """Override to handle sprite removal.

        Called when the sprite is removed from the scene. Override this method
        to perform any necessary cleanup.
        """
        pass

    def _draw_hitbox_wrapper(self, screen: pygame.Surface) -> None:
        """Wrapper to draw the hitbox if enabled.

        Automatically called by the engine to draw debug hitboxes when
        `game.show_hitboxes` is True. Delegates to the `draw_hitbox` method.

        Do not override this method; instead, override `draw_hitbox`.

        Args:
            screen: The pygame surface to draw the hitbox on.
        """
        if self.game.show_hitboxes:
            self.draw_hitbox(screen)

    def draw_hitbox(self, screen: pygame.Surface) -> None:
        """Override to draw the sprite's hitbox.

        Called when hitbox rendering is enabled to visualize the sprite's
        bounding box. Override this method to customize hitbox rendering.

        Args:
            screen: The pygame surface to draw the hitbox on.
        """
        pass

    @property
    def center_pos(self) -> Vec:
        """Get the center position of the sprite in world space.

        This is calculated as `pos + size / 2`, representing the geometric
        center of the sprite's bounding box.

        Returns:
            The center position of the sprite as a Vec.
        """
        return self.pos + self.size / 2

    @property
    def screen_pos(self) -> Vec:
        """Get the screen position of the sprite relative to the camera.

        If the scene has a camera, this is calculated as `pos - camera.pos`,
        converting world coordinates to screen coordinates. If the scene has no
        camera, returns the world position unchanged.

        Returns:
            The screen position of the sprite as a Vec.
        """
        camera = getattr(self.scene, "camera", None)
        if camera is None:
            return self.pos
        return self.pos - camera.pos

    @property
    def screen_center_pos(self) -> Vec:
        """Get the center position of the sprite in screen space.

        Combines the camera-relative position with the sprite's size to
        calculate the center point on screen.

        Returns:
            The center position of the sprite relative to the camera as a Vec.
        """
        return self.screen_pos + self.size / 2

    def __hash__(self) -> int:
        return id(self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}#{self.uuid}"

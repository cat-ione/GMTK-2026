from .timer import Timer
from .debug import *
import pygame

class Animation:
    """A single sequence of frames."""

    def __init__(self,
        frames: list[pygame.Surface], time_per_frame: float
    ) -> None:
        """Initialize the animation.

        Args:
            frame_names: A list of image names for each frame of the animation.
            time_per_frame: The time in second each frame lasts. If negative,
                the animation will stay permanently on the first frame.
        """
        self.frames = frames
        self.time_per_frame = time_per_frame

        self._frame_index = 0
        self._timer = Timer(time_per_frame)

        self._done = False

    @property
    def frame(self) -> pygame.Surface:
        return self.frames[self._frame_index]

    @property
    def done(self) -> bool:
        """Check if animation completed last frame."""
        return self._done

    def update(self) -> None:
        """Update animation by one tick."""
        if self.time_per_frame < 0 or self._done: return

        if self._timer.done:
            if self._frame_index >= len(self.frames) - 1:
                self._done = True
            else:
                self._frame_index += 1
                self._timer.reset()

    def reset(self) -> None:
        """Reset animation to first frame."""
        self._frame_index = 0
        self._timer.reset()
        self._done = False

class AnimationManager:
    """Manages multiple animations for a sprite.

    Call update() every game tick to advance the current animation.
    Call loop() to set a looping animation, or one_shot() to play a one-time
    animation.
    """

    def __init__(self, animations: dict[str, Animation], default: str) -> None:
        """Initialize the animation manager.

        Args:
            animations: A dictionary of animation name to Animation object.
            default: The name of the default animation to loop.
        """
        self.animations = animations
        self.current = animations[default]
        self.current_name = default
        self.looping_anim = animations[default]
        self.looping_name = default
        self.loop_count = 0
        self.one_shot_anim = None

    def loop(self, name: str) -> None:
        """Set an animation to loop continuously.

        This becomes the new base animation that will be returned to after any
        one-shot animation completes.

        Args:
            name: The name of the animation to loop.

        Raises:
            KeyError: If the animation name doesn't exist in this manager.
        """
        try:
            animation = self.animations[name]
        except KeyError:
            raise KeyError(f"Animation '{name}' doesn't exist in manager")

        # If already the looping animation and no one-shot active, do nothing
        if self.looping_anim is animation and self.one_shot_anim is None:
            return

        if self.one_shot_anim is None:
            self.current = animation
            self.current_name = name
            animation.reset()
        self.looping_anim = animation
        self.looping_name = name
        self.loop_count = 0

    def one_shot(self, name: str) -> None:
        """Play through an animation once, then return to the looping animation.

        Args:
            name: The name of the animation to play once.

        Raises:
            KeyError: If the animation name doesn't exist in this manager.
        """
        try:
            animation = self.animations[name]
        except KeyError:
            raise KeyError(f"Animation '{name}' doesn't exist in manager.")

        animation.reset()
        self.loop_count = 0
        self.current = animation
        self.current_name = name
        self.one_shot_anim = animation

    def update(self) -> None:
        """Update the current animation.

        Called every game tick to advance the current animation.
        """
        if self.current is None:
            return

        self.current.update()

        # If one-shot is active and done, return to looping animation
        if self.one_shot_anim is not None:
            if self.one_shot_anim.done:
                if self.looping_anim is not None:
                    self.current = self.looping_anim
                    self.current_name = self.looping_name
                self.one_shot_anim = None
        # If a looping animation is active, loop it if done
        elif self.looping_anim is not None:
            if self.looping_anim.done:
                self.looping_anim.reset()
                self.loop_count += 1

    @property
    def frame(self) -> pygame.Surface:
        """Get the current frame of the active animation."""
        return self.current.frame

    @property
    def one_shot_done(self) -> bool:
        """Check if the current one-shot animation is done.

        Returns:
            True if there is a one-shot animation active and it is done,
            False otherwise.
        """
        if self.one_shot_anim is None:
            return True
        return self.one_shot_anim.done

__all__ = ["Animation", "AnimationManager"]

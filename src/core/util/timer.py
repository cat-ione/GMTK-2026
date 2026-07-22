import time

class Timer:
    """A simple timer class with pause, resume, and progress tracking."""

    def __init__(self, duration: float, paused: bool = False) -> None:
        """Initialize the timer.

        Args:
            duration: The duration of the timer in seconds.
            paused (optional): Whether the timer starts as paused.
        """
        self.reset(duration)
        if paused:
            self.paused = True

    def pause(self) -> bool:
        """Pause the timer.

        Returns:
            True if the timer was paused, False if it was already paused or
            is done.
        """
        if not self.paused and not self.done:
            self.accumulated_time += time.time() - self.start_time
            self.paused = True
            return True
        return False

    def resume(self) -> bool:
        """Resume the timer.

        Returns:
            True if the timer was resumed, False if it was not paused or is
            done.
        """
        if self.paused and not self.done:
            self.start_time = time.time()
            self.paused = False
            return True
        return False

    @property
    def elapsed(self) -> float:
        """Get the elapsed time of the timer.

        Returns:
            The elapsed time in seconds.
        """
        if self.paused: return self.accumulated_time
        new_elapsed = time.time() - self.start_time
        return min(self.accumulated_time + new_elapsed, self.duration)

    @property
    def done(self) -> bool:
        """Check if the timer is done. This means the elapsed time is greater
        than or equal to the duration.

        Returns:
            True if the timer is done, False otherwise.
        """
        return self.elapsed >= self.duration

    def reset(self, duration: float | None = None) -> None:
        """Reset the timer.

        Args:
            duration (optional): The new duration of the timer in seconds. If
                None, the duration is not changed.
        """
        if duration is not None:
            self.duration = duration
        self.start_time = time.time()
        self.accumulated_time = 0
        self.paused = False

    @property
    def progress(self) -> float:
        """Get the progress of the timer.

        Returns:
            The progress as a float between 0.0 and 1.0.
        """
        return self.elapsed / self.duration

    @property
    def progress_remaining(self) -> float:
        """Get the remaining progress of the timer.

        Returns:
            The remaining progress as a float between 0.0 and 1.0.
        """
        return (self.duration - self.elapsed) / self.duration

class LoopTimer(Timer):
    """A timer that automatically loops when done."""

    @property
    def done(self) -> bool:
        """Check if the timer is done. If it is, reset it and return True.

        Effectively, this method will return True for one call when the timer
        completes, and immediately return to False on subsequent calls until
        the timer completes again.

        Returns:
            True if the timer is done, False otherwise.
        """
        if self.elapsed >= self.duration:
            self.reset()
            return True
        return False

__all__ = ["Timer", "LoopTimer"]

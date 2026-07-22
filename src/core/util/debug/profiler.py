from typing import Callable, Any, TYPE_CHECKING
from src.settings import PROFILER_DUMP_DIR
import datetime
import inspect
import pygame
import os

# pygbag hates these two modules probably because they're C modules
# so they have to be explicitly excluded in production
# `or TYPE_CHECKING` to still include them for type checkers not to complain
if __debug__ or TYPE_CHECKING:
    import cProfile
    import pstats

class Profiler:
    """A profiler that can be wrapped around functions to profile them.

    Attributes:
        activated: Whether the profiler is activated, waiting for selection.
        selected: The indices of the selected profilers.
        profilers: The list of all profilers.
        running: Whether the profilers are still running. Setting this to
            True will start the selected profilers, and will be automatically
            set to False when all selected profilers finish.

    Args:
        func: The function to profile.
        save: Whether to save the profile to a file. Defaults to True.
        print: Whether to print the profile to the console. Defaults to False.
    """

    activated = False
    selected: list[int] = []
    profilers: list[Profiler] = []
    running = False

    @classmethod
    def update(cls, key: int) -> None:
        """Update the profiler based on the key pressed.

        If F9 is pressed, toggle the profiler activation state.
        If a number key is pressed and the profiler is activated, select
        or deselect the profiler at that index.
        If 0 is pressed and the profiler is activated, clear all selected
        profilers.

        Args:
            key: The key that was pressed.
        """
        if key == pygame.K_F9:
            Profiler.toggle()
        elif pygame.K_1 <= key <= pygame.K_9 and Profiler.activated:
            Profiler.select(key - pygame.K_0 - 1)
        elif key == pygame.K_0 and Profiler.activated:
            Profiler.clear()

    @classmethod
    def toggle(cls) -> None:
        """Toggle the profiler activation state.

        If activated, print the list of profilers and wait for selection.
        If deactivated, start the selected profilers.
        """
        cls.activated = not cls.activated
        if cls.activated:
            print("Profiler activated, please select profilers:")
            for i, profiler in enumerate(Profiler.profilers):
                print(f"{i + 1}) {profiler.name} (Index: {i})")
            print("Press Backspace to clear selection")
            print("Press F9 again to start selected profilers")
        else:
            print("Starting selected profilers:", Profiler.selected)
            cls.running = True

    @classmethod
    def select(cls, index: int) -> None:
        """Select or deselect a profiler by its index.

        Args:
            index: The index of the profiler to select or deselect.
        """
        if not Profiler.activated:
            print("Profiler is not activated, cannot select profilers")
            return

        if index >= len(Profiler.profilers):
            max_index = len(Profiler.profilers) - 1
            print(f"Profiler at index {index} does not exist, "
                  f"max index is {max_index}")
            return

        profiler = Profiler.profilers[index]

        if index in Profiler.selected:
            Profiler.selected.remove(index)
            print(f"Profiler at index {index} deselected: {profiler.name}")
            return

        Profiler.selected.append(index)
        print(f"Profiler at index {index} selected: {profiler.name}")

    @classmethod
    def clear(cls) -> None:
        """Clear all selected profilers."""
        Profiler.selected = []
        print("All profilers deselected")

    def __init__(self, func: Callable, save: bool = True, print: bool = False) -> None:
        self.func = func
        self.name = func.__name__
        self.save = save
        self.print = print
        self.index = len(Profiler.profilers)
        self.is_async = inspect.iscoroutinefunction(func)

        Profiler.profilers.append(self)

    def __call__(self, *args, **kwargs) -> Any:
        """Profile the function and return its return value.

        This will also save the profile to a file if the save attribute is
        set to True, and print the profile to the console if the print
        attribute is set to True.

        Args:
            *args: The positional arguments to pass to the function.
            **kwargs: The keyword arguments to pass to the function.

        Returns:
            The return value of the function.
        """
        if self.is_async:
            return self._async_call(*args, **kwargs)
        else:
            return self._sync_call(*args, **kwargs)

    def _sync_call(self, *args, **kwargs) -> Any:
        """Profile a synchronous function."""
        if not kwargs.pop("cond", True):
            return self.func(*args, **kwargs)

        if not Profiler.running or self.index not in Profiler.selected:
            return self.func(*args, **kwargs)

        with cProfile.Profile() as pr:
            ret = self.func(*args, **kwargs)

        self._save_profile(pr)
        return ret

    async def _async_call(self, *args, **kwargs) -> Any:
        """Profile an asynchronous function."""
        if not kwargs.pop("cond", True):
            return await self.func(*args, **kwargs)

        if not Profiler.running or self.index not in Profiler.selected:
            return await self.func(*args, **kwargs)

        with cProfile.Profile() as pr:
            ret = await self.func(*args, **kwargs)

        self._save_profile(pr)
        return ret

    def _save_profile(self, pr: cProfile.Profile) -> None:
        """Save and optionally print the profiling results."""
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        if self.print:
            stats.print_stats()

        if self.save:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"{PROFILER_DUMP_DIR}/{self.name}_{timestamp}.prof"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            stats.dump_stats(path)
            print(f"Profile saved to {path}")

        Profiler.selected.remove(self.index)
        print(f"Profiler {self.name} at index {self.index} finished")
        if not Profiler.selected:
            Profiler.running = False
            print("All profilers finished")

__all__ = ["Profiler"]

from src.settings import WATCHER_DUMP_SIZE, WATCHER_DUMP_HISTORY, \
    WATCHER_DUMP_DIR
from src.core.util.debug.logger import info
from typing import Any, TYPE_CHECKING
from datetime import datetime
import json
import os

if TYPE_CHECKING:
    from src.core.engine.game import Game

class Watcher:
    """A simple variable watcher that can be used to track the values of
    variables over time. The watcher keeps a recent history of the values of
    watched variables, and can dump this history to a JSON file.

    The watcher must be initialized first by calling `Watcher.init(game)`.

    Call `Watcher.watch(name, value)` to watch a variable.
    Call `Watcher.step()` to advance the watcher's internal timestamp. This
    should happen once per frame.
    Call `Watcher.dump(exit_status)` to dump the watch history to a JSON file.
    """

    _name: str = "unknown"
    _game: Game | None = None

    values: dict[str, Any] = {}
    history: dict[int, dict[str, Any]] = {}

    @staticmethod
    def init(name: str, game: Game) -> None:
        """Initialize the watcher with the game instance.

        This method must be called before any watching methods are used.

        Args:
            name: The name of the watcher. This is used to differentiate between
                multiple watcher instances.
            game: The game instance to associate with the watcher.
        """
        Watcher._name = name
        Watcher._game = game

    @staticmethod
    def step() -> None:
        """Advance the watcher's internal timestamp. This should happen once per
        frame."""

        assert Watcher._game is not None, \
            "Watcher not initialized. Call Watcher.init(game) first."
        Watcher.history[Watcher._game.frame_count] = {
            "<time>": datetime.now().isoformat()
        }
        oldest_timestamp = Watcher._game.frame_count - WATCHER_DUMP_SIZE
        Watcher.history.pop(oldest_timestamp, None)

    if __debug__:

        @staticmethod
        def watch(name: str, value: Any) -> None:
            """Watch a variable.

            Args:
                name: The name of the variable to watch.
                value: The value of the variable to watch.
            """

            assert Watcher._game is not None, \
                "Watcher not initialized. Call Watcher.init(game) first."
            if name not in Watcher.values:
                info(f"Watcher now watching '{name}' with initial value: {value}")
            Watcher.values[name] = value
            Watcher.history[Watcher._game.frame_count][name] = str(value)

        @staticmethod
        def dump(exit_status: str) -> None:
            """Dump the watcher history to a JSON file.

            The dump files are stored in the `WATCHER_DUMP_DIR` directory,
            storing up to `WATCHER_DUMP_HISTORY` previous dumps.

            Args:
                exit_status: The exit status of the game.
            """

            dump = {
                "exit_time": datetime.now().isoformat(),
                "exit_status": exit_status,
                "history": Watcher.history,
            }

            path = Watcher._save_dump(dump)

            info(f"Watcher history dumped. Check {path} for more details.")

    else:

        @staticmethod
        def watch(name: str, value: Any) -> None:
            """Watch a variable.

            Args:
                name: The name of the variable to watch.
                value: The value of the variable to watch.
            """
            pass

        @staticmethod
        def dump(exit_status: str) -> None:
            """Dump the watcher history to a JSON file.

            The dump files are stored in the `WATCHER_DUMP_DIR` directory,
            storing up to `WATCHER_DUMP_HISTORY` previous dumps.

            Args:
                exit_status: The exit status of the game.
            """
            pass

    @staticmethod
    def _save_dump(dump: dict[str, Any]) -> str:
        if not os.path.exists(WATCHER_DUMP_DIR):
            os.makedirs(WATCHER_DUMP_DIR)

        current_dump_path = os.path.join(
            WATCHER_DUMP_DIR,
            f"latest_{Watcher._name}_watcher_dump.json"
        )

        # Find the existing dump and rename it with a timestamp
        if os.path.exists(current_dump_path):
            Watcher._rename_previous_dump(current_dump_path)

        # Create the latest dump
        with open(current_dump_path, "w") as file:
            json.dump(dump, file, indent=4)

        Watcher._remove_old_dumps()

        return current_dump_path

    @staticmethod
    def _rename_previous_dump(current_dump_path: str) -> None:
        creation_time = os.path.getctime(current_dump_path)
        datetime_str = datetime.fromtimestamp(creation_time)
        datetime_str = datetime_str.strftime("%Y%m%d_%H%M%S")
        new_path = os.path.join(
            WATCHER_DUMP_DIR,
            f"{datetime_str}_{Watcher._name}_watcher_dump.json"
        )
        try:
            os.rename(current_dump_path, new_path)
        except FileExistsError:
            os.remove(new_path)
            os.rename(current_dump_path, new_path)

    @staticmethod
    def _remove_old_dumps() -> None:
        dump_files = [f for f in os.listdir(WATCHER_DUMP_DIR)
                      if f.endswith(f"_{Watcher._name}_watcher_dump.json")]
        while len(dump_files) > WATCHER_DUMP_HISTORY:
            # Remove the oldest dump file if we exceed the maximum history
            oldest = min(dump_files, key=lambda f: os.path.getctime(
                os.path.join(WATCHER_DUMP_DIR, f)))
            os.remove(os.path.join(WATCHER_DUMP_DIR, oldest))
            dump_files.remove(oldest)

watch = Watcher.watch

__all__ = ["watch"]

from src.settings import LOGGER_DUMP_DIR, LOGGER_DUMP_HISTORY
from typing import Any, TYPE_CHECKING
from datetime import datetime
import json
import os

if TYPE_CHECKING:
    from src.core.engine.game import Game

class Logger:
    """A simple logging class that can be used to log messages to the console.

    The class has three logging methods: `debug`, `info`, and `warn`.
    Each method takes a single argument, the message to log. The message will
    be prefixed with the type of message and the current time.

    Call `Logger.dump(exit_status)` to dump the logger history to a JSON file.

    The logger must be initialized first by calling `Logger.init(game)`.
    """

    _HEADER = "\033[95m"
    _OKBLUE = "\033[94m"
    _OKCYAN = "\033[96m"
    _OKGREEN = "\033[92m"
    _WARNING = "\033[93m"
    _FAIL = "\033[91m"
    _ENDC = "\033[0m"
    _BOLD = "\033[1m"
    _UNDERLINE = "\033[4m"

    _INFO_STR = f"{_OKGREEN}INFO{_ENDC}"
    _WARN_STR = f"{_WARNING}WARNING{_ENDC}"
    _ERROR_STR = f"{_BOLD}{_FAIL}CRITICAL{_ENDC}"
    _FORMAT_STR = f"[%s {_UNDERLINE}%s{_ENDC}] %s"

    _name: str = "unknown"
    _game: Game | None = None

    @staticmethod
    def init(name: str, game: Game) -> None:
        """Initialize the logger with the game instance.

        This method must be called before any logging methods are used.

        Args:
            name: The name of the logger. This is used to differentiate between
                multiple logger instances.
            game: The game instance to associate with the logger.
        """
        Logger._name = name
        Logger._game = game

    if __debug__:

        @staticmethod
        def info(*contents: Any) -> None:
            """Log an informational message.

            Args:
                *contents: An arbitrary number of objects to log.
            """

            assert Logger._game is not None, \
                "Logger not initialized. Call Logger.init(game) first."

            time = Logger._datetime()
            content = " ".join(str(x) for x in contents)
            print(Logger._FORMAT_STR % (Logger._INFO_STR, time, content))
            Logger.history.append({
                "level": "info",
                "time": time,
                "tick": Logger._game.frame_count,
                "content": content
            })

        @staticmethod
        def warn(*contents: Any) -> None:
            """Log a warning message.

            Args:
                *contents: An arbitrary number of objects to log.
            """

            assert Logger._game is not None, \
                "Logger not initialized. Call Logger.init(game) first."

            time = Logger._datetime()
            content = " ".join(str(x) for x in contents)
            print(Logger._FORMAT_STR % (Logger._WARN_STR, time, content))
            Logger.history.append({
                "level": "warn",
                "time": time,
                "tick": Logger._game.frame_count,
                "content": content
            })

        @staticmethod
        def error(*contents: Any) -> None:
            """Log an error message.

            Args:
                *contents: An arbitrary number of objects to log.
            """

            assert Logger._game is not None, \
                "Logger not initialized. Call Logger.init(game) first."

            time = Logger._datetime()
            content = " ".join(str(x) for x in contents)
            print(Logger._FORMAT_STR % (Logger._ERROR_STR, time, content))

            Logger.history.append({
                "level": "error",
                "time": time,
                "tick": Logger._game.frame_count,
                "content": content
            })

        @staticmethod
        def dump(exit_status: str) -> None:
            """Dump the logger history to a JSON file.

            The dump files are stored in the `LOGGER_DUMP_DIR` directory,
            storing up to `LOGGER_DUMP_HISTORY` previous dumps.

            Args:
                exit_status: The exit status of the game.
            """

            dump = {
                "exit_time": datetime.now().isoformat(),
                "exit_status": exit_status,
                "history": Logger.history,
            }

            path = Logger._save_dump(dump)

            info(f"Logger history dumped. Check {path} for more details.")

    else:

        @staticmethod
        def info(*contents: Any) -> None:
            """Log an informational message.

            Args:
                *contents: An arbitrary number of objects to log.
            """
            pass

        @staticmethod
        def warn(*contents: Any) -> None:
            """Log a warning message.

            Args:
                *contents: An arbitrary number of objects to log.
            """
            pass

        @staticmethod
        def error(*contents: Any) -> None:
            """Log an error message.

            Args:
                *contents: An arbitrary number of objects to log.
            """
            pass

        @staticmethod
        def dump(exit_status: str) -> None:
            """Dump the logger history to a JSON file.

            The dump files are stored in the `LOGGER_DUMP_DIR` directory,
            storing up to `LOGGER_DUMP_HISTORY` previous dumps.

            Args:
                exit_status: The exit status of the game.
            """
            pass

    @staticmethod
    def _datetime() -> str:
        return datetime.now().strftime("%H:%M:%S.%f")

    history: list[dict[str, str | int]] = []

    @staticmethod
    def _save_dump(dump: dict[str, Any]) -> str:
        if not os.path.exists(LOGGER_DUMP_DIR):
            os.makedirs(LOGGER_DUMP_DIR)

        current_dump_path = os.path.join(
            LOGGER_DUMP_DIR,
            f"latest_{Logger._name}_logger_dump.json"
        )

        # Find the existing dump and rename it with a timestamp
        if os.path.exists(current_dump_path):
            Logger._rename_previous_dump(current_dump_path)

        # Create the latest dump
        with open(current_dump_path, "w") as file:
            json.dump(dump, file, indent=4)

        Logger._remove_old_dumps()

        return current_dump_path

    @staticmethod
    def _rename_previous_dump(current_dump_path: str) -> None:
        creation_time = os.path.getctime(current_dump_path)
        datetime_str = datetime.fromtimestamp(creation_time)
        datetime_str = datetime_str.strftime("%Y%m%d_%H%M%S")
        new_path = os.path.join(
            LOGGER_DUMP_DIR,
            f"{datetime_str}_{Logger._name}_logger_dump.json"
        )
        try:
            os.rename(current_dump_path, new_path)
        except FileExistsError:
            os.remove(new_path)
            os.rename(current_dump_path, new_path)

    @staticmethod
    def _remove_old_dumps() -> None:
        dump_files = [f for f in os.listdir(LOGGER_DUMP_DIR)
                      if f.endswith(f"_{Logger._name}_logger_dump.json")]
        while len(dump_files) > LOGGER_DUMP_HISTORY:
            # Remove the oldest dump file if we exceed the maximum history
            oldest = min(dump_files, key=lambda f: os.path.getctime(
                os.path.join(LOGGER_DUMP_DIR, f)))
            os.remove(os.path.join(LOGGER_DUMP_DIR, oldest))
            dump_files.remove(oldest)

info = Logger.info
warn = Logger.warn
error = Logger.error

__all__ = ["Logger", "info", "warn", "error"]

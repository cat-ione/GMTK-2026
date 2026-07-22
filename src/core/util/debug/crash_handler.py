from src.settings import CRASH_DUMP_DIR, CRASH_DUMP_HISTORY, CRASH_DUMP_IGNORE
from typing import TYPE_CHECKING, Any, Literal
from collections.abc import Iterable
from src.core.util import error
from datetime import datetime
import traceback
import datetime
import weakref
import json
import sys
import os

if TYPE_CHECKING:
    from src.core.engine.game import Game

class CrashHandler:
    """A crash handler that dumps the game state and exception details to a
    JSON file when an unhandled exception occurs.

    Call `CrashHandler.dump(game, exc)` to create a crash dump.
    """

    _name: str = "unknown"

    @staticmethod
    def init(name: str) -> None:
        """Initialize the crash handler with a name for the dumps.

        Args:
            name: The name to use for the crash dumps.
        """
        CrashHandler._name = name

    @staticmethod
    def dump(game: Game, exc: Exception) -> None:
        """Dump a crash report including the exception details and game state,
        to a JSON file.

        The dump files are stored in the `CRASH_DUMP_DIR` directory, storing up
        to `CRASH_DUMP_HISTORY` previous dumps.

        Args:
            game: The game instance to dump.
            exc: The exception instance that was raised.
        """

        exc_type = type(exc).__name__
        exc_msg = str(exc)
        exc_trace = traceback.format_exc()

        error("Game crashed!")
        error(f"Exception Type: {exc_type}")
        error(f"Exception Message: {exc_msg}")
        error(f"Traceback:\n{exc_trace}")

        try:
            stack_locals = CrashHandler._extract_locals()
        except Exception as e:
            error("Failed to extract stack locals:", e)
            stack_locals = {"error": "Failed to extract stack locals."}

        try:
            game_state = CrashHandler._state(game)["state"]
        except Exception as e:
            error("Failed to serialize game state:", e)
            game_state = {"error": "Failed to serialize game state."}

        dump = {
            "exit_time": datetime.datetime.now().isoformat(),
            "frame": game.frame_count,
            "exception": {
                "type": exc_type,
                "message": exc_msg,
                "traceback": exc_trace.splitlines(),
            },
            "stack_locals": stack_locals,
            "game_state": game_state,
        }

        path = CrashHandler._save_dump(dump)

        error(f"Crash dump complete. Check {path} for more details.")

    @staticmethod
    def _extract_locals() -> list[dict[str, Any]]:
        """Extract local variables from each frame in the traceback.

        Returns:
            A list of dicts with frame info and locals as strings.
        """
        frames: list[dict[str, Any]] = []
        tb = sys.exc_info()[2]

        while tb is not None:
            frame = tb.tb_frame
            frame_info: dict[str, Any] = {
                "file": frame.f_code.co_filename,
                "function": frame.f_code.co_name,
                "line": tb.tb_lineno,
                "locals": {}
            }

            for name, value in frame.f_locals.items():
                meta = f"{value.__class__.__name__}#{id(value)}"
                frame_info["locals"][f"{name}<{meta}>"] = str(value)

            frames.append(frame_info)
            tb = tb.tb_next

        return frames

    @staticmethod
    def _state(obj: Any, _visited: set[int] | None = None
               ) -> dict[Literal["meta", "state"], str | Any]:
        """Recursively serialize an object's state.

        Args:
            obj: The object to serialize.
            _visited: A set of visited object IDs to handle circular references.

        Returns:
            A dict containing the meta information of the object and its
            serialized value.
        """

        if _visited is None: _visited = set()

        # Ignore certain manually specified types
        if type(obj).__name__ in CRASH_DUMP_IGNORE:
            return {"meta": "ignored", "state": str(obj)}

        # Special handling for weak references
        if isinstance(obj, weakref.ProxyType):
            try:
                type_name = obj.__class__.__name__
                obj_id = id(obj)
            except ReferenceError:
                type_name = "DeadWeakRef"
                obj_id = "n/a"
            return {
                "meta": f"WeakRef#{obj_id}",
                "state": f"<{type_name}>"
            }

        # Primitives
        if isinstance(obj, (str, int, float, bool, type(None))):
            return {"meta": "", "state": obj}

        # Circular references
        obj_id = id(obj)
        if obj_id in _visited:
            return {
                "meta": "reference",
                "state": f"<{type(obj).__name__}#{obj_id}>"
            }

        # Mark as visited
        _visited.add(obj_id)

        # Dictionaries
        if isinstance(obj, dict):
            value = {}
            for key, val in obj.items():
                meta, state = CrashHandler._state(val, _visited).values()
                value[f"{key}{f"<{meta}>" if meta else ""}"] = state
            return {
                "meta": f"{type(obj).__name__}#{obj_id}",
                "state": value
            }

        # Iterables
        if isinstance(obj, Iterable):
            try:
                return {
                    "meta": f"{type(obj).__name__}#{obj_id}",
                    "state": {
                        # Display iterables as indexed entries, this allows for
                        # meta info on each key if applicable
                        f"<{i}>{f"<{meta}>" if meta else ""}": state
                        for i, (meta, state) in enumerate(map(
                            lambda o: CrashHandler._state(o, _visited).values(),
                            obj
                        ))
                    }
                }
            # Strange Iterables that can't be iterated over
            except: # i.e. pygame.key.ScancodeWrapper
                pass

        # Custom objects
        if hasattr(obj, "__dict__"):
            value: dict[str, Any] = {}
            for key, val in obj.__dict__.items():
                if not key.startswith("__"):
                    meta, state = CrashHandler._state(val, _visited).values()
                    value[f"{key}{f"<{meta}>" if meta else ""}"] = state
            return {
                "meta": f"{type(obj).__name__}#{obj_id}",
                "state": value
            }

        # Fallback
        return {"meta": "unserializable", "state": str(obj)}

    @staticmethod
    def _save_dump(dump: dict[str, Any]) -> str:
        # Ensure dump directory exists
        if not os.path.exists(CRASH_DUMP_DIR):
            os.makedirs(CRASH_DUMP_DIR)

        current_dump_path = os.path.join(
            CRASH_DUMP_DIR,
            f"latest_{CrashHandler._name}_crash_dump.json"
        )

        # Find the existing dump and rename it with a timestamp
        if os.path.exists(current_dump_path):
            CrashHandler._rename_previous_dump(current_dump_path)

        # Create the latest dump
        with open(current_dump_path, "w") as file:
            json.dump(dump, file, indent=4)

        CrashHandler._remove_old_dumps()

        return current_dump_path

    @staticmethod
    def _rename_previous_dump(current_dump_path: str) -> None:
        creation_time = os.path.getctime(current_dump_path)
        datetime_str = datetime.datetime.fromtimestamp(creation_time)
        datetime_str = datetime_str.strftime("%Y%m%d_%H%M%S")
        new_path = os.path.join(
            CRASH_DUMP_DIR,
            f"{datetime_str}_{CrashHandler._name}_crash_dump.json"
        )
        try:
            os.rename(current_dump_path, new_path)
        except FileExistsError:
            os.remove(new_path)
            os.rename(current_dump_path, new_path)

    @staticmethod
    def _remove_old_dumps() -> None:
        dump_files = [f for f in os.listdir(CRASH_DUMP_DIR)
                      if f.endswith(f"_{CrashHandler._name}_crash_dump.json")]
        while len(dump_files) > CRASH_DUMP_HISTORY:
            # Remove the oldest dump file if we exceed the maximum history
            oldest = min(dump_files, key=lambda f: os.path.getctime(
                os.path.join(CRASH_DUMP_DIR, f)))
            os.remove(os.path.join(CRASH_DUMP_DIR, oldest))
            dump_files.remove(oldest)

__all__ = ["CrashHandler"]

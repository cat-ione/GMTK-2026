from enum import Enum, auto
from pathlib import Path

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
DARK_GREEN = (0, 128, 0)

# Logger settings
LOGGER_DUMP_DIR = Path("dumps/logger")
LOGGER_DUMP_HISTORY = 4

# Watcher settings
WATCHER_DUMP_DIR = Path("dumps/watcher")
WATCHER_DUMP_HISTORY = 4
WATCHER_DUMP_SIZE = 10000

# Crash handler settings
CRASH_DUMP_DIR = Path("dumps/crashes")
CRASH_DUMP_HISTORY = 4
CRASH_DUMP_IGNORE = set()

# Profiler settings
PROFILER_DUMP_DIR = Path("dumps/profiles")

# Debug overlay settings
OVERLAY_BG = BLACK
OVERLAY_FG = WHITE
OVERLAY_ALPHA = 128

class DGroup(Enum):
    BACKGROUND = auto()
    PLAYER = auto()
    HUD = auto()

class UGroup(Enum):
    PLAYER = auto()
    HUD = auto()

TITLE = "Pygame"
SIZE = WIDTH, HEIGHT = 200, 150
PX = 6 # Size of a pixel
FPS = 1200

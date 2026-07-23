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
    ROOM = auto()
    HUD = auto()

class UGroup(Enum):
    CAMERA = auto()
    MAIN = auto()
    HUD = auto()

TITLE = "Pygame"
SIZE = WIDTH, HEIGHT = 240, 180
PX = 5 # Size of a pixel
FPS = 60

# Color palette
COLOR1 = (70, 66, 94)
COLOR2 = (21, 120, 140)
COLOR3 = (0, 185, 190)
COLOR4 = (255, 238, 204)
COLOR5 = (255, 176, 163)
COLOR6 = (255, 105, 115)

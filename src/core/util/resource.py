from src.core.util.debug.logger import info
from src.core.util.general import pathof
from dataclasses import dataclass
from typing import Any, ClassVar
from abc import abstractmethod
import pygame
import os

class ResourceMeta(type):
    def __init__(cls, name: str, bases: tuple[type, ...], dct: dict[str, Any]) -> None:
        super().__init__(name, bases, dct)

        if not hasattr(cls, "DIR"):
            raise AttributeError(f"Resource class {cls.__name__} must have a 'DIR' attribute.")

        # Append subclass directory to parent's base directory
        for base in bases:
            if not hasattr(base, "DIR"): continue
            cls.DIR = pathof(os.path.join(base.DIR, cls.DIR))
            break

        # Create copy of instances for each subclass
        cls.instances = {}

@dataclass
class Resource[T](metaclass=ResourceMeta):
    """A resource loaded from disk."""
    DIR = "res"
    instances: ClassVar[dict[str, Resource]] = {}

    @classmethod
    def preload(cls) -> int:
        """Preload all resources."""
        loaded = 0
        for subclass in cls.__subclasses__():
            loaded += subclass.preload()
        for instance in cls.instances.values():
            cls.get(instance.name)
        loaded += len(cls.instances)
        info(f"Preloaded {loaded} {cls.__name__}s.")
        return loaded

    @classmethod
    def get(cls, name: str) -> T:
        """Get a resource by name, loading it if necessary."""
        instance = cls.instances[name]
        if instance.object is None:
            instance.object = instance.load()
        return instance.object

    name: str
    path: str

    def __post_init__(self) -> None:
        self.path = os.path.join(self.DIR, self.path)
        self.object = None
        self.instances[self.name] = self

    @abstractmethod
    def load(self) -> T:
        """Load the resource from disk."""
        pass

@dataclass
class Image(Resource[pygame.Surface]):
    """An image resource."""
    DIR = "images"

    scale: float = 1.0
    convert_alpha: bool = True
    colorkey: tuple[int, int, int] | None = None
    opacity: int = 255

    @staticmethod
    def load_image(
        path: str,
        scale: float,
        convert_alpha: bool,
        colorkey: tuple[int, int, int] | None,
        opacity: int,
    ) -> pygame.Surface:
        if convert_alpha:
            surface = pygame.image.load(path).convert_alpha()
        else:
            surface = pygame.image.load(path).convert()
        if colorkey is not None:
            surface.set_colorkey(colorkey)
        if opacity < 255:
            surface.set_alpha(opacity)
        if scale != 1.0:
            surface = pygame.transform.scale_by(surface, scale)
        return surface

    def load(self) -> pygame.Surface:
        return Image.load_image(
            self.path,
            self.scale,
            self.convert_alpha,
            self.colorkey,
            self.opacity,
        )

@dataclass
class Spritesheet(Resource[list[pygame.Surface]]):
    """A spritesheet resource."""
    DIR = "images"

    columns: int
    rows: int = 1
    scale: float = 1.0
    convert_alpha: bool = True
    colorkey: tuple[int, int, int] | None = None
    opacity: int = 255

    def load(self) -> list[pygame.Surface]:
        full_surface = Image.load_image(
            self.path,
            self.scale,
            self.convert_alpha,
            self.colorkey,
            self.opacity,
        )
        surfaces: list[pygame.Surface] = []

        # Width and height of each subsurface
        width = full_surface.width // self.columns
        height = full_surface.height // self.rows
        for y in range(0, self.rows):
            for x in range(0, self.columns):
                surface = full_surface.subsurface(
                    x * width, y * height,
                    width, height
                )
                surfaces.append(surface)

        return surfaces

@dataclass
class Sound(Resource[pygame.Sound]):
    """A sound resource."""
    DIR = "sounds"

    volume: float = 1.0

    def load(self) -> pygame.Sound:
        sound = pygame.Sound(self.path)
        sound.set_volume(self.volume)
        return sound

@dataclass
class Font(Resource[pygame.Font]):
    """A font resource."""
    DIR = "fonts"

    size: int
    bold: bool = False
    italic: bool = False
    underline: bool = False
    striketrough: bool = False

    def load(self) -> pygame.Font:
        font = pygame.Font(self.path, self.size)
        font.set_bold(self.bold)
        font.set_italic(self.italic)
        font.set_underline(self.underline)
        font.set_strikethrough(self.striketrough)
        return font

__all__ = [
    "Resource",
    "Image",
    "Spritesheet",
    "Sound",
    "Font",
]

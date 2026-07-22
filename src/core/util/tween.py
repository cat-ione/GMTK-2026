from typing import Callable
import modules.pytweening as tween

class Tween:
    def __init__(
        self,
        start: float,
        end: float,
        speed: float,
        func: Callable[[float], float]
    ) -> None:
        self.start = start
        self.end = end
        self.speed = speed
        self.func = func
        self.current = 0.0

    def step(self) -> None:
        self.current = min(self.current + self.speed, 1.0)

    def get(self) -> float:
        return self.start + (self.end - self.start) * self.func(self.current)

    def done(self) -> bool:
        return self.current >= 1.0

__all__ = [
    "Tween",
    "tween",
]

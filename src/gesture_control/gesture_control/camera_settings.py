"""Validated bounded camera requests; drivers may negotiate different values."""
from dataclasses import dataclass
from .validation import finite


@dataclass(frozen=True)
class CameraSettings:
    width: int = 640
    height: int = 480
    fps: float = 30.
    model_complexity: int = 0

    def __post_init__(self):
        if (type(self.width) is not int or not 160 <= self.width <= 1920
                or type(self.height) is not int or not 120 <= self.height <= 1080
                or self.width * self.height > 1920 * 1080
                or not finite(self.fps) or not 5 <= self.fps <= 60
                or type(self.model_complexity) is not int
                or self.model_complexity not in (0, 1)):
            raise ValueError('camera requires 160..1920 x 120..1080, 5..60 fps, model 0/1')

    def matches(self, width, height, fps):
        return (all(finite(v) for v in (width, height, fps))
                and width == self.width and height == self.height
                and self.fps * .9 <= fps <= self.fps * 1.1)

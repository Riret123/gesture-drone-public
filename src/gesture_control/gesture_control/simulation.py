"""Toy 2D horizontal + height landing model; not flight validation."""
import random
from .landing import LandingController


def trial(seed: int, steps: int = 3000) -> bool:
    rng = random.Random(seed)
    x, y, z = rng.uniform(-1, 1), rng.uniform(-1, 1), 2.
    drift_x, drift_y = rng.uniform(-.04, .04), rng.uniform(-.04, .04)
    controller = LandingController()
    dt = .05
    for _ in range(steps):
        command = controller.update((x, y, max(.01, z)), contact=z <= .05)
        if command.state == 'touchdown':
            return True
        if command.state == 'abort':
            return False
        # Relative marker error decreases with camera-plane velocity.
        x += (drift_x - command.vx + rng.gauss(0, .02)) * dt
        y += (drift_y - command.vy + rng.gauss(0, .02)) * dt
        z -= command.descent * dt
    return False


def batch(count: int = 100, seed: int = 0) -> dict:
    if type(count) is not int or count <= 0:
        raise ValueError('positive integer count required')
    successes = sum(trial(seed + i) for i in range(count))
    return dict(trials=count, successes=successes, rate=successes / count)

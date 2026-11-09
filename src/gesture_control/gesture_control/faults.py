"""Deterministic landing fault campaign, exercising proposal-level aborts only."""
from .landing import LandingController


def campaign() -> dict:
    outcomes = {}
    for name, bad in (('lost_tag', None), ('invalid_height', (0, 0, -1)),
                      ('nonfinite_pose', (float('nan'), 0, 1))):
        controller = LandingController()
        controller.update((0, 0, 1))
        command = controller.update(bad)
        outcomes[name] = command.state == 'abort' and command.descent == 0
    controller = LandingController()
    outcomes['false_contact'] = controller.update((0, 0, 2), contact=True).state == 'abort'
    controller = LandingController()
    command = controller.update((1, 0, .1))
    outcomes['lateral_error_stops_descent'] = command.state == 'align' and command.descent == 0
    return outcomes

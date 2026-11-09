"""Seeded adversarial replay campaign; no middleware or flight dynamics."""
from pathlib import Path
import random
import unittest
from drone_bringup.deterministic_replay import Frame, ReplayHarness, read_landmark_csv


FIXTURE = Path(__file__).parent / 'fixtures/core_landmarks_synthetic.csv'


class ReplayRecoveryCampaignTests(unittest.TestCase):
    def test_every_missing_or_duplicated_landmark_rejects(self):
        lines = FIXTURE.read_text().splitlines()
        # Mutate every actual landmark row independently, preserving CSV syntax.
        self.assertGreater(len(lines), 21)
        for index in range(1, len(lines)):
            for mutation in ('missing', 'duplicate'):
                with self.subTest(row=index, mutation=mutation):
                    changed = lines[:]
                    if mutation == 'missing':
                        del changed[index]
                    else:
                        changed.insert(index, changed[index])
                    with self.assertRaises(ValueError):
                        read_landmark_csv('\n'.join(changed) + '\n')

    def test_seeded_camera_events_cannot_rearm_latched_chain(self):
        frames = read_landmark_csv(FIXTURE.read_text())
        opened, fist = frames[0].hands, frames[-1].hands
        rng = random.Random(930783455)
        harness = ReplayHarness()
        for frame in frames[:2]:
            harness.frame(frame)
        harness.command('emergency')
        boundary = len(harness.services)
        options = (opened, fist, (), (fist[0], fist[0]),
                   (opened[0], fist[0]))
        for index in range(1, 2001):
            harness.frame(Frame(.2 + index * .1, rng.choice(options)))
            if index % 13 == 0:
                harness.command('open_palm')
            if index % 17 == 0:
                harness.command('hold')
        for _, operation, value in harness.services[boundary:]:
            self.assertNotIn(operation, ('arm', 'takeoff'))
            self.assertNotEqual((operation, value), ('set_mode', 'GUIDED'))

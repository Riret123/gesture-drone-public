from pathlib import Path
from types import SimpleNamespace
import unittest
from drone_bringup.deterministic_replay import Frame, ReplayHarness, read_landmark_csv
from gesture_control.frame_classifier import classify_frame
from gesture_control.pose_features import PoseProfile
from test_pose_features import pose


FIXTURE = Path(__file__).resolve().parent / 'fixtures/core_landmarks_synthetic.csv'


class DeterministicReplayTests(unittest.TestCase):
    def setUp(self):
        self.frames = read_landmark_csv(FIXTURE.read_text())
        self.opened, self.fist = self.frames[0].hands, self.frames[-1].hands

    def flight(self):
        harness = ReplayHarness()
        for frame in self.frames[:2]:
            harness.frame(frame)
        return harness

    def test_normal_csv_flight_and_landing_latch(self):
        harness = ReplayHarness()
        for frame in self.frames:
            harness.frame(frame)
        self.assertEqual([command for _, command in harness.commands], ['open_palm', 'fist'])
        self.assertEqual([name for _, name, _ in harness.services],
                         ['set_mode', 'arm', 'takeoff', 'land'])
        self.assertTrue(harness.state.armed)  # Landing ACK is not touchdown.
        self.assertFalse(harness.command('open_palm')[0])

    def test_lost_hand_has_exact_hold_then_land(self):
        harness = self.flight()
        harness.frame(Frame(2.2, ()))
        harness.frame(Frame(5.2, ()))
        self.assertEqual(harness.commands, [(.2, 'open_palm'), (2.2, 'hold'), (5.2, 'land')])
        self.assertEqual(harness.services[-2:], [(2.2, 'set_mode', 'LOITER'), (5.2, 'land', None)])

    def test_flicker_abstains_and_does_not_arm(self):
        harness = ReplayHarness()
        for index in range(1, 20):
            harness.frame(Frame(index / 10, self.opened if index % 2 else self.fist))
        self.assertEqual(harness.services, [])
        harness.frame(Frame(2., ()))
        self.assertEqual(harness.commands, [(2., 'hold')])

    def test_two_fists_bypass_debounce(self):
        harness = self.flight()
        harness.frame(Frame(.3, (self.fist[0], self.fist[0])))
        self.assertEqual(harness.commands[-1], (.3, 'emergency'))
        self.assertEqual(harness.services[-1], (.3, 'land', None))

    def test_rc_battery_and_link_loss_are_explicit_supervisor_events(self):
        for fault in ('rc-loss', 'battery-low', 'fc-link-loss'):
            harness = self.flight()
            result = harness.safety_event(fault)
            self.assertEqual(result[0], fault != 'fc-link-loss')
            self.assertFalse(harness.command('open_palm')[0])
            self.assertEqual(harness.services[-1][1:], ('land', None))

    def test_duplicates_cannot_escape_landing(self):
        harness = self.flight()
        harness.command('land')
        before = len(harness.services)
        for _ in range(100):
            self.assertFalse(harness.command('open_palm')[0])
            self.assertFalse(harness.command('hold')[0])
        self.assertEqual(len(harness.services), before)

    def test_malformed_csv_rejects(self):
        text = FIXTURE.read_text()
        for payload in (text.replace('time,hand', 'stamp,hand'),
                        text + '0.1,0,0,0,0,0\n',
                        text.replace('0.1,0,0,0,0,0', 'nan,0,0,0,0,0'),
                        text.replace('0.1,0,0,0,0,0\n', ''),
                        text.replace('0.1,0,0,0,0,0', '0.1,2,0,0,0,0'),
                        text.replace('0.1,0,0,0,0,0', '0.1,-1,-1,,,')):
            with self.assertRaises(ValueError):
                read_landmark_csv(payload)

    def test_empty_frame_csv(self):
        frames = read_landmark_csv('time,hand,index,x,y,z\n0,-1,-1,,,\n')
        self.assertEqual(frames, (Frame(0., ()),))

    def test_csv_decoder_errors_are_bounded_value_errors(self):
        for payload in ('time,hand,index,x,y,z\n0,0,0,"unterminated',
                        'time,hand,index,x,y,z\n0,0,0,' + '1' * 140000 + ',0,0',
                        'x' * 140000):
            with self.assertRaises(ValueError):
                read_landmark_csv(payload)

    def test_world_profile_gates_orientation_and_missing_outputs(self):
        images = [[SimpleNamespace(x=p[0], y=p[1]) for p in self.opened[0]]]
        for opened, expected in ((True, 'open_palm'), (False, 'fist')):
            world = [[(-x, y, -z) for x, y, z in pose(opened)]]
            self.assertEqual(classify_frame(images, world_hands=world, profile=PoseProfile()), [expected])
        self.assertEqual(classify_frame(images, profile=PoseProfile()), [])
        self.assertEqual(classify_frame(images * 3), [])

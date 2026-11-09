import unittest
from drone_bringup.sitl_scenarios import run_scenario, SCENARIOS


class ScenarioTransport:
    def __init__(self):
        self.events = []
        self.accept = True
        self.observe = True

    def command(self, command):
        self.events.append(('command', command))
        return self.accept

    def expect(self, condition, timeout):
        self.events.append(('expect', condition, timeout))
        return self.observe

    def fault(self, name):
        self.events.append(('fault', name))
        return self.accept


class SitlScenarioTests(unittest.TestCase):
    def test_all_scenarios_have_observed_landing(self):
        for name in SCENARIOS:
            transport = ScenarioTransport()
            self.assertTrue(run_scenario(name, transport)[0])
            self.assertEqual(transport.events[-1], ('expect', 'landed_disarmed', 60.))

    def test_rejection_does_not_advance_takeoff(self):
        transport = ScenarioTransport()
        transport.accept = False
        self.assertFalse(run_scenario('takeoff', transport)[0])
        self.assertEqual(transport.events, [('expect', 'connected_disarmed', 10.),
                                           ('command', 'open_palm')])

    def test_missing_initial_state_sends_nothing(self):
        transport = ScenarioTransport()
        transport.observe = False
        self.assertFalse(run_scenario('hold', transport)[0])
        self.assertFalse(any(event[0] == 'command' for event in transport.events))

    def test_rc_loss_requires_fault_injection_and_fc_transition(self):
        transport = ScenarioTransport()
        self.assertTrue(run_scenario('rc-loss', transport)[0])
        self.assertIn(('fault', 'rc_loss'), transport.events)
        self.assertIn(('expect', 'configured_rc_failsafe', 15.), transport.events)

    def test_unknown_scenario_rejects_before_io(self):
        transport = ScenarioTransport()
        with self.assertRaises(ValueError):
            run_scenario('arm-real', transport)
        self.assertEqual(transport.events, [])

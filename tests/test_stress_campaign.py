import importlib.util
from pathlib import Path
import unittest


class StressCampaignTests(unittest.TestCase):
    def test_seeded_model_and_thread_campaign(self):
        path = Path(__file__).resolve().parents[1] / 'tools/stress_core.py'
        spec = importlib.util.spec_from_file_location('offline_stress_fixture', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for seed in (17, 20261109):
            campaign = module.Campaign(seed)
            for _ in range(25):
                campaign.case()
            self.assertEqual(campaign.commands, 2500)
            self.assertEqual(campaign.geometry, 100)
            self.assertEqual(campaign.thread_trials, 1)
        self.assertTrue(all(len(value) == 64 for value in module.manifest().values()))

import unittest
from gesture_control.camera_settings import CameraSettings


class CameraSettingsTests(unittest.TestCase):
    def test_defaults_and_supported_envelopes(self):
        self.assertEqual(CameraSettings().fps, 30.)
        for model in (0, 1):
            for fps in (5, 15., 30., 60):
                CameraSettings(160, 120, fps, model)
                CameraSettings(1920, 1080, fps, model)

    def test_negotiated_profile_settings_fail_closed(self):
        settings = CameraSettings()
        self.assertTrue(settings.matches(640., 480., 29.97))
        for values in ((320, 240, 30), (640, 480, 0), (640, 480, 15),
                       (640, 480, float('nan')), (True, 480, 30)):
            self.assertFalse(settings.matches(*values))

    def test_malformed_and_extreme_configuration(self):
        for field, values in {
                'width': (True, 159, 1921, 640., '640'),
                'height': (False, 119, 1081, 480.),
                'fps': (True, 4.9, 60.1, float('nan'), float('inf'), '30', 10**1000),
                'model_complexity': (True, -1, 2, 0., '0')}.items():
            for value in values:
                with self.subTest(field=field, value=str(value)[:20]):
                    with self.assertRaises(ValueError):
                        CameraSettings(**{field: value})

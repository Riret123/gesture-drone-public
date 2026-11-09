from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.display_text import bounded_text
from gesture_control.telemetry_contract import decode_telemetry
from gesture_control.replay_analysis import analyze_events


class DisplayTextTests(unittest.TestCase):
    def test_ru_en_and_emoji_remain_valid(self):
        self.assertTrue(bounded_text('СИМ / SIM 🚁',1,64))

    def test_direction_overrides_and_isolates_reject(self):
        for code in [0x061C,0x200E,0x200F,*range(0x202A,0x202F),*range(0x2066,0x206A)]:
            self.assertFalse(bounded_text('SIM'+chr(code)+'SAFE',1,64))

    def test_ascii_and_c1_controls_reject(self):
        for code in [*range(32),*range(127,160)]:
            self.assertFalse(bounded_text(chr(code),0,64))

    def test_unpaired_surrogates_reject(self):
        for value in ['\ud800','\udfff','a\ud800b']:
            self.assertFalse(bounded_text(value,1,64))

    def test_text_type_and_codepoint_bounds(self):
        self.assertTrue(bounded_text('🚁'*64,1,64))
        self.assertFalse(bounded_text('🚁'*65,1,64))
        self.assertFalse(bounded_text(True,0,64))
        self.assertFalse(bounded_text('',1,64))

    def test_json_escape_surrogate_cannot_bypass_decoder(self):
        source='{"schema":1,"mock":true,"age":0,"mode":"\\ud800","battery":50,"deadman":false,"acks":[]}'
        self.assertEqual(decode_telemetry(source,0,0,1).status,'INVALID')

    def test_replay_cannot_export_spoofed_direction_label(self):
        with self.assertRaises(ValueError):
            analyze_events([dict(time=0,mode='SAFE\u202e',battery=50,ack='')],gap_s=1)

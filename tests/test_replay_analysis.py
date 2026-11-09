from pathlib import Path
import sys
import io
import json
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.replay_analysis import analyze_events, read_jsonl


def event(time=0, mode='SIM', battery=50, ack=''):
    return dict(time=time, mode=mode, battery=battery, ack=ack)


class ReplayAnalysisTests(unittest.TestCase):
    def test_empty_is_explicit_without_fake_battery(self):
        result = analyze_events([], gap_s=1)
        self.assertEqual(result.count, 0)
        self.assertIsNone(result.battery_min_percent)

    def test_single_event_has_no_inferred_duration(self):
        result = analyze_events([event(10)], gap_s=1)
        self.assertEqual(result.duration_s, 0)
        self.assertEqual(result.mode_dwell_s, ())

    def test_dwell_and_changes_have_independent_oracle(self):
        result = analyze_events([event(0,'A',90), event(2,'B',80,'OK'),
                                 event(5,'B',85), event(6,'C',70)], gap_s=3)
        self.assertEqual(result.duration_s, 6)
        self.assertEqual(dict(result.mode_dwell_s), {'A':2,'B':4})
        self.assertEqual(result.mode_transitions, 2)
        self.assertEqual(result.gap_intervals, ((2,5),))
        self.assertEqual(result.battery_change_points, -20)
        self.assertEqual(result.battery_min_percent, 70)
        self.assertEqual(result.battery_max_percent, 90)
        self.assertEqual(result.acknowledgement_rows, 1)

    def test_duplicates_count_without_infinite_rate(self):
        result = analyze_events([event(0), event(0,'B'), event(1)], gap_s=1)
        self.assertEqual(result.repeated_timestamps, 1)
        self.assertEqual(result.mode_transitions, 2)

    def test_reversal_rejects_instead_of_sorting(self):
        with self.assertRaises(ValueError):
            analyze_events([event(1),event(0)], gap_s=1)

    def test_boolean_nonfinite_overflow_and_string_numbers_reject(self):
        for key in ('time','battery'):
            for value in (True, '1', float('nan'), float('inf'), 10**10000):
                with self.subTest(key=key, type=type(value)), self.assertRaises(ValueError):
                    row = event(); row[key] = value
                    analyze_events([row], gap_s=1)

    def test_unknown_fields_and_control_text_reject(self):
        for row in [dict(event(),command='land'),event(mode=''),event(ack='x\ny'),
                    event(ack='x'*257), [], None]:
            with self.assertRaises(ValueError):
                analyze_events([row], gap_s=1)

    def test_event_budget_exact_boundary(self):
        self.assertEqual(analyze_events([event()],gap_s=1,max_events=1).count,1)
        with self.assertRaises(ValueError):
            analyze_events([event(),event()],gap_s=1,max_events=1)

    def test_invalid_limits(self):
        for threshold in [True,0,-1,float('nan')]:
            with self.assertRaises(ValueError):
                analyze_events([],gap_s=threshold)
        for maximum in [False,0,100001]:
            with self.assertRaises(ValueError):
                analyze_events([],gap_s=1,max_events=maximum)

    def test_reports_do_not_classify_ack_as_completed_flight(self):
        result = analyze_events([event(ack='arm command accepted')],gap_s=1)
        self.assertEqual(result.acknowledgement_rows,1)
        self.assertFalse(hasattr(result,'airborne'))


class ReplayReaderTests(unittest.TestCase):
    def test_text_and_binary_utf8_streams(self):
        source=json.dumps(event(mode='СИМ'),ensure_ascii=False)+'\n'
        for stream in (io.StringIO(source),io.BytesIO(source.encode('utf-8'))):
            self.assertEqual(list(read_jsonl(stream))[0]['mode'],'СИМ')
            self.assertFalse(stream.closed)

    def test_duplicate_key_rejects(self):
        source=json.dumps(event()).replace('"time": 0','"time": 0, "time": 0')
        with self.assertRaises(ValueError):
            list(read_jsonl(io.StringIO(source)))

    def test_byte_line_budget_and_invalid_encoding(self):
        for stream in [io.StringIO('x'*20),io.BytesIO(b'\xff\n'),
                       io.StringIO(json.dumps(event(mode='中'*10),ensure_ascii=False))]:
            with self.assertRaises(ValueError):
                list(read_jsonl(stream,max_line_bytes=10))

    def test_blank_constants_and_nested_input(self):
        for source in ['\n',json.dumps(event()).replace('"battery": 50','"battery": NaN'),
                       '['*1100+'0'+']'*1100]:
            with self.assertRaises(ValueError):
                list(read_jsonl(io.StringIO(source)))

    def test_chronology_and_count_caps(self):
        source='\n'.join(json.dumps(event(t)) for t in (1,0))
        with self.assertRaises(ValueError):
            list(read_jsonl(io.StringIO(source)))
        source='\n'.join(json.dumps(event(t)) for t in (0,1))
        with self.assertRaises(ValueError):
            list(read_jsonl(io.StringIO(source),max_events=1))

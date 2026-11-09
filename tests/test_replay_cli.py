from pathlib import Path
import sys
import io
import json
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'tools'))
from analyze_replay import main


class ReplayCLITests(unittest.TestCase):
    def run_cli(self, source, *extra):
        calls=[]
        def opener(path, mode):
            calls.append((str(path), mode))
            return io.BytesIO(source)
        output, errors=io.StringIO(),io.StringIO()
        code=main(['synthetic.jsonl','--gap','1',*extra],opener=opener,
                  output=output,errors=errors)
        return code,output.getvalue(),errors.getvalue(),calls

    def test_valid_report_is_json_and_marked_offline(self):
        source=json.dumps(dict(time=0,mode='SIM',battery=50,ack='')).encode()
        code,output,errors,calls=self.run_cli(source)
        self.assertEqual(code,0)
        report=json.loads(output)
        self.assertFalse(report['flight_validated'])
        self.assertFalse(report['causal_diagnosis'])
        self.assertEqual(report['summary']['count'],1)
        self.assertEqual(errors,'')
        self.assertEqual(calls,[('synthetic.jsonl','rb')])

    def test_bad_later_row_does_not_emit_partial_report(self):
        source=json.dumps(dict(time=0,mode='SIM',battery=50,ack='')).encode()+b'\n{}'
        code,output,errors,_=self.run_cli(source)
        self.assertEqual(code,2)
        self.assertEqual(output,'')
        self.assertIn('no report',errors)

    def test_raw_ack_text_never_printed_in_error_or_summary(self):
        raw='UNTRUSTED_EXTERNAL_TEXT'
        source=json.dumps(dict(time=0,mode='SIM',battery=50,ack=raw)).encode()
        code,output,errors,_=self.run_cli(source)
        self.assertEqual(code,0)
        self.assertNotIn(raw,output+errors)

    def test_missing_file_error_has_no_traceback_or_path_echo(self):
        def missing(*args):
            raise OSError('attacker controlled failure message')
        output,errors=io.StringIO(),io.StringIO()
        code=main(['missing','--gap','1'],opener=missing,output=output,errors=errors)
        self.assertEqual(code,2)
        self.assertEqual(output.getvalue(),'')
        self.assertNotIn('attacker',errors.getvalue())

    def test_analysis_resource_limits_reject(self):
        for extra in [('--gap','0'),('--max-events','0'),('--max-line-bytes','0')]:
            code,output,errors,_=self.run_cli(b'',*extra)
            self.assertEqual(code,2)
            self.assertEqual(output,'')

    def test_blank_log_is_explicitly_empty(self):
        code,output,errors,_=self.run_cli(b'')
        self.assertEqual(code,0)
        self.assertEqual(json.loads(output)['summary']['count'],0)

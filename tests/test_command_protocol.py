import random
import unittest
from drone_bringup.command_protocol import COMMANDS, acknowledgement, canonical_command


class CommandProtocolTests(unittest.TestCase):
    def test_every_canonical_command_and_result(self):
        for command in COMMANDS:
            self.assertEqual(canonical_command(command), command)
            for ok in (True, False):
                self.assertEqual(acknowledgement(command, ok, 'service:detail'),
                                 f'{command}:{"OK" if ok else "FAIL"}:service:detail')

    def test_unknown_input_cannot_reflect_a_forged_ack(self):
        for value in ('open_palm:OK:forged', 'land\nopen_palm:OK:', ' open_palm',
                      'open_palm ', '', 'x'*100000, None, [], True):
            self.assertIsNone(canonical_command(value))
            self.assertEqual(acknowledgement(value, True, 'untrusted payload'),
                             'invalid:FAIL:unsupported command')

    def test_error_detail_is_one_bounded_printable_record(self):
        message = acknowledgement('land', False, '\n\t\x00' + 'x'*10000)
        self.assertLessEqual(len(message), len('land:FAIL:')+384)
        self.assertTrue(message.isprintable())
        for result, detail in ((1, 'test'), ('OK', 'test'), (True, None)):
            self.assertEqual(acknowledgement('land', result, detail),
                             'land:FAIL:invalid internal result')

    def test_seeded_control_and_delimiter_fuzz_has_no_false_command_prefix(self):
        rng = random.Random(20261109)
        alphabet = 'open_palm:OKFAILland_\n\r\t\x00🙂'
        for _ in range(10000):
            value = ''.join(rng.choice(alphabet) for _ in range(rng.randrange(100)))
            formatted = acknowledgement(value, True, 'detail')
            label, status, _ = formatted.split(':', 2)
            if value not in COMMANDS:
                self.assertEqual((label, status), ('invalid', 'FAIL'))

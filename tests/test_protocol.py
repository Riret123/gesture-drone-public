import unittest
from gesture_control.protocol import encode, decode


class ProtocolTests(unittest.TestCase):
    def test_roundtrip(self):
        self.assertEqual(decode(encode(4, 'hold'))['seq'], 4)
        self.assertEqual(decode(encode(5, 'follow', .2, -1))['linear'], .2)

    def test_rejections(self):
        for raw in (b'{}', b'[]', b'x', b'x'*1025,
                    encode(1, 'hold').replace(b'hold', b'evil'),
                    encode(1, 'hold').replace(b'"version":1', b'"version":2'),
                    b'{"seq":1,"seq":2}'):
            with self.assertRaises(ValueError):
                decode(raw)
        for seq in (-1, True, 2**32):
            with self.assertRaises(ValueError):
                encode(seq, 'hold')
        with self.assertRaises(ValueError):
            encode(1, 'follow', float('nan'))

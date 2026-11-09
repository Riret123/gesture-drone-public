import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import json
from pathlib import Path
import threading
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from gesture_control.mock_server import handler


class MockTests(unittest.TestCase):
    def test_loopback_http_contract(self):
        root = Path(__file__).resolve().parents[1]
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler(root))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        try:
            with urlopen(base + '/telemetry', timeout=2) as response:
                self.assertTrue(json.load(response)['mock'])
                self.assertEqual(response.headers['Cache-Control'], 'no-store')
            with urlopen(base, timeout=2) as response:
                self.assertIn(b'/flight_cmd_ack', response.read())
            with self.assertRaises(HTTPError):
                urlopen(base + '/../AGENTS.md', timeout=2)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(2)

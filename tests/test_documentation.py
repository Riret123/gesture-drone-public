import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class IDs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        self.ids.extend(value for name, value in attrs if name == 'id')


class DocumentationTests(unittest.TestCase):
    def test_readme_local_links(self):
        for name in ('README.md', 'README_RU.md'):
            path = ROOT / name
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if '://' not in target:
                    self.assertTrue((path.parent / target.split('#')[0]).is_file(), target)

    def test_interface_ids_and_readonly_transport(self):
        for name in ('quest/index.html', 'dashboard/index.html'):
            source = (ROOT / name).read_text(encoding='utf-8')
            parser = IDs()
            parser.feed(source)
            self.assertEqual(len(parser.ids), len(set(parser.ids)), name)
            for key in ('link', 'mode', 'battery', 'deadman'):
                self.assertIn(key, parser.ids)
            self.assertNotIn('innerHTML', source)
            self.assertNotIn('WebSocket', source)
            self.assertNotIn("method:'POST'", source)

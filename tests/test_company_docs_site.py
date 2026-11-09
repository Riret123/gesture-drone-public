"""Integration checks for checked-in static documentation, not browser QA."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from company_docs_audit import audit_site


class CompanyDocsSiteTests(unittest.TestCase):
    def test_checked_in_site_links_and_static_policy(self):
        self.assertEqual(audit_site(ROOT), [])

    def test_russian_page_preserves_cyrillic_after_windows_writes(self):
        source = (ROOT / 'docs/site/ru.html').read_text(encoding='utf-8')
        self.assertGreater(sum(0x400 <= ord(ch) <= 0x4ff for ch in source), 500)
        self.assertIn('\u041d\u0435 \u0430\u0440\u043c\u0438\u0442\u044c', source)
        self.assertNotIn('????', source)

    def test_glossary_preserves_cyrillic(self):
        source = (ROOT / 'docs/company/devrel/GLOSSARY_EN_RU.md').read_text(encoding='utf-8')
        self.assertGreater(sum(0x400 <= ord(ch) <= 0x4ff for ch in source), 100)
        self.assertNotIn('????', source)

    def test_local_styles_have_no_external_dependencies(self):
        source = (ROOT / 'docs/site/site.css').read_text(encoding='utf-8').lower()
        self.assertNotIn('@import', source)
        self.assertNotIn('url(', source)


if __name__ == '__main__':
    unittest.main()

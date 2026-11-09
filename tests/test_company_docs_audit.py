"""Pure source-audit checks; no HTTP, hardware, ROS, or temporary files."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from company_docs_audit import Page, audit_pages, relative_target


def html(body='', lang='en'):
    return f'<html lang="{lang}"><head><title>Evidence</title></head><body><main>{body}</main></body></html>'


class CompanyDocsAuditTests(unittest.TestCase):
    def test_relative_repository_source_link(self):
        self.assertEqual(relative_target('docs/site/index.html', '../../README.md'),
                         ('README.md', ''))

    def test_fragment_and_query(self):
        self.assertEqual(relative_target('docs/site/index.html', '#evidence'),
                         ('docs/site/index.html', 'evidence'))
        self.assertEqual(relative_target('docs/site/index.html', 'guide.html?v=1#units'),
                         ('docs/site/guide.html', 'units'))

    def test_percent_encoded_unicode_and_spaces(self):
        self.assertEqual(relative_target('docs/site/index.html', '%D1%82%D0%B5%D1%81%D1%82.html#two%20words'),
                         ('docs/site/тест.html', 'two words'))

    def test_external_links_are_classified_without_fetch(self):
        for link in ('https://example.org/a', 'http://example.org/b'):
            self.assertIsNone(relative_target('docs/site/index.html', link))

    def test_schemes_and_absolute_paths_reject(self):
        for link in ('javascript:alert(1)', 'data:text/html,x', 'file:///tmp/x',
                     '//example.org/x', '/README.md', 'C:/file', 'https:/missing-host'):
            with self.subTest(link=link), self.assertRaises(ValueError):
                relative_target('docs/site/index.html', link)

    def test_parent_escape_and_protected_targets_reject(self):
        for link in ('../../../outside', '../../network/config', '../../.git/config',
                     '../../NETWORK/config', '../../.aws/config', '../../.codex/a'):
            with self.subTest(link=link), self.assertRaises(ValueError):
                relative_target('docs/site/index.html', link)

    def test_encoded_protected_path_rejects_before_exists(self):
        calls = []
        issues = audit_pages({'docs/site/index.html': html('<a href="../../%6eetwork/x">x</a>')},
                             lambda path: calls.append(path) or True)
        self.assertEqual(calls, [])
        self.assertEqual([item.code for item in issues], ['unsafe_reference'])

    def test_backslash_control_and_alternate_stream_reject(self):
        for link in ('..\\README.md', 'bad\x00path', 'a%00b', 'a%5Cb', 'a%3Ab'):
            with self.subTest(link=link), self.assertRaises(ValueError):
                relative_target('docs/site/index.html', link)

    def test_malformed_url_and_encoding_reject(self):
        for link in ('https://[bad', 'bad%2', 'bad%xx', '%FF.html'):
            with self.subTest(link=link), self.assertRaises(ValueError):
                relative_target('docs/site/index.html', link)

    def test_empty_type_and_size_reject(self):
        for link in (None, 1, '', 'a' * 4097):
            with self.subTest(link=type(link).__name__), self.assertRaises(ValueError):
                relative_target('docs/site/index.html', link)

    def test_valid_internal_navigation(self):
        sources = {'docs/site/index.html': html('<a href="guide.html#units">guide</a>'),
                   'docs/site/guide.html': html('<h1 id="units">Units</h1>')}
        self.assertEqual(audit_pages(sources, lambda path: path in sources), [])

    def test_missing_target_is_reported(self):
        issues = audit_pages({'docs/site/index.html': html('<a href="missing.md">x</a>')},
                             lambda path: False)
        self.assertEqual([item.code for item in issues], ['missing_target'])

    def test_missing_fragment_is_reported(self):
        sources = {'docs/site/index.html': html('<a href="#absent">x</a>')}
        issues = audit_pages(sources, lambda path: path in sources)
        self.assertEqual([item.code for item in issues], ['missing_fragment'])

    def test_duplicate_and_empty_identifiers(self):
        page = Page(html('<p id="x"></p><p id="x"></p><p id=""></p>'))
        self.assertEqual([code for code, _ in page.problems],
                         ['duplicate_or_empty_id', 'duplicate_or_empty_id'])

    def test_active_tags_reject(self):
        for tag in ('script', 'iframe', 'object', 'embed', 'form', 'base'):
            page = Page(html(f'<{tag}></{tag}>'))
            self.assertIn(('active_content', tag), page.problems)

    def test_event_handlers_reject(self):
        page = Page(html('<img src="a.png" onerror="x()">'))
        self.assertIn(('event_handler', 'img'), page.problems)

    def test_meta_refresh_rejects(self):
        page = Page(html('<meta http-equiv="REFRESH" content="0;url=x">'))
        self.assertIn(('redirect', 'meta refresh'), page.problems)

    def test_duplicate_attributes_reject(self):
        page = Page(html('<a href="a" href="b">x</a>'))
        self.assertIn(('duplicate_attribute', 'a'), page.problems)

    def test_language_and_landmarks(self):
        issues = audit_pages({'docs/site/a.html': '<html><body>draft</body></html>'},
                             lambda path: True)
        self.assertEqual({item.code for item in issues}, {'language', 'structure'})

    def test_russian_page_is_supported(self):
        self.assertEqual(audit_pages({'docs/site/ru.html': html('Проверка', 'ru')},
                                    lambda path: True), [])


if __name__ == '__main__':
    unittest.main()

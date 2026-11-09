"""Audit the local evidence site without fetching URLs or reading protected trees.

Only HTML under docs/site is read. Relative target existence is checked inside
the repository, excluding network and metadata/credential directories. This is
a source audit, not a browser, accessibility certification, or legal review.
"""
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import os
import posixpath
import re
from urllib.parse import unquote, urlsplit


PROTECTED = frozenset({'network', '.git', '.aws', '.codex', '.agents'})
UNSAFE_TAGS = frozenset({'script', 'iframe', 'object', 'embed', 'form', 'base'})


@dataclass(frozen=True, order=True)
class Issue:
    page: str
    code: str
    detail: str


@dataclass(frozen=True)
class Reference:
    tag: str
    attribute: str
    value: str


def css_problems(source):
    """Conservative buildless-site policy, deliberately not a CSS parser.

    Escapes are disallowed so spelling tricks cannot hide URL/import tokens.
    Some harmless string literals will be refused; report that limit instead of
    claiming general CSS security. Local site styles need no loaded resources.
    """
    problems = []
    if '\\' in source:
        problems.append(('css_escape', 'CSS escapes are unsupported'))
    clean = re.sub(r'/\*.*?\*/', '', source, flags=re.S).lower()
    if '/*' in clean:
        problems.append(('css_comment', 'unterminated CSS comment'))
    if re.search(r'url\s*\(|(?:-webkit-)?image-set\s*\(', clean):
        problems.append(('css_resource', 'CSS resource functions are unsupported'))
    if re.search(r'expression\s*\(|(?:behavior|-moz-binding)\s*:', clean):
        problems.append(('css_active', 'legacy active CSS is unsupported'))
    for directive in re.findall(r'@\s*([-a-z]+)', clean):
        if directive not in ('media', 'supports', 'page'):
            problems.append(('css_directive', '@' + directive))
    return problems


class Page(HTMLParser):
    """Collect navigation and a deliberately small static-page policy."""

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.problems = []
        self.language = None
        self.title_seen = False
        self.main_seen = False
        self.in_style = False
        self.styles = []
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        names = [name for name, _ in attrs]
        if len(names) != len(set(names)):
            self.problems.append(('duplicate_attribute', tag))
        values = dict(attrs)
        if tag in UNSAFE_TAGS:
            self.problems.append(('active_content', tag))
        if any(name.startswith('on') for name in names):
            self.problems.append(('event_handler', tag))
        if tag == 'meta' and (values.get('http-equiv') or '').strip().lower() == 'refresh':
            self.problems.append(('redirect', 'meta refresh'))
        if tag == 'html':
            self.language = values.get('lang')
        self.title_seen |= tag == 'title'
        self.main_seen |= tag == 'main'
        if tag == 'style':
            self.in_style = True
        if 'style' in values:
            self.styles.append(values['style'] or '')
        for unsupported in ('srcset', 'ping', 'srcdoc'):
            if unsupported in values:
                self.problems.append(('resource_attribute', unsupported))
        if 'id' in values:
            identifier = values['id']
            if not identifier or identifier in self.ids:
                self.problems.append(('duplicate_or_empty_id', str(identifier)))
            self.ids.add(identifier)
        for name in ('href', 'src', 'poster', 'background', 'manifest', 'data', 'action'):
            if name in values:
                self.references.append(Reference(tag, name, values[name]))

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)


def relative_target(page, reference):
    """Return (repository-relative target, fragment), or None for HTTP(S).

    URL decoding occurs before normalization and protected-path checks. Windows
    separators, drives and alternate data streams are deliberately unsupported.
    No filesystem operation or network request occurs in this function.
    """
    if not isinstance(reference, str) or not reference or len(reference) > 4096:
        raise ValueError('empty or oversized reference')
    if any(ord(ch) < 32 for ch in reference) or '\\' in reference:
        raise ValueError('control character or backslash')
    try:
        parts = urlsplit(reference)
    except ValueError as exc:
        raise ValueError('malformed URL') from exc
    if parts.scheme in ('https', 'http'):
        if not parts.netloc:
            raise ValueError('external URL requires a host')
        return None
    if parts.scheme or parts.netloc or parts.path.startswith('/'):
        raise ValueError('unsupported scheme or absolute reference')
    if re.search(r'%(?![0-9a-fA-F]{2})', parts.path + parts.fragment):
        raise ValueError('invalid percent escape')
    try:
        path = unquote(parts.path, encoding='utf-8', errors='strict')
        fragment = unquote(parts.fragment, encoding='utf-8', errors='strict')
    except UnicodeError as exc:
        raise ValueError('invalid UTF-8 escape') from exc
    if any(ord(ch) < 32 for ch in path + fragment) or '\\' in path or ':' in path:
        raise ValueError('unsafe decoded reference')
    target = posixpath.normpath(posixpath.join(posixpath.dirname(page), path)) if path else page
    if target == '..' or target.startswith('../') or target.startswith('/'):
        raise ValueError('reference escapes repository')
    if any(part.casefold() in PROTECTED for part in target.split('/')):
        raise ValueError('protected reference')
    return target, fragment


def audit_pages(sources, exists, styles=None):
    """Audit supplied HTML strings; exists receives only normalized safe paths."""
    parsed = {name: Page(source) for name, source in sources.items()}
    issues = []
    for name, page in parsed.items():
        issues.extend(Issue(name, code, detail) for code, detail in page.problems)
        issues.extend(Issue(name, code, detail)
                      for code, detail in css_problems('\n'.join(page.styles)))
        if page.language not in ('en', 'ru'):
            issues.append(Issue(name, 'language', 'expected en or ru'))
        if not page.title_seen or not page.main_seen:
            issues.append(Issue(name, 'structure', 'title and main are required'))
        for reference in page.references:
            try:
                target = relative_target(name, reference.value)
            except ValueError as exc:
                issues.append(Issue(name, 'unsafe_reference', str(exc)))
                continue
            if target is None:
                if reference.tag != 'a' or reference.attribute != 'href':
                    issues.append(Issue(name, 'remote_resource',
                                        reference.tag + '[' + reference.attribute + ']'))
                continue
            path, fragment = target
            if not exists(path):
                issues.append(Issue(name, 'missing_target', path))
            elif fragment and path in parsed and fragment not in parsed[path].ids:
                issues.append(Issue(name, 'missing_fragment', path + '#' + fragment))
    for name, source in (styles or {}).items():
        issues.extend(Issue(name, code, detail) for code, detail in css_problems(source))
    return sorted(set(issues))


def read_utf8_limited(stream, limit):
    """Read at most limit + 1 bytes, rejecting oversize or invalid UTF-8."""
    if type(limit) is not int or limit <= 0:
        raise ValueError('positive integer byte limit required')
    data = stream.read(limit + 1)
    if not isinstance(data, bytes) or len(data) > limit:
        raise ValueError('source byte budget exceeded or nonbinary stream')
    try:
        return data.decode('utf-8'), len(data)
    except UnicodeError as exc:
        raise ValueError('source must be UTF-8') from exc


def audit_site(repository, max_bytes=1_048_576, max_pages=128,
               max_total_bytes=8_388_608):
    """Read only local site HTML; do not follow directory or file symlinks."""
    if any(type(value) is not int or value <= 0
           for value in (max_bytes, max_pages, max_total_bytes)):
        raise ValueError('positive integer audit budgets required')
    repository = Path(repository).resolve()
    site = repository / 'docs' / 'site'
    if not site.is_dir() or site.is_symlink():
        return [Issue('docs/site', 'missing_site', 'ordinary site directory required')]
    sources = {}
    styles = {}
    load_issues = []
    total_bytes = 0
    file_count = 0
    for directory, subdirs, filenames in os.walk(site, followlinks=False):
        subdirs[:] = sorted(name for name in subdirs
                            if name.casefold() not in PROTECTED
                            and not (Path(directory) / name).is_symlink())
        for name in sorted(filenames):
            path = Path(directory) / name
            if path.suffix.lower() not in ('.html', '.css') or path.is_symlink():
                continue
            relative = path.relative_to(repository).as_posix()
            file_count += 1
            if file_count > max_pages:
                load_issues.append(Issue('docs/site', 'file_budget', 'HTML/CSS file budget exceeded'))
                continue
            remaining = max_total_bytes - total_bytes
            if remaining <= 0:
                load_issues.append(Issue('docs/site', 'total_byte_budget', 'total source budget exceeded'))
                continue
            try:
                with path.open('rb') as stream:
                    source, length = read_utf8_limited(stream, min(max_bytes, remaining))
            except (OSError, ValueError) as exc:
                load_issues.append(Issue(relative, 'source_read', str(exc)))
                continue
            total_bytes += length
            (sources if path.suffix.lower() == '.html' else styles)[relative] = source

    def exists(relative):
        path = repository / Path(relative)
        # No target content is read. Reject symlink traversal before stat-ing the
        # final target; a link cannot redirect the audit into a protected tree.
        for parent in (path, *path.parents):
            if parent == repository:
                break
            if parent.is_symlink():
                return False
        return path.is_file()

    issues = audit_pages(sources, exists, styles) + load_issues
    if 'docs/site/index.html' not in sources:
        issues.append(Issue('docs/site', 'missing_index', 'index.html required'))
    return sorted(set(issues))


def main():
    root = Path(__file__).resolve().parents[1]
    issues = audit_site(root)
    for issue in issues:
        print(f'{issue.page}: {issue.code}: {issue.detail}')
    print(f'Local site source audit: {len(issues)} issue(s); no URLs fetched.')
    return int(bool(issues))


if __name__ == '__main__':
    raise SystemExit(main())

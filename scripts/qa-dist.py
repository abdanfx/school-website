#!/usr/bin/env python3
"""Dependency-free integrity checks for the generated production artifact."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PAGES = {'index.html', 'about.html', 'contact.html', 'admissions.html', '404.html'}
LEGACY_IMAGES = {
    '20250825_194632.jpg',
    'Gemini_Generated_Image_1n6shh1n6shh1n6s.png',
    'Gemini_Generated_Image_ap7tpiap7tpiap7t.png',
}
FORBIDDEN_PARTS = {'docs', 'scripts', '.git', '.qa', '__pycache__', '_incoming'}
FORBIDDEN_SUFFIXES = {'.jpg', '.jpeg', '.png', '.py', '.pyc', '.md', '.map', '.log', '.tmp', '.swp', '.swo'}
SCHOOL_LOGO = Path('assets/images/brand/smptqf-logo.png')
EXPECTED_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    'X-Frame-Options': 'DENY',
}


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for name in ('href', 'src'):
            if attrs.get(name):
                self.references.append(attrs[name])
        for candidate in attrs.get('srcset', '').split(','):
            if candidate.strip():
                self.references.append(candidate.strip().split()[0])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_headers(source):
    rules = []
    current = None
    for number, raw in enumerate(source.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        if raw[0].isspace():
            if current is None or ':' not in raw:
                raise ValueError(f'invalid header line {number}')
            name, value = raw.strip().split(':', 1)
            current[1][name.strip()] = value.strip()
        else:
            current = [raw.strip(), {}]
            rules.append(current)
    return rules


def main():
    results = []

    def check(name, condition, details=None):
        results.append({'check': name, 'pass': bool(condition), 'details': details})

    check('dist exists as a real directory', DIST.is_dir() and not DIST.is_symlink())
    if not DIST.is_dir():
        print(json.dumps({'checks': len(results), 'failures': results, 'files': 0, 'bytes': 0}, indent=2))
        raise SystemExit(1)

    files = sorted(path for path in DIST.rglob('*') if path.is_file())
    relative_files = {path.relative_to(DIST) for path in files}
    check('five production HTML pages are top-level',
          {path.name for path in DIST.glob('*.html')} == PAGES and
          sum(path.suffix == '.html' for path in files) == len(PAGES))
    check('404 is at artifact root', (DIST / '404.html').is_file())
    check('Cloudflare headers control is at artifact root', (DIST / '_headers').is_file())
    check('no redirects control was invented', not (DIST / '_redirects').exists())
    check('artifact contains no symlinks', not any(path.is_symlink() for path in DIST.rglob('*')))

    forbidden = []
    for path in relative_files:
        if FORBIDDEN_PARTS.intersection(path.parts) or path.name in LEGACY_IMAGES or (path.suffix.lower() in FORBIDDEN_SUFFIXES and path != SCHOOL_LOGO):
            forbidden.append(path.as_posix())
    check('no development, raw, legacy, or debug files', not forbidden, forbidden)
    check('only reviewed school logo PNG is published',
          {path for path in relative_files if path.suffix.lower() == '.png'} == {SCHOOL_LOGO})

    documents = {name: Document((DIST / name).read_text(encoding='utf-8')) for name in PAGES}
    referenced = {Path(name) for name in PAGES}
    reference_errors = []
    for name, document in documents.items():
        for reference in document.references:
            url = urlsplit(reference)
            if url.scheme or url.netloc or reference.startswith('//'):
                continue
            path = unquote(url.path)
            target_name = path or name
            if path.startswith('/') or '..' in Path(path).parts:
                reference_errors.append(f'{name}: unsafe reference {reference}')
                continue
            target = Path(target_name)
            referenced.add(target)
            if target not in relative_files:
                reference_errors.append(f'{name}: missing {reference}')
                continue
            if url.fragment and target.suffix == '.html' and url.fragment not in documents[target.name].ids:
                reference_errors.append(f'{name}: missing fragment {reference}')
    check('all local HTML references stay inside artifact and resolve', not reference_errors, reference_errors)

    css_references = []
    for stylesheet in (path for path in tuple(referenced) if path.suffix == '.css'):
        source = (DIST / stylesheet).read_text(encoding='utf-8')
        for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", source, re.I):
            reference = match.group(2)
            url = urlsplit(reference)
            if url.scheme or url.netloc or reference.startswith('//') or not url.path:
                continue
            if url.path.startswith('/'):
                css_references.append(f'{stylesheet}: {reference}')
                continue
            target_absolute = (DIST / stylesheet.parent / unquote(url.path)).resolve()
            try:
                target = target_absolute.relative_to(DIST.resolve())
            except ValueError:
                css_references.append(f'{stylesheet}: {reference}')
                continue
            if target not in relative_files:
                css_references.append(f'{stylesheet}: {reference}')
                continue
            referenced.add(target)
    check('all local CSS references stay inside artifact and resolve', not css_references, css_references)

    runtime_files = relative_files - {Path('_headers')}
    check('artifact contains only referenced runtime files', runtime_files == referenced,
          {'unexpected': sorted(str(path) for path in runtime_files - referenced),
           'missing': sorted(str(path) for path in referenced - runtime_files)})

    mismatches = []
    for path in runtime_files:
        source = ROOT / path
        if not source.is_file() or digest(source) != digest(DIST / path):
            mismatches.append(path.as_posix())
    check('runtime bytes exactly match reviewed source', not mismatches, mismatches)
    check('headers bytes match reviewed Cloudflare source',
          digest(DIST / '_headers') == digest(ROOT / 'cloudflare/_headers'))

    try:
        header_rules = parse_headers((DIST / '_headers').read_text(encoding='utf-8'))
        header_error = None
    except ValueError as error:
        header_rules = []
        header_error = str(error)
    check('headers syntax is one global rule', header_error is None and len(header_rules) == 1 and header_rules[0][0] == '/*',
          header_error or header_rules)
    check('headers are the reviewed conservative set',
          bool(header_rules) and header_rules[0][1] == EXPECTED_HEADERS, header_rules)
    headers_text = (DIST / '_headers').read_text(encoding='utf-8').lower()
    check('no untested CSP or unsafe directives',
          'content-security-policy' not in headers_text and 'unsafe-inline' not in headers_text and 'unsafe-eval' not in headers_text)

    public_text = '\n'.join(path.read_text(encoding='utf-8') for path in files
                            if path.suffix in {'.html', '.css', '.js'} or path.name == '_headers')
    check('no secrets or debug markers in public text',
          not re.search(r'(?i)(?:api[_-]?key|secret|password|private[_-]?key|access[_-]?token)\s*[:=]|\bdebugger\b|console\.(?:log|debug)', public_text))

    byte_count = sum(path.stat().st_size for path in files)
    failures = [result for result in results if not result['pass']]
    report = {'checks': len(results), 'failures': failures, 'files': len(files), 'bytes': byte_count,
              'mebibytes': round(byte_count / 1024 / 1024, 2)}
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Build the exact public artifact consumed by Cloudflare Pages."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PAGES = ('index.html', 'about.html', 'contact.html', 'admissions.html', '404.html')
CONTROL_FILES = {Path('cloudflare/_headers'): Path('_headers')}
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I)


class References(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name in ('href', 'src'):
            if attrs.get(name):
                self.references.append(attrs[name])
        for candidate in attrs.get('srcset', '').split(','):
            if candidate.strip():
                self.references.append(candidate.strip().split()[0])


def fail(message):
    raise SystemExit('Production build failed: ' + message)


def local_reference(reference, owner):
    url = urlsplit(reference)
    if url.scheme or url.netloc or reference.startswith('//'):
        return None
    path = unquote(url.path)
    if not path:
        return None
    if path.startswith('/'):
        fail(f'root-absolute reference is not supported: {reference!r} in {owner}')
    candidate = (ROOT / owner.parent / path).resolve()
    try:
        return candidate.relative_to(ROOT)
    except ValueError:
        fail(f'reference escapes repository root: {reference!r} in {owner}')


def allowed_runtime_file(path):
    if path.as_posix() in PAGES:
        return True
    if path.parts[:1] == ('css',) and path.suffix == '.css':
        return True
    if path.parts[:1] == ('js',) and path.suffix == '.js':
        return True
    if path == Path('assets/images/brand/smptqf-logo.png'):
        return True
    return path.parts[:3] == ('assets', 'images', 'p03') and path.suffix == '.webp'


def discover_runtime_files():
    files = {Path(page) for page in PAGES}
    for page in PAGES:
        source = ROOT / page
        if not source.is_file():
            fail(f'missing required page: {page}')
        for reference in References(source.read_text(encoding='utf-8')).references:
            local = local_reference(reference, Path(page))
            if local is not None:
                files.add(local)

    checked_css = set()
    while True:
        pending = [path for path in files if path.suffix == '.css' and path not in checked_css]
        if not pending:
            break
        for stylesheet in pending:
            source = ROOT / stylesheet
            if not source.is_file():
                fail(f'missing referenced stylesheet: {stylesheet}')
            checked_css.add(stylesheet)
            for _, reference in CSS_URL.findall(source.read_text(encoding='utf-8')):
                local = local_reference(reference, stylesheet)
                if local is not None:
                    files.add(local)

    for path in sorted(files):
        if not allowed_runtime_file(path):
            fail(f'referenced file is outside the reviewed runtime policy: {path}')
        source = ROOT / path
        if not source.is_file():
            fail(f'missing referenced runtime file: {path}')
        if source.is_symlink():
            fail(f'runtime source must not be a symlink: {path}')

    for source in CONTROL_FILES:
        if not (ROOT / source).is_file():
            fail(f'missing deployment control file: {source}')
    return files


def clean_output():
    if DIST.parent != ROOT or DIST.name != 'dist':
        fail(f'refusing to clean unexpected output path: {DIST}')
    if DIST.exists():
        if DIST.is_symlink() or not DIST.is_dir():
            fail(f'output path must be a real directory: {DIST}')
        shutil.rmtree(DIST)
    DIST.mkdir()


def main():
    runtime_files = discover_runtime_files()
    clean_output()
    for relative in sorted(runtime_files):
        destination = DIST / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    for source, destination in CONTROL_FILES.items():
        shutil.copy2(ROOT / source, DIST / destination)

    built = sorted(path for path in DIST.rglob('*') if path.is_file())
    expected = {DIST / path for path in runtime_files}
    expected.update(DIST / path for path in CONTROL_FILES.values())
    if set(built) != expected:
        fail('output file set differs from the discovered runtime manifest')
    byte_count = sum(path.stat().st_size for path in built)
    print(f'Built dist/: {len(built)} files, {byte_count} bytes ({byte_count / 1024 / 1024:.2f} MiB)')


if __name__ == '__main__':
    main()

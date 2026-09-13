"""Source and asset regression checks. Uses only Python's standard library."""
import hashlib
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.words = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_data(self, text):
        self.words.append(text)

    def all(self, tag):
        return [attrs for name, attrs in self.elements if name == tag]


def run():
    results = []
    def check(name, condition):
        results.append({'check': name, 'pass': bool(condition)})

    pages = {p.name: Document(p.read_text()) for p in ROOT.glob('*.html')}
    for filename, page in pages.items():
        ids = [attrs['id'] for _, attrs in page.elements if 'id' in attrs]
        check(filename + ': unique IDs', len(ids) == len(set(ids)))
        check(filename + ': Indonesian language and landmarks',
              page.all('html')[0].get('lang') == 'id' and
              all(len(page.all(tag)) == 1 for tag in ('header', 'main', 'footer', 'h1')))
        for tag, attrs in page.elements:
            for attr in ('href', 'src'):
                ref = attrs.get(attr)
                if not ref:
                    continue
                url = urlsplit(ref)
                if url.scheme or url.netloc:
                    continue
                target = unquote(url.path) or filename
                exists = (ROOT / target).is_file()
                check(f'{filename}: {attr} {ref}', exists)
                if url.fragment and target in pages:
                    check(f'{filename}: anchor {ref}', any(a.get('id') == url.fragment for _, a in pages[target].elements))
            if attrs.get('target') == '_blank':
                check(filename + ': protected external link', 'noopener' in attrs.get('rel', '').split())
            if tag == 'img':
                check(filename + ': image alternative and dimensions', all(attrs.get(k) for k in ('alt', 'width', 'height')))
                for candidate in attrs.get('srcset', '').split(','):
                    if candidate.strip():
                        check(filename + ': responsive asset ' + candidate.strip(), (ROOT / candidate.split()[0]).is_file())

    home = pages['index.html']
    home_text = ' '.join(''.join(home.words).split())
    source = (ROOT / 'docs/prototype-03-source-of-truth.md').read_text()
    frozen = re.findall(r'^`([^`]+)`$', source, re.M)
    for text in frozen:
        if text.startswith(('https:', '#')):
            continue
        check('Frozen copy: ' + text[:95], text in home_text)
    check('Original locked H1', "Tumbuh dengan Al-Qur'an, Belajar untuk Masa Depan." in home_text)
    check('Exact archive label', 'ARSIP KEGIATAN · 2022' in home_text)
    check('Only approved homepage sections', [a['id'] for a in home.all('section')] ==
          ['hero', 'profil', 'program', 'quran-teknologi', 'capaian-tahfizh', 'kehidupan', 'ppdb'])
    expected = ['1000534854', '1000512148', '1000160830', '1000520096', '1000163805',
                '1000344565', '1000512176', '1000512147', '1000213703', 'IMG-20221202-WA0016']
    check('Exact ten-photo mapping and order', [Path(a['src']).stem.rsplit('-', 1)[0] for a in home.all('img')] == expected)
    check('Hero eager with high priority', home.all('img')[0].get('loading') != 'lazy' and home.all('img')[0].get('fetchpriority') == 'high')
    check('Below-fold lazy and async', all(a.get('loading') == 'lazy' and a.get('decoding') == 'async' for a in home.all('img')[1:]))

    for filename in ('about.html', 'contact.html', 'admissions.html', '404.html'):
        baseline = subprocess.check_output(['git', 'show', 'd965e1c:' + filename], cwd=ROOT, text=True)
        before = Document(baseline)
        # Every original visible text fragment survives; new accessibility help is allowed.
        after_text = ' '.join(' '.join(pages[filename].words).split())
        fragments = [' '.join(word.split()) for word in before.words if word.strip()]
        check(filename + ': original copy preserved', all(fragment in after_text for fragment in fragments))
        check(filename + ': Maps source unchanged', [a['src'] for a in before.all('iframe')] == [a['src'] for a in pages[filename].all('iframe')])
        before_links = [a['href'] for a in before.all('a') if a['href'].startswith('https://wa.me/')]
        check(filename + ': WhatsApp destination preserved', all(link in [a['href'] for a in pages[filename].all('a')] for link in before_links))

    css = (ROOT / 'css/style.css').read_text()
    js = (ROOT / 'js/script.js').read_text()
    check('No obsolete homepage visual selectors', not re.search(r'\.promo|\.why|\.news|\.programs__card|nth-child|#f39c12|Poppins', css))
    # M1 explicitly permits gated reveal opacity and a progressive navigation blur.
    # The browser suite verifies the actual no-JS computed visibility.
    check('Future reveals armed only after observer installation',
          '.motion-ready .is-pending' in css and
          js.index('revealObserver.observe(element)') < js.index("element.classList.add('is-pending')") < js.index("root.classList.add('motion-ready')"))
    check('Explicit reduced motion', '@media (prefers-reduced-motion: reduce)' in css and 'scroll-behavior: auto' in css)
    check('No heavy scroll listener', "addEventListener('scroll'" not in js)
    manifest = []
    for stem in expected:
        source_path = ROOT / 'assets/_incoming' / (stem + '.jpg')
        dimensions = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', str(source_path)], text=True)
        manifest.append({
            'source': str(source_path.relative_to(ROOT)),
            'sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
            'bytes': source_path.stat().st_size,
            **json.loads(dimensions)['streams'][0],
            'derivatives': [{'file': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size}
                            for p in sorted((ROOT / 'assets/images/p03').glob(stem + '-*.webp'))]
        })
    output = ROOT / '.qa'
    output.mkdir(exist_ok=True)
    (output / 'static-results.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
    (output / 'asset-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    failures = [r for r in results if not r['pass']]
    print(json.dumps({'checks': len(results), 'failures': failures, 'source_photos': len(manifest)}, indent=2))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(run())

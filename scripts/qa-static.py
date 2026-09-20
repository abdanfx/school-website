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
        self.source = source
        self.declarations = []
        self.elements = []
        self.words = []
        self.feed(source)

    def handle_decl(self, declaration):
        self.declarations.append(declaration)

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

    page_paths = sorted(ROOT.glob('*.html'))
    pages = {p.name: Document(p.read_text()) for p in page_paths}
    expected_pages = {'index.html', 'about.html', 'contact.html', 'admissions.html', '404.html'}
    check('Exact production page set', set(pages) == expected_pages)
    titles = []
    descriptions = []
    for filename, page in pages.items():
        ids = [attrs['id'] for _, attrs in page.elements if 'id' in attrs]
        titles_found = re.findall(r'<title>(.*?)</title>', page.source, re.I | re.S)
        description_meta = [attrs for attrs in page.all('meta') if attrs.get('name', '').lower() == 'description']
        viewport_meta = [attrs for attrs in page.all('meta') if attrs.get('name', '').lower() == 'viewport']
        charset_meta = [attrs for attrs in page.all('meta') if 'charset' in attrs]
        headings = [int(tag[1]) for tag, _ in page.elements if re.fullmatch(r'h[1-6]', tag)]
        labels = {attrs.get('for') for attrs in page.all('label') if attrs.get('for')}
        controls = [attrs for tag, attrs in page.elements if tag in ('input', 'textarea', 'select') and attrs.get('type') != 'hidden']
        check(filename + ': HTML5 document shell',
              any(value.lower() == 'doctype html' for value in page.declarations) and
              all(len(page.all(tag)) == 1 for tag in ('html', 'head', 'body', 'title')))
        check(filename + ': charset and viewport metadata',
              len(charset_meta) == 1 and charset_meta[0].get('charset', '').lower() == 'utf-8' and
              len(viewport_meta) == 1 and viewport_meta[0].get('content') == 'width=device-width, initial-scale=1.0')
        check(filename + ': title and meta description',
              len(titles_found) == 1 and bool(titles_found[0].strip()) and
              len(description_meta) == 1 and bool(description_meta[0].get('content', '').strip()))
        titles.extend(value.strip() for value in titles_found)
        descriptions.extend(attrs['content'].strip() for attrs in description_meta)
        check(filename + ': unique IDs', len(ids) == len(set(ids)))
        check(filename + ': Indonesian language and landmarks',
              page.all('html')[0].get('lang') == 'id' and
              all(len(page.all(tag)) == 1 for tag in ('header', 'main', 'footer', 'h1')))
        check(filename + ': logical heading order',
              headings and headings[0] == 1 and not any(current > previous + 1 for previous, current in zip(headings, headings[1:])))
        check(filename + ': controls have explicit labels',
              all(control.get('id') in labels for control in controls))
        for tag, attrs in page.elements:
            if tag == 'a':
                check(filename + ': link has valid href',
                      bool(attrs.get('href', '').strip()) and
                      not attrs.get('href', '').strip().lower().startswith(('javascript:', 'data:')))
            if tag == 'button':
                check(filename + ': button has explicit type', attrs.get('type') in ('button', 'submit', 'reset'))
            for reference_attr in ('aria-controls', 'aria-labelledby', 'aria-describedby'):
                if attrs.get(reference_attr):
                    for reference in attrs[reference_attr].split():
                        check(f'{filename}: {reference_attr} target {reference}', reference in ids)
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
                protections = attrs.get('rel', '').split()
                check(filename + ': protected external link',
                      'noopener' in protections and 'noreferrer' in protections)
            if tag == 'img':
                check(filename + ': image alternative and dimensions', all(attrs.get(k) for k in ('alt', 'width', 'height')))
                for candidate in attrs.get('srcset', '').split(','):
                    if candidate.strip():
                        check(filename + ': responsive asset ' + candidate.strip(), (ROOT / candidate.split()[0]).is_file())

        metadata = {(attrs.get('property') or attrs.get('name')): attrs.get('content') for attrs in page.all('meta')}
        if filename == '404.html':
            check('404: explicit noindex directive', metadata.get('robots') == 'noindex, follow')
        else:
            title = titles_found[0].strip()
            description = description_meta[0]['content'].strip()
            check(filename + ': hostname-independent social metadata',
                  metadata.get('og:locale') == 'id_ID' and metadata.get('og:type') == 'website' and
                  metadata.get('og:title') == title and metadata.get('og:description') == description and
                  metadata.get('twitter:card') == 'summary' and metadata.get('twitter:title') == title and
                  metadata.get('twitter:description') == description)

    check('Unique page titles', len(titles) == len(set(titles)) == len(expected_pages))
    check('Unique page descriptions', len(descriptions) == len(set(descriptions)) == len(expected_pages))
    logo = ROOT / 'assets/images/brand/smptqf-logo.png'
    logo_bytes = logo.read_bytes() if logo.is_file() else b''
    check('Official school logo production copy is a transparent PNG',
          logo_bytes.startswith(b'\x89PNG\r\n\x1a\n') and logo_bytes[25:26] == b'\x06')
    check('School identity has official logo in every header and footer',
          all(len([a for a in page.all('span') if 'brand-logo' in a.get('class', '').split()]) == 2
              for page in pages.values()))
    check('Hero decorative signature removed', 'hero__signature' not in pages['index.html'].source)

    home = pages['index.html']
    home_text = ' '.join(''.join(home.words).split())
    source = (ROOT / 'docs/prototype-03-source-of-truth.md').read_text()
    frozen = re.findall(r'^`([^`]+)`$', source, re.M)
    # P04 corrects the metric and selects one approved Profile paragraph for its compact composition.
    superseded = {
        'Santri telah menyelesaikan setoran hafalan 30 juz',
        'Sebagai bagian dari Pondok Pesantren Daarul Quran Fantastis Pusat, sekolah ini menghadirkan suasana belajar yang dekat, terarah, dan membina. Proses pendidikan dirancang untuk menjaga keseimbangan antara pembentukan karakter Islami, penguatan akademik, dan kesiapan menghadapi perkembangan teknologi.'
    }
    for text in frozen:
        if text.startswith(('https:', '#')) or text in superseded:
            continue
        check('Frozen copy: ' + text[:95], text in home_text)
    check('Original locked H1', "Tumbuh dengan Al-Qur'an, Belajar untuk Masa Depan." in home_text)
    check('Exact archive label', 'ARSIP KEGIATAN · 2022' in home_text)
    check('Only approved homepage sections', [a['id'] for a in home.all('section')] ==
          ['hero', 'profil', 'program', 'quran-teknologi', 'capaian-tahfizh', 'kehidupan', 'ppdb'])
    expected = ['1000534854', '1000512148', '1000160830', '1000520097', '1000163805',
                '1000344565', '1000512176', '1000512147', '1000213703', 'IMG-20221202-WA0016']
    check('Exact ten-photo mapping and order', [Path(a['src']).stem.rsplit('-', 1)[0] for a in home.all('img')] == expected)
    check('Hero eager with high priority', home.all('img')[0].get('loading') != 'lazy' and home.all('img')[0].get('fetchpriority') == 'high')
    check('Below-fold lazy and async', all(a.get('loading') == 'lazy' and a.get('decoding') == 'async' for a in home.all('img')[1:]))
    check('P04 isolated homepage stylesheet and scope',
          'p04' in home.all('body')[0].get('class', '').split() and
          any(a.get('href') == 'css/p04-home.css' for a in home.all('link')) and
          all('p04-home.css' not in pages[name].source for name in ('about.html', 'contact.html', 'admissions.html', '404.html')))
    check('P04 truthful tahfizh metric',
          '230+' in home_text and 'Juz hafalan yang telah disetorkan santri secara kumulatif' in home_text and
          'Santri telah menyelesaikan setoran hafalan 30 juz' not in home_text and
          not re.search(r'\b(?:120\+|15\+|30\+|100%)\b', home_text))
    check('P04 benefit strip is structural, not numbered section',
          'benefits' in home.source and all(text in home_text for text in (
              'Berbasis pondok pesantren', 'Fokus pada tahfizh dan adab',
              'Pembelajaran akademik yang terarah', 'Penguatan karakter dan kemandirian')))
    check('P04 references excluded from runtime', 'docs/p04-reference/' not in home.source and
          'docs/p04-reference/' not in (ROOT / 'css/p04-home.css').read_text())
    check('P04 correct Maps destination',
          'https://maps.app.goo.gl/YsTcqxBpNeu3tXBFA?g_st=ac' in [a.get('href') for a in home.all('a')])

    internal_names = ('about.html', 'contact.html', 'admissions.html', '404.html')
    for filename in internal_names:
        page = pages[filename]
        body_classes = page.all('body')[0].get('class', '').split()
        header_classes = page.all('header')[0].get('class', '').split()
        footer_classes = page.all('footer')[0].get('class', '').split()
        hrefs = [a['href'] for a in page.all('a') if a.get('href')]
        check(filename + ': shared Prototype 03 shell',
              'internal' in body_classes and 'header--internal' in header_classes and 'footer--home' in footer_classes)
        check(filename + ': six-link primary navigation',
              len([a for a in page.all('a') if 'nav__link' in a.get('class', '').split()]) == 6)
        check(filename + ': institutional footer destinations',
              all(link in hrefs for link in ('about.html', 'index.html#program', 'index.html#kehidupan',
                                             'admissions.html', 'contact.html')))
        check(filename + ': verified WhatsApp destination',
              'https://wa.me/6281315452107' in hrefs)

    about_text = ' '.join(' '.join(pages['about.html'].words).split())
    check('About: supported vision and mission preserved',
          all(text in about_text for text in (
              'Menjadi sekolah unggulan dalam mencetak generasi penghafal Al-Qur’an yang cerdas dan berwawasan teknologi.',
              'Menyelenggarakan pendidikan tahfidz yang berkualitas',
              'Mengintegrasikan ilmu agama dan teknologi',
              'Membentuk karakter islami yang kuat')))

    admissions_text = ' '.join(' '.join(pages['admissions.html'].words).split())
    check('Admissions: cautious operational guidance preserved',
          all(text in admissions_text for text in (
              'Hubungi pihak sekolah untuk mendapatkan informasi pendaftaran terbaru.',
              'Konfirmasikan persyaratan dan dokumen yang perlu disiapkan.',
              'Ikuti tahapan pendaftaran sesuai arahan dari pihak sekolah.',
              'Pastikan informasi jadwal dan ketentuan lainnya telah dikonfirmasi.')))

    not_found_text = ' '.join(' '.join(pages['404.html'].words).split())
    check('404: calm recovery copy and primary action',
          'Maaf, halaman ini tidak tersedia' in not_found_text and
          any(a.get('href') == 'index.html' and 'btn--light' in a.get('class', '').split()
              for a in pages['404.html'].all('a')))

    contact_source = (ROOT / 'contact.html').read_text()
    contact_hrefs = [a.get('href') for a in pages['contact.html'].all('a')]
    check('Contact: exact authoritative school Maps destination',
          'https://maps.app.goo.gl/YsTcqxBpNeu3tXBFA?g_st=ac' in contact_hrefs)
    check('Contact: exact school-building address',
          'Jl. Bulak Jagal No.94, RT.01/RW.14, Rw. Panjang, Kecamatan Bojonggede, Kabupaten Bogor, Jawa Barat 16920'
          in ' '.join(' '.join(pages['contact.html'].words).split()))
    check('Contact: deprecated Yayasan map fully removed',
          not pages['contact.html'].all('iframe') and
          "Yayasan Qur'an Fantastis" not in contact_source and
          'google.com/maps/embed' not in contact_source)
    production_html = '\n'.join(page.source for page in pages.values())
    check('Production pages: authoritative Bojonggede spelling',
          'Bojong Gede' not in production_html and production_html.count('Bojonggede, Bogor') >= len(expected_pages))
    check('Production pages: no deprecated institution language',
          "Yayasan Qur'an Fantastis" not in production_html and 'foundation-owner-home' not in production_html)
    check('Production pages: verified WhatsApp number only',
          '6281315452107' in production_html and not re.search(r'(?:wa\.me/|WhatsApp\D{0,30})(?!6281315452107|0813-1545-2107)\d{10,15}', production_html))

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
    check('No production debug logging', not re.search(r'\b(?:console\.(?:log|debug)|debugger)\b', js))
    check('No source maps or editor artifacts',
          not any(ROOT.rglob('*.map')) and
          not any(path.name in ('.DS_Store', 'Thumbs.db') or path.suffix in ('.swp', '.swo')
                  for path in ROOT.rglob('*') if '.git' not in path.parts and '.qa' not in path.parts))
    ignore = (ROOT / '.gitignore').read_text().splitlines()
    check('QA/source/build/cache exclusions',
          all(value in ignore for value in ('.qa/', '__pycache__/', 'dist/', 'assets/_incoming/')))
    manifest = []
    for stem in expected:
        source_name = '1000520097(1).jpg' if stem == '1000520097' else stem + '.jpg'
        source_path = ROOT / 'assets/_incoming' / source_name
        derivatives = []
        for derivative in sorted((ROOT / 'assets/images/p03').glob(stem + '-*.webp')):
            dimensions = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', str(derivative)], text=True))['streams'][0]
            check('Integrity: ' + derivative.name, not derivative.is_symlink() and derivative.stat().st_size > 0 and
                  dimensions['width'] > 0 and dimensions['height'] > 0)
            derivatives.append({'file': str(derivative.relative_to(ROOT)), 'bytes': derivative.stat().st_size,
                                'sha256': hashlib.sha256(derivative.read_bytes()).hexdigest(), **dimensions})
        check('Responsive derivatives present: ' + stem,
              all((ROOT / 'assets/images/p03' / f'{stem}-{width}.webp').is_file() for width in (480, 768)))
        source_details = {}
        if source_path.is_file():
            source_details = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', str(source_path)], text=True))['streams'][0]
        manifest.append({
            'source': str(source_path.relative_to(ROOT)),
            'source_present': source_path.is_file(),
            'sha256': hashlib.sha256(source_path.read_bytes()).hexdigest() if source_path.is_file() else None,
            'bytes': source_path.stat().st_size if source_path.is_file() else None,
            **source_details,
            'derivatives': derivatives
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

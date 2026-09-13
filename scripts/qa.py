"""Browser QA against existing Chrome on port 9333; no production dependencies."""
import argparse
import json
import time
from pathlib import Path
from cdp import Browser

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.qa'


def inspect(browser):
    return browser.evaluate("""(() => {
      const rect = el => { const r = el.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; };
      return {
        width: innerWidth, overflow: document.documentElement.scrollWidth > innerWidth,
        font: document.fonts.check('16px "Plus Jakarta Sans"'),
        headings: [...document.querySelectorAll('h1,h2,h3')].map(e=>({tag:e.tagName,text:e.textContent.trim()})),
        sections: [...document.querySelectorAll('main > section')].map(e=>({id:e.id,...rect(e)})),
        hero: document.querySelector('.hero__image') && rect(document.querySelector('.hero__image')),
        visibleLife: [...document.querySelectorAll('.life__mosaic figure')].filter(e=>e.getClientRects().length).length,
        images: [...document.images].map(e=>({src:e.currentSrc,loaded:e.complete && e.naturalWidth>0,...rect(e)})),
        resources: performance.getEntriesByType('resource').map(e=>({name:e.name,bytes:e.transferSize})),
        hiddenSections: [...document.querySelectorAll('main > section')].filter(e=>getComputedStyle(e).opacity==='0').length
      };
    })()""")


def settle_reveals(browser):
    """Traverse once so full-page review captures represent the settled reading state."""
    browser.evaluate("""(async () => {
      for (const target of [...document.querySelectorAll('[data-reveal]')]) {
        target.scrollIntoView({block:'center',behavior:'instant'});
        await new Promise(resolve => setTimeout(resolve, 40));
      }
      scrollTo({top:0,behavior:'instant'});
      await new Promise(resolve => setTimeout(resolve, 800));
      return !document.querySelector('.is-pending,.is-entering');
    })()""")


def preview(width, page):
    browser = Browser()
    try:
        browser.viewport(width)
        browser.navigate((ROOT / page).as_uri())
        print(json.dumps(inspect(browser), ensure_ascii=False, indent=2))
        browser.screenshot(OUTPUT / f'{page}-{width}-top.png')
        browser.evaluate("Promise.all([...document.images].filter(e=>e.getClientRects().length).map(e=>{e.loading='eager'; return e.decode().catch(()=>{});})).then(()=>true)")
        settle_reveals(browser)
        browser.screenshot(OUTPUT / f'{page}-{width}-full.png', full=True)
        print('Runtime exceptions:', [e for e in browser.events if e.get('method') == 'Runtime.exceptionThrown'])
    finally:
        browser.close()


def suite():
    results = []
    layouts = []
    errors = []
    def check(name, passed, details=None):
        results.append({'check': name, 'pass': bool(passed), 'details': details})

    # Fresh targets avoid the image cache obscuring responsive source selection.
    for page in ('index.html', 'about.html', 'contact.html', 'admissions.html', '404.html'):
        for width in (320, 360, 390, 768, 1024, 1280, 1440, 1920):
            browser = Browser()
            try:
                browser.viewport(width)
                browser.navigate((ROOT / page).as_uri())
                layout = inspect(browser)
                layout['page'] = page
                layouts.append(layout)
                check(f'{page} {width}: no horizontal overflow', browser.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth'))
                check(f'{page} {width}: content visible', layout['hiddenSections'] == 0)
                check(f'{page} {width}: single H1', len([h for h in layout['headings'] if h['tag'] == 'H1']) == 1)
                check(f'{page} {width}: no clipped controls', browser.evaluate("""[...document.querySelectorAll('a,button,input,textarea')].filter(e=>e.getClientRects().length && !e.classList.contains('skip-link')).every(e=>{const r=e.getBoundingClientRect(); return r.left>=-1 && r.right<=document.documentElement.clientWidth+1;})"""))
                if page == 'index.html':
                    check(f'Home {width}: landscape Hero 5:4', abs(layout['hero']['w'] / layout['hero']['h'] - 1.25) < 0.01)
                    check(f'Home {width}: correct life image count', layout['visibleLife'] == (3 if width <= 600 else 4))
                    check(f'Home {width}: Profile 4:3', browser.evaluate("Math.abs(document.querySelector('.profile__visual img').width / document.querySelector('.profile__visual img').height - 4/3) < 0.02"))
                    if width >= 1024:
                        depth = next(s['h'] for s in layout['sections'] if s['id'] == 'capaian-tahfizh')
                        check(f'Home {width}: 420–500px evidence depth', 420 <= depth <= 500, depth)
                    if width <= 600:
                        check(f'Home {width}: left-aligned metric', browser.evaluate("getComputedStyle(document.querySelector('.evidence__metric')).textAlign === 'left' && Math.abs(document.querySelector('.evidence__metric').getBoundingClientRect().left - document.querySelector('.evidence .container').getBoundingClientRect().left) < 1"))
                        check(f'Home {width}: mobile Hero order', browser.evaluate("""(() => {const selectors=['.hero__eyebrow','.hero h1','.hero__tagline','.hero__support','.hero .actions','.hero__image']; const rects=selectors.map(s=>document.querySelector(s).getBoundingClientRect()); return rects.every((r,i)=>i===0 || r.top>=rects[i-1].bottom-1);})()"""))
                        check(f'Home {width}: mobile image payload', layout['images'][0]['src'].endswith('-480.webp'))
                else:
                    check(f'{page} {width}: shared internal header and footer',
                          browser.evaluate("!!document.querySelector('.header--internal') && !!document.querySelector('.footer--home')"))
                    check(f'{page} {width}: six-link primary navigation',
                          browser.evaluate("document.querySelectorAll('#primary-navigation .nav__link').length===6"))
                    if page == 'contact.html':
                        check(f'Contact {width}: verified location without deprecated embed',
                              browser.evaluate("!document.querySelector('iframe') && document.querySelector('.location a').href==='https://maps.app.goo.gl/YsTcqxBpNeu3tXBFA?g_st=ac'"))
                    if page == '404.html':
                        check(f'404 {width}: primary recovery action',
                              browser.evaluate("document.querySelector('.error-state .btn--light').getAttribute('href')==='index.html'"))
                runtime = [e for e in browser.events if e.get('method') == 'Runtime.exceptionThrown']
                check(f'{page} {width}: no runtime exceptions', not runtime, runtime)
                errors.extend([e for e in browser.events if e.get('method') == 'Network.loadingFailed'])
                if width in (390, 1440):
                    browser.screenshot(OUTPUT / f'{page}-{width}-top.png')
                    browser.evaluate("Promise.all([...document.images].filter(e=>e.getClientRects().length).map(e=>{e.loading='eager'; return e.decode().catch(()=>{});})).then(()=>true)")
                    check(f'{page} {width}: visible photos decode', browser.evaluate("[...document.images].filter(e=>e.getClientRects().length).every(e=>e.complete && e.naturalWidth>0)"))
                    settle_reveals(browser)
                    check(f'{page} {width}: settled review state', browser.evaluate("!document.querySelector('.is-pending,.is-entering')"))
                    browser.screenshot(OUTPUT / f'{page}-{width}-full.png', full=True)
            finally:
                browser.close()
        print('Viewport checks complete:', page, flush=True)

    browser = Browser()
    try:
        browser.viewport(390)
        browser.navigate((ROOT / 'index.html').as_uri())
        browser.evaluate("document.querySelector('.nav__toggle').focus()")
        browser.key('Enter')
        check('Menu opens with Enter', browser.evaluate("document.querySelector('.nav__toggle').getAttribute('aria-expanded') === 'true'"))
        browser.screenshot(OUTPUT / 'mobile-menu.png')
        browser.key('Escape')
        check('Escape closes and returns focus', browser.evaluate("document.activeElement.matches('.nav__toggle') && document.activeElement.getAttribute('aria-expanded')==='false'"))
        check('Visible keyboard focus', browser.evaluate("document.activeElement.matches(':focus-visible') && parseFloat(getComputedStyle(document.activeElement).outlineWidth)>=3"))
        browser.key(' ', 'Space')
        check('Menu opens with Space', browser.evaluate("document.querySelector('.nav__toggle').getAttribute('aria-expanded') === 'true'"))
        browser.key('Tab')
        check('Tab reaches first menu link', browser.evaluate("document.activeElement.matches('.nav__link')"))
        browser.evaluate("document.querySelector('.nav__link[href=\"#profil\"]').focus()")
        browser.key('Enter')
        check('Link closes menu and focuses destination', browser.evaluate("document.querySelector('.nav__toggle').getAttribute('aria-expanded')==='false' && document.activeElement.id==='profil'"))
        browser.evaluate("document.querySelector('.nav__toggle').click(); document.querySelector('main').click()")
        check('Outside click closes menu', browser.evaluate("document.querySelector('.nav__toggle').getAttribute('aria-expanded')==='false'"))
        browser.evaluate("document.querySelector('.nav__toggle').click()")
        browser.viewport(1280)
        time.sleep(0.1)
        check('Resize synchronizes state', browser.evaluate("document.querySelector('.nav__toggle').getAttribute('aria-expanded')==='false' && getComputedStyle(document.querySelector('.nav__list')).display==='flex'"))

        browser.viewport(390, 844)
        for page, current in (('about.html', 'about.html'), ('contact.html', 'contact.html'),
                              ('admissions.html', 'admissions.html')):
            browser.navigate((ROOT / page).as_uri())
            check(page + ': current-page navigation state',
                  browser.evaluate("document.querySelector('.nav__link[aria-current]').getAttribute('href')===" + json.dumps(current)))
            browser.evaluate("document.querySelector('.nav__toggle').focus()")
            browser.key('Enter')
            browser.key('Escape')
            check(page + ': mobile disclosure Escape and focus return',
                  browser.evaluate("document.activeElement.matches('.nav__toggle') && document.activeElement.getAttribute('aria-expanded')==='false'"))

        browser.navigate((ROOT / 'about.html').as_uri())
        browser.evaluate("window.__internalPhoto=document.querySelector('.photo-trigger');__internalPhoto.focus();__internalPhoto.click()")
        check('About: shared lightbox opens from approved photography',
              browser.evaluate("document.querySelector('.photo-lightbox').open"))
        browser.key('Escape')
        time.sleep(0.2)
        check('About: shared lightbox closes and returns focus',
              browser.evaluate("!document.querySelector('.photo-lightbox').open && document.activeElement===__internalPhoto"))

        # Equivalent CSS viewport / DPR at 200% on a 1440px display.
        browser.viewport(720, 450, dpr=2)
        for page in ('index.html', 'about.html', 'contact.html', 'admissions.html', '404.html'):
            browser.navigate((ROOT / page).as_uri())
            check(page + ': 200% reflow emulation', browser.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth'))
        browser.viewport(390, 280)
        browser.navigate((ROOT / 'index.html').as_uri())
        browser.evaluate("document.querySelector('.nav__toggle').click()")
        check('Short viewport menu scrolls internally', browser.evaluate("const n=document.querySelector('.nav__list'); n.clientHeight<=innerHeight-70 && getComputedStyle(n).overflowY==='auto'"))

        browser.viewport(390, 844, dpr=2)
        browser.call('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})
        for page in ('index.html', 'about.html', 'contact.html', 'admissions.html', '404.html'):
            browser.navigate((ROOT / page).as_uri())
            check(page + ': reduced motion makes content immediate and static',
                  browser.evaluate("getComputedStyle(document.documentElement).scrollBehavior==='auto' && getComputedStyle(document.querySelector('.btn')).transitionDuration==='0s' && !document.querySelector('.is-pending,.is-entering') && [...document.querySelectorAll('section')].every(e=>getComputedStyle(e).opacity==='1') && document.getAnimations().length===0"))
        mobile_browser = Browser()
        try:
            mobile_browser.viewport(390, 844, dpr=2)
            mobile_browser.navigate((ROOT / 'index.html').as_uri())
            check('Mobile 2x Hero uses 800px derivative on fresh navigation', mobile_browser.evaluate("document.querySelector('.hero__image').currentSrc.endsWith('-800.webp')"))
        finally:
            mobile_browser.close()
        browser.call('Emulation.setEmulatedMedia', {'features': []})

        browser.viewport(390)
        browser.navigate((ROOT / 'contact.html').as_uri())
        browser.evaluate("document.querySelector('#contactForm button').focus()")
        browser.key('Enter')
        check('Required name/message and first invalid focus', browser.evaluate("document.activeElement.id==='name' && document.querySelector('#name').getAttribute('aria-invalid')==='true' && document.querySelector('#message').getAttribute('aria-invalid')==='true' && !document.querySelector('#email').hasAttribute('aria-invalid')"))
        check('Validation associated with controls', browser.evaluate("['name','email','message'].every(id=>document.getElementById(id).getAttribute('aria-describedby').split(' ').includes(id+'Error'))"))
        browser.evaluate("document.querySelector('#name').value='Test'; document.querySelector('#message').value='Pertanyaan'; document.querySelector('#email').value='invalid'; document.querySelector('#contactForm button').focus()")
        browser.key('Enter')
        check('Invalid optional email blocks and receives focus', browser.evaluate("document.activeElement.id==='email' && document.querySelector('#email').getAttribute('aria-invalid')==='true'"))
        for email in ('', 'qa@example.com'):
            browser.evaluate("""window.__popup={opener:'original',location:{replace(url){window.__whatsapp=url}}}; window.open=()=>window.__popup;
              document.querySelector('#name').value='Uji & Nama +';
              document.querySelector('#message').value='Pesan & tanya?\\nBaris kedua + %';
              document.querySelector('#email').value=""" + json.dumps(email) + ";document.querySelector('#contactForm button').focus()")
            browser.key('Enter')
            actual = browser.evaluate("({url:window.__whatsapp || '', opener:window.__popup.opener, reset:[...document.querySelectorAll('.form input,.form textarea')].every(e=>e.value===''),text:window.__whatsapp ? new URL(window.__whatsapp).searchParams.get('text') : '', errors:[...document.querySelectorAll('.error-message')].map(e=>e.textContent),active:document.activeElement.id})")
            expected = "Assalamu'alaikum, saya ingin bertanya:\n\n👤 Nama: Uji & Nama +\n📧 Email: " + (email or '(tidak diisi)') + "\n📝 Pesan: Pesan & tanya?\nBaris kedua + %"
            check('WhatsApp content encoding, reset and isolation: ' + (email or 'optional email blank'), actual['text'] == expected and actual['reset'] and actual['opener'] is None and actual['url'].startswith('https://wa.me/6281315452107?'), actual)
        browser.evaluate("window.open=()=>null; document.querySelector('#name').value='Test';document.querySelector('#message').value='Keep this message';document.querySelector('#contactForm button').focus()")
        browser.key('Enter')
        check('Blocked popup preserves form and announces recovery', browser.evaluate("document.querySelector('#message').value==='Keep this message' && document.querySelector('#formStatus').textContent.includes('belum terbuka')"))
        browser.screenshot(OUTPUT / 'contact-popup-recovery.png')

        # Disable page scripts before navigation. DevTools inspection remains available.
        browser.call('Emulation.setScriptExecutionDisabled', {'value': True})
        for page in ('index.html', 'about.html', 'contact.html', 'admissions.html', '404.html'):
            browser.navigate((ROOT / page).as_uri())
            check(page + ': no-JS navigation and content visible', browser.evaluate("getComputedStyle(document.querySelector('.nav__list')).display!=='none' && [...document.querySelectorAll('section')].every(e=>getComputedStyle(e).opacity==='1')"))
            if page == 'contact.html':
                check('No-JS contact has direct WhatsApp fallback', browser.evaluate("document.querySelector('#contactForm').hidden && document.querySelector('noscript a').getClientRects().length>0"))
            if page == 'index.html':
                browser.screenshot(OUTPUT / 'home-no-js-mobile.png')
        browser.call('Emulation.setScriptExecutionDisabled', {'value': False})
    finally:
        browser.close()

    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / 'browser-results.json').write_text(json.dumps({'results': results, 'layouts': layouts, 'networkFailures': errors}, indent=2, ensure_ascii=False) + '\n')
    failures = [r for r in results if not r['pass']]
    print(json.dumps({'checks': len(results), 'failures': failures, 'networkFailures': len(errors)}, indent=2, ensure_ascii=False))
    return bool(failures)


def audit():
    data = []
    for page in ('index.html', 'about.html', 'contact.html', 'admissions.html', '404.html'):
        browser = Browser()
        try:
            browser.viewport(1440)
            browser.call('Page.addScriptToEvaluateOnNewDocument', {'source': """
              window.__qaLcp = null; window.__qaCls = 0;
              new PerformanceObserver(list => {for(const e of list.getEntries()) window.__qaLcp={tag:e.element?.tagName,id:e.element?.id,url:e.url,time:e.startTime};}).observe({type:'largest-contentful-paint',buffered:true});
              new PerformanceObserver(list => {for(const e of list.getEntries()) if(!e.hadRecentInput) window.__qaCls+=e.value;}).observe({type:'layout-shift',buffered:true});
            """})
            browser.navigate((ROOT / page).as_uri())
            browser.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
            contrast = browser.evaluate((ROOT / 'scripts/qa-contrast.js').read_text())
            metrics = browser.evaluate('({lcp:window.__qaLcp,cls:window.__qaCls,fonts:[...document.fonts].map(f=>({family:f.family,status:f.status,weight:f.weight}))})')
            browser.call('DOM.enable')
            browser.call('CSS.enable')
            root = browser.call('DOM.getDocument')['root']['nodeId']
            heading = browser.call('DOM.querySelector', {'nodeId': root, 'selector': 'h1'})['nodeId']
            platform_fonts = browser.call('CSS.getPlatformFontsForNode', {'nodeId': heading})
            ax = browser.call('Accessibility.getFullAXTree')['nodes']
            landmarks = [n['role']['value'] for n in ax if not n.get('ignored') and n.get('role', {}).get('value') in ('banner', 'main', 'navigation', 'contentinfo')]
            entry = {'page': page, 'contrast': contrast, 'metrics': metrics, 'renderedFonts': platform_fonts, 'landmarks': landmarks}
            if page == 'contact.html':
                browser.evaluate("document.querySelector('.location').scrollIntoView({behavior:'instant'})")
                entry['location'] = browser.evaluate("""({
                  address: document.querySelector('.location__address').textContent.trim().replace(/\s+/g,' '),
                  mapUrl: document.querySelector('.location .btn').href,
                  embeddedFrames: document.querySelectorAll('iframe').length
                })""")
                browser.screenshot(OUTPUT / 'contact-location.png')
            data.append(entry)
        finally:
            browser.close()
    (OUTPUT / 'accessibility-performance.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return any(entry['contrast']['failures'] for entry in data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--width', type=int, default=1440)
    parser.add_argument('--page', default='index.html')
    parser.add_argument('--suite', action='store_true')
    parser.add_argument('--audit', action='store_true')
    args = parser.parse_args()
    if args.suite:
        raise SystemExit(suite())
    if args.audit:
        raise SystemExit(audit())
    preview(args.width, args.page)

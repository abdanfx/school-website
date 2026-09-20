"""M1 browser regression checks using the existing local CDP client (port 9333)."""
import argparse
import json
import time
from pathlib import Path
from cdp import Browser as CDPBrowser

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.qa/m1'
RESULTS = []
PORT = 9333


def Browser():
    return CDPBrowser(port=PORT)

GEOMETRY = """(() => {
  const rect=e=>{const r=e.getBoundingClientRect();return [r.x,r.y+scrollY,r.width,r.height]};
  return {text:document.querySelector('main').textContent.replace(/\\s+/g,' ').trim(),
    elements:[...document.querySelectorAll('.header,main>section,h1,h2,h3,main p,main li,main img,figure,.actions,.footer')].map(e=>({tag:e.tagName,rect:rect(e)})),
    images:[...document.querySelectorAll('main img')].map(e=>({src:e.getAttribute('src'),srcset:e.getAttribute('srcset'),sizes:e.sizes,alt:e.alt,objectFit:getComputedStyle(e).objectFit,objectPosition:getComputedStyle(e).objectPosition})),
    height:document.documentElement.scrollHeight};
})()"""


def check(name, passed, details=None):
    RESULTS.append({'check': name, 'pass': bool(passed), 'details': details})
    if not passed:
        print('FAIL:', name, details, flush=True)


def settle(browser):
    # Native scrolling exercises each one-time observer before a settled capture.
    browser.call('Page.bringToFront')
    browser.call('Input.dispatchMouseEvent', {'type':'mouseMoved','x':0,'y':0})
    height = browser.evaluate('document.documentElement.scrollHeight')
    for y in range(0, height, 550):
        browser.evaluate(f"window.scrollTo({{top:{y},behavior:'instant'}})")
        time.sleep(0.08)
    browser.evaluate("Promise.all([...document.querySelectorAll('main img')].filter(e=>e.getClientRects().length).map(e=>{e.loading='eager';return e.decode().catch(()=>{});})).then(()=>true)")
    browser.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    time.sleep(1.2)


def geometry():
    # P04 deliberately rebuilds P03 geometry; test its composition and photo mapping.
    approved = ['1000534854', '1000512148', '1000160830', '1000520097',
                '1000163805', '1000344565', '1000512176', '1000512147',
                '1000213703', 'IMG-20221202-WA0016']
    layouts = {}
    for width in (320, 390, 768, 1024, 1440):
        browser = Browser()
        try:
            browser.viewport(width)
            browser.navigate((ROOT / 'index.html').as_uri())
            settle(browser)
            layout = browser.evaluate(GEOMETRY)
            composition = browser.evaluate("""(() => {
              const box=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};
              return {clientWidth:document.documentElement.clientWidth,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,
                sections:[...document.querySelectorAll('main>section')].map(e=>e.id),benefits:document.querySelectorAll('.benefit').length,
                hero:box('.hero'),heroImage:box('.hero__image'),heroTitle:box('.hero h1'),profileImage:box('.profile__visual img'),profilePanel:box('.profile__panel'),
                program:box('.pillars'),cards:[...document.querySelectorAll('.pillar')].map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})};
            })()""")
            check(f'{width}: P04 seven-section order', composition['sections'] ==
                  ['hero','profil','program','quran-teknologi','capaian-tahfizh','kehidupan','ppdb'])
            check(f'{width}: four-benefit strip', composition['benefits'] == 4)
            check(f'{width}: real image mapping and accessible alternatives',
                  [Path(image['src']).stem.rsplit('-', 1)[0] for image in layout['images']] == approved and
                  all(image['alt'] for image in layout['images']) and
                  not any('1000520096' in image['src'] for image in layout['images']))
            check(f'{width}: accurate cumulative metric',
                  'Juz hafalan yang telah disetorkan santri secara kumulatif' in layout['text'] and
                  'Santri telah menyelesaikan setoran hafalan 30 juz' not in layout['text'])
            check(f'{width}: no horizontal overflow', not composition['overflow'])
            if width >= 1024:
                check(f'{width}: integrated Hero, image covers majority of plane',
                      composition['heroImage']['w'] > composition['clientWidth'] * .5 and
                      abs(composition['heroImage']['y'] - composition['hero']['y']) < 6 and
                      composition['heroTitle']['right'] > composition['heroImage']['x'])
                check(f'{width}: compact desktop Hero and program',
                      480 <= composition['hero']['h'] <= 650 and composition['program']['h'] <= 700)
                check(f'{width}: three cards form one row',
                      max(card['y'] for card in composition['cards']) - min(card['y'] for card in composition['cards']) < 1)
            check(f'{width}: factual panel overlaps authentic Profile photo',
                  composition['profilePanel']['x'] < composition['profileImage']['right'] and
                  composition['profilePanel']['y'] < composition['profileImage']['bottom'])
            layouts[width] = {'layout': layout, 'composition': composition}
            if width in (320, 390, 1440):
                browser.screenshot(OUTPUT / f'p04-{width}-full.png', full=True)
                browser.screenshot(OUTPUT / f'p04-{width}-top.png')
                if width in (390, 1440):
                    for section in ('profil', 'program', 'quran-teknologi', 'capaian-tahfizh', 'kehidupan', 'ppdb'):
                        browser.evaluate(f"document.getElementById('{section}').scrollIntoView({{behavior:'instant'}})")
                        time.sleep(0.3)
                        browser.screenshot(OUTPUT / f'p04-{width}-{section}.png')
        finally:
            browser.close()
    (OUTPUT / 'geometry.json').write_text(json.dumps(layouts, indent=2))


INSTRUMENT = """(() => {
  window.__m1 = {raf:0, listeners:0, observers:[], cls:0, clsEntries:[], metricChanges:0};
  const raf=window.requestAnimationFrame;
  window.requestAnimationFrame=function(...args){__m1.raf++;return raf.apply(this,args)};
  const listen=EventTarget.prototype.addEventListener;
  EventTarget.prototype.addEventListener=function(...args){__m1.listeners++;return listen.apply(this,args)};
  const Native=window.IntersectionObserver;
  window.IntersectionObserver=class extends Native {
    constructor(callback, options){super(callback,options);this.record={options,active:new Set(),removed:0};__m1.observers.push(this.record)}
    observe(target){this.record.active.add(target);super.observe(target)}
    unobserve(target){if(this.record.active.delete(target))this.record.removed++;super.unobserve(target)}
    disconnect(){this.record.active.clear();super.disconnect()}
  };
  new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput){__m1.cls+=e.value;__m1.clsEntries.push({value:e.value,sources:e.sources.map(s=>({tag:s.node?.tagName,cls:s.node?.className,previous:s.previousRect.toJSON(),current:s.currentRect.toJSON()}))})}}).observe({type:'layout-shift',buffered:true});
  document.addEventListener('DOMContentLoaded',()=>{
    __m1.hero=document.getAnimations().filter(a=>a.effect.target?.closest('[data-hero]')).map(a=>({duration:a.effect.getTiming().duration,delay:a.effect.getTiming().delay}));
    new MutationObserver(list=>__m1.metricChanges+=list.length).observe(document.querySelector('.evidence__value'),{childList:true,characterData:true,subtree:true});
  },{once:true});
})()"""


def point(browser, selector):
    return browser.evaluate("""(() => {const r=document.querySelector(""" + json.dumps(selector) + """).getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()""")


def tap(browser, coordinates, touch=False):
    if touch:
        browser.call('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [coordinates]})
        browser.call('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    else:
        browser.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'button': 'left', 'clickCount': 1, **coordinates})
        browser.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'button': 'left', 'clickCount': 1, **coordinates})


def interaction():
    for width in (1440, 390, 320):
        browser = Browser()
        try:
            browser.viewport(width, 900 if width == 1440 else 844)
            browser.call('Page.addScriptToEvaluateOnNewDocument', {'source': INSTRUMENT})
            touch = width < 760
            browser.call('Emulation.setTouchEmulationEnabled', {'enabled': touch, 'maxTouchPoints': 1})
            browser.navigate((ROOT / 'index.html').as_uri())
            time.sleep(1.1)
            label = f'{width}'
            check(label + ': three shared observers', browser.evaluate('__m1.observers.length===3'))
            check(label + ': Hero rests within 950ms', browser.evaluate('__m1.hero.every(a=>a.duration+a.delay<=950) && document.getAnimations().length===0'), browser.evaluate('__m1.hero'))
            check(label + ': only ten explicit photo buttons, one dormant dialog', browser.evaluate("document.querySelectorAll('[data-photo] > .photo-trigger').length===10 && document.querySelectorAll('dialog').length===1 && !document.querySelector('dialog').open && !document.querySelector('.photo-lightbox__image').hasAttribute('src')"))
            check(label + ': compact P04 navigation geometry', browser.evaluate("!document.querySelector('.header').classList.contains('is-scrolled') && document.querySelector('.header').getBoundingClientRect().height>=80 && document.querySelector('.header').getBoundingClientRect().height<=90"))
            check(label + ': no layout shift', browser.evaluate('__m1.cls===0'), browser.evaluate('({value:__m1.cls,entries:__m1.clsEntries})'))
            for y in (24, 25, 24, 25):
                browser.evaluate(f"scrollTo({{top:{y},behavior:'instant'}})")
                time.sleep(0.06)
                check(label + f': nav stable at {y}px', browser.evaluate("document.querySelector('.header').classList.contains('is-scrolled')"))
            browser.evaluate("scrollTo({top:0,behavior:'instant'})")
            time.sleep(0.1)
            check(label + ': return to top restores surface', browser.evaluate("!document.querySelector('.header').classList.contains('is-scrolled')"))
            for section in ('hero', 'profil', 'program', 'quran-teknologi', 'capaian-tahfizh', 'kehidupan', 'ppdb'):
                browser.evaluate('location.hash=' + json.dumps('beranda' if section == 'hero' else section))
                time.sleep(1.05)
                state = browser.evaluate("""({active:document.querySelector('.header').dataset.activeSection,
                    count:document.querySelectorAll('.nav__link[aria-current]').length,
                    top:document.getElementById(""" + json.dumps(section) + """).getBoundingClientRect().top,
                    header:document.querySelector('.header').getBoundingClientRect().bottom,
                    scroll:scrollY,max:document.documentElement.scrollHeight-innerHeight})""")
                check(label + ': active anchor ' + section, state['active'] == section and state['count'] == 1, state)
                if section != 'hero':
                    # A short final PPDB section can settle lower when the document reaches its end.
                    at_document_end = section == 'ppdb' and abs(state['scroll'] - state['max']) <= 1
                    check(label + ': sticky offset ' + section,
                          state['top'] >= state['header'] and (state['top'] <= 150 or at_document_end), state)
            browser.navigate((ROOT / 'index.html').as_uri() + '#quran-teknologi')
            time.sleep(1.1)
            check(label + ': deep reload state', browser.evaluate("document.querySelector('.header').dataset.activeSection==='quran-teknologi' && document.querySelector('.header').classList.contains('is-scrolled') && document.querySelectorAll('.nav__link[aria-current]').length===1"))
            restored_y = browser.evaluate('scrollY')
            browser.evaluate("history.replaceState(null,'',location.pathname)")
            browser.call('Page.reload')
            time.sleep(1.1)
            check(label + ': reload restores reading position without hash', browser.evaluate("document.querySelector('.header').dataset.activeSection==='quran-teknologi' && Math.abs(scrollY-" + str(restored_y) + ")<=1"))
            if touch:
                check(label + ': touch has no fine-pointer hover', browser.evaluate("!matchMedia('(hover: hover) and (pointer: fine)').matches"))
                browser.evaluate("document.querySelector('.nav__toggle').focus()")
                browser.key('Enter')
                browser.key('Tab')
                check(label + ': keyboard opens menu and reaches link', browser.evaluate("document.querySelector('.nav__toggle').getAttribute('aria-expanded')==='true' && document.activeElement.matches('.nav__link') && document.activeElement.matches(':focus-visible')"))
                browser.key('Escape')
                check(label + ': closing menu immediately excludes hidden links', browser.evaluate("document.querySelector('.nav__list').inert && document.activeElement.matches('.nav__toggle')"))
                time.sleep(0.15)
                check(label + ': Escape completes menu close', browser.evaluate("getComputedStyle(document.querySelector('.nav__list')).display==='none'"))
                browser.key('Enter')
                browser.viewport(width, 390)
                time.sleep(0.15)
                check(label + ': orientation resize clears disclosure state', browser.evaluate("document.querySelector('.nav__toggle').getAttribute('aria-expanded')==='false'"))
                browser.viewport(width, 844)
            settle(browser)
            check(label + ': one-time reveals unobserved after traversal', browser.evaluate("__m1.observers.filter(o=>o.options?.rootMargin==='0px 0px 140px 0px').every(o=>o.active.size===0 && o.removed>0)"))
            contrast = browser.evaluate((ROOT / 'scripts/qa-contrast.js').read_text())
            check(label + ': settled homepage text contrast', not contrast['failures'], contrast)
            check(label + ': no pending visible content or idle animations', browser.evaluate("![...document.querySelectorAll('.is-pending')].some(e=>e.getClientRects().length) && document.getAnimations().length===0"))
            check(label + ': metric never mutates', browser.evaluate("__m1.metricChanges===0 && document.querySelector('.evidence__value').textContent==='230+'"))
            check(label + ': native motion uses zero RAF calls', browser.evaluate('__m1.raf===0'))
            if not touch:
                browser.evaluate("document.querySelector('.pillar .photo-trigger').scrollIntoView({block:'center',behavior:'instant'})")
                frame = browser.evaluate("const f=document.querySelector('.pillar .media-frame').getBoundingClientRect();({x:f.x,y:f.y,w:f.width,h:f.height})")
                browser.call('Input.dispatchMouseEvent', {'type':'mouseMoved', **point(browser, '.pillar .photo-trigger')})
                time.sleep(0.7)
                check(label + ': photographic hover is a contained 1.02 scale', browser.evaluate("Math.abs(new DOMMatrix(getComputedStyle(document.querySelector('.pillar img')).transform).a-1.02)<0.001 && getComputedStyle(document.querySelector('.pillar .media-frame')).overflow==='hidden'"), browser.evaluate("({fine:matchMedia('(hover: hover) and (pointer: fine)').matches,hover:document.querySelector('.pillar .media-frame').matches(':hover'),transform:getComputedStyle(document.querySelector('.pillar img')).transform,overflow:getComputedStyle(document.querySelector('.pillar .media-frame')).overflow,classes:document.querySelector('.pillar .media-frame').className})"))
                check(label + ': hover never lifts the program', frame == browser.evaluate("const f2=document.querySelector('.pillar .media-frame').getBoundingClientRect();({x:f2.x,y:f2.y,w:f2.width,h:f2.height})"))
                browser.call('Input.dispatchMouseEvent', {'type':'mouseMoved','x':5,'y':5})
                time.sleep(0.7)
                check(label + ': photo returns to rest after hover', browser.evaluate("getComputedStyle(document.querySelector('.pillar img')).transform==='none'"))
            browser.evaluate("document.querySelector('.hero .btn').focus()")
            browser.key('Tab');browser.key('Tab', modifiers=8)
            time.sleep(0.2)
            check(label + ': CTA focus visible with precise 4px arrow response', browser.evaluate("document.activeElement.matches('.hero .btn:focus-visible') && parseFloat(getComputedStyle(document.activeElement).outlineWidth)>=3 && Math.abs(new DOMMatrix(getComputedStyle(document.activeElement.querySelector('span')).transform).e-4)<0.01"))
            photo_count = 10
            for i in range(photo_count):
                browser.evaluate(f"window.__trigger=document.querySelectorAll('.photo-trigger')[{i}];__trigger.scrollIntoView({{block:'center',behavior:'instant'}});__trigger.focus({{preventScroll:true}})")
                time.sleep(0.1)
                reading = browser.evaluate("({y:scrollY,x:__trigger.getBoundingClientRect().x,w:__trigger.getBoundingClientRect().width})")
                browser.key(' ' if i % 2 else 'Enter', 'Space' if i % 2 else 'Enter')
                time.sleep(0.35)
                browser.evaluate("document.querySelector('.photo-lightbox__image').decode().catch(()=>{})")
                state = browser.evaluate("""(() => {
                  const d=document.querySelector('dialog'),img=d.querySelector('img'),r=img.getBoundingClientRect(),c=d.querySelector('button').getBoundingClientRect(),p=__trigger.getBoundingClientRect();
                  return {open:d.open,modal:d.matches(':modal'),focus:document.activeElement===d.querySelector('button'),name:d.getAttribute('aria-label'),alt:img.alt===__trigger.previousElementSibling.alt,
                    contained:r.x>=0&&r.right<=innerWidth&&r.y>=64&&r.bottom<=innerHeight&&r.width<=Number(__trigger.previousElementSibling.getAttribute('width')),ratio:Math.abs(r.width/r.height-img.naturalWidth/img.naturalHeight)<0.02,
                    closeContained:c.x>=0&&c.right<=innerWidth&&c.y>=0&&c.bottom<=innerHeight&&c.width>=44&&c.height>=44,
                    pageLocked:getComputedStyle(document.body).position==='fixed'&&document.documentElement.classList.contains('is-scroll-locked'),x:p.x,w:p.width,overflow:document.documentElement.scrollWidth>innerWidth};})()""")
                check(label + f': photo {i+1} keyboard modal, alt, focus', all(state[k] for k in ('open','modal','focus','name','alt')), state)
                check(label + f': photo {i+1} containment and aspect ratio', all(state[k] for k in ('contained','ratio','closeContained')) and not state['overflow'], state)
                check(label + f': photo {i+1} locks without horizontal jump', state['pageLocked'] and abs(state['x']-reading['x'])<0.1 and abs(state['w']-reading['w'])<0.1, state)
                browser.key('Tab')
                browser.key('Tab', modifiers=8)
                check(label + f': photo {i+1} Tab/Shift+Tab contained', browser.evaluate("document.activeElement.matches('.photo-lightbox__close')"))
                browser.evaluate("document.querySelector('.hero .btn').focus()")
                check(label + f': photo {i+1} background is inert', browser.evaluate("document.activeElement.matches('.photo-lightbox__close')"))
                tap(browser, point(browser, '.photo-lightbox__image'), touch)
                check(label + f': photo {i+1} image tap stays open', browser.evaluate("document.querySelector('dialog').open"))
                browser.call('Input.dispatchMouseEvent', {'type':'mouseWheel','x':10,'y':700,'deltaY':400,'deltaX':0})
                check(label + f': photo {i+1} wheel cannot scroll background', browser.evaluate('scrollY===0'))
                if i == 0:
                    ax = browser.call('Accessibility.getFullAXTree')['nodes']
                    roles = [n.get('role', {}).get('value') for n in ax if not n.get('ignored')]
                    check(label + ': modal accessibility tree excludes background landmarks', 'dialog' in roles and 'banner' not in roles and 'main' not in roles, roles)
                    browser.screenshot(OUTPUT / f'lightbox-{width}.png')
                if i % 3 == 0:
                    browser.key('Escape')
                elif i % 3 == 1:
                    tap(browser, point(browser, '.photo-lightbox__close'), touch)
                else:
                    tap(browser, {'x':10,'y':browser.evaluate('innerHeight-10')}, touch)
                time.sleep(0.2)
                check(label + f': photo {i+1} closes, returns focus and exact scroll', browser.evaluate("!document.querySelector('dialog').open && document.activeElement===__trigger && !document.documentElement.classList.contains('is-scroll-locked') && getComputedStyle(document.body).position!=='fixed' && Math.abs(scrollY-" + str(reading['y']) + ")<=1"))
            # Native mouse/touch opening; pointer-down on image then release on backdrop cannot dismiss.
            browser.evaluate("document.querySelector('.life__learning .photo-trigger').scrollIntoView({block:'center',behavior:'instant'})")
            tap(browser, point(browser, '.life__learning .photo-trigger'), touch)
            time.sleep(0.35)
            check(label + ': photo activates by pointer/touch', browser.evaluate("document.querySelector('dialog').open"))
            image_point = point(browser, '.photo-lightbox__image')
            browser.call('Input.dispatchMouseEvent', {'type':'mousePressed','button':'left','clickCount':1,**image_point})
            browser.call('Input.dispatchMouseEvent', {'type':'mouseReleased','button':'left','clickCount':1,'x':10,'y':10})
            check(label + ': image-to-backdrop release stays open', browser.evaluate("document.querySelector('dialog').open"))
            # No selected photograph is portrait: use a test-only intrinsic portrait fixture.
            browser.evaluate("const im=document.querySelector('.photo-lightbox__image');im.srcset='';im.width=600;im.height=900;im.src='data:image/svg+xml,'+encodeURIComponent('<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"600\" height=\"900\"><rect width=\"600\" height=\"900\" fill=\"#103e32\"/></svg>')")
            browser.evaluate("document.querySelector('.photo-lightbox__image').decode()")
            check(label + ': portrait fixture contained without crop', browser.evaluate("(() => {const r=document.querySelector('.photo-lightbox__image').getBoundingClientRect();return r.left>=0 && r.right<=innerWidth && r.top>=64 && r.bottom<=innerHeight && Math.abs(r.width/r.height-2/3)<0.01})()"))
            browser.viewport(844, 390)
            time.sleep(0.2)
            check(label + ': rotated modal keeps photo/close visible', browser.evaluate("(() => {const r=document.querySelector('.photo-lightbox__image').getBoundingClientRect(),c=document.querySelector('.photo-lightbox__close').getBoundingClientRect();return r.top>=64 && r.bottom<=innerHeight && c.bottom<=innerHeight})()"))
            browser.key('Escape');time.sleep(0.2)
            check(label + ': rotation close releases scroll', browser.evaluate("!document.querySelector('dialog').open && !document.documentElement.classList.contains('is-scroll-locked')"))
            browser.viewport(width, 844)
            # Repeated activation must reuse nodes and listeners.
            counts = browser.evaluate('({nodes:document.querySelectorAll("*").length,listeners:__m1.listeners})')
            for _ in range(12):
                browser.evaluate("document.querySelector('.life__learning .photo-trigger').click()")
                browser.key('Escape');time.sleep(0.14)
            check(label + ': 12 repeat cycles do not add nodes/listeners', counts == browser.evaluate('({nodes:document.querySelectorAll("*").length,listeners:__m1.listeners})'))
            check(label + ': no runtime errors', not [e for e in browser.events if e.get('method') == 'Runtime.exceptionThrown'])
            check(label + ': no animation dependency/canvas', browser.evaluate("document.scripts.length===1 && !document.querySelector('canvas') && __m1.raf===0"))
            print('Interaction checks complete:', width, flush=True)
        finally:
            browser.close()


def accessibility_modes():
    for width in (1440, 390, 320):
        browser = Browser()
        try:
            browser.viewport(width, 844)
            browser.call('Emulation.setEmulatedMedia', {'features':[{'name':'prefers-reduced-motion','value':'reduce'}]})
            browser.navigate((ROOT / 'index.html').as_uri())
            check(f'{width} reduced: content immediate, zero pending/spatial animation', browser.evaluate("!document.querySelector('.is-pending,.is-entering') && getComputedStyle(document.documentElement).scrollBehavior==='auto' && [...document.querySelectorAll('[data-reveal]')].every(e=>getComputedStyle(e).opacity==='1' && getComputedStyle(e).transform==='none') && document.querySelector('.evidence__value').textContent==='230+'"))
            browser.evaluate("location.hash='kehidupan'");time.sleep(0.1)
            check(f'{width} reduced: active navigation still works', browser.evaluate("document.querySelector('.header').dataset.activeSection==='kehidupan'"))
            browser.evaluate("window.__trigger=document.querySelector('.life__group .photo-trigger');__trigger.focus()")
            browser.key('Enter')
            check(f'{width} reduced: modal immediate without zoom', browser.evaluate("document.querySelector('dialog').open && getComputedStyle(document.querySelector('.photo-lightbox__image')).transform==='none' && getComputedStyle(document.querySelector('dialog')).transitionDuration==='0s'"))
            browser.key('Escape')
            check(f'{width} reduced: modal immediate dismissal and focus return', browser.evaluate("!document.querySelector('dialog').open && document.activeElement===__trigger && !document.documentElement.classList.contains('is-scroll-locked')"))
            if width < 760:
                browser.evaluate("document.querySelector('.nav__toggle').focus()")
                browser.key('Enter');browser.key('Tab');browser.key('Escape')
                check(f'{width} reduced: keyboard menu immediate and usable', browser.evaluate("document.activeElement.matches('.nav__toggle') && getComputedStyle(document.querySelector('.nav__list')).display==='none'"))
            browser.call('Emulation.setEmulatedMedia', {'features':[]})
            browser.navigate((ROOT / 'index.html').as_uri())
            browser.call('Emulation.setEmulatedMedia', {'features':[{'name':'prefers-reduced-motion','value':'reduce'}]})
            time.sleep(0.05)
            check(f'{width}: live reduced preference resolves pending content', browser.evaluate("!document.querySelector('.is-pending,.is-entering') && document.getAnimations().length===0"))
            browser.call('Emulation.setScriptExecutionDisabled', {'value':True})
            browser.navigate((ROOT / 'index.html').as_uri())
            check(f'{width} no-JS: all original visible content at rest', browser.evaluate("![...document.querySelectorAll('[data-reveal],main img')].some(e=>e.getClientRects().length && (getComputedStyle(e).opacity!=='1'||getComputedStyle(e).transform!=='none')) && document.querySelectorAll('main img').length===10 && document.querySelector('.evidence__value').textContent==='230+'"))
            check(f'{width} no-JS: navigation/CTA anchors and images usable', browser.evaluate("getComputedStyle(document.querySelector('.nav__list')).display!=='none' && !document.querySelector('.photo-trigger,dialog') && document.querySelector('.hero .btn').getAttribute('href')==='#ppdb' && document.querySelector('.ppdb .btn').href.startsWith('https://wa.me/')"))
            browser.evaluate("document.querySelector('.hero .btn').click()")
            time.sleep(0.1)
            check(f'{width} no-JS: native anchor actually navigates', browser.evaluate("location.hash==='#ppdb' && document.querySelector('#ppdb').getBoundingClientRect().top>=document.querySelector('.header').getBoundingClientRect().bottom"))
            browser.screenshot(OUTPUT / f'no-js-{width}.png')
            browser.call('Emulation.setScriptExecutionDisabled', {'value':False})
        finally:
            browser.close()
    browser = Browser()
    try:
        browser.call('Page.addScriptToEvaluateOnNewDocument', {'source':'delete window.IntersectionObserver;'})
        browser.navigate((ROOT / 'index.html').as_uri())
        check('Missing IntersectionObserver: page visible, lightbox still functional', browser.evaluate("!document.querySelector('.is-pending') && !document.documentElement.classList.contains('motion-ready') && document.querySelectorAll('.photo-trigger').length===10"))
    finally:
        browser.close()


def cold_loads():
    samples = []
    for width in (390, 1440):
        for name, base in (('p04', ROOT),):
            browser = Browser()
            try:
                browser.call('Page.bringToFront')
                browser.viewport(width, 844)
                browser.call('Emulation.setTouchEmulationEnabled', {'enabled': width < 760, 'maxTouchPoints': 1})
                browser.call('Page.addScriptToEvaluateOnNewDocument', {'source': INSTRUMENT})
                browser.call('Network.clearBrowserCache')
                browser.call('Network.setCacheDisabled', {'cacheDisabled':True})
                browser.call('Network.emulateNetworkConditions', {'offline':False,'latency':250,'downloadThroughput':128000,'uploadThroughput':128000})
                browser.navigate((base / 'index.html').as_uri())
                time.sleep(1.2)
                metrics = browser.evaluate('({cls:__m1.cls,entries:__m1.clsEntries,fontStatus:document.fonts.status})')
                samples.append({'variant':name,'width':width,**metrics})
                print(json.dumps(samples[-1]), flush=True)
            finally:
                browser.close()
    (OUTPUT / 'cold-loads.json').write_text(json.dumps(samples, indent=2))


def delayed_script():
    samples = []
    for name, base in (('p04', ROOT),):
        browser = Browser()
        try:
            browser.call('Page.bringToFront')
            browser.viewport(390, 844)
            browser.call('Emulation.setTouchEmulationEnabled', {'enabled': True, 'maxTouchPoints': 1})
            browser.call('Page.addScriptToEvaluateOnNewDocument', {'source': INSTRUMENT})
            browser.call('Fetch.enable', {'patterns':[{'urlPattern':'*js/script.js','requestStage':'Request'}]})
            browser.call('Page.navigate', {'url':(base / 'index.html').as_uri()})
            time.sleep(1)
            browser.evaluate('document.readyState')
            browser.evaluate('document.fonts.ready.then(()=>true)')
            before = browser.evaluate("({y:document.querySelector('main').getBoundingClientRect().y,nav:document.querySelector('.nav__list').getBoundingClientRect().height})")
            request = next(e['params']['requestId'] for e in browser.events if e.get('method') == 'Fetch.requestPaused')
            browser.call('Fetch.continueRequest', {'requestId':request})
            time.sleep(1.2)
            metrics = browser.evaluate("({cls:__m1.cls,entries:__m1.clsEntries,y:document.querySelector('main').getBoundingClientRect().y})")
            samples.append({'variant':name,'before':before,**metrics})
            print(json.dumps(samples[-1]), flush=True)
        finally:
            browser.close()
    (OUTPUT / 'delayed-script.json').write_text(json.dumps(samples, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--delayed-script', action='store_true')
    parser.add_argument('--cold-loads', action='store_true')
    parser.add_argument('--port', type=int, default=9333)
    parser.add_argument('--geometry', action='store_true')
    parser.add_argument('--interactions', action='store_true')
    parser.add_argument('--accessibility', action='store_true')
    args = parser.parse_args()
    PORT = args.port
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.delayed_script:
        delayed_script()
        raise SystemExit(0)
    if args.cold_loads:
        cold_loads()
        raise SystemExit(0)
    if not args.interactions and not args.accessibility:
        geometry()
    if not args.geometry and not args.accessibility:
        interaction()
    if not args.geometry and not args.interactions:
        accessibility_modes()
    failures = [r for r in RESULTS if not r['pass']]
    (OUTPUT / 'results.json').write_text(json.dumps(RESULTS, indent=2))
    print(json.dumps({'checks': len(RESULTS), 'failures': len(failures)}, indent=2))
    raise SystemExit(bool(failures))

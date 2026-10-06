# P04 Expressive Motion v0.2 — implementation and QA

Status: **ready for Abdan visual review**, uncommitted. No merge, push, deployment, Cloudflare change, or domain migration was performed.

## Baseline and scope

Before implementation, the branch was `phase-p04-expressive-motion-v02`, with `HEAD` and `origin/main` both at `8a8fb68eb70849ca02925523bad6199e7712631d`. The approved prior-phase content changes were already uncommitted and were preserved. The public Tahfizh metric remains the literal `230` with the label “Santri yang telah menyelesaikan setoran hafalan Al-Qur'an 30 juz.” No number counter, plus sign, cumulative-juz claim, banner image, or student names were added.

P04 layout, typography, palette, photo selection, section order, navigation destinations, and link targets remain fixed. A direct comparison with the saved pre-motion P04 capture found **zero rectangle difference, zero page-height difference, and identical text** at 320, 390, 768, 1024, and 1440px after motion settled.

## Architecture

- `index.html` adds `data-motion` roles to the existing content. Only existing grouping is redistributed; no extra section, image, or content is added. The value `230` remains a literal text node.
- `css/p04-home.css` defines P04-only durations, distances, directions, easings, masks, menu responses, and lightbox presentation. All opacity, translation, and clipping states require the successfully initialized `motion-ready` class and an `is-pending` or early-Hero `is-entering` class. Static P04 is the default.
- `js/script.js` retains one shared reveal IntersectionObserver and the two existing navigation observers. It observes each card/figure box for clipped photography, then animates the photo inside its stationary frame. This lets fully clipped media reveal reliably and keeps the overlaid photo button within viewport bounds. One-time targets unobserve after arrival.
- A `scrollend` safety check resolves only targets already passed by a fast jump; older browsers use a debounced passive scroll fallback for that safety check only. Hash navigation, resize, focus, back/forward restoration, print, reduced motion, and observer initialization failure resolve pending content. No scroll-linked visual animation or RAF loop was introduced.
- The existing native `<dialog>` and its semantic photo buttons remain the only lightbox. P04 adds a finite visual opening and bounded 140ms exit while preserving modal focus, Escape, backdrop dismissal, scroll restoration, and focus return.

The editorial arrival easing is `cubic-bezier(.16,1,.3,1)`, photo glide is `cubic-bezier(.22,.61,.36,1)`, and control response is `cubic-bezier(.2,0,0,1)`. The P04-specific stylesheet grew by about 2,500 gzip bytes; the shared script grew by about 528 gzip bytes. There is no added runtime dependency, animation framework, canvas, or permanent timer/animation loop.

## Implemented choreography

| Area | Desktop | Mobile / reduced motion |
| --- | --- | --- |
| Header/navigation | Existing surface blends over 280ms; active rule draws over 220ms; no header travel. | In-flow menu opens over 240ms with 12px/200ms item arrival and 25ms stagger. Reduced motion changes state immediately. |
| Hero | Eyebrow from left; headline rises 56px/950ms; support and CTAs follow; the authentic photo reveals from the right and its image travels 60px over 1100ms; callout follows. | Text arrives first; headline rises 34px/760ms, photo moves at most 40px/850ms, and the callout follows without blocking the CTA. Reduced motion shows the complete static Hero. |
| Profile | Label/text from left 28–48px; photo reveals from right with 52px travel/1000ms; panel rises 26px/650ms. | Text, photo, panel follow reading order with 24–36px vertical travel. Reduced motion has no travel or mask. |
| Three pillars | Heading from left; card photos reveal bottom-up with 54px travel/950ms and 0/120/240ms card offsets; number, title, and copy follow. | Each stacked card triggers from its own box, with zero between-card offset and 22–36px travel. Reduced motion leaves all cards static. |
| Qur'an × Technology | Heading rises 44px/920ms; photo reveals from left with 72px image travel/1150ms; copy enters from right 48px/850ms; cyan rule and four 30px list rows follow at 75ms offsets. | Photo and copy follow document order with shorter vertical travel and row offsets. Reduced motion removes clip, travel, and rule draw. |
| Capaian Tahfizh | Intro enters first; literal `230` rises 64px through its own clip over 1000ms; label and opposing copy follow. | Number rises at most 36px. Reduced motion presents the literal value and all copy immediately. |
| Kehidupan | Intro then independent mosaic figures from left, right, and below, with 48–64px travel over 850–1000ms; captions follow their own photos. | Each figure reveals independently in document order with 30–36px vertical travel. Reduced motion leaves figures and captions static. |
| PPDB | Kicker/heading from left up to 48px/850ms, copy then action group from right 34px/750ms. | Single-column upward travel at most 28px. Reduced motion makes CTAs immediately visible. |
| Footer | Identity and columns rise 20–28px over 600–650ms; copyright rule draws once. | Shorter vertical travel; reduced motion shows all details at rest. |
| Controls/photos | Button and link response 220ms; arrow shift 5px; contained fine-pointer photo hover max 1.02. | No touch hover zoom. Reduced motion removes spatial response while retaining focus and color feedback. |
| Lightbox | Backdrop 240ms; image rises 20px and scales 0.98→1 over 360ms; exit remains bounded at 140ms. | Image travels 10px or less over 280ms. Reduced motion opens and closes immediately with native modal behavior intact. |

## Progressive enhancement and accessibility

Before JavaScript, during a delayed script, when IntersectionObserver is missing or throws, and with JavaScript disabled, content has its original visible P04 styling. Late initialization does not replay the Hero. Offscreen targets are armed only after observer installation succeeds. Focus on an offscreen photo button immediately resolves its section; the photo button stays inside its stationary frame during animation. Live reduced-motion changes clear all pending targets and remove translation, clip, scale, stagger, and decorative rule drawing. Native anchors, keyboard navigation, the in-flow menu, and the dialog remain functional.

## QA and evidence

| Command / comparison | Result |
| --- | --- |
| `python3 scripts/qa-static.py` | 545 checks, 0 failures; ten approved photos. |
| `python3 scripts/qa-m1.py --geometry` | 36 checks, 0 failures; settled P04 geometry/text comparison is exact at five widths. |
| `python3 scripts/qa-m1.py --interactions` | 373 checks, 0 failures; navigation, hover/focus, observer cleanup, dialog, and zero RAF use. |
| `python3 scripts/qa-m1.py --accessibility` | 27 checks, 0 failures; reduced motion, live preference change, no-JS, missing observer. |
| `python3 scripts/qa-m1.py --expressive` | 60 checks, 0 failures; actual observer-triggered section motion, independent mobile card, fast scroll, focus, delayed script, failed observer, lightbox, and captures. |
| `python3 scripts/qa.py --suite` | 408 checks, 0 failures, 0 network failures across five pages and 320–1920px viewports. |
| `python3 scripts/qa.py --audit` | All five pages have zero contrast failures; homepage minimum measured ratio 6.117:1 and CLS 0 in the settled audit. |
| `python3 scripts/build-production.py` then `python3 scripts/qa-dist.py` | 39-file local artifact; 17 distribution checks, 0 failures. No deployment. |
| `git diff --check` | Pass. |

Ignored local evidence is in `.qa/p04-v02/`: for **1440, 390, and 320px**, `*-hero-during.png`, `*-hero-after.png`, `*-{profil,program,quran-teknologi,capaian-tahfizh,kehidupan,ppdb}-{during,after}.png`, `*-lightbox-{during,after}.png`, and `*-full-after.png`. Additional observer-driven mid-state captures show the technology photo, literal metric, life primary photo, and third mobile card. `.qa/m1/geometry.json` and `.qa/p04-v02/baseline/geometry.json` hold the compared settled geometry.

Cold-load CLS varies with the inherited font/navigation loading path. In one controlled comparison against an ignored local archive of the P04 commit, both variants measured CLS 0 at 390px; at 1440px v0.2 measured 0.021715 and baseline 0.034784. Holding the deferred script at 390px produced the **same** 0.138586 CLS in both variants as the baseline expanded mobile menu collapses after enhancement. These stress results are not a guarantee of zero CLS under delayed JavaScript. The motion itself changes no layout boxes or page height. Browser evidence uses headless Chrome; physical-device Safari/Firefox and a live screen-reader session were outside this local QA.

## Plan refinements and review state

The Hero headline uses full-line opacity/translation instead of a deep text clip so the early frame does not look blank. Hero photography begins with a partial visible slice, and offscreen Hero media has no extra entrance delay. Photography moves inside fixed frames; observer triggers use their existing card or figure box to keep clipping robust and photo controls in bounds. Tablet travel is capped at 30px where a longer horizontal offset would cross the viewport edge. These changes preserve the approved P04 resting composition and the plan's timing, hierarchy, and direction.

**Recommendation: READY FOR ABDAN VISUAL REVIEW.** Keep the branch uncommitted until review.

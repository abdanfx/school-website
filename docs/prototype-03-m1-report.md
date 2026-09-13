# Prototype 03 — M1 core motion and interaction report

Implemented on `phase-p03-m1-motion-interaction`, starting from a clean worktree at `4d8a3309aefe7c82e90e140042761d0b7ce2b546`. The protected `p03-visual-strong-pass-pre-motion` tag remains at that checkpoint. Changes are left uncommitted.

## Files changed

- `index.html`: explicit reveal/group timing metadata and ten photography clipping containers. Image nodes, source sets, sizes, dimensions, alternatives, visible copy, navigation links, section order, and captions are preserved.
- `css/style.css`: shared motion tokens, editorial/media/rule/quiet primitives, responsive stagger, CTA responses, navigation surfaces, focus treatments, modal presentation, and reduced-motion/print fallbacks. Grid placement moves from the two grid-level images to their corresponding clipping containers, preserving measured geometry.
- `js/script.js`: shared disclosure state, homepage observers, fail-open reveal initialization, and one native photography dialog. Existing contact-form behavior remains in an independent closure.
- `scripts/qa-static.py`: replaces the pre-M1 ban on reveal opacity with an observer-initialization guard and removes the obsolete prohibition on the now-approved navigation backdrop filter. All content, asset, anchor, and internal-page regressions remain.
- `scripts/qa-m1.py`: adds targeted browser checks using the existing dependency-free `scripts/cdp.py`; reconstructs the protected baseline in ignored QA storage for direct geometry comparison.
- `README.md`: documents M1 behavior, verification, and report location.
- `docs/prototype-03-m1-report.md`: records implementation decisions, checks, and review artifacts.

No production photographs or internal-page HTML files changed.

## Motion architecture

Visible HTML is the baseline. JavaScript first installs one shared reveal observer, arms only future offscreen targets, then applies `motion-ready`. Preparation itself has no transition. Content already in view stays available; a prompt initial Hero load receives a finite CSS entrance. Late initialization and deep loading do not replay Hero animation. Initialization failure removes pending state. Keyboard focus immediately resolves the relevant group. Each one-time target is unobserved when revealed; restored back/forward pages and printing resolve pending content.

Tokens: 120 / 180 / 280 / 420 / 620 / 760ms; interface, editorial, and exit easing; 20px desktop and 12px mobile travel; 60ms desktop and 30ms mobile stagger; 4px arrow movement; 1.025 media entrance and 1.02 fine-pointer photographic hover. Programs use zero inter-program delay on mobile. Modal settling uses 0.985 → 1.

Reusable primitives cover grouped opacity/translation, internal image scale inside a fixed clipping context, transform-based drawing of existing rules, shared stagger, CTA arrow shifts, surface transitions, quiet image hover, and the single photography modal. Content and animation never require a completion event to become functional.

## Navigation

A non-layout sentinel and IntersectionObserver coordinate top/scrolled surface state. The top surface retains the approved Hero relationship; scrolling uses deeper emerald, a subtle border, and progressive 8px navigation-only blur with a solid fallback. Header dimensions remain unchanged; optional compression was unnecessary.

A separate observer watches all seven sections at a narrow 30%-viewport reading line. It maintains one `aria-current="location"` link and records the exact current section on the header. The frozen navigation has no separate Q×T/Capaian links: those sections retain the Program indication. Native anchors and CSS smooth scrolling remain intact. Reduced motion makes scrolling immediate. The no-JS mobile anchor offset accounts for the fully expanded fallback navigation.

The mobile menu remains the approved in-flow disclosure. It has `aria-expanded`, `aria-controls`, changing accessible labels, a 280ms opening surface, restrained item arrivals, and a 120ms exit. Closing immediately makes its links inert. Escape restores trigger focus; choosing an anchor collapses menu geometry before native scrolling and focuses the destination. Outside interaction, focus departure, and resize close the disclosure. It is not an overlay and does not need modal background locking.

## Section behavior

| Section | Implemented behavior |
| --- | --- |
| Hero | Shared A/B/C timing; editorial text groups overlap the clipped 1.025 → 1 image entrance. Typical configured settlement is 740ms on desktop. No parallax or continuing movement. |
| Profile | Calm introduction/content group, media reveal, four short fact/rule steps. |
| Programs | Equal 0/60/120ms desktop story timing, overlapping photo/index/title/copy, existing section rule draw; independent viewport arrivals with zero inter-program delay on mobile. |
| Qur’an × Technology | Identity, heading, supporting copy, cyan line, staggered technical rows, and the longest media completion. All motion stops after the one-time entrance. |
| Capaian | One editorial reveal of the metric group and supporting evidence. The literal `230+` remains in the initial DOM and is never mutated. |
| Kehidupan | Existing mosaic and DOM order; primary, secondary, supporting, and archive photo timing. Captions resolve quietly. The original archive label and mobile archive visibility rule remain. |
| PPDB | Label/heading and content/CTA groups; shared Hero interaction vocabulary. |
| Footer | One short quiet group and the existing copyright rule. |

## Photography lightbox

All ten approved photographs are explicitly eligible: Hero, Profile, three Programs, Q×T, three Kehidupan photographs, and archive. The archive retains its baseline `display: none` rule at widths ≤600px, so nine photo triggers are visible at 390/320px.

One dialog is built once when native modal support is available. Ten named semantic buttons overlay the photographs, leaving the image nodes and alternatives intact. Enter, Space, click, and touch open the chosen photograph. The dialog provides a visible 48×48px `×` button named “Tutup foto”, blank-backdrop dismissal, and Escape. Backdrop dismissal checks both the pointer origin and final target: the enlarged image does not close itself, and dragging from image to backdrop does not dismiss it.

Native `showModal()` establishes modal semantics and background inertness. Focus enters the close button; Tab and Shift+Tab stay there. Closing restores the original trigger with `preventScroll`. The fixed-body scroll lock preserves the original inline body style, compensates the scrollbar gutter, and restores the saved coordinates before releasing the temporary scroll behavior. The bounded exit has a timeout independent of CSS transition completion; reduced motion closes immediately. Repeated activation reuses the same dialog/image/control and listeners.

The image preserves its aspect ratio and fits within viewport breathing room. Its maximum width is capped at its existing production derivative width. A larger existing responsive derivative may load on demand; no image generation, processing, new asset, or gallery dependency is involved. No carousel, navigation controls, zoom/pan, downloads, or fullscreen behavior is added.

## Accessibility and progressive enhancement

Reduced motion is a live behavioral mode: pending content resolves, spatial entrances/hover zoom/stagger disappear, anchors become immediate, and the modal/menu continue functioning. Explicit visible focus covers links, CTAs, menu items, photograph buttons, and the modal close control. Photography uses an inset two-color focus treatment so clipping cannot hide it.

With JavaScript disabled, original text/images and native links remain available, the mobile navigation stays expanded, the literal metric remains visible, and lightbox buttons/dialog are absent. Missing IntersectionObserver leaves the content visible while supported modal functionality remains available. No focus or conversion requires pointer hover.

## Performance

Normal motion uses three shared IntersectionObservers: reveal, section state, and navigation sentinel. Resizing replaces/disconnects the section observer rather than accumulating observers. Reduced-motion startup uses only the two navigation observers. There is no scroll listener, RAF call, permanent animation loop, global `will-change`, canvas, or new runtime dependency. Main animation properties are opacity and transform; only restrained interface surface colors and the small navigation blur supplement them.

Listeners are installed at initialization, including ten photo activation listeners and shared modal/disclosure handlers. No listeners or DOM nodes are added by repeated lightbox opening. The complete shared JavaScript is 15,665 bytes raw and 4,605 bytes gzip; the increase over the protected checkpoint is 2,823 bytes gzip. The final instrumented run recorded zero animation-frame calls and zero layout shift on the homepage at 1440, 390, and 320px.

## QA results

| Command / check | Final outcome |
| --- | --- |
| `python3 scripts/qa-static.py` | PASS — 210 checks, zero failures, all ten approved source photographs. |
| `python3 scripts/qa.py --suite` | PASS — 267 checks, zero failures, zero network failures. Five pages at 320, 360, 390, 768, 1024, 1280, 1440, and 1920px, including existing form and no-JS behavior. |
| `python3 scripts/qa.py --audit` | PASS — all five pages returned zero computed contrast failures; homepage CLS 0 in the final standalone audit. |
| `python3 scripts/qa-m1.py --port 9334` | PASS — 399 checks, zero failures. |
| `git diff --check` | PASS — no whitespace errors. |

The 399 M1 checks include five direct baseline geometry comparisons (320/390/768/1024/1440px, 0.1px tolerance), unchanged copy/photo attributes, explicit observer bookkeeping, native anchors and offsets across all seven sections, deep reload with and without a hash, menu resize handling, Hero timing, quiet hover/CTA focus, all visible photographs at 1440/390/320px, native modal accessibility-tree isolation, keyboard trapping/return, actual pointer/touch clicks, all close methods, image-to-backdrop release, exact scroll restoration, a test-only portrait fixture, rotation, 12 repeated modal cycles per viewport, live reduced motion, no-JS links, and missing-IntersectionObserver fallback.

The final Hero samples settled at 740ms desktop, 680ms at 390px, and 650ms for the visible text at 320px; the below-fold mobile photograph reveals when approached. After traversal, the reveal observer had no remaining targets and no animations remained active. Settled homepage contrast passed 71 text samples at 1440px and 64 at each mobile width, with a minimum ratio of 5.2996:1. The final run recorded homepage CLS 0 at all three interaction widths and zero runtime exceptions.

QA refinements: pending-state preparation was made transition-free; no-JS mobile anchor clearance was corrected; smaller lightbox assets gained an explicit maximum-width cap. Early overlapping browser runs caused background-observer sampling failures, so final suites ran sequentially. The initial headless browser reported no fine pointer; a separate browser on port 9334 explicitly declared desktop pointer capabilities, with touch emulation enabled for mobile tests. This verified the capability-gated hover branch without changing production CSS to bypass it. Additional baseline comparisons identified the existing load-time limitations:

- `python3 scripts/qa-m1.py --cold-loads --port 9334`: browser cache cleared, 250ms network latency and 128,000 bytes/s throughput. At 390px, baseline CLS was 0.0009958 and M1 was 0. At 1440px, baseline was 0.0021140 and M1 was 0.0002349. Recorded sources include the navigation text metrics during font loading. No increased CLS was measured.
- `python3 scripts/qa-m1.py --delayed-script --port 9334`: intentionally held the deferred script until after the fallback page rendered. Both baseline and M1 recorded exactly 0.1215636 total CLS. The expanded-to-enhanced mobile navigation contributed exactly 0.1185448 in each version, moving the main-content start from 174.15625px to 67px. This reproduced the larger transient mobile reading and confirmed it is pre-existing behavior.

The normal completed suite recorded zero CLS; the stress comparisons found no M1 increase. **Absolute zero CLS under delayed JavaScript or cold font loading is not guaranteed by the protected baseline or this implementation.** Its expanded no-JS navigation and external font-loading policy are preserved. The stress-test results are saved separately as `cold-loads.json` and `delayed-script.json`.

A standalone `node --check` attempt was unavailable because Node is not installed. Chrome successfully parsed and executed the complete production script in the browser suites. No runtime dependency was installed for syntax checking.

QA artifacts are local and ignored under `.qa/m1/`.

The existing audit measures opaque text contrast and an early local-file rendering snapshot. It is not a production-network LCP benchmark or a complete WCAG certification. M1 additionally checks settled homepage contrast, native modal accessibility-tree isolation, keyboard interactions, and reduced-motion behavior. Testing uses installed headless Chrome with desktop/touch emulation; physical-device Safari/Firefox and an actual screen-reader session were not available in this environment.

Review artifacts include `m1-1440-full.png`, `m1-390-full.png`, `m1-320-full.png`, per-section 1440/390px captures, `lightbox-1440.png`, `lightbox-390.png`, `lightbox-320.png`, no-JS captures, and machine-readable `geometry.json` / `results.json`.

## Deviations

No intentional deviations from the locked M1 specification.

The six-link navigation mapping, in-flow mobile disclosure, lack of optional header compression, and mobile archive visibility preserve the protected implementation. No M2 behavior was introduced.

## Git state

Final worktree: five modified tracked files and two new untracked files, all available for review. Implementation and documentation remain uncommitted on `phase-p03-m1-motion-interaction`. No history, branch, protected tag, baseline asset, or internal-page HTML was changed; no merge, push, or deployment occurred.

Implementation and automated acceptance gate: **PASS — ready for review, uncommitted.**

# M1 CORE MOTION & INTERACTION IMPLEMENTATION STATUS

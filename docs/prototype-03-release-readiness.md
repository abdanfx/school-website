# Prototype 03 — production QA and release readiness v0.1

Date: 2026-09-16
Branch: `phase-p03-production-qa-release-hardening`
Protected starting point: `2edea99` / `p03-internal-pages-strong-pass`

## Decision

**PASS WITH DEPLOYMENT PREREQUISITES.** No remaining code-level BLOCKER or MAJOR finding was identified. The five-page site is coherent, lightweight, keyboard-operable, responsive across the tested matrix, and regression-safe against the protected homepage/M1 geometry. This is not a WCAG certification or a production-network Core Web Vitals report.

No redesign, M2 motion, WebGL/Three.js, framework, dependency, backend, hosting migration, deployment, commit, tag, merge, or push was performed.

## Baseline and changes

The initial worktree was clean at `2edea99`. Protected tags resolved as expected: `p03-internal-pages-strong-pass` → `2edea99`, `p03-m1-motion-strong-pass` → `1d1da20`, and `p03-visual-strong-pass-pre-motion` → `4d8a330`.

Before edits, the current suites passed: static 300/300, browser 377/377 with zero network failures, rendered contrast with no failures, M1 399/399, and `git diff --check`.

Justified production changes:

- Corrected the footer shorthand from `Bojong Gede` to the authoritative `Bojonggede` spelling on all five pages.
- Added page-specific, hostname-independent Open Graph and Twitter summary metadata to the four indexable pages.
- Added `noindex, follow` to `404.html`.
- Expanded the existing static/browser QA gates for document structure, unique metadata, heading order, labels and ARIA references, valid links, external-link protections, social metadata, authoritative contact data, debug/artifact hygiene, 24 × 24 CSS-pixel target minimums, skip links, and settled fragment back/forward behavior.

No CSS, production JavaScript, photography, layout, visible homepage copy, or approved internal-page composition changed.

## Audit results

### Architecture, content, semantics, and accessibility

- All primary/footer/logo/CTA destinations and local fragments resolve; no empty or script/data links exist.
- Active-page states are correct on About, Contact, and PPDB. Homepage location state, deep hashes, reloads, and settled browser history pass.
- The institution name is consistent. The verified WhatsApp target is `6281315452107`; Contact contains the authoritative school-building address and exact Google Maps URL. No deprecated Yayasan map or Prototype 01 production language remains.
- PPDB keeps cautious guidance and invents no fees, dates, quotas, requirements, or other operational facts.
- Every page has Indonesian language, charset, viewport, one unique title/description, one H1, logical heading order, header/main/footer landmarks, unique IDs, and valid referenced IDs.
- Contact labels, required controls, error associations, first-invalid focus, optional-email validation, safe URL encoding, opener isolation, popup recovery, form preservation, and no-JS direct WhatsApp fallback pass. Tests intercept popups and send no message.
- Skip links are first in keyboard order and move focus to `main`; focus remains visible. Mobile disclosure Enter/Space/Escape, focus return, outside close, resize synchronization, and short-viewport scrolling pass.
- Visible interactive targets pass the WCAG 2.2 AA 24 × 24 CSS-pixel minimum check at 320 and 390 px. Automated opaque-text contrast has no failures (lowest measured ratio 5.2996:1).
- Reduced motion, 200% reflow emulation, content without JavaScript, modal isolation/focus containment/focus return, and repeated lightbox/menu behavior pass. Automation cannot certify screen-reader announcements, physical-device input, or all WCAG success criteria.

### Responsive, photography, JavaScript, and CSS

- Five pages pass at 320, 360, 390, 768, 1024, 1280, 1440, and 1920 px with no horizontal overflow, clipped controls, hidden sections, runtime exceptions, or failed resource loads.
- Hero/profile ratios, mobile reading order, PPDB flow, address wrapping, form layout, footer, 404, 200% reflow emulation, and short viewport navigation pass.
- All approved responsive WebP sources exist and decode. Hero remains eager/high-priority; below-fold images remain lazy/async with dimensions. No production image or crop changed.
- The single native dialog implementation passes keyboard, pointer/touch, Escape, close button, backdrop, image-click, rotation, portrait containment, scroll restoration, reduced motion, and 12-cycle node/listener stability checks.
- Scripts tolerate all page variants. No runtime exceptions, duplicate modal, permanent animation-frame loop, scroll listener, animation/gallery dependency, or debug logging was found. Observer and resize behavior pass existing instrumentation.
- CSS was left unchanged. No proven collision, overflow defect, invalid rendered state, or reduced-motion conflict justified design-system edits. Potential utility/dead-rule cleanup was deliberately not performed without a stronger usage proof.

### Performance, SEO, sharing, structure, and hygiene

- Runtime remains framework-free: shared CSS 36,242 bytes raw / 7,561 gzip; JavaScript 15,663 bytes raw / 4,624 gzip; selected production image derivatives total about 2.3 MB across responsive variants. No new runtime dependency or request was added.
- Normal completed suites record no homepage layout shift. The synthetic delayed-script comparison reproduces the protected no-JS-to-enhanced mobile navigation shift equally in baseline and current (`0.1215636`). Two cold-load samples were timing-sensitive (current mobile CLS `0.1195389` once and `0` once); these local stress values are not production Core Web Vitals. The functional no-JS-first navigation behavior was preserved.
- Titles, descriptions, headings, crawlable links, language, image alternatives, basic Open Graph fields, and Twitter summary fields are present. The 404 is explicitly `noindex, follow`.
- Canonicals, `og:url`, absolute `og:image`, sitemap, and production `robots.txt` were not invented because no authoritative production hostname or approved social-preview URL is documented.
- Structured data was not added. Verified facts could support a limited educational-organization entity, but a stable production URL/entity identifier should be established first.
- Every `_blank` link has `noopener noreferrer`. No secrets, API keys, source maps, editor artifacts, QA output, Python caches, or incoming raw assets are tracked as production additions. `.qa/`, `__pycache__/`, and `assets/_incoming/` remain ignored.
- Three legacy, unreferenced initial-commit images remain tracked under `assets/images/` (about 3.6 MB). They were not deleted because they are historical source material; a production publish allow-list should exclude them.

### 404 and hosting

`404.html` works directly without JavaScript, has correct relative paths, shared navigation/footer, responsive recovery actions, and a Home CTA. No hosting target/configuration is documented, so the selected platform must be configured to serve this file for unknown routes. No hosting provider was chosen.

## Findings by severity

### BLOCKER

None in the reviewed site code.

### MAJOR

None remaining.

### MINOR

- The progressive-enhancement mobile menu can create a transient layout shift when the deferred script is intentionally delayed. This is inherited from the protected no-JS-visible navigation architecture; changing it safely requires an explicit tradeoff between pre-script stability and navigation availability if JavaScript fails.
- Production-domain metadata is incomplete until the hostname and approved share image are known.
- The existing repository email and social-account destinations were preserved but were not independently owner-verified during this local phase.

### INFORMATIONAL

- Google-hosted Plus Jakarta Sans is the only intentional third-party page-load dependency; a blocked font request falls back to sans-serif.
- A limited structured-data entity is possible after production identity/URL decisions.
- Physical Safari/Firefox/device, actual screen reader, real WhatsApp handoff, external-account availability, deployed headers, and production-network performance remain human/deployment checks.
- Legacy unreferenced images and non-runtime documentation/scripts should not be included in the public artifact.

## Deployment prerequisites

1. Establish the authoritative HTTPS production hostname and URL policy.
2. Add canonical URLs, `og:url`, and an absolute `og:image` only after the hostname and approved preview asset are known; then decide whether sitemap/production `robots.txt` are appropriate.
3. Configure the chosen static host's unknown-route behavior for `404.html` and verify direct deep links.
4. Publish an allow-listed runtime artifact: the five HTML pages, `css/`, `js/`, and referenced `assets/images/p03/` files. Exclude `.qa/`, `assets/_incoming/`, docs, scripts, browser profiles, caches, and the three unreferenced legacy images.
5. Confirm the preserved email/social accounts, real WhatsApp handoff, consent/authorization for published photography, and any host-level security/cache headers with the site owner.
6. Perform final physical-device/browser/screen-reader review and production-network measurement after deployment configuration exists.

## Reproducible QA

With the documented fine-pointer Chrome running on CDP port 9333, run sequentially:

```sh
python3 scripts/qa-static.py
python3 scripts/qa.py --suite
python3 scripts/qa.py --audit
python3 scripts/qa-m1.py --port 9333
python3 scripts/qa-m1.py --delayed-script --port 9333
python3 scripts/qa-m1.py --cold-loads --port 9333
git diff --check
```

Final authoritative outcomes before handoff: static 489/489; browser 400/400 with zero network failures; rendered contrast zero failures; M1 399/399. The delayed/cold commands are diagnostic comparisons and do not claim production CWV.

No existing QA assertion was weakened or removed. New checks provide stronger release protection. During development of the history check, an intentionally premature Back action captured a mid-animation position; the test was corrected to wait for native smooth fragment navigation to settle before recording history.

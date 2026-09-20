# SMP Tahfizh Quran Fantastis — Prototype 04

Framework-free site: HTML, the shared P03 stylesheet, a P04 homepage-only stylesheet, and deferred vanilla JavaScript. No package installation is required.

Open `index.html` directly, or serve this directory with an existing static server. The homepage uses approved P03 content, links, photography, and interactions, with a new presentation in `css/p04-home.css`. The corrected `230+` metric means cumulative juz of memorization submitted by students. `docs/p04-reference/` contains untracked local visual specifications and is excluded from the site and production artifact.

About, Contact, Admissions, and 404 use the shared Prototype 03 internal-page shell: compact institutional Hero, six-link navigation, editorial content patterns, contextual actions, and the institutional footer. Their surfaces, text, rules, and controls now follow the P04 emerald, white, and pale green palette without changing that layout. Contact uses the verified school-building address and Google Maps destination; the deprecated Yayasan/home embed is removed.

The contact form opens the verified WhatsApp destination; it does not send a message itself. Without JavaScript, navigation remains visible and the contact page offers a direct WhatsApp link.

M1 adds one-time editorial and photographic reveals, scroll-responsive homepage navigation, precise CTA feedback, and one accessible native photography dialog. Internal pages reuse these primitives at a quieter cadence. Content is visible by default; reduced motion removes spatial animation and stagger while preserving interactions. There is no animation library or continuous animation loop. See [the M1 implementation report](docs/prototype-03-m1-report.md) for the original architecture and homepage regression scope.

## Assets

The homepage requests only the selected WebP derivatives in `assets/images/p03/`. Approved originals may be kept locally in ignored `assets/_incoming/`; this isolated checkout does not require them for static QA or the production build. Additional older baseline assets have not been substituted into the homepage.

The official school mark is copied without recoloring from `assets/images/WhatsApp_Image_2024-08-17_at_07.25.14-removebg-preview(2).png` to `assets/images/brand/smptqf-logo.png`. The transparent source and the separate white-background JPEG stay outside the production artifact. Headers and footers place the green mark on a compact circular white backing beside the readable school name.

Optional deterministic regeneration, when the approved originals are available locally, with the existing FFmpeg installation:

```sh
bash scripts/prepare-images.sh
```

Source dimensions, crops, hashes, and derivative sizes are documented in [docs/prototype-03-assets.md](docs/prototype-03-assets.md). This utility is not a production build dependency.

## Local verification

```sh
python3 scripts/qa-static.py
```

## Production artifact

Cloudflare Pages must publish the generated `dist/` artifact, never the repository root:

```sh
python3 scripts/build-production.py
python3 scripts/qa-dist.py
```

The build discovers the reviewed runtime references, fails if a required source is missing, cleans stale output, and includes only the five pages, both stylesheets, shared JavaScript, referenced Prototype 03 WebP derivatives, the official school logo at `assets/images/brand/smptqf-logo.png`, and the reviewed Cloudflare `_headers` control. The source logo files remain outside the artifact. See [the Cloudflare deployment-preparation guide](docs/prototype-03-cloudflare-deployment.md) for project settings, preview verification, routing, header policy, deferred domain work, and rollback.

For browser QA, start existing Chrome in a separate terminal from this directory:

```sh
google-chrome --headless --no-sandbox --disable-gpu --disable-extensions --disable-background-networking --no-first-run --blink-settings=primaryPointerType=4,availablePointerTypes=4,primaryHoverType=2,availableHoverTypes=2 --remote-debugging-port=9333 --remote-allow-origins=http://localhost:9333 --user-data-dir="$PWD/.qa/chrome-profile" --allow-file-access-from-files about:blank
```

Then run:

```sh
python3 scripts/qa.py --suite
python3 scripts/qa.py --audit
python3 scripts/qa-m1.py
```

The QA utilities use Python's standard library and the existing browser. They intercept form popups for encoding/reset tests; they never send WhatsApp messages. Screenshots and machine-readable results are stored in the ignored `.qa/` directory. [The P03 execution report](docs/prototype-03-execution-report.md) remains historical background.

The static and browser gates cover page metadata and semantics, ARIA/label references, external-link protection, authoritative contact details, mobile target sizes, skip links, settled fragment-history behavior, P04 composition, the corrected tahfizh metric, and image integrity. [The P03 release-readiness report](docs/prototype-03-release-readiness.md) documents the baseline before this prototype.

Run browser suites sequentially so each target can receive viewport-observer callbacks without background-tab throttling. The Chrome command declares fine-pointer desktop capabilities; M1 tests explicitly switch to touch emulation for mobile checks. P04 captures in `.qa/m1/` traverse the page before taking settled full-page screenshots and check the new composition and approved image mapping. Targeted reruns are available with `--geometry`, `--interactions`, or `--accessibility` on `qa-m1.py`; `--port` selects a different local Chrome port.

The prepared Cloudflare Pages configuration uses framework preset None, build command `python3 scripts/build-production.py`, build output directory `dist`, and repository root as the root directory. Source photos, unreferenced legacy images, documentation, scripts, QA output, caches, browser profiles, and local P04 reference images are excluded from the public artifact. This prototype has not been deployed.

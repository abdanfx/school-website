# SMP Tahfizh Quran Fantastis — Prototype 03

Framework-free production integration: HTML, one shared stylesheet, and deferred vanilla JavaScript. No package installation or build step is required.

Open `index.html` directly, or serve this directory with an existing static server. The homepage uses the frozen source in [docs/prototype-03-source-of-truth.md](docs/prototype-03-source-of-truth.md), subject to the original execution specification's locked H1 and mandatory desktop archive image.

About, Contact, Admissions, and 404 use the shared Prototype 03 internal-page shell: compact institutional Hero, six-link navigation, editorial content patterns, contextual actions, and the institutional footer. The pages preserve supported school content while replacing their Prototype 01 visual patterns. Contact uses the verified school-building address and Google Maps destination; the deprecated Yayasan/home embed is removed.

The contact form opens the verified WhatsApp destination; it does not send a message itself. Without JavaScript, navigation remains visible and the contact page offers a direct WhatsApp link.

M1 adds one-time editorial and photographic reveals, scroll-responsive homepage navigation, precise CTA feedback, and one accessible native photography dialog. Internal pages reuse these primitives at a quieter cadence. Content is visible by default; reduced motion removes spatial animation and stagger while preserving interactions. There is no animation library or continuous animation loop. See [the M1 implementation report](docs/prototype-03-m1-report.md) for the original architecture and homepage regression scope.

## Assets

Approved originals remain in `assets/_incoming/`. The homepage requests only the selected derivatives in `assets/images/p03/`. Additional supplied originals and older baseline assets have not been deleted or substituted into the homepage.

Optional deterministic regeneration with the existing FFmpeg installation:

```sh
bash scripts/prepare-images.sh
```

Source dimensions, crops, hashes, and derivative sizes are documented in [docs/prototype-03-assets.md](docs/prototype-03-assets.md). This utility is not a production build dependency.

## Local verification

```sh
python3 scripts/qa-static.py
```

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

The QA utilities use Python's standard library and the existing browser. They intercept form popups for encoding/reset tests; they never send WhatsApp messages. Screenshots and machine-readable results are stored in the ignored `.qa/` directory. See [docs/prototype-03-execution-report.md](docs/prototype-03-execution-report.md) for results and outstanding human checks.

The current whole-site production audit, finding severities, and deployment prerequisites are recorded in [docs/prototype-03-release-readiness.md](docs/prototype-03-release-readiness.md). The strengthened static/browser gates also cover page metadata and semantics, ARIA/label references, external-link protection, authoritative contact details, mobile target sizes, skip links, and settled fragment-history behavior.

Run browser suites sequentially so each target can receive viewport-observer callbacks without background-tab throttling. The Chrome command declares fine-pointer desktop capabilities; M1 tests explicitly switch to touch emulation for mobile checks. M1 captures in `.qa/m1/` traverse the page before taking settled full-page screenshots and compare geometry against `4d8a330`. Targeted reruns are available with `--geometry`, `--interactions`, or `--accessibility` on `qa-m1.py`; `--port` selects a different local Chrome port. After the baseline snapshot has been created, `--cold-loads` and `--delayed-script` reproduce the load-time comparisons documented in the M1 report.

Hosting configuration, production-domain URL metadata, publishing, and Git commits remain outside this execution. Serve only the five HTML pages, `css/`, `js/`, and referenced production derivatives in `assets/images/p03/`; source photos, unreferenced legacy images, documentation, scripts, QA output, caches, and browser profiles are not required at runtime. Configure the selected static host to serve `404.html` for unknown routes.

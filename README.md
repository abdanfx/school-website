# SMP Tahfizh Quran Fantastis — Prototype 03

Framework-free production integration: HTML, one shared stylesheet, and deferred vanilla JavaScript. No package installation or build step is required.

Open `index.html` directly, or serve this directory with an existing static server. The homepage uses the frozen source in [docs/prototype-03-source-of-truth.md](docs/prototype-03-source-of-truth.md), subject to the original execution specification's locked H1 and mandatory desktop archive image.

The original About, Contact, Admissions, and 404 content is retained. Shared typography, navigation disclosure, focus treatment, and form accessibility are updated. The contact form opens the existing WhatsApp destination; it does not send a message itself. Without JavaScript, navigation remains visible and the contact page offers a direct WhatsApp link.

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
google-chrome --headless --no-sandbox --disable-gpu --disable-extensions --disable-background-networking --no-first-run --remote-debugging-port=9333 --remote-allow-origins=http://localhost:9333 --user-data-dir="$PWD/.qa/chrome-profile" --allow-file-access-from-files about:blank
```

Then run:

```sh
python3 scripts/qa.py --suite
python3 scripts/qa.py --audit
```

The QA utilities use Python's standard library and the existing browser. They intercept form popups for encoding/reset tests; they never send WhatsApp messages. Screenshots and machine-readable results are stored in the ignored `.qa/` directory. See [docs/prototype-03-execution-report.md](docs/prototype-03-execution-report.md) for results and outstanding human checks.

Hosting configuration, production-domain metadata, publishing, and Git commits remain outside this execution. Serve the site files and production image derivatives; source-photo, documentation, QA, and browser-profile directories are not required at runtime.

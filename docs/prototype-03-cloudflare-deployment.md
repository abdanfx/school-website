# Prototype 03 — Cloudflare Pages deployment preparation v0.1

Status: prepared locally; not deployed
Target: Cloudflare Pages with GitHub Git integration
Protected baseline: `830b5f8` / `p03-release-hardening-strong-pass`

## Deployment architecture

The repository remains the authoritative source. Cloudflare Pages must run the dependency-free production builder and publish only generated `dist/`; the repository root must never be selected as the build output directory.

```text
reviewed source HTML/CSS/JS + referenced p03 images + cloudflare/_headers
                                 │
                                 ▼
              python3 scripts/build-production.py
                                 │
                                 ▼
                 dist/ (public artifact only)
```

The builder parses all five production pages, discovers local `href`, `src`, and `srcset` dependencies, follows local CSS `url()` dependencies, rejects paths outside the reviewed runtime policy, fails on missing files, removes the old `dist/`, and copies only discovered runtime bytes. No package installation, network access, environment variable, or build-time content transformation is required.

Build and validate locally:

```sh
python3 scripts/build-production.py
python3 scripts/qa-dist.py
```

Current output: 37 files, 2,367,143 bytes (2.26 MiB).

## Artifact policy

Included:

- `index.html`, `about.html`, `contact.html`, `admissions.html`, and top-level `404.html`
- `css/style.css`
- `js/script.js`
- the 29 WebP files actually referenced beneath `assets/images/p03/`
- top-level `_headers`, copied from `cloudflare/_headers`

Excluded:

- `.git/`, `.qa/`, `docs/`, `scripts/`, caches, profiles, logs, and editor artifacts
- `assets/_incoming/` and every raw/source photograph
- the three unreferenced legacy images directly under `assets/images/`
- build sources under `cloudflare/`
- all files not reachable from the reviewed runtime pages

`dist/` is generated, ignored by Git, and cleaned on every build. It is not authoritative source.

## Intended Cloudflare Pages project settings

| Setting | Value |
| --- | --- |
| Git provider | GitHub |
| Repository | `abdanfx/school-website` (current `origin`) |
| Production branch | Human selection required; do not accept an accidental default |
| Framework preset | None |
| Build command | `python3 scripts/build-production.py` |
| Build output directory | `dist` |
| Root directory | Repository root / blank default |
| Environment variables | None required |
| Initial host | Cloudflare-assigned `*.pages.dev` URL |
| Custom domain | Deferred |

Branch recommendation: after review, merge the release preparation through the repository's normal approval process and use `main` as the long-lived production branch. The current `main` is an ancestor and is 13 commits behind the protected baseline, so it must not be selected until the approved release is integrated. A dedicated release branch is viable only if the maintainers want an explicit ongoing promotion workflow. Do not use this temporary phase branch as a permanent production branch.

Cloudflare Git integration can create branch/PR preview deployments. Use those for change review after the initial project is authorized. The first `*.pages.dev` deployment must remain a platform-verification target; do not attach a custom school domain until the checklist below passes.

## Headers and CSP

`cloudflare/_headers` produces one global rule:

```text
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  X-Frame-Options: DENY
```

These headers are conservative for the current static site: it does not use the disabled browser capabilities and is not intended to be embedded. No custom caching header is set; Cloudflare Pages' deployment-aware cache defaults should be evaluated in preview.

Content Security Policy is deliberately deferred. A future policy must account for local script/style/images, `https://fonts.googleapis.com`, and `https://fonts.gstatic.com`, and must be exercised against M1's runtime style updates, the lightbox, the contact flow, and reduced motion through the real Pages response path. No `unsafe-inline` or `unsafe-eval` exception has been introduced.

## Routing and 404 behavior

No `_redirects` file is created. There is no SPA rewrite or catch-all redirect.

Cloudflare Pages should use the artifact's top-level `404.html` for unmatched routes. Preview verification must confirm a real 404 status and the approved recovery page.

Cloudflare Pages currently redirects matching `.html` routes to extensionless public paths, such as `/contact.html` → `/contact`. Source links remain unchanged in this preparation because they are valid static references and no deployed failure has been demonstrated. Preview must verify `.html`, extensionless, fragment, reload, and back/forward behavior before any URL policy change.

## Domain-dependent work deferred

Do not add until an authoritative hostname and approved social-preview asset exist:

- canonical links
- `og:url`
- absolute `og:image` or `twitter:image`
- production sitemap URLs
- hostname-specific robots policy or redirects
- structured-data entity URLs
- apex/`www` or `pages.dev` redirect policy

Current hostname-independent title, description, Open Graph, Twitter, language, and 404 metadata remain unchanged.

## Preview verification checklist

After a separately authorized Git integration deployment, verify on the temporary Pages URL:

- build log runs the documented command and uploads only `dist/`
- all five pages and genuine 404 response behavior
- `.html` redirects and extensionless routes, fragments, reloads, and history
- desktop/mobile navigation, skip link, keyboard focus, disclosure, and reduced motion
- responsive images, MIME types, dimensions, loading priority, and lightbox behavior
- Contact validation, popup-block recovery, WhatsApp destination, and Maps destination without sending a test message unintentionally
- Google Fonts success and blocked-font fallback
- the four `_headers` values on HTML and static assets
- Cloudflare cache behavior without custom cache rules
- absence of `/docs/`, `/scripts/`, `/.qa/`, `/assets/_incoming/`, legacy images, raw photos, and repository internals
- no runtime exceptions, failed local resources, unexpected redirects, or content changes

Only after this passes should maintainers consider a custom domain, domain-dependent SEO metadata, and a tested CSP.

## Rollback principle

Keep the last verified production deployment available. If a later production deployment fails verification, use the Cloudflare Pages production rollback control to restore the last successful production deployment, then correct the source through normal Git review. Preview deployments are verification artifacts, not production rollback targets. Never repair production by editing generated `dist/` manually.

## Known limitations

- No deployment, response-header fetch, Cloudflare MIME/cache observation, or extensionless-route network test is possible before project creation is authorized.
- The existing Google Fonts request remains the sole page-load third-party dependency.
- CSP and hostname-dependent SEO remain intentionally unresolved.
- Existing release-readiness manual checks—physical browsers/devices, screen reader, live external-app handoff, and photography authorization—still apply.

References: [Cloudflare build configuration](https://developers.cloudflare.com/pages/configuration/build-configuration/), [build image](https://developers.cloudflare.com/pages/configuration/build-image/), [serving pages](https://developers.cloudflare.com/pages/configuration/serving-pages/), [headers](https://developers.cloudflare.com/pages/configuration/headers/), [Git integration](https://developers.cloudflare.com/pages/get-started/git-integration/), and [rollbacks](https://developers.cloudflare.com/pages/configuration/rollbacks/).

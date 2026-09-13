# Prototype 03 — production asset traceability

All ten approved originals remain untouched in `assets/_incoming/`. The other 39 supplied assets are retained and are not used on the homepage. Derivatives were produced with the existing FFmpeg `libwebp` encoder, quality 82, compression level 6, Lanczos scaling, and metadata removal. Crops are recorded in original pixels. No derivative exceeds its crop's useful resolution. No AI imagery was generated.

| Source | Original dimensions | Original bytes | Production crop |
|---|---|---:|---|
| `1000534854.jpg` | 1536 × 864 | 415544 | 1080 × 864, x=228 y=0; 5:4 Hero |
| `1000512148.jpg` | 1536 × 864 | 575216 | 1152 × 864, x=180 y=0; 4:3 Profile |
| `1000160830.jpg` | 1536 × 1152 | 405652 | 1536 × 1152, x=0 y=0; full 4:3 source |
| `1000520096.jpg` | 1536 × 864 | 191889 | 1152 × 864, x=0 y=0; presenters/whiteboard, right laptop excluded |
| `1000163805.jpg` | 1536 × 1152 | 436894 | 1536 × 1152, x=0 y=0; full 4:3 source |
| `1000344565.jpg` | 1536 × 864 | 221671 | 1536 × 864, x=0 y=0; full 16:9 source |
| `1000512176.jpg` | 1536 × 864 | 499725 | 1536 × 864, x=0 y=0; full group, 16:9 |
| `1000512147.jpg` | 1536 × 864 | 520245 | 864 × 864, x=600 y=0; square, foreground student line |
| `1000213703.jpg` | 1536 × 864 | 346004 | 1152 × 864, x=80 y=0; 4:3 learning scene |
| `IMG-20221202-WA0016.jpg` | 1080 × 607 | 85034 | 900 × 600, x=90 y=0; 3:2 archive |

The Hero has 480, 768, 800, and 1080px widths. The 800px variant avoids selecting 1080px for a fresh 390px viewport at 2× density. The square and archive photos have 480/768px variants; all other photographs have 480/768/1080px variants. The 2022 archive is shown on desktop and hidden at widths of 600px and below, leaving the three approved current photographs.

| Derivative | Bytes |
|---|---:|
| `1000534854-1080.webp` | 166990 |
| `1000534854-480.webp` | 34560 |
| `1000534854-768.webp` | 82750 |
| `1000534854-800.webp` | 88102 |
| `1000512148-1080.webp` | 251694 |
| `1000512148-480.webp` | 52670 |
| `1000512148-768.webp` | 129608 |
| `1000160830-1080.webp` | 109676 |
| `1000160830-480.webp` | 34656 |
| `1000160830-768.webp` | 69460 |
| `1000520096-1080.webp` | 47376 |
| `1000520096-480.webp` | 15880 |
| `1000520096-768.webp` | 30630 |
| `1000163805-1080.webp` | 117374 |
| `1000163805-480.webp` | 36406 |
| `1000163805-768.webp` | 73356 |
| `1000344565-1080.webp` | 52552 |
| `1000344565-480.webp` | 16448 |
| `1000344565-768.webp` | 32582 |
| `1000512176-1080.webp` | 157716 |
| `1000512176-480.webp` | 39416 |
| `1000512176-768.webp` | 88398 |
| `1000512147-480.webp` | 54244 |
| `1000512147-768.webp` | 135572 |
| `1000213703-1080.webp` | 112088 |
| `1000213703-480.webp` | 35626 |
| `1000213703-768.webp` | 70106 |
| `IMG-20221202-WA0016-480.webp` | 41696 |
| `IMG-20221202-WA0016-768.webp` | 85514 |

Source checksums (SHA-256), for subsequent integrity checks:

```text
d3c847d7bcd54793b37531755f2c5af8cdf75ef52f262eacfcffb05761eafc63  assets/_incoming/1000534854.jpg
857987fc16c17d1454f86289447242277c6adbc60ebce75587d4d9267064c107  assets/_incoming/1000512148.jpg
bf2ef5a8d30be7792df65d06430358c056c3562487d11ea15104d9598b5203d1  assets/_incoming/1000160830.jpg
0f125ffc31b768e1b6e981dee2d647e0382d791bdda563d9ed0af30b198665ce  assets/_incoming/1000520096.jpg
90972a37c3dba7d23ac73b3666c94b69a5d255d54edf5f24e901b7bb307d2064  assets/_incoming/1000163805.jpg
a67b664a5bbb14dc71396e5d6a4539cf144f38e5e83c5614907dc4368c1c8ba1  assets/_incoming/1000344565.jpg
46cbc56d063e2a16bccf69a4da95f4c1b500955dd35eec91e7d9ea3a61f80028  assets/_incoming/1000512176.jpg
1c0300c0270f355c43109a08c4849569ff7de1a30c005377940b6027aad63e63  assets/_incoming/1000512147.jpg
7fdbbd5cd973f721489057358d13efb42dbafedbd0a4de331b705cbdcabbd9fb  assets/_incoming/1000213703.jpg
6965d47056a273be23081460cb141ef3ab58c007cee46413ec0aa8fe26bd5750  assets/_incoming/IMG-20221202-WA0016.jpg
```

Regenerate only production derivatives with `bash scripts/prepare-images.sh`. This leaves the source photographs intact. Re-run `python3 scripts/qa-static.py` to refresh `.qa/asset-manifest.json` and verify references. The content document is preserved as supplied; the original execution specification overrides its alternate Hero H1 and optional archive wording.

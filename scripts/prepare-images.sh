#!/usr/bin/env bash
# Optional asset preparation using the existing FFmpeg installation; no build step.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p assets/images/p03

prepare() {
  local source="$1" crop="$2" max_width="$3" input="${4:-$1.jpg}"
  local width output
  for width in 480 768 800 1080; do
    if (( width == 800 )) && [[ "$source" != 1000534854 ]]; then continue; fi
    if (( width > max_width )); then continue; fi
    output="assets/images/p03/${source}-${width}.webp"
    ffmpeg -hide_banner -loglevel error -nostdin -y \
      -i "assets/_incoming/${input}" \
      -vf "${crop},scale=${width}:-1:flags=lanczos" \
      -frames:v 1 -c:v libwebp -quality 82 -compression_level 6 \
      -map_metadata -1 "$output"
  done
}

# Crops are in original-source pixels. Originals remain untouched.
prepare 1000534854 'crop=1080:864:228:0' 1080
prepare 1000512148 'crop=1152:864:180:0' 1080
prepare 1000160830 'crop=1536:1152:0:0' 1080
# Preserve the presenters and whiteboard; exclude the right-hand laptop.
prepare 1000520097 'crop=1152:864:0:0' 1080 '1000520097(1).jpg'
prepare 1000163805 'crop=1536:1152:0:0' 1080
prepare 1000344565 'crop=1536:864:0:0' 1080
prepare 1000512176 'crop=1536:864:0:0' 1080
prepare 1000512147 'crop=864:864:600:0' 864
prepare 1000213703 'crop=1152:864:80:0' 1080
prepare IMG-20221202-WA0016 'crop=900:600:90:0' 900

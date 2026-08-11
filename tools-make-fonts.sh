#!/bin/bash
# OTF -> subsetted WOFF2 for the web.
# Subset to the Latin range the page actually uses; keeps each face tiny
# enough to inline as a data URI in the artifact build.
set -eu

SRC=/private/tmp/claude-501/-Users-austinw/cddb8bcd-079b-433f-873e-36afb837eca3/scratchpad/fonts_in/pangram-fonts
OUT=/private/tmp/claude-501/-Users-austinw/cddb8bcd-079b-433f-873e-36afb837eca3/scratchpad/saveourcats/fonts
PY=/private/tmp/claude-501/-Users-austinw/cddb8bcd-079b-433f-873e-36afb837eca3/scratchpad/.fontvenv/bin/pyftsubset

mkdir -p "$OUT"

# basic latin + latin-1 (Malay needs none beyond ASCII, but keep it safe)
# + curly quotes, dashes, ellipsis, arrow, bullet, middot, non-breaking space
UNI="U+0020-007E,U+00A0-00FF,U+2010-2015,U+2018,U+2019,U+201C,U+201D,U+2022,U+2026,U+2192,U+00B7,U+2013,U+2014"

conv () {
  local in="$1" out="$2"
  "$PY" "$in" \
    --output-file="$OUT/$out" \
    --flavor=woff2 \
    --unicodes="$UNI" \
    --layout-features='kern,liga,clig,calt,onum,tnum,frac' \
    --no-hinting \
    --desubroutinize \
    --drop-tables+=DSIG
  printf '  %-34s %s KB\n' "$out" "$(( $(stat -f%z "$OUT/$out") / 1024 ))"
}

E="$SRC/PP_Editorial_Old-Free_For_Personal_Use/PP Editorial Old - Free For Personal Use v1.0/otf"
M="$SRC/PP_Neue_Montreal-Free_For_Personal_Use/PP Neue Montreal - Free for Personal Use v3.0/otf"

echo "  ── PP Editorial Old ──"
conv "$E/PPEditorialOld-Regular.otf"        editorial-regular.woff2
conv "$E/PPEditorialOld-Italic.otf"         editorial-italic.woff2
conv "$E/PPEditorialOld-Ultrabold.otf"      editorial-ultrabold.woff2

echo "  ── PP Neue Montreal ──"
conv "$M/PPNeueMontreal-Regular.otf"        montreal-regular.woff2
conv "$M/PPNeueMontreal-Semibold.otf"       montreal-semibold.woff2

echo
echo "  total: $(du -sh "$OUT" | awk '{print $1}')"

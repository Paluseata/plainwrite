#!/bin/sh
# Builds both editions of Plainwrite-K into out/dist.
#   PW:  a Plainwrite Multilingual release folder (index.html, pixel-gothic.ttf and the other fonts)
#   PJ:  a Plainwrite-J folder (its pixel-gothic.ttf, Pixel Gothic J, supplies the Hanja glyphs)
#   fonts-in/: Galmuri11.ttf and neodgm.ttf (without them a Noto stand-in is used)
set -e
cd "$(dirname "$0")"
PW=${PW:-../src/ml}; PJ=${PJ:-../src/j}
B=out/build; rm -rf "$B"; mkdir -p "$B"
[ -f build/lo_hanja.json ] || python3 tools/dump_lo_hanja.py build/lo_hanja.json
python3 tools/make_dict.py build/lo_hanja.json "$PJ/pixel-gothic.ttf" "$B/dict-ko.txt"
python3 tools/make_fonts.py screen "$PW" "$PJ" fonts-in "$B/dict-ko.txt" "$B"
python3 tools/make_icon.py unification "$B"
python3 tools/build.py "$PW/index.html" "$B"
python3 tools/make_fonts.py ui "$B/ko/index.html" "$B/en-ko/index.html" --out "$B"
python3 tools/assemble.py "$PW" "$B" out/dist

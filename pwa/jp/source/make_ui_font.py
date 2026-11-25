#!/usr/bin/env python3
"""Cuts M PLUS 1p (SIL OFL 1.1, M+ FONTS PROJECT) down to the letters the device's own labels and the Help
sheet use: ASCII, Latin-1, kana, Japanese punctuation, full-width forms and every kanji in Plainwrite-J's
Japanese text. Usage: make_ui_font.py MPLUS1p-folder outdir textfile..."""
import sys, os, subprocess
src, out, texts = sys.argv[1], sys.argv[2], sys.argv[3:]
chars = set()
for t in texts: chars |= set(open(t, encoding='utf-8').read())
ranges = [(0x20, 0x7e), (0xa0, 0xff), (0x2010, 0x2027), (0x2190, 0x2199), (0x25a0, 0x25ff), (0x3000, 0x30ff), (0xff01, 0xff9f)]
for a, b in ranges: chars |= {chr(c) for c in range(a, b + 1)}
chars = {c for c in chars if c >= ' '}
text = ''.join(sorted(chars))
os.makedirs(out, exist_ok=True)
for w, name in [('Regular', 'ui-ja-400'), ('Medium', 'ui-ja-500'), ('Bold', 'ui-ja-700')]:
    subprocess.run(['pyftsubset', os.path.join(src, f'MPLUS1p-{w}.ttf'), '--text=' + text, '--flavor=woff',
                    '--layout-features=*', '--output-file=' + os.path.join(out, name + '.woff')], check=True)
print(len(chars), 'characters')

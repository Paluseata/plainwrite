"""Builds dict-ko.txt, the Hangul -> Hanja table for Plainwrite-K.

Source: LibreOffice's Korean character conversion table (i18npool hhc_char, MPL 2.0), which lists the
Hanja for each Hangul syllable in order of how often they are used. dump_lo_hanja.py reads it out of
libtextconv_dict.so. Every KS X 1001 Hanja is kept; others only when Pixel Gothic J (DotGothic16) can
draw them, so rare and Extension B characters that no bundled font has are left out.

Output: one line per syllable, "가<TAB>可家加歌…" (each character after the tab is one choice).
"""
import json, sys
from fontTools.ttLib import TTFont

lo = json.load(open(sys.argv[1], encoding='utf-8'))
pgj = TTFont(sys.argv[2]).getBestCmap()
out = sys.argv[3]

ks = set()
for a in range(0xCA, 0xFE):
    for b in range(0xA1, 0xFF):
        try: ks.add(bytes([a, b]).decode('euc_kr'))
        except UnicodeDecodeError: pass

keep = lambda c: len(c) == 1 and ord(c) < 0x10000 and (c in ks or ord(c) in pgj)
# LibreOffice files 不 under no syllable at all; it reads 불 (and 부 before ㄷ and ㅈ)
lo['불'] = '不' + lo.get('불', '').replace('不', '')
b = lo.get('부', '').replace('不', ''); lo['부'] = b[:3] + '不' + b[3:]
lines, total, seen = [], 0, set()
for syl in sorted(lo):
    cands = []
    for c in lo[syl]:
        if keep(c) and c not in cands: cands.append(c)
    if cands:
        lines.append(syl + '\t' + ''.join(cands)); total += len(cands); seen.update(cands)
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(f'{len(lines)} readings, {total} choices, {len(seen)} Hanja; KS X 1001 covered: {len(ks & seen)}/{len(ks)}')
missing = sorted(ks - seen)
print('KS Hanja with no reading in the table:', ''.join(missing[:60]), len(missing))

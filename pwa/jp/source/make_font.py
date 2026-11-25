#!/usr/bin/env python3
"""Builds pixel-gothic.ttf: DotGothic16 with half-width Cyrillic redrawn on its own pixel grid.

DotGothic16 takes its Cyrillic from the Japanese JIS X 0208 set: 66 Russian letters drawn full width
(as wide as a kanji), with no Ukrainian, Belarusian, Serbian, Macedonian, Kazakh, Kyrgyz or Mongolian
letters. This replaces them with half-width letters that match the Latin ones and adds the missing ones.
Usage: make_font.py DotGothic16-Regular.ttf out.ttf
"""
import sys, copy
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from cyr_glyphs import GLYPHS, MARKS, ACCENTED

src, out = sys.argv[1], sys.argv[2]
font = TTFont(src)
PIL = ImageFont.truetype(src, 16)
cmap = font.getBestCmap()
glyf, hmtx, vmtx = font['glyf'], font['hmtx'], font['vmtx']
X0, CW = 28, (472 - 28) / 7          # pixel columns, from the Latin letters
Y0, RH = -28, (787 + 28) / 13        # pixel rows: y18 (baseline row) starts at -28
ADV = 500

def raster(ch):
    """bitmap rows y0..y21 of a character as the font draws it at 16 px"""
    im = Image.new('1', (16, 24), 0); d = ImageDraw.Draw(im); d.fontmode = '1'; d.text((0, 0), ch, font=PIL, fill=1)
    return {y: ''.join('#' if im.getpixel((x, y)) else '.' for x in range(8)) for y in range(24)}

def bitmap(ch):
    """{y: row} for a Cyrillic letter"""
    spec = GLYPHS.get(ch)
    if ch in ACCENTED:
        base, mark = ACCENTED[ch]
        bm = dict(bitmap(base))
        if base == 'І' and mark == 'uml':
            rows = ['..#.#...', '..#.#...']
        else:
            rows = MARKS[mark]
        top = 3 if base.isupper() else 7
        for i, r in enumerate(rows): bm[top + i] = r
        return bm
    if isinstance(spec, str) and spec.startswith('copy:'):
        return {y: r for y, r in raster(spec[5:]).items() if '#' in r}
    if isinstance(spec, tuple) and isinstance(spec[0], str) and spec[0].startswith('copy+desc:'):
        b = spec[0][10:]
        bm = bitmap(b) if b in GLYPHS else {y: r for y, r in raster(b).items() if '#' in r}
        bm = dict(bm); col = spec[1]
        for y in (19, 20): bm[y] = '.' * col + '#' + '.' * (7 - col)
        return bm
    top, rows = spec
    return {top + i: r for i, r in enumerate(rows)}

def draw(bm):
    pen = TTGlyphPen(None)
    # merge equal runs on consecutive rows into one rectangle
    runs = {}
    for y in sorted(bm):
        r = bm[y]; c = 0
        while c < 8:
            if r[c] == '#':
                e = c
                while e + 1 < 8 and r[e + 1] == '#': e += 1
                runs.setdefault(y, []).append((c, e)); c = e + 1
            else: c += 1
    rects = []; open_ = {}
    for y in sorted(runs):
        nxt = {}
        for run in runs[y]:
            if run in open_ and open_[run][1] == y - 1: nxt[run] = (open_[run][0], y)
            else: nxt[run] = (y, y)
        for run, span in open_.items():
            if run not in nxt or nxt[run][0] != span[0]: rects.append((run, span))
        open_ = nxt
    rects += list(open_.items())
    for (c0, c1), (ya, yb) in rects:
        # DotGothic16's dots are about 74 units, a little more than the 63-unit grid: grow each run to match its stroke weight
        x0, x1 = max(X0, round(X0 + (c0 - 1) * CW) - 5), min(X0 + 7 * CW, round(X0 + c1 * CW) + 6)
        yb0, yt = round(Y0 + (18 - yb) * RH) - (5 if yb != 18 else 0), round(Y0 + (19 - ya) * RH) + (6 if ya != 6 else 0)
        pen.moveTo((x0, yb0)); pen.lineTo((x0, yt)); pen.lineTo((x1, yt)); pen.lineTo((x1, yb0)); pen.closePath()
    return pen.glyph()

order = font.getGlyphOrder()
vref = vmtx[cmap[ord('A')]]
added = 0
for ch in list(GLYPHS) + list(ACCENTED):
    o = ord(ch)
    name = cmap.get(o)
    spec = GLYPHS.get(ch)
    if isinstance(spec, str) and spec.startswith('copy:') and spec[5:] not in ('ë', 'ï'):
        g = copy.deepcopy(glyf[cmap[ord(spec[5:])]])
    else:
        g = draw(bitmap(ch))
    if name is None:
        name = 'uni%04X' % o
        order.append(name); added += 1
        for t in font['cmap'].tables:
            if t.isUnicode(): t.cmap[o] = name
        vmtx[name] = vref
    glyf[name] = g
    g.recalcBounds(glyf)
    hmtx[name] = (ADV, getattr(g, 'xMin', 0) or 0)
font.setGlyphOrder(order)
font['maxp'].numGlyphs = len(order)
# new family name, so it never clashes with the Google-hosted DotGothic16
for rec in font['name'].names:
    if rec.nameID in (1, 3, 4, 16):
        s = rec.toUnicode().replace('DotGothic16', 'Pixel Gothic J')
        rec.string = s
    if rec.nameID == 6:
        rec.string = 'PixelGothicJ-Regular'
if 'DSIG' in font: del font['DSIG']
font.save(out)
print('glyphs:', len(GLYPHS) + len(ACCENTED), 'new:', added)

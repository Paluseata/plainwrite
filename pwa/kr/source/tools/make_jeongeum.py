#!/usr/bin/env python3
"""Plain Jeongeum (플레인 정음): a geometric Hangul font after the letters printed in the Hunminjeongeum
Haerye (훈민정음 해례본, 1446).

    python3 make_jeongeum.py <out.woff>

The Haerye draws Hangul from a few shapes: straight strokes of one weight, a true circle for ㅇ, and
round dots for the short strokes of the vowels (ㅏ is a line and a dot: heaven ·, earth ㅡ, person ㅣ).
This script draws each jamo that way, once for every place it can take in a syllable, and builds all
11,172 modern syllables as composites of those parts, so the file stays small. It also has the
compatibility jamo (ㄱ…ㅣ) and the four letters modern Korean dropped: ㆍ ㅿ ㆁ ㆆ.

Latin letters are not drawn: Plainwrite-K pairs it with Jost, which is geometric too.
"""
import math, sys
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent

W = 76          # stroke weight, the same in every box
R = 64          # dot radius
UPM = 1000
CHO = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
JUNG = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
JONG = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
DOUBLE = {'ㄲ': 'ㄱㄱ', 'ㄸ': 'ㄷㄷ', 'ㅃ': 'ㅂㅂ', 'ㅆ': 'ㅅㅅ', 'ㅉ': 'ㅈㅈ', 'ㄳ': 'ㄱㅅ', 'ㄵ': 'ㄴㅈ', 'ㄶ': 'ㄴㅎ', 'ㄺ': 'ㄹㄱ',
          'ㄻ': 'ㄹㅁ', 'ㄼ': 'ㄹㅂ', 'ㄽ': 'ㄹㅅ', 'ㄾ': 'ㄹㅌ', 'ㄿ': 'ㄹㅍ', 'ㅀ': 'ㄹㅎ', 'ㅄ': 'ㅂㅅ'}
VCOMP = {'ㅘ': 'ㅗㅏ', 'ㅙ': 'ㅗㅐ', 'ㅚ': 'ㅗㅣ', 'ㅝ': 'ㅜㅓ', 'ㅞ': 'ㅜㅔ', 'ㅟ': 'ㅜㅣ', 'ㅢ': 'ㅡㅣ'}
VERT = set('ㅏㅐㅑㅒㅓㅔㅕㅖㅣ')
HORI = set('ㅗㅛㅜㅠㅡ')


# ---------- drawing ----------
class Shape:
    def __init__(self):
        self.contours = []      # each a list of (x, y), or ('circle', cx, cy, r, clockwise)

    def poly(self, pts):
        a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
        if a > 0:               # TrueType fills clockwise contours
            pts = pts[::-1]
        self.contours.append([(round(x), round(y)) for x, y in pts])

    def line(self, x1, y1, x2, y2, cap=True):
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        nx, ny = -uy * W / 2, ux * W / 2
        e = W / 2 if cap else 0
        ax, ay, bx, by = x1 - ux * e, y1 - uy * e, x2 + ux * e, y2 + uy * e
        self.poly([(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)])

    def circle(self, cx, cy, r, cw=True):
        self.contours.append(('circle', cx, cy, r, cw))

    def ring(self, cx, cy, r):
        self.circle(cx, cy, r + W / 2, True)
        self.circle(cx, cy, r - W / 2, False)

    def dot(self, cx, cy, r=R):
        self.circle(cx, cy, r, True)

    def draw(self, pen):
        for c in self.contours:
            if c[0] == 'circle':
                # an all-off-curve quadratic contour: the implied points between them lie on the circle
                _, cx, cy, r, cw = c
                n = 12
                k = r / math.cos(math.pi / n)
                ang = [2 * math.pi * i / n for i in range(n)]
                if cw:
                    ang = ang[::-1]
                pen.qCurveTo(*[(round(cx + k * math.cos(t)), round(cy + k * math.sin(t))) for t in ang], None)
                pen.closePath()
            else:
                pen.moveTo(c[0])
                for p in c[1:]:
                    pen.lineTo(p)
                pen.closePath()


def fit(box, lo=0.72, hi=1.18):
    """A consonant keeps a sensible shape: the box is narrowed or shortened to an aspect between lo and hi."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if h / w > hi:
        nh = w * hi; y0 += (h - nh) / 2; y1 = y0 + nh
    elif h / w < lo:
        nw = h / lo; x0 += (w - nw) / 2; x1 = x0 + nw
    return x0, y0, x1, y1


def consonant_raw(s, ch, box):
    if ch in DOUBLE:
        a, b = DOUBLE[ch]
        x0, y0, x1, y1 = box
        gap = W * 1.1
        m = (x0 + x1) / 2
        consonant_raw(s, a, (x0, y0, m - gap / 2, y1))
        consonant_raw(s, b, (m + gap / 2, y0, x1, y1))
        return
    x0, y0, x1, y1 = fit(box, .5, 1.7)
    # centrelines sit half a stroke inside the box, so the ink fills it exactly
    x0 += W / 2; y0 += W / 2; x1 -= W / 2; y1 -= W / 2
    X = lambda u: x0 + (x1 - x0) * u
    Y = lambda v: y0 + (y1 - y0) * v
    L = lambda u1, v1, u2, v2, cap=True: s.line(X(u1), Y(v1), X(u2), Y(v2), cap)
    if ch == 'ㄱ':
        L(0, 1, 1, 1); L(1, 1, 1, 0)
    elif ch == 'ㄴ':
        L(0, 1, 0, 0); L(0, 0, 1, 0)
    elif ch == 'ㄷ':
        L(0, 1, 1, 1); L(0, 1, 0, 0); L(0, 0, 1, 0)
    elif ch == 'ㄹ':
        L(0, 1, 1, 1); L(1, 1, 1, .5); L(1, .5, 0, .5); L(0, .5, 0, 0); L(0, 0, 1, 0)
    elif ch == 'ㅁ':
        L(0, 1, 1, 1); L(1, 1, 1, 0); L(1, 0, 0, 0); L(0, 0, 0, 1)
    elif ch == 'ㅂ':
        L(0, 1, 0, 0); L(1, 1, 1, 0); L(0, .5, 1, .5); L(0, 0, 1, 0)
    elif ch == 'ㅅ':
        L(0, 0, .5, 1, False); L(.5, 1, 1, 0, False); s.dot(X(.5), Y(1) - W * .18, W * .5)
    elif ch == 'ㅇ':
        r = min(x1 - x0, y1 - y0) / 2
        s.ring((x0 + x1) / 2, (y0 + y1) / 2, r)
    elif ch == 'ㅈ':
        L(0, 1, 1, 1); L(.5, 1, 0, 0, False); L(.5, 1, 1, 0, False)
    elif ch == 'ㅊ':
        L(.5, 1, .5, .8); L(0, .8, 1, .8); L(.5, .8, 0, 0, False); L(.5, .8, 1, 0, False)
    elif ch == 'ㅋ':
        L(0, 1, 1, 1); L(1, 1, 1, 0); L(0, .5, 1, .5)
    elif ch == 'ㅌ':
        L(0, 1, 1, 1); L(0, .5, 1, .5); L(0, 1, 0, 0); L(0, 0, 1, 0)
    elif ch == 'ㅍ':
        L(0, 1, 1, 1); L(0, 0, 1, 0); L(.27, 1, .27, 0); L(.73, 1, .73, 0)
    elif ch == 'ㅎ':
        L(.5, 1, .5, .8); L(0, .8, 1, .8)
        r = min((x1 - x0) / 2, (Y(.8) - y0 - W * 1.3) / 2)
        s.ring((x0 + x1) / 2, y0 + r, r)
    elif ch == 'ㆆ':      # yeorinhieut: ㅎ without its top stroke
        L(0, .8, 1, .8)
        r = min((x1 - x0) / 2, (Y(.8) - y0 - W * 1.3) / 2)
        s.ring((x0 + x1) / 2, y0 + r, r)
    elif ch == 'ㅿ':      # bansiot: a triangle
        L(0, 0, .5, 1, False); L(.5, 1, 1, 0, False); L(0, 0, 1, 0); s.dot(X(.5), Y(1) - W * .18, W * .5)
    elif ch == 'ㆁ':      # yesieung: ㅇ with a stroke on top
        L(.5, 1, .5, .78)
        r = min((x1 - x0) / 2, (Y(.78) - y0 - W * .5) / 2)
        s.ring((x0 + x1) / 2, y0 + r, r)
    else:
        raise ValueError(ch)


def vowel(s, ch, box, r=R):
    x0, y0, x1, y1 = box
    X = lambda u: x0 + (x1 - x0) * u
    Y = lambda v: y0 + (y1 - y0) * v
    if ch in VERT:
        spec = {'ㅣ': ([.5], []), 'ㅏ': ([.32], [(.8, .5)]), 'ㅑ': ([.32], [(.8, .63), (.8, .37)]),
                'ㅓ': ([.68], [(.2, .5)]), 'ㅕ': ([.68], [(.2, .63), (.2, .37)]),
                'ㅐ': ([.18, .86], [(.52, .5)]), 'ㅒ': ([.18, .86], [(.52, .63), (.52, .37)]),
                'ㅔ': ([.5, .86], [(.14, .5)]), 'ㅖ': ([.5, .86], [(.14, .63), (.14, .37)])}[ch]
        for u in spec[0]:
            s.line(X(u), y0 + W / 2, X(u), y1 - W / 2)
        for u, v in spec[1]:
            s.dot(X(u), Y(v), r)
    elif ch in HORI:
        spec = {'ㅡ': ([.5], []), 'ㅗ': ([.3], [(.5, .78)]), 'ㅛ': ([.3], [(.34, .78), (.66, .78)]),
                'ㅜ': ([.7], [(.5, .22)]), 'ㅠ': ([.7], [(.34, .22), (.66, .22)]), 'ㆍ': ([], [(.5, .5)])}[ch]
        for v in spec[0]:
            s.line(x0 + W / 2, Y(v), x1 - W / 2, Y(v))
        for u, v in spec[1]:
            s.dot(X(u), Y(v), r)
    elif ch == 'ㆍ':
        s.dot((x0 + x1) / 2, (y0 + y1) / 2, r * 1.15)
    else:
        raise ValueError(ch)


# ---------- uniform jamo ----------
# Every jamo is drawn once, at one size, and syllables place those same shapes without scaling them,
# the way the Haerye's letters keep their size whether they start or end a syllable. A syllable with a
# last consonant is taller than one without, and a double consonant is twice as wide as a single one.
C = 340           # a consonant is a C × C square
HV = 600          # length of a vowel's long vertical stroke
WH = 560          # length of a vowel's long horizontal stroke
D = 124           # from a stroke to its dot
G = 56            # gap between jamo
MID = 380         # vertical middle of the em (ascent 880, descent 120)


def cons_shape(s, ch):
    # a double (ㄲ) or a cluster (ㄺ) keeps the full height; its two letters are narrower, as in the Haerye
    w = int(2 * C * .62 + W * 1.1) if ch in DOUBLE else C
    consonant_raw(s, ch, (0, 0, w, C))


def vert_shape(s, ch, r=R):
    lines, dots = {'ㅣ': ([0], []), 'ㅏ': ([0], [(D, .5)]), 'ㅑ': ([0], [(D, .63), (D, .37)]),
                   'ㅓ': ([D], [(0, .5)]), 'ㅕ': ([D], [(0, .63), (0, .37)]),
                   'ㅐ': ([0, 2 * D], [(D, .5)]), 'ㅒ': ([0, 2 * D], [(D, .63), (D, .37)]),
                   'ㅔ': ([D, 2 * D], [(0, .5)]), 'ㅖ': ([D, 2 * D], [(0, .63), (0, .37)])}[ch]
    for x in lines:
        s.line(x, W / 2, x, HV - W / 2)
    for x, v in dots:
        s.dot(x, HV * v, r)


def hori_shape(s, ch, width=WH, r=R):
    lines, dots = {'ㅡ': ([0], []), 'ㅗ': ([0], [(.5, D)]), 'ㅛ': ([0], [(.33, D), (.67, D)]),
                   'ㅜ': ([0], [(.5, -D)]), 'ㅠ': ([0], [(.33, -D), (.67, -D)]), 'ㆍ': ([], [(.5, 0)])}[ch]
    for y in lines:
        s.line(W / 2, y, width - W / 2, y)
    for u, y in dots:
        s.dot(width * u, y, r)


def build(out):
    glyphs, order, cmap = {}, ['.notdef', 'space'], {0x20: 'space'}
    empty = TTGlyphPen(None).glyph()
    glyphs['.notdef'] = empty
    glyphs['space'] = empty
    bounds = {}

    def make(name, fn):
        s = Shape(); fn(s)
        pen = TTGlyphPen(None); s.draw(pen)
        g = pen.glyph(); glyphs[name] = g; order.append(name)
        xs = [p[0] for c in s.contours for p in ([c] if False else [])]
        return g

    parts = {}

    def part(kind, ch):
        key = (kind, ch)
        if key not in parts:
            name = f'{kind}_{ord(ch):04X}'
            make(name, {'C': lambda s: cons_shape(s, ch), 'V': lambda s: vert_shape(s, ch),
                        'H': lambda s: hori_shape(s, ch), 'h': lambda s: hori_shape(s, ch, WH * .78, R * .92)}[kind])
            parts[key] = name
        return parts[key]

    def box(name):
        if name not in bounds:
            g = glyphs[name]
            from fontTools.ttLib import newTable
            g.recalcBounds(None) if not g.isComposite() else None
            bounds[name] = (g.xMin, g.yMin, g.xMax, g.yMax)
        return bounds[name]

    def place(items):
        """items: (glyph name, x, y) with x, y the offset for the part's own origin; returns components centred in the em"""
        bs = [(n, x + box(n)[0], y + box(n)[1], x + box(n)[2], y + box(n)[3], x, y) for n, x, y in items]
        x0 = min(b[1] for b in bs); x1 = max(b[3] for b in bs); y0 = min(b[2] for b in bs); y1 = max(b[4] for b in bs)
        dx = round(500 - (x0 + x1) / 2); dy = round(MID - (y0 + y1) / 2)
        g = Glyph(); g.numberOfContours = -1; g.components = []
        for n, *_, x, y in bs:
            gc = GlyphComponent(); gc.glyphName = n; gc.x = x + dx; gc.y = y + dy; gc.flags = 0x4
            g.components.append(gc)
        return g

    def width(n):
        b = box(n); return b[2] - b[0]

    def height(n):
        b = box(n); return b[3] - b[1]

    for i in range(11172):
        L, V, T = CHO[i // 588], JUNG[i // 28 % 21], JONG[i % 28]
        cl = part('C', L)
        items = []
        if V in VERT:
            v = part('V', V)
            # consonant to the left, its middle level with the middle of the vowel's stroke
            items.append((v, 0, 0))
            items.append((cl, box(v)[0] - G - box(cl)[2], (HV - C) // 2))
            bottom = 0
        elif V in HORI:
            v = part('H', V)
            items.append((v, 0, 0))
            items.append((cl, WH // 2 - (box(cl)[0] + box(cl)[2]) // 2, box(v)[3] + G))
            bottom = box(v)[1]
        else:
            h, vv = VCOMP[V]
            hp, vp = part('h', h), part('V', vv)
            # the left column: consonant over the ㅗ/ㅜ/ㅡ part; the ㅏ/ㅓ/ㅣ part beside it, as tall as the column
            col_w = max(width(cl), width(hp))
            hy = 0
            items.append((hp, (col_w - width(hp)) // 2 - box(hp)[0], hy))
            cy = box(hp)[3] + G
            items.append((cl, (col_w - width(cl)) // 2 - box(cl)[0], cy))
            top = cy + C
            items.append((vp, col_w + G - box(vp)[0], (top + box(hp)[1]) // 2 - HV // 2))
            bottom = min(box(hp)[1], (top + box(hp)[1]) // 2 - HV // 2)
        if T:
            tl = part('C', T)
            xs = [x + box(n)[0] for n, x, y in items] + [x + box(n)[2] for n, x, y in items]
            cx = (min(xs) + max(xs)) // 2
            items.append((tl, cx - (box(tl)[0] + box(tl)[2]) // 2, bottom - G - C))
        name = f'uni{0xAC00 + i:04X}'
        glyphs[name] = place(items); order.append(name); cmap[0xAC00 + i] = name

    # letters on their own: ㄱ…ㅎ, ㅏ…ㅣ and the old letters ㅿ ㆁ ㆆ ㆍ, the same size as in syllables
    alone = {chr(c): c for c in range(0x3131, 0x3164)}
    for ch, c in (('ㅿ', 0x317F), ('ㆁ', 0x3181), ('ㆆ', 0x3186), ('ㆍ', 0x318D)):
        alone[ch] = c
    for ch, code in alone.items():
        if ch in VCOMP:
            h, vv = VCOMP[ch]; hp, vp = part('h', h), part('V', vv)
            items = [(hp, 0, HV // 3), (vp, box(hp)[2] + G - box(vp)[0], 0)]
        elif ch in VERT:
            items = [(part('V', ch), 0, 0)]
        elif ch in HORI or ch == 'ㆍ':
            items = [(part('H', ch), 0, 0)]
        else:
            items = [(part('C', ch), 0, 0)]
        name = f'uni{code:04X}'
        glyphs[name] = place(items); order.append(name); cmap[code] = name

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    gt = fb.font['glyf']
    for c in gt.glyphs.values():
        if c.isComposite():
            for comp in c.components:
                comp.flags |= 0x2
    metrics = {}
    for n in order:
        g = gt[n]
        g.recalcBounds(gt)
        metrics[n] = (1000 if n != 'space' else 400, getattr(g, 'xMin', 0) or 0)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=880, descent=-120)
    fam = 'Plain Jeongeum'
    fb.setupNameTable({'familyName': fam, 'styleName': 'Regular', 'uniqueFontIdentifier': 'PlainJeongeum-Regular',
                       'fullName': fam, 'psName': 'PlainJeongeum-Regular', 'version': 'Version 0.1',
                       'copyright': 'Copyright 2026 Jeremy Orpano. Drawn for Plainwrite-K after the letterforms of the Hunminjeongeum Haerye (1446).',
                       'licenseDescription': 'This Font Software is licensed under the SIL Open Font License, Version 1.1.',
                       'licenseInfoURL': 'https://openfontlicense.org'})
    fb.setupOS2(sTypoAscender=880, sTypoDescender=-120, sTypoLineGap=0, usWinAscent=900, usWinDescent=140, fsType=0,
                ulCodePageRange1=1 << 19)   # Korean Wansung
    fb.setupPost()
    fb.setupMaxp()
    fb.font.flavor = 'woff'
    fb.save(out)
    print(f'{len(order)} glyphs, {len(parts)} parts')


if __name__ == '__main__':
    build(sys.argv[1])

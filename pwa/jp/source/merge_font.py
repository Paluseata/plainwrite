#!/usr/bin/env python3
"""Builds Plainwrite-J's pixel-gothic.ttf: the full DotGothic16 (kana and kanji included) with every
non-Japanese glyph taken from Plainwrite's own Pixel Gothic (its half-width Cyrillic, Tajik letters,
menu symbols and fixes), so the two apps draw Latin and Cyrillic exactly alike.
Usage: merge_font.py DotGothic16-Regular.ttf plainwrite-pixel-gothic.ttf out.ttf"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen

full, main, out = sys.argv[1:4]
F, M = TTFont(full), TTFont(main)
fc, mc = F.getBestCmap(), M.getBestCmap()
mgs = M.getGlyphSet()
order = F.getGlyphOrder()
vref = F['vmtx'][fc[ord('A')]]
taken = added = 0
# keep DotGothic16's own wide (JIS) Russian letters at U+E401-U+E451, before Plainwrite's half-width ones replace them:
# Plainwrite-J's Wide letters setting draws Cyrillic with these
import copy
for cp in [0x401, 0x451] + list(range(0x410, 0x450)):
    src = fc.get(cp)
    if not src: continue
    name = 'uniE%03X' % cp
    order.append(name)
    F['glyf'][name] = copy.deepcopy(F['glyf'][src]); F['hmtx'][name] = F['hmtx'][src]; F['vmtx'][name] = F['vmtx'][src]
    for t in F['cmap'].tables:
        if t.isUnicode(): t.cmap[0xE000 + cp] = name
for cp, mname in mc.items():
    rp = DecomposingRecordingPen(mgs); mgs[mname].draw(rp); pen = TTGlyphPen(None); rp.replay(pen); g = pen.glyph()   # decomposed, so no component names cross over
    name = fc.get(cp)
    if name is None:
        name = 'uni%04X' % cp if cp < 0x10000 else 'u%05X' % cp
        while name in F['glyf'].glyphs: name += '.pw'
        order.append(name); added += 1
        for t in F['cmap'].tables:
            if t.isUnicode() and (cp < 0x10000 or t.format in (12, 13)): t.cmap[cp] = name
        F['vmtx'][name] = vref
    F['glyf'][name] = g
    g.recalcBounds(F['glyf'])
    F['hmtx'][name] = (M['hmtx'][mname][0], getattr(g, 'xMin', 0) or 0)
    taken += 1
F.setGlyphOrder(order)
F['maxp'].numGlyphs = len(order)
for rec in F['name'].names:
    if rec.nameID in (1, 3, 4, 16):
        rec.string = rec.toUnicode().replace('DotGothic16', 'Pixel Gothic J')
    if rec.nameID == 6:
        rec.string = 'PixelGothicJ-Regular'
if 'DSIG' in F: del F['DSIG']
F.save(out)
print('from Plainwrite:', taken, 'new:', added)

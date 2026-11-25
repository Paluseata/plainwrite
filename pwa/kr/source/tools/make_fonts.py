#!/usr/bin/env python3
"""Fonts for Plainwrite-K.

    python3 make_fonts.py screen <plainwrite dir> <plainwrite-j dir> <fonts-in dir> <dict-ko.txt> <out dir>
    python3 make_fonts.py ui <built index.html>... --out <out dir>

screen: the fonts the LCD draws with, and faces.json, which build.py reads.
  - Galmuri11.ttf and neodgm.ttf from <fonts-in>, as they are (both SIL OFL 1.1). Without them a cut-down
    Noto Sans CJK KR stands in, so the app still runs; drop the real files in and build again.
  - pixel-gothic.ttf, "Pixel Gothic K": Plainwrite's Pixel Gothic with the Hanja, CJK punctuation and
    full-width forms of DotGothic16 (from Pixel Gothic J) added on the same pixel grid.
  - hanja-fallback.woff: Noto Sans CJK KR for the few dictionary Hanja DotGothic16 doesn't have.
  - logo-k.woff: the K in the logo, from Lora Bold.
ui: Noto Sans CJK KR (400, 500, 700) cut down to the characters the key labels, menus and Help use.
"""
import glob, json, os, shutil, sys
from fontTools.ttLib import TTFont, TTCollection
from fontTools import subset
from fontTools.varLib import instancer

NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc'
LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'


def noto_kr(weight):
    for f in TTCollection(NOTO.format(weight)).fonts:
        if f['name'].getDebugName(1).startswith('Noto Sans CJK KR'):
            return f
    raise SystemExit('no Noto Sans CJK KR ' + weight)


def cut(font, text, out, flavor='woff', name=None, features=('*',)):
    opts = subset.Options()
    opts.flavor = flavor
    opts.layout_features = list(features)
    opts.name_IDs = ['*']
    opts.notdef_outline = True
    s = subset.Subsetter(opts)
    s.populate(text=text)
    s.subset(font)
    if name:
        rename(font, name)
    font.flavor = flavor
    font.save(out)


def rename(font, family):
    for n in font['name'].names:
        if n.nameID in (1, 16):
            n.string = family
        elif n.nameID == 4:
            n.string = family + (' Bold' if 'Bold' in str(n) else '')
        elif n.nameID == 6:
            n.string = family.replace(' ', '') + '-Regular'
    if 'CFF ' in font:
        font['CFF '].cff.fontNames = [family.replace(' ', '')]


def copyright_of(path):
    f = TTFont(path)
    return (f['name'].getDebugName(0) or '').strip()


def screen(pw, pj, fin, dict_path, out):
    os.makedirs(out, exist_ok=True)
    hanja = set()
    for line in open(dict_path, encoding='utf-8'):
        if '\t' in line:
            hanja.update(line.rstrip('\n').split('\t')[1])
    faces = []

    def find(*pats):
        for p in pats:
            hit = sorted(glob.glob(os.path.join(fin, p)))
            if hit:
                return hit[0]

    gal = find('Galmuri11.woff2', '*/Galmuri11.woff2')
    dgm = find('neodgm.ttf', 'NeoDunggeunmo*.ttf', 'neodgm*.ttf')
    if gal:
        shutil.copy(gal, os.path.join(out, 'galmuri11.woff2'))
        faces.append(dict(name='Galmuri', family='Galmuri11', file='galmuri11.woff2', format='woff2', pixel=12,
                          langs='ru uk be bg sr el', credit_ko='갈무리 (OFL)', credit_en='Galmuri (OFL)',
                          copyright=copyright_of(find('Galmuri11.ttf', '*/Galmuri11.ttf') or gal)))
    if dgm:
        f = TTFont(dgm); f.flavor = 'woff'; f.save(os.path.join(out, 'neodgm.woff'))
        faces.append(dict(name='Neo DunggeunMo', family='NeoDunggeunmo', file='neodgm.woff', format='woff', pixel=16,
                          langs='', credit_ko='Neo 둥근모 (OFL)', credit_en='Neo DunggeunMo (OFL)', copyright=copyright_of(dgm)))
    # Plain Jeongeum: drawn by make_jeongeum.py after the Hunminjeongeum Haerye; Latin comes from Jost, geometric too
    import subprocess
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make_jeongeum.py'), os.path.join(out, 'jeongeum.woff')], check=True)
    jeong = dict(name='Jeongeum', family='Plain Jeongeum', file='jeongeum.woff', format='woff', langs='', fb='"Jost",',
                 credit_ko='정음 (훈민정음 해례본을 본뜸)', credit_en='Jeongeum (after the Hunminjeongeum Haerye)', copyright='', extra=True)
    if not faces:
        # stand-in until the pixel fonts are added: Hangul from Noto Sans CJK KR
        text = ''.join(chr(c) for c in range(0xAC00, 0xD7A4)) + ''.join(chr(c) for c in range(0x3131, 0x318F)) + \
            ''.join(chr(c) for c in range(0x20, 0x7F))
        cut(noto_kr('Regular'), text, os.path.join(out, 'hangul-standin.woff'), name='Hangul Standin')
        faces.append(dict(name='Noto Sans KR (stand-in)', family='Hangul Standin', file='hangul-standin.woff', format='woff',
                          langs='', credit_ko='Noto Sans CJK KR (임시)', credit_en='Noto Sans CJK KR (stand-in)', copyright=''))
    faces.append(jeong)
    json.dump(faces, open(os.path.join(out, 'faces.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # Pixel Gothic K
    base = TTFont(os.path.join(pw, 'pixel-gothic.ttf'))
    donor = TTFont(os.path.join(pj, 'pixel-gothic.ttf'))
    want = set(hanja)
    want.update(chr(c) for c in range(0x3000, 0x3040))       # CJK punctuation: 、。「」『』〈〉《》…
    want.update(chr(c) for c in range(0xFF01, 0xFF5F))       # full-width ASCII
    want.update('·※…‥―ㆍ')
    bcmap, dcmap = base.getBestCmap(), donor.getBestCmap()
    add = sorted(c for c in want if ord(c) in dcmap and ord(c) not in bcmap)
    glyf, hmtx = base['glyf'], base['hmtx']
    order = base.getGlyphOrder()
    names = set(order)
    new_map = {}
    for ch in add:
        g = dcmap[ord(ch)]
        n = 'uni%04X' % ord(ch)
        while n in names:
            n += '.k'
        names.add(n)
        dg = donor['glyf'][g]
        if dg.isComposite():
            dg.expand(donor['glyf'])
            # flatten composites so they don't point at glyphs we don't copy
            from fontTools.pens.ttGlyphPen import TTGlyphPen
            pen = TTGlyphPen(donor.getGlyphSet())
            donor.getGlyphSet()[g].draw(pen)
            dg = pen.glyph()
        glyf.glyphs[n] = dg
        order.append(n)
        hmtx.metrics[n] = donor['hmtx'][g]
        new_map[ord(ch)] = n
    base.setGlyphOrder(order)
    glyf.glyphOrder = order
    for t in base['cmap'].tables:
        if t.isUnicode():
            if t.format == 4:
                t.cmap.update({k: v for k, v in new_map.items() if k < 0x10000})
            else:
                t.cmap.update(new_map)
    base['maxp'].numGlyphs = len(order)
    if 'post' in base and base['post'].formatType == 2.0:
        base['post'].extraNames = []
        base['post'].mapping = {}
    for n in base['name'].names:
        s = str(n)
        if n.nameID in (3, 4, 6, 16, 17) or n.nameID == 1:
            pass
    rename_keep_family(base)
    base.save(os.path.join(out, 'pixel-gothic.ttf'))
    have = set(chr(c) for c in base.getBestCmap())
    missing = sorted(set(hanja) - have)
    print(f'Pixel Gothic K: +{len(add)} glyphs; Hanja not in it: {len(missing)}')

    # Hanja fallback
    cut(noto_kr('Regular'), ''.join(missing) or '一', os.path.join(out, 'hanja-fallback.woff'), name='Hanja Fallback', features=())
    # the K in the logo
    lora = instancer.instantiateVariableFont(TTFont(LORA), {'wght': 700})
    cut(lora, 'K', os.path.join(out, 'logo-k.woff'), name='Plainwrite K')


def rename_keep_family(font):
    # CSS still calls it "Pixel Gothic"; the font itself says it's Pixel Gothic K, a modified version
    for n in font['name'].names:
        if n.nameID == 1:
            n.string = 'Pixel Gothic K'
        elif n.nameID == 4:
            n.string = 'Pixel Gothic K Regular'
        elif n.nameID == 6:
            n.string = 'PixelGothicK-Regular'
        elif n.nameID == 3:
            n.string = 'Pixel Gothic K'


def ui(htmls, out):
    text = set()
    for h in htmls:
        text.update(open(h, encoding='utf-8').read())
    keep = ''.join(sorted(c for c in text if ord(c) >= 0x1100))
    keep += ''.join(chr(c) for c in range(0x20, 0x7F))
    for w in (400, 500, 700):
        weight = {400: 'Regular', 500: 'Medium', 700: 'Bold'}[w]
        cut(noto_kr(weight), keep, os.path.join(out, f'ui-ko-{w}.woff'), name='Noto Sans KR K')
    print('UI font:', len(keep), 'characters')


if __name__ == '__main__':
    if sys.argv[1] == 'screen':
        screen(*sys.argv[2:7])
    else:
        i = sys.argv.index('--out')
        ui(sys.argv[2:i], sys.argv[i + 1])

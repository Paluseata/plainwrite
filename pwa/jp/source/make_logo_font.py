#!/usr/bin/env python3
"""The serif J of the Plainwrite-J wordmark: Playfair Display (SIL OFL 1.1, The Playfair Display Project Authors), renamed as its licence asks, at weight 700,
cut down to the one letter. Usage: make_logo_font.py PlayfairDisplay[wght].ttf out.woff"""
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset
f = instancer.instantiateVariableFont(TTFont(sys.argv[1]), {'wght': 700})
o = subset.Options(); o.flavor = 'woff'; o.layout_features = []; o.name_IDs = ['*']
s = subset.Subsetter(o); s.populate(text='J'); s.subset(f)
# a cut-down font is a Modified Version, and "Playfair Display" is a Reserved Font Name: rename it
for rec in f['name'].names:
    if rec.nameID in (1, 3, 4, 16): rec.string = 'Plainwrite J Logo'
    elif rec.nameID == 6: rec.string = 'PlainwriteJLogo-Bold'
    elif rec.nameID in (2, 17): rec.string = 'Bold'
f.flavor = 'woff'; f.save(sys.argv[2])

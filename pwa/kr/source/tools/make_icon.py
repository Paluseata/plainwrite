"""The Plainwrite-K icon, drawn from Plainwrite's icon layout in the colours of a Korean flag.

    python3 make_icon.py <style> <out dir>       style: taegukgi (default) | unification

taegukgi:    a white body like the flag's field; the top row red and the file row blue, like the
             taegeuk; the bottom row black, like the four trigrams.
unification: the Korean Unification Flag: a white field with the device in its sky blue, like the peninsula.
"""
import sys
from PIL import Image, ImageDraw

style = sys.argv[1] if len(sys.argv) > 1 else 'unification'
out = sys.argv[2] if len(sys.argv) > 2 else '.'
S = 4                                   # drawn at 4x, then scaled down for smooth edges
COL = {
    'taegukgi':    dict(body='#f4f3ee', edge='#dcdad2', top='#cd2e3a', file='#0047a0', active='#00306c', bottom='#1d1d1f'),
    'unification': dict(bg='#ffffff', body='#4a90d6', edge='#3570ad', top='#9fcdf0', file='#f4f8fc', active='#cfe6f8', bottom='#9fcdf0'),
}[style]
im = Image.new('RGB', (512 * S, 512 * S), COL.get('bg', '#121417'))
d = ImageDraw.Draw(im)
R = lambda x0, y0, x1, y1, r, fill: d.rounded_rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], r * S, fill=fill)
R(40, 104, 472, 408, 44, COL['edge'])
R(40, 104, 472, 404, 44, COL['body'])
R(80, 140, 432, 244, 9, '#9aa38b')       # bezel line round the screen
R(81, 141, 432, 244, 8, '#b3bca3')
for x0, y0, x1, y1 in ((101, 159, 359, 169), (101, 185, 299, 195), (101, 211, 329, 221), (336, 206, 341, 226)):
    R(x0, y0, x1, y1, 0, '#1b2317')
for i in range(9):
    R(80 + 40 * i, 262, 112 + 40 * i, 288, 5, COL['top'])
R(80, 300, 118, 328, 5, COL['active'])
for i in range(7):
    R(126 + 45 * i, 301, 162 + 45 * i, 328, 5, COL['file'])
for i in range(8):
    R(80 + 45 * i, 340, 117 + 45 * i, 368, 5, COL['bottom'])
big = im.resize((512, 512), Image.LANCZOS)
big.save(f'{out}/icon-512.png')
im.resize((192, 192), Image.LANCZOS).save(f'{out}/icon-192.png')

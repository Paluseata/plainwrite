#!/usr/bin/env python3
"""Puts each edition's files together: python3 assemble.py <plainwrite dir> <build dir> <out dir>

<build dir> holds what the other scripts made (faces.json, fonts, dict-ko.txt, icons, ko/ and en-ko/ index.html).
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
pw, b, out = sys.argv[1:4]
faces = json.load(open(os.path.join(b, 'faces.json'), encoding='utf-8'))
PW_FONTS = ['bedstead.otf', 'bedstead-condensed.otf', 'plain-sans.ttf', 'home-computer.ttf', 'home-computer-thin.ttf', 'jost.ttf',
            'vt323.ttf', 'press-start-2p.ttf', 'tiny5.ttf', 'ibm-plex-mono-medium.ttf', 'courier-prime-bold.ttf', 'share-tech-mono.ttf']
K_FILES = ['pixel-gothic.ttf', 'hanja-fallback.woff', 'logo-k.woff', 'ui-ko-400.woff', 'ui-ko-500.woff', 'ui-ko-700.woff', 'dict-ko.txt',
           'icon-192.png', 'icon-512.png'] + [f['file'] for f in faces]
for ed in ('ko', 'en-ko'):
    d = os.path.join(out, ed)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    shutil.copy(os.path.join(b, ed, 'index.html'), d)
    for f in PW_FONTS:
        shutil.copy(os.path.join(pw, f), d)
    for f in K_FILES:
        shutil.copy(os.path.join(b, f), d)
    for f in ('OFL.txt', 'MPL-2.0-dictionary.txt'):
        shutil.copy(os.path.join(HERE, f), d)
    ko = ed == 'ko'
    json.dump({
        'name': 'Plainwrite-K', 'short_name': 'Plainwrite-K', 'lang': 'ko' if ko else 'en',
        'description': '한글 입력이 들어 있는 레트로 워드프로세서. 자동 저장되는 파일 여덟 개, 오프라인에서도 동작.' if ko else
                       'Retro minimalist word processor with Korean input. Eight auto-saving files, works offline.',
        'start_url': './', 'scope': './', 'display': 'standalone', 'orientation': 'any',
        'background_color': '#121417', 'theme_color': '#121417',
        'icons': [{'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
                  {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
                  {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]},
        open(os.path.join(d, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    fonts = PW_FONTS + [f for f in K_FILES if f.endswith(('.ttf', '.otf', '.woff'))]
    sw = open(os.path.join(HERE, 'sw.js'), encoding='utf-8').read().replace('%FONTS%', ', '.join(f"'./{f}'" for f in fonts))
    open(os.path.join(d, 'sw.js'), 'w', encoding='utf-8').write(sw)
    shutil.copy(os.path.join(HERE, 'README-ko.md' if ko else 'README-en-ko.md'), os.path.join(d, 'README.md'))
    print(ed, len(os.listdir(d)), 'files')

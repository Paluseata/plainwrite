#!/usr/bin/env python3
"""Bundle Plainwrite's Google-hosted fonts into the app, so the APK needs no internet.

Run once on a computer with internet access (Python 3, no extra packages):
    python3 tools/fetch_fonts.py

For each edition (app/src/english/assets/www and app/src/multilingual/assets/www) it downloads the
fonts named in index.html's Google Fonts <link> into www/fonts/, writes www/fonts/fonts.css and points
index.html at it. Only Latin, Cyrillic and Greek subsets are kept (CJK and Vietnamese are out of scope).
All these fonts are under the SIL Open Font License, which allows bundling them in an app.
"""
import os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EDITIONS = [os.path.join(ROOT, 'app', 'src', e, 'assets', 'www') for e in ('english', 'multilingual')]
KEEP = {'latin', 'latin-ext', 'cyrillic', 'cyrillic-ext', 'greek', 'greek-ext'}
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60).read()

def bundle(www):
    index = os.path.join(www, 'index.html')
    html = open(index, encoding='utf-8').read()
    m = re.search(r'<link href="(https://fonts\.googleapis\.com/css2\?[^"]+)" rel="stylesheet">', html)
    if not m:
        print('  already bundled or no Google Fonts link:', www); return
    css = get(m.group(1).replace('&amp;', '&')).decode('utf-8')
    os.makedirs(os.path.join(www, 'fonts'), exist_ok=True)
    out, n = [], 0
    for subset, block in re.findall(r'/\* ([^*]+?) \*/\s*(@font-face \{.*?\})', css, re.S):
        if subset.strip() not in KEEP:
            continue
        url = re.search(r'url\((https://[^)]+)\)', block).group(1)
        fam = re.search(r"font-family: '([^']+)'", block).group(1)
        wt = re.search(r'font-weight: (\d+)', block).group(1)
        name = f"{fam.replace(' ', '')}-{wt}-{subset.strip()}.woff2"
        path = os.path.join(www, 'fonts', name)
        if not os.path.exists(path):
            open(path, 'wb').write(get(url)); n += 1
        out.append(block.replace(url, name))
    open(os.path.join(www, 'fonts', 'fonts.css'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    html = html.replace(m.group(0), '<link href="fonts/fonts.css" rel="stylesheet">')
    html = re.sub(r'\s*<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>', '', html)
    open(index, 'w', encoding='utf-8').write(html)
    print(f'  {www}: {len(out)} font files ({n} downloaded)')

if __name__ == '__main__':
    for www in (sys.argv[1:] or EDITIONS):
        if os.path.isdir(www):
            bundle(www)

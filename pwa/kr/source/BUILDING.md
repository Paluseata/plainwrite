# Building Plainwrite-K

`build.sh` makes both editions in `out/dist` from:

- `PW`: a Plainwrite Multilingual release folder (1.07): its `index.html` and fonts.
- `PJ`: a Plainwrite-J folder: its `pixel-gothic.ttf` (Pixel Gothic J) supplies DotGothic16's Hanja.
- `fonts-in/`: `Galmuri11.woff2` (and `Galmuri11.ttf` for its copyright line) and `neodgm.ttf`.

Needs Python 3 with fontTools and Pillow, and Noto Sans CJK and Lora installed (Debian: fonts-noto-cjk).

| Script | What it does |
|---|---|
| `tools/build.py` | Every change to Plainwrite, as find-and-replace; each must match exactly once |
| `tools/ime-ko.js` | The Hangul input method and Hanja conversion |
| `tools/tutor-ko.js` | Hangul Tutor and Hanja Tutor lessons (edit freely) |
| `tools/quiz-ko.js` | English Quiz (Games), from Plainwrite-J, with Korean vocabulary |
| `tools/i18n-ko.js` | Korean menus, and the English messages for Korean input |
| `tools/help-ko.html`, `tools/help-en-ko.html` | The Korean Help sheet, and the Korean section of the English one |
| `tools/sheets-ko.json` | Korean labels for the other sheets (Korean edition) |
| `tools/about-*.txt`, `tools/welcome-*.txt` | About screen and first-start text (edit freely) |
| `tools/make_dict.py` | `dict-ko.txt` from LibreOffice's Hangul–Hanja table (`lo_hanja.json`; `dump_lo_hanja.py` reads it out of LibreOffice) |
| `tools/make_jeongeum.py` | Draws Plain Jeongeum, the Hunminjeongeum-style font |
| `tools/make_fonts.py` | Pixel Gothic K, the Hanja fallback, the UI font and the logo K |
| `tools/make_icon.py` | The icon: `taegukgi` or `unification` |
| `tools/assemble.py` | Puts each edition's files together |

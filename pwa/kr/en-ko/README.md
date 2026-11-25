# Plainwrite-K

A Korean edition of Plainwrite, the retro minimalist word processor. It runs offline once it has been opened once.

## AI disclosure

This application was written using the assistance of Claude, an artificial intelligence large language model by Anthropic.

## Editions

- **Korean** (한국어판): Korean menus and Help only.
- **English–Korean**: English and Korean menus. It starts in Korean if the system language is Korean, otherwise in English.

Both editions have the same Hangul input method, fonts and Hanja table.

## Korean input

The input method works with physical keyboards. Phone and tablet on-screen keyboards keep their own Korean input.

- **Hangul keyboard** (Control Panel → Hangul keyboard): Dubeolsik 두벌식, Sebeolsik 390, Sebeolsik Final 세벌식 최종, or Romanized (one Latin letter per jamo: `hangug'eo` → 한국어).
- **Switching**: the 한 / Ａ / A badge in the top bar, 한/영, Shift+Space, Ctrl+Space, or Right Alt on its own.
- **Hanja**: 한자, F9 or Right Ctrl on its own converts the syllable before the cursor (or each syllable of a selection). The choices show on the bottom line, most-used first.
- **Hanja table**: LibreOffice's Hangul–Hanja table, in `dict-ko.txt` (MPL 2.0).

The Help sheet has the full key list. The Applets menu also has a **Hangul Tutor** (Dubeolsik rows, words, sentences; speed in keystrokes a minute) and a **Hanja Tutor** (grade 8 Hanja with their meaning and reading, typed with the Hanja key).

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app |
| `sw.js` | Offline cache |
| `manifest.json` | App name and icons |
| `galmuri11.woff2`, `neodgm.woff` | Galmuri and Neo DunggeunMo, the Korean pixel fonts |
| `jeongeum.woff` | Plain Jeongeum, a geometric Hangul after the Hunminjeongeum Haerye, drawn by `make_jeongeum.py` |
| `pixel-gothic.ttf` | Pixel Gothic K: Plainwrite's Pixel Gothic with DotGothic16's Hanja added |
| `hanja-fallback.woff` | Noto Sans CJK KR for the Hanja DotGothic16 lacks |
| `ui-ko-400/500/700.woff` | Noto Sans CJK KR for the Korean key labels and Help sheet, cut down to the letters they use |
| `logo-k.woff` | The K in the logo (Lora Bold) |
| `dict-ko.txt` | Hangul-to-Hanja table |
| Other `.ttf` and `.otf` files | Plainwrite's bundled fonts |
| `OFL.txt`, `MPL-2.0-dictionary.txt` | Licences for the fonts and the Hanja table |

To install, upload every file to the same folder on any web host, open it once, then add it to the home screen.

## Building

The `source` folder has the build scripts. `build.sh` turns a Plainwrite release (currently 1.07, Multilingual) into both editions.

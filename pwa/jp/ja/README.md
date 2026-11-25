# Plainwrite-J

A Japanese fork of Plainwrite, the retro minimalist word processor. It runs offline once it has been opened once.

## Editions

- **Japanese** (日本語版): Japanese menus only.
- **English–Japanese**: English and Japanese menus. It starts in Japanese if the system language is Japanese, otherwise in English.

Both editions have the same Japanese input method, and the same font and dictionary.

## Japanese input

The input method works with physical keyboards. Phone and tablet on-screen keyboards keep their own Japanese input.

- **Kana input** (Control Panel → Kana input): Romaji, JIS kana (たていすかんな) or Thumb shift (NICOLA).
- **Converting:** kana go into the text underlined. Space converts them. The highlighted part's choices cycle on the bottom line, the same way status messages show there.
- **Dictionary:** SKK-JISYO.L, in `dict-ja.txt`.

The Help sheet has the full key list.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app |
| `sw.js` | Offline cache |
| `manifest.json` | App name and icons |
| `pixel-gothic.ttf` | Pixel Gothic J, the default font |
| `ui-ja-400/500/700.woff` | M PLUS 1p for the Japanese key labels and Help sheet, cut down to the letters they use |
| `dict-ja.txt` | Kana-to-kanji dictionary |
| Other `.ttf` and `.otf` files | Bundled fonts, from Plainwrite (Jost, VT323, Press Start 2P, Tiny5, IBM Plex Mono, Courier Prime, Share Tech Mono, Bedstead and Plainwrite's own) |
| `OFL.txt` | Licence for Pixel Gothic J |
| `COPYING-dictionary.txt` | Licence for the dictionary |

To install, upload every file to the same folder on any web host, open it once, then add it to the home screen.

## Other platforms

plainwrite-j-android.zip and plainwrite-j-desktop.zip hold the Android (Gradle) and Windows, macOS and Linux (Tauri 2) projects, each with both editions inside. Their README files say how to build them.

## Building

The `source` folder has the build scripts. `build.py` turns a Plainwrite release (currently 1.07) into both editions:

- `merge_font.py` builds Pixel Gothic J: the full DotGothic16, with Plainwrite's own Pixel Gothic laid over it for Latin, Cyrillic and symbols. Both apps draw those letters exactly alike.
- `make_dict.py` builds `dict-ja.txt` from SKK-JISYO.L and SKK-JISYO.M.
- `make_ui_font.py` cuts M PLUS 1p down to the letters the interface uses.

## Licences

- **Pixel Gothic J:** a modified version of DotGothic16 (© The DotGothic16 Project Authors), under the SIL Open Font License 1.1.
  - DotGothic16 drew its Cyrillic letters as wide as a kanji and had Russian only.
  - Pixel Gothic J uses Plainwrite's half-width redraw, on the font's own pixel grid. It also has the Ukrainian, Belarusian, Serbian, Macedonian, Kazakh, Kyrgyz, Mongolian and Tajik letters.
- **M PLUS 1p:** © M+ FONTS PROJECT, under the SIL Open Font License 1.1.
- **Playfair Display** (the J in the logo): © The Playfair Display Project Authors, under the SIL Open Font License 1.1. It is cut down to one letter and renamed, as the licence asks.
- **Dictionary:** SKK-JISYO.L © the SKK Development Team and contributors, under the GNU GPL v2 or later.

# Plainwrite (PWA)

Plainwrite is a retro minimalist-ish word processing application.
It is inspired by numerous "writer decks" or portable dedicated word processing devices
made between the 1980s and 2000s.
It uses eight auto-saving files or text buffers, and it even works perfectly offline.
Your writing is stored in the browser's local storage on each device and never leaves it.

## AI disclosure

This application was written using the assistance of Claude, an artificial intelligence
large language model by Anthropic.

## Editions

- **English** (`pwa/english`): English-only single language edition. Other languages can
  be added later with Control Panel → Language packs… → Import language pack… and a pack file.
- **Multilingual** (`pwa/multilingual`): The same app, plus 48 language packs in `langs/`.
  On first start, every pack is installed and the menu language follows the system language when
  there's a match, otherwise English is used. Packs can be ticked off and on again in Control Panel.

## Installing

1. Host the files of one edition on any static HTTPS host (GitHub Pages, Netlify, Cloudflare Pages).
2. Open the URL once while online and give it a few seconds: the app, its fonts and (in the
   Multilingual edition) the language packs are saved on the device in the background.
3. Add to Home Screen. From this point on the app will need no connection at all.

## Language packs

Each `langs/<code>.json` holds one language: menu text (`strings`), keyboard layouts (`keyboards`),
system-language codes it answers to (`locales`) and, for Cyrillic and Greek, the alphabet a font must
cover (`letters`). `langs/all.json` holds every pack; importing it installs them all. To make a new
language, copy a pack, change `id`, `name` and the strings; keys you leave out stay in English.

## Out of scope

Chinese, Korean and Vietnamese are deliberately not supported. These need an input method
(IME) and fonts which are a bit beyond what this device is about.
A fork that supports Japanese IME named "Plainwrite-J" is also in development.

## Fonts

Pixel Gothic is DotGothic16 by Fontworks (SIL Open Font License 1.1), cut down to Latin, Greek and
Cyrillic, with the Cyrillic letters redrawn at half width on its 16-pixel grid and some more added.
It is a modified version, so it is renamed as the licence asks.

Jost by Indestructible Type (SIL Open Font License 1.1) is bundled for the device's logo, keys and menus, cut down to Latin and Cyrillic.
Also bundled, cut down to Latin, Greek and Cyrillic where they have them, all under the SIL Open Font License 1.1:
VT323 by Peter Hull, Press Start 2P by CodeMan38, Tiny5 by Stefie Justprince, IBM Plex Mono (Medium) by IBM
and Courier Prime (Bold) by Alan Dague-Greene. Share Tech Mono (the Terminal font) still loads from Google Fonts.

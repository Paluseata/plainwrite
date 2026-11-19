# Plainwrite for Godot 3.6 (core port)

A first port of Plainwrite, the retro word processor inspired by the AlphaSmart Neo, to the
Godot 3.6 game engine. It uses the GLES2 renderer, so it can run on old and thrifted hardware:
Android 4.4 and up, and almost any desktop with OpenGL 2.1.

## Open and run

1. Download **Godot 3.6** (the "Standard" build, not Mono) from godotengine.org and unzip it.
2. Start Godot → **Import** → pick this folder's `project.godot` → **Import & Edit**.
3. Press **F5** (or the ▶ button) to run.

## Export

- **Desktop (Windows, macOS, Linux):** Editor → Manage Export Templates → Download. Then
  Project → Export → Add… → pick the platform → Export Project.
- **Android:** install Android Studio's SDK and a JDK (Godot 3.6 wants OpenJDK 11), set their
  paths in Editor → Editor Settings → Export → Android, download the export templates, then
  Project → Export → Add… → Android. The debug keystore is made for you. Set
  Screen → Orientation to *Sensor Landscape* if you like; the project already asks for landscape.

## Keys

| Key | What it does |
|---|---|
| F1–F8, Alt+1–8 | Switch to file 1–8 |
| F9 | Applets menu (again to go back to the writer) |
| F10 | On/off |
| Esc, Backspace | Back out of menus (Android's back button too) |
| Arrows, Home, End, Page Up/Down | Move (Ctrl for words / whole file), Shift to select |
| Insert | Type over text / insert text |
| Ctrl+A, C, X, V | Select all, copy, cut, paste |
| Ctrl+Z, Ctrl+Y (Ctrl+Shift+Z) | Undo, redo |

The on-screen keys do the same as F10, F1–F8, F9, plus **clear file** (asks Y/N first).

## What's here

- Writer with eight files, saved automatically to `user://plainwrite.json`
  (on Windows: `%APPDATA%\Godot\app_userdata\Plainwrite`).
- Word wrap by on-screen width, ↑ ↓ that keep their column, selection, clipboard, undo/redo,
  Insert to type over text.
- Five pixel fonts drawn at whole-pixel sizes: Plain sans, Pixel gothic (half-width Cyrillic on
  a 16-pixel grid), Home computer, Home computer thin, Teletext. All of them include Cyrillic
  (Tajik letters too), and all but Pixel gothic include Greek.
- Text sizes from Large (4 lines, the Neo's default) to Tiny (12 lines).
- The device is sized from your display's real size (its screen is about 6 inches across), so text
  is about the same size on a laptop, desktop monitor or tablet; small screens use the full width.
  Control Panel → Screen size → Fill window makes the screen grow with the window instead.
- Screen palettes (Device editor → Screen: Classic LCD, Amber, Paper, Pink, Creamed spinach, Black & white, plus the
  C64 / Atari / MSX / ZX Spectrum / Apple II screens, which suggest their own font, and five
  Amp media-player displays plus Slate blue and Slate purple), dark mode.
- Cursor: full block, tall line or underscore, with or without blinking.
- Gaps between selected lines on/off.
- Power: logo at power-on; auto off after 2–60 minutes (or never), with the logo shown before
  an automatic power off but not when you switch off by hand.
- Control Panel → Device, and Device editor…:
  - Device (in the Control Panel): the same 34 themes as the web app, including the pastels, the three-colour
    gradients (Sunset, Aurora, Vaporwave, Cotton candy, Lagoon, Ember, Pastel rainbow) and the
    media-player Amp themes, Slate blue, Slate purple, Sakura, Matcha and Workbench, which switch to their own screen (and back when you leave them).
  - Screen (in the Device editor): the screen palettes below.
  - Screen border: off by default; on, it frames the screen in one of eight colours (Border colour).
  - Device shadow: 0–3×.
  - Power colour: Auto (green that stays readable on any key colour) or Green, Red, Amber, Blue,
    White, Pink.
  - Background: plain (from the theme), gradient (12 presets; straight, round or sweep, any
    angle), pattern (13 vector patterns in 12 colour schemes, any size), generated (static,
    plasma, starfield, 10 PRINT maze, Truchet tiles, dither, topography, cells; pixel size and
    Shuffle), or your own picture (fill, fit, stretch, centre or tile).
    Pixel rendering draws gradients, patterns and pictures in big sharp pixels (with optional
    dither for gradients).
    Dim darkens any of them. Everything is drawn by two shaders in `shaders/`.
  - Your picture is copied to `user://wallpaper.*`. On Android the file chooser only sees
    folders the app may read, so desktop is the easier place to pick one.
- Key click made in code (no sound files).
- Factory reset.
- Low processor mode: the screen only redraws when something changes, which saves battery.

## Not ported yet

Calculator, typing tutor, games, find, spell check, Send, the other keyboard layouts and dead
keys, language packs and menu translations, the palette and bevel editors, key colours,
custom screen sizes, wake on key, battery check, the easter eggs, and the web fonts that
aren't bundled (Terminal, Typewriter, LCD and the other Google Fonts).

## How the code is laid out

| File | Job |
|---|---|
| `scripts/store.gd` | Autoload `Store`: settings, files, tables (sizes, fonts, palettes, device themes, backgrounds), saving |
| `shaders/body.shader` | The device body: rounded, gradient-filled, with its drop shadow |
| `shaders/backdrop.shader` | Everything behind the device: gradients, patterns, generated patterns, your picture |
| `scripts/writer.gd` | The text: wrap, caret, selection, editing, undo; no drawing |
| `scripts/lcd.gd` | Draws the screen: logo, writer, menu rows, messages |
| `scripts/main.gd` | The device: keys row, power, menus, keyboard handling |
| `Main.tscn` | One Control node running `main.gd`; everything else is built in code |

Good first things to try: add a palette to `PALETTES` in `store.gd`, or a menu entry in
`control_items()` and `control_step()` in `main.gd`.

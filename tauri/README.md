# Plainwrite for desktop (Tauri 2)

The full Plainwrite web app in its own desktop window: every applet, game, language pack and easter
egg, with nothing rewritten. Tauri uses the web view already built into the operating system, so the
installer is a few MB instead of the 100+ MB an Electron app carries.

What the desktop shell adds:
- **The device in its own window.** By default there's no title bar and no background: just the
  device, with its shadow, sitting on your desktop. Drag it by its body. The corner buttons are
  **?** (help), **−** (minimise) and **✕** (close). The window follows the device's size, and grows
  downwards while a settings sheet is open. Control Panel → Device editor → **Window: Normal**
  brings back an ordinary resizable window with the app's own background.
- **Send → Type into another program** types the current file into whatever you click into: Word,
  Notepad, LibreOffice, a box on a web page, anything that takes typing. It's what a real Neo does
  when it's plugged in as a keyboard. Pick it, click where the text should go, and typing starts
  after a 5-second countdown. **Speed** (slow, normal or fast) is just below it in the Send menu.
  Press **Esc** anywhere to stop, or click back into Plainwrite. Programs with autocorrect or
  auto-indent (Word, for one) may change what arrives, just as they would with a real Neo.
  - **macOS** asks once to let Plainwrite control the keyboard (System Settings → Privacy &
    Security → Accessibility).
  - **Linux** types through X11 (libxdo). On Wayland it reaches programs running under XWayland;
    native Wayland programs may not receive it, and the Esc stop may only work from Plainwrite.
- **Send → Save as text file** opens the system Save dialog.
- **Full screen** makes the whole window full screen.
- Your writing is stored by the app itself (separately for the English and Multilingual editions),
  not in a browser profile, so clearing browser data can't erase it.

## Works on

| System | Needs |
|---|---|
| Windows 10 and 11 | Nothing extra; the WebView2 runtime is built in (the installer fetches it if missing) |
| macOS 10.15 Catalina and later | Nothing extra |
| Linux | WebKitGTK 4.1 (Ubuntu 22.04, Debian 12, Fedora 36, Linux Mint 21, Arch, openSUSE Tumbleweed and newer); X11 or Wayland |

Older systems such as Windows 7 or 8 can't run Tauri 2 apps. For those, use the web app in a browser,
or a native port.

### Linux notes

- **See-through window:** "Device only" needs a compositing desktop, which is every modern one
  (GNOME, KDE Plasma, Cinnamon, Xfce with compositing on, and anything on Wayland). Without a
  compositor the area around the device shows black; switch to **Window: Normal** then.
- **NVIDIA:** WebKitGTK's DMA-BUF renderer can give a blank window with NVIDIA's driver, so the app
  turns it off by itself when that driver is loaded. If you still see a blank window on other
  hardware, start it with `WEBKIT_DISABLE_DMABUF_RENDERER=1 plainwrite`.
- **Packages:** `.deb` (Debian, Ubuntu, Mint, Pop!_OS), `.rpm` (Fedora, openSUSE) and `.AppImage`
  (runs almost anywhere: `chmod +x Plainwrite*.AppImage` and open it).
- Your writing is kept in `~/.local/share/app.plainwrite.desktop/` (Multilingual:
  `app.plainwrite.desktop.multilingual`).
- Battery level isn't available to WebKitGTK, so the Battery screen says so.

## Build it

No Linux, Windows or Mac to build on? Run the **Build desktop apps** workflow from the repository's
Actions tab: it builds both editions for all three systems. The workflow lives at the repository root,
in `.github/workflows/build-desktop.yml`.


One-time setup:
1. Install **Rust**: https://rustup.rs
2. Install **Node.js** LTS: https://nodejs.org
3. System bits:
   - **Windows:** Microsoft C++ Build Tools ("Desktop development with C++").
   - **macOS:** `xcode-select --install`
   - **Linux (Debian/Ubuntu):**
     `sudo apt install libwebkit2gtk-4.1-dev build-essential curl wget file libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev`
4. In this folder: `npm install`

Then:

| Command | What it does |
|---|---|
| `npm run dev` | Runs the English edition in a window |
| `npm run dev:multilingual` | Runs the Multilingual edition |
| `npm run build` | Builds the English installer |
| `npm run build:multilingual` | Builds the Multilingual installer |

The first build compiles a lot and can take several minutes. After that, builds are quick.
Installers end up in `src-tauri/target/release/bundle/`:
- Windows: `.msi` and `-setup.exe`
- macOS: `.dmg` and `.app`
- Linux: `.deb`, `.rpm` and `.AppImage`

## Fonts offline

Every font is bundled inside `www/`, so the app needs no connection except to download spelling
dictionaries and, in the English edition, language packs.

## Layout

| Path | What it is |
|---|---|
| `www/en`, `www/multi` | The two editions of the web app, exactly as published |
| `src-tauri/src/lib.rs` | The window (frameless or normal), moving, minimising and closing it, the Save dialog and full screen, and the small script that links them to the web app |
| `src-tauri/src/main.rs` | Starts the app (and the Linux NVIDIA fix) |
| `src-tauri/tauri.conf.json` | Name, version, app id, icons (English edition) |
| `src-tauri/tauri.multilingual.conf.json` | What changes for the Multilingual edition |
| `src-tauri/icons/` | App icons for Windows, macOS and Linux |
| `../.github/workflows/build-desktop.yml` | Builds everything on GitHub (Linux, Windows, macOS), at the repository root |

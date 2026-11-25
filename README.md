# Plainwrite

Plainwrite is a retro minimalist-ish word processor inspired by "writer decks" or portable
dedicated word processors made between the 1980s and 2000s, like the AlphaSmart Neo and the
King Jim Pomera. It has eight auto-saving text buffers and works fully offline.

## AI disclosure

This application was written with the assistance of Claude, an artificial intelligence
large language model by Anthropic.
In other words, THIS IS VIBE CODED AI SLOP!!

## Versions

| Folder | Platform | Notes |
|---|---|---|
| [`pwa/english`](pwa/english) | Web app (PWA) | English only; language packs can be downloaded or imported |
| [`pwa/multilingual`](pwa/multilingual) | Web app (PWA) | Includes 48 language packs |
| [`android`](android) | Android (APK) | English and multilingual build variants |
| [`tauri`](tauri) | Desktop: Windows, Mac, Linux (Tauri 2) | English and multilingual editions |
| [`experimental/godot`](experimental/godot) | Godot 3.6 port | ⚠️ Experimental, core port only |

Each folder has its own README with build and install instructions.

## Try it or build it online

No tools needed: GitHub can do the building.

- **Web app:** published on GitHub Pages at
  [paluseata.github.io/plainwrite](https://paluseata.github.io/plainwrite/) by the
  **Publish web app** workflow, every time `pwa/` changes.
- **Desktop (Tauri):** Actions tab → **Build desktop apps** → **Run workflow**. Installers for
  Windows, macOS and Linux appear under the finished run's **Artifacts**.
- **Android:** Actions tab → **Build Android app** → **Run workflow**. Both APKs appear under the
  finished run's **Artifacts**.

Pushing a tag like `v1.0.4` runs both app builds at once.

## License

The code is under the [MIT License](LICENSE).

The bundled fonts keep their own licences, most of them the SIL Open Font License 1.1.
See the **Fonts** section of [`pwa/english/README.md`](pwa/english/README.md) for the full list.

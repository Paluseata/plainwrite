# Plainwrite for Android

A native Android app (APK) for Plainwrite: a full-screen WebView that runs the web app bundled inside the APK.
No browser, no service worker, no internet needed (after you bundle the fonts, step 2).

There are two build variants, like the web downloads:
- **english**: `app.plainwrite`, English only (language packs can still be imported)
- **multilingual**: `app.plainwrite.multilingual`, all 47 language packs; can be installed next to the English one

## Build it

1. **Open** this folder in Android Studio (Koala 2024.1 or newer). Let it sync: it downloads Gradle 8.7,
   the Android Gradle Plugin 8.5 and the AndroidX libraries. If it asks about a missing Gradle wrapper,
   accept its offer to create one, or run `gradle wrapper` once.
2. **Choose the edition**: View → Tool Windows → Build Variants → `englishDebug` or `multilingualDebug`.
3. **Run on the Tab S3**: Settings → About tablet → Software information → tap *Build number* 7 times,
   then Developer options → USB debugging on. Plug it in and press Run.
4. **Make an APK file**: Build → Build App Bundle(s) / APK(s) → Build APK(s).
   You'll find it in `app/build/outputs/apk/english/debug/` (or `multilingual/debug/`).
   For one you can share or keep long term, use Build → Generate Signed App Bundle / APK and create a keystore.
   Keep that keystore: updates must be signed with the same one.

No Android Studio? Run the **Build Android app** workflow from the repository's Actions tab. It builds
both editions as debug APKs on GitHub's machines and puts them under the run's Artifacts.
The workflow lives at the repository root, in `.github/workflows/build-android.yml`.

## What the app adds over the PWA

| | PWA in a browser | This app |
|---|---|---|
| Works offline | after the first visit | always, everything is inside the APK |
| Send → Save as text file | download / share sheet | Android's own Save dialog (Downloads, Drive, …) |
| Full screen | browser full screen | hides the status and navigation bars (swipe to peek) |
| Battery | Chromium browsers only | always, read from Android |
| Back button | leaves the page | works like Esc; in the writer it sends the app to the background |
| Keyboard cover | works | works; attaching/detaching it, rotating or split screen don't reload the page |
| Import font / language pack / key sound | file picker | Android file picker |

The page is served from `https://appassets.androidplatform.net/assets/www/` (androidx.webkit's
WebViewAssetLoader). That's a proper https origin, so your files, settings, imported fonts and language
packs are kept in the app's own storage and survive updates. They're separate from the browser PWA's storage:
to move writing across, use Send → Save as text file in one and paste it into the other.

## Updating the web part

The web app lives in `app/src/english/assets/www/` and `app/src/multilingual/assets/www/`. To update,
replace those folders with the contents of `pwa/english/` / `pwa/multilingual/` from the repo root,
and bump `versionCode` in `app/build.gradle.kts`.

The web app spots the Android shell by `window.PlainwriteAndroid` (see `MainActivity.kt`, class `Bridge`):
`saveText(name, text)`, `setFullscreen(on)`, `setFocus(on)` / `focusOn()` (focus mode: app pinning, hidden system bars,
screen kept on) and `battery()`. The Back button calls the page's `plainwriteBack()`, and `plainwriteFocus(on)` tells
the page when focus mode ends.

## Which devices it runs on (thrifted ones too)

The app installs on **Android 5.0 (2014) and newer** (minSdk 21). What really decides whether an old device
can run it is its web engine, the WebView: Plainwrite needs **Chromium 60 (2017) or newer**, and avoids newer
browser features or falls back when they're missing, so old engines get the same app.

| Android | Web engine it shipped with | Newest it can update to | Runs Plainwrite |
|---|---|---|---|
| 8.0, 8.1, 9 | Chromium 60–69 | current | yes, out of the box |
| 10 and newer | Chromium 77+ | current | yes |
| 7.0, 7.1 | Chromium 51–55 | 119 (update **Chrome**) | after one Play Store update |
| 6.0 | Chromium 44 | 106 (update **Android System WebView**) | after one Play Store update |
| 5.0, 5.1 | Chromium 37–39 | 95 (update **Android System WebView**) | after one Play Store update |
| 4.4 and older | Chromium 30–33, can't be updated | — | no (minSdk 21 keeps it off the list) |

If the engine is too old, the app says so and offers the Play Store page instead of showing a blank screen.
Devices without Google Play (some Fire, Huawei or de-Googled tablets) need a WebView or browser engine
from 2017 or later installed some other way.

## Requirements and notes

- Android 5.0 or newer with a Chromium 60+ WebView (see above). The Galaxy Tab S3 runs Android 9.
- Keep **Android System WebView** up to date from the Play Store; it's the engine the app runs on.
- Debug builds can be inspected from a computer's Chrome at `chrome://inspect`.
- Package name, app name and icon: `app/build.gradle.kts` (`applicationId`, `resValue app_name`) and
  `app/src/main/res/mipmap-*/ic_launcher.png`.
- I couldn't compile it where I wrote it (no Android SDK there), so the first Gradle sync is the real test.
  If a version clashes with your Android Studio, let it upgrade the Android Gradle Plugin when it offers.

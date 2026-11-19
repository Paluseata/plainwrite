// Plainwrite desktop: a window showing the web app, plus the things a browser can't do in a desktop
// app — saving a text file through the system Save dialog, real full screen, and a frameless,
// see-through window that is just the device sitting on your desktop (with ? − ✕ drawn by the app).
// The web app already looks for save/full screen on `window.PlainwriteAndroid` (the Android app
// provides the same object), and for the window controls on `window.PlainwriteDesktop`.

use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{Mutex, OnceLock};
use std::time::Duration;
use tauri_plugin_global_shortcut::{Code, GlobalShortcutExt, Modifiers, Shortcut, ShortcutState};
use tauri::{LogicalSize, Size, WebviewUrl, WebviewWindow, WebviewWindowBuilder};
use tauri_plugin_dialog::DialogExt;

const BRIDGE: &str = r#"
(function () {
  function invoke(cmd, args) { return window.__TAURI_INTERNALS__.invoke(cmd, args); }
  function saved(ok, name) { if (window.plainwriteSaved) window.plainwriteSaved(ok, name); }
  window.PlainwriteAndroid = window.PlainwriteDesktop = {
    saveText: function (name, text) {
      invoke('save_text', { name: name, text: text })
        .then(function (n) { saved(!!n, n || name); }, function () { saved(false); });
    },
    setFullscreen: function (on) { invoke('set_fullscreen', { on: !!on }); },
    // the device in its own window
    windowed: true,
    minimize: function () { invoke('win_minimize'); },
    close: function () { invoke('win_close'); },
    startDrag: function () { invoke('win_drag'); },
    fitWindow: function (w, h) { invoke('win_fit', { w: w, h: h }); },
    setFramed: function (on) { invoke('win_framed', { on: !!on }); },
    // Send → Type into another program
    typeText: function (text, cps) { return invoke('type_text', { text: text, cps: cps }); },
    typeStatus: function () { return invoke('type_status'); },
    typeStop: function () { return invoke('type_stop'); }
  };
})();
"#;

/// Asks where to save, then writes the text. Returns the file name, or nothing if cancelled.
#[tauri::command]
async fn save_text(app: tauri::AppHandle, name: String, text: String) -> Result<Option<String>, String> {
    let picked = app
        .dialog()
        .file()
        .set_file_name(&name)
        .add_filter("Text", &["txt"])
        .blocking_save_file();
    match picked {
        None => Ok(None),
        Some(p) => {
            let path = PathBuf::from(p.to_string());
            std::fs::write(&path, text).map_err(|e| e.to_string())?;
            Ok(path.file_name().map(|n| n.to_string_lossy().into_owned()))
        }
    }
}

#[tauri::command]
fn set_fullscreen(window: WebviewWindow, on: bool) -> Result<(), String> {
    window.set_fullscreen(on).map_err(|e| e.to_string())
}

#[tauri::command]
fn win_minimize(window: WebviewWindow) -> Result<(), String> {
    window.minimize().map_err(|e| e.to_string())
}

#[tauri::command]
fn win_close(window: WebviewWindow) -> Result<(), String> {
    window.close().map_err(|e| e.to_string())
}

/// Starts moving the window with the mouse (the web app calls this on a press on the device body).
#[tauri::command]
fn win_drag(window: WebviewWindow) -> Result<(), String> {
    window.start_dragging().map_err(|e| e.to_string())
}

/// Makes the window exactly as big as the device (plus room for its shadow), in CSS pixels.
#[tauri::command]
fn win_fit(window: WebviewWindow, w: f64, h: f64) -> Result<(), String> {
    if window.is_fullscreen().unwrap_or(false) {
        return Ok(());
    }
    let w = w.clamp(200.0, 4000.0);
    let h = h.clamp(150.0, 4000.0);
    window.set_size(LogicalSize::new(w, h)).map_err(|e| e.to_string())
}

/// Window: Normal (title bar, resizable, the app's own background) or Device only (frameless, see-through).
#[tauri::command]
fn win_framed(window: WebviewWindow, on: bool) -> Result<(), String> {
    let e = |e: tauri::Error| e.to_string();
    window.set_decorations(on).map_err(e)?;
    window.set_resizable(on).map_err(e)?;
    let _ = window.set_shadow(on);
    if on {
        window.set_min_size(Some(LogicalSize::new(420.0, 320.0))).map_err(e)?;
        window.set_size(LogicalSize::new(900.0, 560.0)).map_err(e)?;
        let _ = window.center();
    } else {
        window.set_min_size(None::<Size>).map_err(e)?;
    }
    Ok(())
}

// ---------- Send → Type into another program ----------
// Types the file into whichever program has the keyboard, one character at a time, like a real Neo
// plugged in as a keyboard. Esc (anywhere, while it types) or coming back to Plainwrite stops it.

struct Typing {
    running: AtomicBool,
    stop: AtomicBool,
    sent: AtomicUsize,
    total: AtomicUsize,
    error: Mutex<Option<String>>,
}

fn typing() -> &'static Typing {
    static T: OnceLock<Typing> = OnceLock::new();
    T.get_or_init(|| Typing {
        running: AtomicBool::new(false),
        stop: AtomicBool::new(false),
        sent: AtomicUsize::new(0),
        total: AtomicUsize::new(0),
        error: Mutex::new(None),
    })
}

fn esc() -> Shortcut {
    Shortcut::new(None, Code::Escape)
}

fn type_all(text: &str, cps: f64) -> Result<(), String> {
    use enigo::{Direction, Enigo, Key, Keyboard, Settings};
    let t = typing();
    let mut kb = Enigo::new(&Settings::default()).map_err(|e| e.to_string())?;
    let pause = Duration::from_secs_f64(1.0 / cps.clamp(5.0, 500.0));
    let mut buf = [0u8; 4];
    for ch in text.chars() {
        if t.stop.load(Ordering::SeqCst) {
            break;
        }
        match ch {
            '\r' => {}
            '\n' => kb.key(Key::Return, Direction::Click).map_err(|e| e.to_string())?,
            '\t' => kb.key(Key::Tab, Direction::Click).map_err(|e| e.to_string())?,
            c => kb.text(c.encode_utf8(&mut buf)).map_err(|e| e.to_string())?,
        }
        t.sent.fetch_add(1, Ordering::SeqCst);
        std::thread::sleep(pause);
    }
    Ok(())
}

#[tauri::command]
fn type_text(app: tauri::AppHandle, text: String, cps: f64) -> Result<(), String> {
    let t = typing();
    if t.running.swap(true, Ordering::SeqCst) {
        return Err("already typing".into());
    }
    t.stop.store(false, Ordering::SeqCst);
    t.sent.store(0, Ordering::SeqCst);
    t.total.store(text.chars().count(), Ordering::SeqCst);
    *t.error.lock().unwrap() = None;
    let _ = app.global_shortcut().register(esc());
    std::thread::spawn(move || {
        if let Err(e) = type_all(&text, cps) {
            *typing().error.lock().unwrap() = Some(e);
        }
        let _ = app.global_shortcut().unregister(esc());
        typing().running.store(false, Ordering::SeqCst);
    });
    Ok(())
}

#[derive(serde::Serialize)]
struct TypeStatus {
    running: bool,
    sent: usize,
    total: usize,
    error: Option<String>,
}

#[tauri::command]
fn type_status() -> TypeStatus {
    let t = typing();
    TypeStatus {
        running: t.running.load(Ordering::SeqCst),
        sent: t.sent.load(Ordering::SeqCst),
        total: t.total.load(Ordering::SeqCst),
        error: t.error.lock().unwrap().clone(),
    }
}

#[tauri::command]
fn type_stop() {
    typing().stop.store(true, Ordering::SeqCst);
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(
            tauri_plugin_global_shortcut::Builder::new()
                .with_handler(|_app, shortcut, event| {
                    if event.state() == ShortcutState::Pressed && shortcut.matches(Modifiers::empty(), Code::Escape) {
                        typing().stop.store(true, Ordering::SeqCst);
                    }
                })
                .build(),
        )
        .invoke_handler(tauri::generate_handler![
            save_text,
            set_fullscreen,
            win_minimize,
            win_close,
            win_drag,
            win_fit,
            win_framed,
            type_text,
            type_status,
            type_stop
        ])
        .setup(|app| {
            WebviewWindowBuilder::new(app, "main", WebviewUrl::App("index.html".into()))
                .title("Plainwrite")
                // starts as "Device only": no title bar, see-through, sized to the device by the app
                .inner_size(760.0, 430.0)
                .decorations(false)
                .transparent(true)
                .shadow(false)
                .resizable(false)
                .center()
                .initialization_script(BRIDGE)
                .build()?;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running Plainwrite");
}

extends Node
# Settings, the eight files, and the fixed tables (text sizes, fonts, screen palettes).
# Everything is kept in user://plainwrite.json, written a quarter of a second after the last change.

const VERSION = "Godot port 1.08"
const SAVE_PATH = "user://plainwrite.json"

# Text sizes: how many lines fit on the screen, and roughly how many characters across.
const SIZES = [
	{"name": "Large", "lines": 4, "cols": 26},
	{"name": "Medium", "lines": 5, "cols": 33},
	{"name": "Standard", "lines": 6, "cols": 40},
	{"name": "Small", "lines": 8, "cols": 48},
	{"name": "Smaller", "lines": 10, "cols": 56},
	{"name": "Tiny", "lines": 12, "cols": 64},
]

# Pixel fonts. Most are drawn on a grid of 10 pixel rows per em (100 font units per pixel), so scaling
# the em to a multiple of 10 screen pixels keeps every pixel square and sharp. Pixel gothic (from
# DotGothic16, with half-width Cyrillic) uses a 16-pixel grid: "grid", "line" and "cw" (a typical
# letter's width) are in font pixels.
const FACES = [
	{"name": "Plain Sans", "path": "res://fonts/plain-sans.ttf"},
	{"name": "Pixel Gothic", "path": "res://fonts/pixel-gothic.ttf", "grid": 16, "line": 17, "cw": 8},
	{"name": "Home Computer", "path": "res://fonts/home-computer.ttf"},
	{"name": "Home Computer Thin", "path": "res://fonts/home-computer-thin.ttf"},
	{"name": "Teletext", "path": "res://fonts/bedstead.otf"},
]
const GRID = 10        # font pixels per em
const LINE = 11        # font pixels per line (one row of space between lines)

# Screen palettes. LCD ones have a light and a dark (inverted) look; classic computer screens have one
# look, a border colour, and can suggest their own font (see Store.set_palette).
const PALETTES = [
	{"name": "Classic LCD", "light": ["#b3bca3", "#8a927d", "#1b2317"], "dark": ["#10150e", "#090c08", "#a3d48c"]},
	{"name": "Amber", "light": ["#f2a227", "#9c6510", "#120a00"], "dark": ["#130b00", "#090500", "#ffb000"]},
	{"name": "Paper", "light": ["#e8e5da", "#a6a399", "#141414"], "dark": ["#0f1011", "#08090a", "#e2e2dc"]},
	{"name": "Pink", "light": ["#f7cfde", "#c99aab", "#3d0b22"], "dark": ["#1e0812", "#10040a", "#ff9cc8"]},
	{"name": "Creamed spinach", "light": ["#efe8cf", "#b9b296", "#2d5a22"], "dark": ["#15240f", "#0b1408", "#e8dfbf"]},
	{"name": "Black & white", "light": ["#ffffff", "#b9b9b9", "#000000"], "dark": ["#000000", "#000000", "#ffffff"]},
	{"name": "C64", "classic": ["#352879", "#6c5eb5", "#6c5eb5"], "font": "Home Computer"},
	{"name": "Atari 8-bit", "classic": ["#1c4f9c", "#000000", "#8fb8f2"], "font": "Home Computer"},
	{"name": "MSX", "classic": ["#5455ed", "#5455ed", "#ffffff"], "font": "Home Computer Thin"},
	{"name": "ZX Spectrum", "classic": ["#d7d7d7", "#d7d7d7", "#000000"], "font": "Home Computer Thin"},
	{"name": "Apple II", "classic": ["#050805", "#050805", "#33ff66"], "font": "Home Computer"},
	# media-player displays, chosen along with the Amp device themes
	{"name": "Amp classic", "classic": ["#000000", "#14141c", "#00e600"]},
	{"name": "Amp modern", "classic": ["#3d62b3", "#1c2b66", "#ffffff"]},
	{"name": "Amp bento", "classic": ["#0e0e0e", "#0c0c0c", "#ffa630"]},
	{"name": "Amp chrome", "classic": ["#05080c", "#20252c", "#bcd2ec"]},
	{"name": "Amp neon", "classic": ["#0b0414", "#05010a", "#ff6fe0"]},
	{"name": "Slate blue", "classic": ["#07111c", "#0d1826", "#8fd3ff"]},
	{"name": "Slate purple", "classic": ["#0f0818", "#170f24", "#cfb2ff"]},
	{"name": "Workbench", "classic": ["#0055aa", "#0055aa", "#ffffff"]},
]

const DEVICES = [
	{"name": "Charcoal", "body": ["#30353d", "#1e2227"], "angle": 170, "keys": ["#4a515b", "#383d45"], "kt": "#e6e8eb", "page": "#121417"},
	{"name": "Retro beige", "body": ["#ddd6c4", "#c2b9a3"], "angle": 170, "keys": ["#f3eee1", "#dad2bf"], "kt": "#3a352b", "page": "#2a2925"},
	{"name": "Snow", "body": ["#f5f6f8", "#dde1e6"], "angle": 170, "keys": ["#ffffff", "#e8ebef"], "kt": "#2a2f36", "page": "#16181b"},
	{"name": "Jet black", "body": ["#1b1b1c", "#060606"], "angle": 170, "keys": ["#2b2b2d", "#1c1c1e"], "kt": "#f0f0f0", "page": "#000000"},
	{"name": "Ocean", "body": ["#2d6293", "#1a3c5d"], "angle": 170, "keys": ["#3c72a3", "#2a5682"], "kt": "#eef6ff", "page": "#0a1520"},
	{"name": "Kiwi", "body": ["#a4d163", "#6c9e37"], "angle": 170, "keys": ["#eef7df", "#d1e5b3"], "kt": "#2a3a14", "page": "#141c0b"},
	{"name": "Ruby", "body": ["#ab3740", "#6c1d24"], "angle": 170, "keys": ["#c44a53", "#9a343c"], "kt": "#fff4f5", "page": "#16070a"},
	{"name": "Pink", "body": ["#f6b3cd", "#e284aa"], "angle": 170, "keys": ["#fff1f7", "#fbd4e5"], "kt": "#5c1a37", "page": "#2a1019"},
	{"name": "Yellow", "body": ["#f6d24a", "#d9ad1f"], "angle": 170, "keys": ["#fff6cc", "#f3e29a"], "kt": "#4a3800", "page": "#1f1a08"},
	{"name": "Purple", "body": ["#7b4fb8", "#4e2c80"], "angle": 170, "keys": ["#8d62c8", "#6c43a6"], "kt": "#f7f1ff", "page": "#120a1e"},
	{"name": "Pastel mint", "body": ["#bfe8d6", "#9fd3bd"], "angle": 170, "keys": ["#f2fbf7", "#d9f1e6"], "kt": "#2c5446", "page": "#1a2420"},
	{"name": "Pastel lavender", "body": ["#d9cff3", "#bfb1e6"], "angle": 170, "keys": ["#f7f3ff", "#e4dcf8"], "kt": "#3f3363", "page": "#1c1726"},
	{"name": "Pastel peach", "body": ["#ffd3b8", "#f6b694"], "angle": 170, "keys": ["#fff4ec", "#ffe0cc"], "kt": "#5e3420", "page": "#261a14"},
	{"name": "Pastel blue", "body": ["#c4ddf6", "#a4c6ea"], "angle": 170, "keys": ["#f3f8fe", "#dbe9f9"], "kt": "#253f5e", "page": "#141c26"},
	{"name": "Pastel lemon", "body": ["#fbefb5", "#f0dc8d"], "angle": 170, "keys": ["#fffcec", "#fbf1c4"], "kt": "#574814", "page": "#221e10"},
	{"name": "Pastel pink", "body": ["#fbd5e0", "#f2b8ca"], "angle": 170, "keys": ["#fff5f8", "#fde0e9"], "kt": "#5c2a3b", "page": "#24161b"},
	{"name": "Pastel lilac", "body": ["#ead0ef", "#d7b3df"], "angle": 170, "keys": ["#fdf5fe", "#f1def5"], "kt": "#4e2a57", "page": "#211624"},
	{"name": "Sunset", "body": ["#ff9a5a", "#ff5e7e", "#7b3fa0"], "angle": 160, "keys": ["#ffe2cf", "#ffb8a8"], "kt": "#5a1f2c", "page": "#1d0b16"},
	{"name": "Aurora", "body": ["#14d6a8", "#2b8be0", "#7a3bd1"], "angle": 160, "keys": ["#d4fbf1", "#a9d9f5"], "kt": "#123a4a", "page": "#0a1220"},
	{"name": "Vaporwave", "body": ["#ff71ce", "#b967ff", "#01cdfe"], "angle": 165, "keys": ["#ffe3f6", "#d9cbff"], "kt": "#3b1458", "page": "#150a22"},
	{"name": "Cotton candy", "body": ["#ffc8e4", "#d7c8ff", "#bfe6ff"], "angle": 160, "keys": ["#fff8fc", "#e9e4ff"], "kt": "#4a2f63", "page": "#1d1826"},
	{"name": "Lagoon", "body": ["#5ee7df", "#3a8fd6", "#1f3c88"], "angle": 165, "keys": ["#e0fbf8", "#b7dcf5"], "kt": "#11324e", "page": "#081226"},
	{"name": "Ember", "body": ["#f9d423", "#ff4e50", "#5c1a2b"], "angle": 165, "keys": ["#fff3c4", "#ffc0b0"], "kt": "#4a1414", "page": "#18070a"},
	{"name": "Pastel rainbow", "body": ["#ffd6d6", "#fff3c4", "#c9f2d9"], "angle": 150, "keys": ["#fdfcff", "#eaf1ff"], "kt": "#3d3a4f", "page": "#1b1a22"},
	# media-player looks: each switches to its own screen ("pal")
	{"name": "Amp classic", "body": ["#4d4d66", "#2c2c3e", "#22222e"], "angle": 180, "keys": ["#c9c9d3", "#8e8e9c"], "kt": "#1a1a22", "page": "#14141c", "pal": "Amp classic"},
	{"name": "Amp modern", "body": ["#ececec", "#c8c8c8", "#a7a7a7"], "angle": 180, "keys": ["#f4f4f4", "#c2c4c8"], "kt": "#1d2433", "page": "#1b1f26", "pal": "Amp modern", "files": ["#56678c", "#2c3858"], "ft": "#ffffff"},
	{"name": "Amp bento", "body": ["#3d3d3d", "#252525", "#1a1a1a"], "angle": 180, "keys": ["#4a4a4a", "#333333"], "kt": "#ececec", "page": "#101010", "pal": "Amp bento"},
	{"name": "Amp chrome", "body": ["#e4e8ee", "#a9b0ba", "#8a919c"], "angle": 180, "keys": ["#f4f6f9", "#c3c9d1"], "kt": "#1e2530", "page": "#1a1d22", "pal": "Amp chrome"},
	{"name": "Amp neon", "body": ["#2c1048", "#170829", "#0d0418"], "angle": 160, "keys": ["#3d1b61", "#27103f"], "kt": "#ff8ae4", "page": "#0a0312", "pal": "Amp neon"},
	{"name": "Slate blue", "body": ["#6d87a8", "#3d5677", "#2b3f5a"], "angle": 180, "keys": ["#b4c7de", "#7f97b6"], "kt": "#10233a", "page": "#0f1825", "pal": "Slate blue"},
	{"name": "Slate purple", "body": ["#8f7bad", "#5c4879", "#41305c"], "angle": 180, "keys": ["#cdc1e2", "#9b88ba"], "kt": "#21163a", "page": "#140e1d", "pal": "Slate purple"},
	{"name": "Sakura", "body": ["#ffe4ec", "#f7c6d6", "#eaa9c0"], "angle": 165, "keys": ["#fff6f9", "#fbdde7"], "kt": "#6b2f45", "page": "#2a161d", "pal": "Pink", "files": ["#f6c3d4", "#eba5bd"], "ft": "#4f1c30"},
	{"name": "Matcha", "body": ["#c8d8a4", "#a4bd78", "#839f58"], "angle": 165, "keys": ["#f6f3e4", "#e2dcc2"], "kt": "#3c4a22", "page": "#171c10", "pal": "Creamed spinach", "files": ["#a9c07c", "#8ea763"], "ft": "#1f2a10"},
	{"name": "Workbench", "body": ["#e6dfce", "#d3cbb7", "#c2b9a3"], "angle": 170, "keys": ["#f1ecdf", "#d8d1bf"], "kt": "#2a2a2a", "page": "#0055aa", "pal": "Workbench", "files": ["#d9d1bd", "#bfb6a0"], "ft": "#2a2a2a"},
]

# Background (Device editor). Gradient presets have three colours; schemes are background + pattern colour.
const BG_KINDS = ["Plain", "Gradient", "Pattern", "Generated", "Picture"]
const BG_GRADS = [
	["Sunset", "#ff7e5f", "#feb47b", "#6a3093"], ["Aurora", "#00c9a7", "#2e86de", "#6c3483"],
	["Vaporwave", "#ff71ce", "#b967ff", "#01cdfe"], ["Peach", "#ffecd2", "#fcb69f", "#ff9a9e"],
	["Mint", "#d4fc79", "#96e6a1", "#5bc0be"], ["Candy", "#fbc2eb", "#a6c1ee", "#c2e9fb"],
	["Pastel", "#ffd6e0", "#fff1c1", "#c9f0e4"], ["Dusk", "#2c3e50", "#4ca1af", "#c4e0e5"],
	["Night", "#0f2027", "#203a43", "#2c5364"], ["Ember", "#200122", "#6f0000", "#e65c00"],
	["Lagoon", "#43cea2", "#185a9d", "#0b2545"], ["Mono", "#3a3f46", "#1b1e22", "#0b0c0e"],
]
const BG_SCHEMES = [
	["Slate", "#16191d", "#3a414b"], ["C64", "#352879", "#6c5eb5"], ["Amber", "#120a00", "#ff9a00"],
	["Mint", "#1a2420", "#9fd3bd"], ["Rose", "#24161b", "#f2b8ca"], ["Ocean", "#0a1520", "#3fa7d6"],
	["Paper", "#e8e5da", "#b9b49f"], ["Lavender", "#d9cff3", "#9d8fcb"], ["Peach", "#ffe0cc", "#f6a57a"],
	["Night sky", "#05060a", "#ffffff"], ["Vaporwave", "#1a0b2e", "#ff71ce"], ["Forest", "#14231a", "#5f9a5a"],
]
const BG_SHAPES = ["Straight", "Round", "Sweep"]
const BG_PATTERNS = ["Dots", "Grid", "Stripes", "Diagonal", "Checker", "Zigzag", "Waves", "Diamonds",
	"Plus", "Bricks", "Rings", "Triangles", "Crosses"]
const BG_STYLES = ["Static", "Plasma", "Starfield", "10 PRINT maze", "Truchet", "Dither", "Topography", "Cells"]
const BG_FITS = ["Fill the window", "Fit inside", "Stretch", "Centre", "Tile"]
const WALLPAPER = "user://wallpaper"     # your picture is copied here (the extension is kept in S.bg_pic)

# Power key colour: Auto adapts to the keys, or one of these, used as it is
const PWR_PRESETS = [["auto", "Auto"], ["#3fd35a", "Green"], ["#ff4d4d", "Red"], ["#ffb020", "Amber"],
	["#4da3ff", "Blue"], ["#ffffff", "White"], ["#ff7ad9", "Pink"]]

# Screen border (Device editor): off by default, like the web app; these are its colours
const BORDER_COLS = [["Dark", "#0e1013"], ["Black", "#000000"], ["Graphite", "#3a3d42"], ["Silver", "#c9ccd1"],
	["Navy", "#1c2b66"], ["Beige", "#cfc6b0"], ["Wine", "#4a1a2a"], ["Forest", "#1d3324"]]

const CURSORS = ["block", "line", "under"]
const CURSOR_NAMES = {"block": "Full block", "line": "Tall line", "under": "Underscore"}
const AUTO_OFF = [0, 2, 5, 10, 30, 60]     # minutes; 0 = never

var S = {}                 # the saved state
var _save_timer: Timer
var _fonts = {}            # "face|size" -> DynamicFont

signal changed               # settings that affect the look changed


func _ready() -> void:
	_save_timer = Timer.new()
	_save_timer.one_shot = true
	_save_timer.wait_time = 0.25
	add_child(_save_timer)
	_save_timer.connect("timeout", self, "_write")
	load_state()


func defaults() -> Dictionary:
	var files = []
	for i in range(8):
		files.append({"text": "", "cur": 0})
	return {
		"text_size": 0, "face": "Plain Sans", "palette": 0, "dark": false,
		"cursor": "line", "blink": true, "sel_gap": true, "auto_off": 10,
		"sound": false, "fill": false, "active": 0, "files": files,
		"device": "Charcoal", "shadow": 1.0,
		"bg_kind": 0, "bg_grad": 0, "bg_scheme": 0, "bg_shape": 0, "bg_angle": 160, "bg_pattern": 0,
		"bg_style": 1, "bg_size": 1.0, "bg_pixel": 3, "bg_seed": 1, "bg_dim": 0, "bg_pic": "", "bg_fit": 0,
		"bg_pic_scale": 100, "bg_sharp": false, "pwr": "auto", "bg_pix": false, "bg_pix_size": 4, "bg_dither": false,
		"screen_border": false, "border_col": 0,
	}


func load_state() -> void:
	S = defaults()
	var f = File.new()
	if not f.file_exists(SAVE_PATH):
		return
	if f.open(SAVE_PATH, File.READ) != OK:
		return
	var data = parse_json(f.get_as_text())
	f.close()
	if typeof(data) != TYPE_DICTIONARY:
		return
	for k in data.keys():
		if S.has(k):
			S[k] = data[k]
	# JSON numbers come back as floats
	for k in ["text_size", "palette", "auto_off", "active", "bg_kind", "bg_grad", "bg_scheme", "bg_shape",
			"bg_angle", "bg_pattern", "bg_style", "bg_pixel", "bg_seed", "bg_dim", "bg_fit", "bg_pic_scale", "bg_pix_size", "border_col"]:
		S[k] = int(S[k])
	S.text_size = int(clamp(S.text_size, 0, SIZES.size() - 1))
	S.palette = int(clamp(S.palette, 0, PALETTES.size() - 1))
	S.active = int(clamp(S.active, 0, 7))
	if not CURSORS.has(S.cursor):
		S.cursor = "line"
	while S.files.size() < 8:
		S.files.append({"text": "", "cur": 0})
	for fl in S.files:
		fl.cur = int(fl.get("cur", 0))


func save() -> void:
	_save_timer.start()


func _write() -> void:
	var f = File.new()
	if f.open(SAVE_PATH, File.WRITE) == OK:
		f.store_string(to_json(S))
		f.close()


func factory_reset() -> void:
	S = defaults()
	var dir = Directory.new()
	for ext in ["png", "jpg", "jpeg", "webp", "bmp", "tga"]:
		if dir.file_exists(WALLPAPER + "." + ext):
			dir.remove(WALLPAPER + "." + ext)
	_write()
	emit_signal("changed")


# ---------- look ----------

func palette() -> Dictionary:
	return PALETTES[S.palette]


# [screen background, unlit/border colour, ink]
func colors() -> Array:
	var p: Dictionary = palette()
	var c: Array = p.classic if p.has("classic") else (p.dark if S.dark else p.light)
	return [Color(c[0]), Color(c[1]), Color(c[2])]


# Classic screens switch to their own font as a suggestion: pick another font while on one and yours
# stays; going back to an ordinary screen puts back the font you had before.
func set_palette(i: int) -> void:
	var prev: Dictionary = palette()
	S.palette = (i + PALETTES.size()) % PALETTES.size()
	var p: Dictionary = palette()
	var from_palette: bool = prev.has("font") and S.face == prev.font
	if p.has("font"):
		if not prev.has("font"):
			S["face_before_classic"] = S.face
		if not prev.has("font") or from_palette:
			S.face = p.font
	elif prev.has("font") and S.has("face_before_classic"):
		if from_palette:
			S.face = S.face_before_classic
		S.erase("face_before_classic")
	save()
	emit_signal("changed")


func device() -> Dictionary:
	for d in DEVICES:
		if d.name == S.device:
			return d
	return DEVICES[0]


func palette_index(name: String) -> int:
	for i in PALETTES.size():
		if PALETTES[i].name == name:
			return i
	return -1


# A device theme with its own screen switches the screen too; pick another screen while on it and yours
# stays; leaving for a theme without one puts back the screen you had.
func set_device(name: String) -> void:
	var prev: Dictionary = device()
	S.device = name
	var cur: Dictionary = device()
	var from_theme: bool = prev.has("pal") and palette().name == prev.pal
	if cur.has("pal"):
		if not prev.has("pal"):
			S["pal_before_device"] = S.palette
		if not prev.has("pal") or from_theme:
			var j = palette_index(cur.pal)
			if j >= 0 and j != S.palette:
				set_palette(j)
	elif prev.has("pal") and S.has("pal_before_device"):
		if from_theme:
			set_palette(int(S.pal_before_device))
		S.erase("pal_before_device")


func device_index() -> int:
	for i in DEVICES.size():
		if DEVICES[i].name == S.device:
			return i
	return 0


func face_grid() -> int:
	return int(FACES[face_index()].get("grid", GRID))


func face_line() -> int:
	return int(FACES[face_index()].get("line", LINE))


func face_cw() -> float:
	return float(FACES[face_index()].get("cw", 6))


func face_index() -> int:
	for i in FACES.size():
		if FACES[i].name.to_lower() == str(S.face).to_lower():   # older saves wrote "Plain sans"
			return i
	return 0


func font(px_per_dot: int) -> DynamicFont:
	var face: Dictionary = FACES[face_index()]
	var size: int = int(face.get("grid", GRID)) * int(max(1, px_per_dot))
	var key: String = "%s|%d" % [face.name, size]
	if _fonts.has(key):
		return _fonts[key]
	var data: DynamicFontData = load(face.path)
	data.antialiased = false
	data.hinting = DynamicFontData.HINTING_NONE
	var df = DynamicFont.new()
	df.font_data = data
	df.size = size
	df.use_filter = false
	df.use_mipmaps = false
	_fonts[key] = df
	return df


# ---------- files ----------

func file() -> Dictionary:
	return S.files[S.active]

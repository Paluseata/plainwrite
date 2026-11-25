extends Control
# The device: body, screen, the row of keys (on/off, file 1–8, applets, clear file), power and auto off,
# the menus (Applets, Control Panel, About, yes/no questions) and all keyboard handling.
#
# Keys: F1–F8 or Alt+1–8 switch file · F9 applets · F10 on/off · Esc or Backspace back out of menus
#       Insert types over text · Ctrl+Z / Ctrl+Y undo / redo · Ctrl+A/C/X/V as usual

const Writer = preload("res://scripts/writer.gd")
const LCD = preload("res://scripts/lcd.gd")

var writer = Writer.new()
var lcd: Control
var keys: HBoxContainer
var file_buttons := []
var desk_color = Color("#121417")     # around the device, before the backdrop draws
var backdrop: ColorRect               # what's behind the device (shaders/backdrop.shader)
var body: ColorRect                   # the device body and its shadow (shaders/body.shader)
var frame: Panel                      # the screen border, when it's on
var key_buttons := []
var pic_dialog: FileDialog
var pic_key = ""                      # which picture is loaded into the backdrop
var kfont: DynamicFont
var body_rect = Rect2()

var mode = "off"            # off | logo | word | applets | control | about | ask
var menu_sel = 0
var ask = {}                # the yes/no question being asked: {"title", "lines", "yes": funcref}
var powering_off = false    # the logo before an automatic power off
var last_activity = 0
var msg_until = 0
var click: AudioStreamPlayer


func _ready() -> void:
	VisualServer.set_default_clear_color(desk_color)
	randomize()
	_build_backdrop()
	lcd = LCD.new()
	lcd.mouse_filter = Control.MOUSE_FILTER_IGNORE   # taps go to the device (for the on-screen keyboard)
	lcd.writer = writer
	add_child(lcd)
	_build_keys()
	_build_click()
	var t = Timer.new()
	t.wait_time = 0.53
	t.autostart = true
	add_child(t)
	t.connect("timeout", self, "_tick")
	connect("resized", self, "_layout")
	_apply_look()
	Store.connect("changed", self, "_restyle")
	_layout()
	power_on()


# ---------- layout ----------

# The device is sized from the display's real size, not the window: its screen is about 6 inches
# across (a bit bigger than a real Neo's), so text looks about the same size on a laptop, a desktop
# monitor or a tablet. On small screens it simply uses the full width. Control Panel → Screen size:
# Fill window brings back a screen that grows with the window.
func _layout() -> void:
	var dpi = float(OS.get_screen_dpi())
	if dpi < 50:
		dpi = 96.0
	var m = clamp(dpi * 0.12, 8, 24)                  # margins and gaps
	var keys_h = clamp(dpi * 0.32, 34, 90)            # about a third of an inch
	var avail = rect_size - Vector2(m * 4, m * 5 + keys_h)
	var w: float
	var h: float
	if Store.S.get("fill", false):
		w = avail.x
		h = avail.y
	else:
		w = min(avail.x, dpi * 6.0)
		h = min(avail.y, w * 0.24)                     # the Neo's wide screen (about 4.7:1)
	var total_h = h + m + keys_h
	var x0 = (rect_size.x - w) / 2.0
	var y0 = (rect_size.y - total_h) / 2.0
	lcd.rect_position = Vector2(x0, y0)
	lcd.rect_size = Vector2(w, h)
	keys.rect_position = Vector2(x0, y0 + h + m)
	keys.rect_size = Vector2(w, keys_h)
	body_rect = Rect2(x0 - m, y0 - m, w + m * 2, total_h + m * 2)
	var pad = m * 0.6                                 # the border sits in the margin round the screen
	frame.rect_position = Vector2(x0 - pad, y0 - pad)
	frame.rect_size = Vector2(w + pad * 2, h + pad * 2)
	_place_backdrop()
	if kfont:
		kfont.size = int(clamp(keys_h * 0.36, 11, 30))
		_power_light()
	update()


# ---------- device look and background ----------

func _build_backdrop() -> void:
	backdrop = ColorRect.new()
	backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	backdrop.set_anchors_preset(Control.PRESET_WIDE)
	var bm = ShaderMaterial.new()
	bm.shader = load("res://shaders/backdrop.shader")
	backdrop.material = bm
	add_child(backdrop)
	body = ColorRect.new()
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var dm = ShaderMaterial.new()
	dm.shader = load("res://shaders/body.shader")
	body.material = dm
	add_child(body)
	frame = Panel.new()
	frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(frame)


const SHADOW_ROOM = 170.0     # room around the body for the biggest shadow


func _place_backdrop() -> void:
	backdrop.rect_position = Vector2.ZERO
	backdrop.rect_size = rect_size
	backdrop.material.set_shader_param("size", rect_size)
	body.rect_position = body_rect.position - Vector2(SHADOW_ROOM, SHADOW_ROOM)
	body.rect_size = body_rect.size + Vector2(SHADOW_ROOM * 2, SHADOW_ROOM * 2)
	var m: ShaderMaterial = body.material
	m.set_shader_param("size", body.rect_size)
	m.set_shader_param("box_pos", Vector2(SHADOW_ROOM, SHADOW_ROOM))
	m.set_shader_param("box_size", body_rect.size)
	m.set_shader_param("radius", float(int(body_rect.size.y * 0.06) + 6))


func _apply_look() -> void:
	var S = Store.S
	var dv: Dictionary = Store.device()
	var cols: Array = dv.body
	var m: ShaderMaterial = body.material
	m.set_shader_param("c1", Color(cols[0]))
	m.set_shader_param("c2", Color(cols[1]))
	m.set_shader_param("c3", Color(cols[cols.size() - 1]))
	m.set_shader_param("three", 1.0 if cols.size() > 2 else 0.0)
	m.set_shader_param("angle", deg2rad(float(dv.angle)))
	m.set_shader_param("shadow", float(S.shadow))
	var b: ShaderMaterial = backdrop.material
	var k = int(S.bg_kind)
	if k == 4 and S.bg_pic == "":
		k = 0                      # no picture chosen yet
	b.set_shader_param("kind", k)
	b.set_shader_param("dim", float(S.bg_dim) / 100.0 if k != 0 else 0.0)
	b.set_shader_param("pix", float(S.bg_pix_size) if S.bg_pix and k != 0 else 0.0)
	b.set_shader_param("dither", 1.0 if S.bg_dither else 0.0)
	desk_color = Color(dv.page)
	b.set_shader_param("c1", desk_color)
	if k == 1:
		var g: Array = Store.BG_GRADS[int(S.bg_grad)]
		b.set_shader_param("c1", Color(g[1]))
		b.set_shader_param("c2", Color(g[2]))
		b.set_shader_param("c3", Color(g[3]))
		b.set_shader_param("three", 1.0)
		b.set_shader_param("sub", int(S.bg_shape))
		b.set_shader_param("angle", deg2rad(float(S.bg_angle)))
		desk_color = Color(g[2])
	elif k == 2 or k == 3:
		var sc: Array = Store.BG_SCHEMES[int(S.bg_scheme)]
		b.set_shader_param("c1", Color(sc[1]))
		b.set_shader_param("c2", Color(sc[2]))
		b.set_shader_param("sub", int(S.bg_pattern) if k == 2 else int(S.bg_style))
		b.set_shader_param("scale", float(S.bg_size) if k == 2 else float(S.bg_pixel))
		b.set_shader_param("seed", float(S.bg_seed))
		desk_color = Color(sc[1])
	elif k == 4:
		var key = "%s|%s" % [S.bg_pic, S.bg_pix]
		if key != pic_key:
			pic_key = key
			var img = Image.new()
			if img.load(S.bg_pic) == OK:
				var t = ImageTexture.new()
				t.create_from_image(img, 0 if S.bg_pix else Texture.FLAG_FILTER)
				b.set_shader_param("pic", t)
				b.set_shader_param("pic_size", img.get_size())
		b.set_shader_param("fit", int(S.bg_fit))
		b.set_shader_param("pic_scale", float(S.bg_pic_scale) / 100.0)
		desk_color = Color(0, 0, 0)
	VisualServer.set_default_clear_color(desk_color)
	frame.visible = bool(S.get("screen_border", false))
	var fs = StyleBoxFlat.new()
	fs.bg_color = Color(Store.BORDER_COLS[int(S.get("border_col", 0)) % Store.BORDER_COLS.size()][1])
	fs.set_corner_radius_all(10)
	frame.add_stylebox_override("panel", fs)
	_style_keys()


func _pick_picture() -> void:
	if not pic_dialog:
		pic_dialog = FileDialog.new()
		pic_dialog.mode = FileDialog.MODE_OPEN_FILE
		pic_dialog.access = FileDialog.ACCESS_FILESYSTEM
		pic_dialog.filters = PoolStringArray(["*.png, *.jpg, *.jpeg, *.webp, *.bmp, *.tga ; Pictures"])
		pic_dialog.window_title = "Choose a picture"
		pic_dialog.connect("file_selected", self, "_picture_chosen")
		add_child(pic_dialog)
	pic_dialog.popup_centered_ratio(0.8)


# Your picture is copied into the app's own folder, so it stays when the original moves.
func _picture_chosen(path: String) -> void:
	var ext = path.get_extension().to_lower()
	var dest = Store.WALLPAPER + "." + ext
	var dir = Directory.new()
	for e in ["png", "jpg", "jpeg", "webp", "bmp", "tga"]:
		if e != ext and dir.file_exists(Store.WALLPAPER + "." + e):
			dir.remove(Store.WALLPAPER + "." + e)
	if dir.copy(path, dest) != OK:
		dest = path                # couldn't copy it: use it where it is
	Store.S.bg_pic = dest
	Store.S.bg_kind = 4
	pic_key = ""
	Store.save()
	Store.emit_signal("changed")


func _key_style(c: Color) -> StyleBoxFlat:
	var s = StyleBoxFlat.new()
	s.bg_color = c
	s.set_corner_radius_all(6)
	s.border_width_bottom = 3
	s.border_color = c.darkened(0.45)
	s.content_margin_left = 4
	s.content_margin_right = 4
	return s


func _build_keys() -> void:
	keys = HBoxContainer.new()
	keys.add_constant_override("separation", 6)
	add_child(keys)
	var labels = ["on/off"]
	for i in range(8):
		labels.append("file %d" % (i + 1))
	labels += ["applets", "clear file"]
	kfont = DynamicFont.new()
	kfont.font_data = load("res://fonts/plain-sans.ttf")
	kfont.size = 20
	for i in range(labels.size()):
		var b = Button.new()
		b.text = labels[i]
		b.focus_mode = Control.FOCUS_NONE
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.add_font_override("font", kfont)
		keys.add_child(b)
		key_buttons.append(b)
		if i == 0:
			b.connect("pressed", self, "toggle_power")
		elif i <= 8:
			b.toggle_mode = true
			b.connect("pressed", self, "switch_file", [i - 1])
			file_buttons.append(b)
		elif labels[i] == "applets":
			b.connect("pressed", self, "open_applets")
		else:
			b.connect("pressed", self, "ask_clear_file")


# keys take their colours from the Device theme
func _style_keys() -> void:
	var dv: Dictionary = Store.device()
	var base = Color(dv.keys[0])
	var low = Color(dv.keys[1])
	var kt = Color(dv.kt)
	for i in range(key_buttons.size()):
		var b: Button = key_buttons[i]
		var file_key = i >= 1 and i <= 8 and dv.has("files")      # some themes give the file row its own colours
		var top = Color(dv.files[0]) if file_key else base
		var bottom = Color(dv.files[1]) if file_key else low
		var text = Color(dv.get("ft", dv.kt)) if file_key else kt
		b.add_stylebox_override("normal", _key_style(top))
		b.add_stylebox_override("hover", _key_style(top.linear_interpolate(bottom, 0.5)))
		var pressed = _key_style(bottom)
		pressed.border_width_bottom = 1
		b.add_stylebox_override("pressed", pressed)
		b.add_color_override("font_color", text)
		b.add_color_override("font_color_hover", text)
		b.add_color_override("font_color_pressed", text)
	_power_light()


# on/off key: text like the other keys, and a little light in the power colour; dark while the device is off.
# Sized from the key font, so it's redrawn whenever the layout changes the font size.
func _power_light() -> void:
	if key_buttons.empty() or not kfont:
		return
	var dv: Dictionary = Store.device()
	var kt = Color(dv.kt)
	var lit = _power_colour(Color(dv.keys[0])) if mode != "off" else Color(kt.r, kt.g, kt.b, 0.18)
	key_buttons[0].icon = _light_icon(lit, int(max(6, kfont.size * 0.45)))


# Auto: green made lighter or darker until it stands out from the key; otherwise the colour you chose
func _power_colour(key: Color) -> Color:
	var p = str(Store.S.get("pwr", "auto"))
	if p != "auto":
		return Color(p)
	var c = Color("#3fd35a")
	var up = _lum(key) < 0.35
	for i in range(20):
		if abs(_lum(c) - _lum(key)) > 0.4:
			break
		c = c.lightened(0.08) if up else c.darkened(0.08)
	return c


func _light_icon(c: Color, d: int) -> ImageTexture:
	var img = Image.new()
	img.create(d, d, false, Image.FORMAT_RGBA8)
	img.lock()
	var r = d / 2.0
	for y in range(d):
		for x in range(d):
			var a = clamp(r - Vector2(x + 0.5 - r, y + 0.5 - r).length() + 0.5, 0.0, 1.0)
			img.set_pixel(x, y, Color(c.r, c.g, c.b, a * c.a))
	img.unlock()
	var t = ImageTexture.new()
	t.create_from_image(img, 0)
	return t


func _lum(c: Color) -> float:
	return 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b


func _mark_file() -> void:
	for i in range(file_buttons.size()):
		file_buttons[i].pressed = (i == Store.S.active and mode != "off")


# A short click made in code, so no sound file is needed.
func _build_click() -> void:
	var rate = 22050
	var n = int(rate * 0.012)
	var data = PoolByteArray()
	data.resize(n * 2)
	for i in range(n):
		var env = pow(1.0 - float(i) / n, 3.0)
		var v = int(clamp((randf() * 2.0 - 1.0) * env * 0.6, -1.0, 1.0) * 32767)
		data[i * 2] = v & 0xff
		data[i * 2 + 1] = (v >> 8) & 0xff
	var sample = AudioStreamSample.new()
	sample.format = AudioStreamSample.FORMAT_16_BITS
	sample.mix_rate = rate
	sample.data = data
	click = AudioStreamPlayer.new()
	click.stream = sample
	click.volume_db = -8.0
	add_child(click)


func _restyle() -> void:
	_apply_look()
	_layout()
	lcd.relayout()
	_redraw()


# ---------- power ----------

func power_on() -> void:
	mode = "logo"
	_power_light()           # power light back on
	powering_off = false
	lcd.logo_text = "plainwirte" if randi() % 10000 == 0 else "plainwrite"   # the rare misspelt logo
	_mark_file()
	_redraw()
	yield(get_tree().create_timer(1.2), "timeout")
	if mode == "logo" and not powering_off:
		load_file()
		mode = "word"
		last_activity = OS.get_ticks_msec()
		_mark_file()
		_redraw()


func power_off() -> void:
	sync_file()
	mode = "off"
	powering_off = false
	_power_light()           # power light off
	writer.overtype = false
	_mark_file()
	_redraw()


func toggle_power() -> void:
	if mode == "off":
		power_on()
	else:
		power_off()


# The logo shows before an automatic power off (never when switched off by hand), like a Casio calculator.
func _auto_off() -> void:
	sync_file()
	mode = "logo"
	powering_off = true
	_redraw()
	yield(get_tree().create_timer(2.0), "timeout")
	if powering_off:
		power_off()


func _tick() -> void:
	if mode == "off":
		return
	lcd.cursor_on = (not lcd.cursor_on) if Store.S.blink else true
	if msg_until and OS.get_ticks_msec() > msg_until:
		msg_until = 0
		lcd.msg = ""
	var mins = int(Store.S.auto_off)
	if mins > 0 and mode != "logo" and OS.get_ticks_msec() - last_activity > mins * 60000:
		_auto_off()
	lcd.update()


# ---------- files ----------

func load_file() -> void:
	var f = Store.file()
	writer.set_text(f.text, f.cur)
	lcd.top = 0


func sync_file() -> void:
	if mode == "off" or mode == "logo":
		return
	var f = Store.file()
	f.text = writer.text
	f.cur = writer.caret
	Store.save()


func switch_file(i: int) -> void:
	if mode == "off":
		_mark_file()
		return
	sync_file()
	Store.S.active = i
	Store.save()
	load_file()
	mode = "word"
	_mark_file()
	_redraw()


func flash(t: String) -> void:
	lcd.msg = t
	msg_until = OS.get_ticks_msec() + 1700
	lcd.update()


# ---------- menus ----------

func open_applets() -> void:
	if mode == "off":
		return
	sync_file()
	mode = "applets"
	menu_sel = 0
	_redraw()


func applet_items() -> Array:
	return ["Writer", "Control Panel", "About"]


func control_items() -> Array:
	var S = Store.S
	var sz = Store.SIZES[S.text_size]
	var off = "Never" if int(S.auto_off) == 0 else "%d minutes" % int(S.auto_off)
	return [
		["font", "Font: ◂ %s ▸" % S.face],
		["size", "Text size: ◂ %s (%d lines) ▸" % [sz.name, sz.lines]],
		["fill", "Screen size: ◂ %s ▸" % ("Fill window" if S.get("fill", false) else "Fit this device")],
		["device", "Device: ◂ %s ▸" % S.device],
		["dark", "Dark mode: %s" % ("On" if S.dark else "Off")],
		["cursor", "Cursor: ◂ %s ▸" % Store.CURSOR_NAMES[S.cursor]],
		["blink", "Cursor blink: %s" % ("On" if S.blink else "Off")],
		["gap", "Gaps between selected lines: %s" % ("On" if S.sel_gap else "Off")],
		["autooff", "Auto off: ◂ %s ▸" % off],
		["sound", "Key sound: %s" % ("On" if S.sound else "Off")],
		["deved", "Device editor…"],
		["reset", "Factory reset"],
	]


func _menu_rows(title: String, items: Array, hint: String) -> Array:
	# header, then as many items as fit, scrolled so the chosen one shows
	var out = [{"t": title, "inv": true, "r": hint}]
	var room = lcd.lines_n - 1
	var first = int(clamp(menu_sel - room + 1, 0, max(0, items.size() - room)))
	for i in range(first, int(min(items.size(), first + room))):
		out.append({"t": items[i], "inv": i == menu_sel})
	return out


func _redraw() -> void:
	match mode:
		"off", "logo":
			lcd.mode = mode
		"word":
			lcd.mode = "word"
		"applets":
			lcd.mode = "rows"
			lcd.rows = _menu_rows("Applets", applet_items(), "Esc to exit")
		"control":
			lcd.mode = "rows"
			var labels = []
			for it in control_items():
				labels.append(it[1])
			lcd.rows = _menu_rows("Control Panel", labels, "Esc to exit")
		"device":
			lcd.mode = "rows"
			var dlabels = []
			for it in device_items():
				dlabels.append(it[1])
			lcd.rows = _menu_rows("Device editor", dlabels, "Esc to go back")
		"about":
			lcd.mode = "rows"
			lcd.rows = [
				{"t": "***** PLAINWRITE *****", "inv": true},
				{"t": Store.VERSION},
				{"t": "F1–F8 files · F9 applets · F10 on/off"},
				{"t": "The real thing will always have better battery life!"},
			]
		"ask":
			lcd.mode = "rows"
			var r = [{"t": ask.title, "inv": true}]
			for l in ask.lines:
				r.append({"t": l})
			lcd.rows = r
	lcd.update()


func control_step(d: int) -> void:
	var S = Store.S
	var id = control_items()[menu_sel][0]
	match id:
		"font":
			S.face = Store.FACES[(Store.face_index() + d + Store.FACES.size()) % Store.FACES.size()].name
		"size":
			S.text_size = (int(S.text_size) + d + Store.SIZES.size()) % Store.SIZES.size()
		"device":
			Store.set_device(Store.DEVICES[wrapi(Store.device_index() + (d if d != 0 else 1), 0, Store.DEVICES.size())].name)
		"fill":
			S["fill"] = not S.get("fill", false)
		"dark":
			S.dark = not S.dark
		"cursor":
			var i = Store.CURSORS.find(S.cursor)
			S.cursor = Store.CURSORS[(i + d + 3) % 3]
		"blink":
			S.blink = not S.blink
		"gap":
			S.sel_gap = not S.sel_gap
		"autooff":
			var j = Store.AUTO_OFF.find(int(S.auto_off))
			S.auto_off = Store.AUTO_OFF[(int(max(0, j)) + d + Store.AUTO_OFF.size()) % Store.AUTO_OFF.size()]
		"sound":
			S.sound = not S.sound
		"reset":
			if d == 0:
				ask_reset()
			return
		"deved":
			if d == 0:
				mode = "device"
				menu_sel = 0
				_redraw()
			return
	Store.save()
	Store.emit_signal("changed")


# ---------- Device editor ----------

func _num(x) -> String:
	return str(stepify(float(x), 0.01))


func _pwr_name() -> String:
	for p in Store.PWR_PRESETS:
		if p[0] == str(Store.S.pwr):
			return p[1]
	return "Custom"


func device_items() -> Array:
	var S = Store.S
	var k = int(S.bg_kind)
	var out = [
		["palette", "Screen: ◂ %s ▸" % Store.palette().name],
		["border", "Screen border: %s" % ("On" if S.screen_border else "Off")],
		["shadow", "Device shadow: ◂ %s× ▸" % _num(S.shadow)],
		["pwr", "Power colour: ◂ %s ▸" % _pwr_name()],
		["bgkind", "Background: ◂ %s ▸" % Store.BG_KINDS[k]],
	]
	if S.screen_border:
		out.insert(2, ["bordercol", "Border colour: ◂ %s ▸" % Store.BORDER_COLS[int(S.border_col) % Store.BORDER_COLS.size()][0]])
	if k == 1:
		out.append(["bggrad", "Colours: ◂ %s ▸" % Store.BG_GRADS[int(S.bg_grad)][0]])
		out.append(["bgshape", "Shape: ◂ %s ▸" % Store.BG_SHAPES[int(S.bg_shape)]])
		if int(S.bg_shape) != 1:
			out.append(["bgangle", "Angle: ◂ %d° ▸" % int(S.bg_angle)])
	elif k == 2:
		out.append(["bgpattern", "Pattern: ◂ %s ▸" % Store.BG_PATTERNS[int(S.bg_pattern)]])
		out.append(["bgscheme", "Colours: ◂ %s ▸" % Store.BG_SCHEMES[int(S.bg_scheme)][0]])
		out.append(["bgsize", "Size: ◂ %s× ▸" % _num(S.bg_size)])
	elif k == 3:
		out.append(["bgstyle", "Style: ◂ %s ▸" % Store.BG_STYLES[int(S.bg_style)]])
		out.append(["bgscheme", "Colours: ◂ %s ▸" % Store.BG_SCHEMES[int(S.bg_scheme)][0]])
		out.append(["bgpixel", "Pixel size: ◂ %d ▸" % int(S.bg_pixel)])
		out.append(["bgseed", "Shuffle (variation #%d)" % int(S.bg_seed)])
	elif k == 4:
		out.append(["bgpick", "Choose picture…"])
		out.append(["bgfit", "Fit: ◂ %s ▸" % Store.BG_FITS[int(S.bg_fit)]])
		if int(S.bg_fit) >= 3:
			out.append(["bgpicscale", "Picture size: ◂ %d%% ▸" % int(S.bg_pic_scale)])
	if k != 0 and k != 3:
		out.append(["bgpix", "Pixel rendering: %s" % ("On" if S.bg_pix else "Off")])
		if S.bg_pix:
			out.append(["bgpixsize", "Pixel size: ◂ %d ▸" % int(S.bg_pix_size)])
			if k == 1:
				out.append(["bgdither", "Dither: %s" % ("On" if S.bg_dither else "Off")])
	if k != 0:
		out.append(["bgdim", "Dim: ◂ %d%% ▸" % int(S.bg_dim)])
	return out


# d: -1 or 1 from ◂ ▸ (Enter counts as ▸), 0 for Enter on an action
func device_step(d: int) -> void:
	var S = Store.S
	var id = device_items()[menu_sel][0]
	var e = d if d != 0 else 1
	match id:
		"palette":
			Store.set_palette(int(S.palette) + e)
		"shadow":
			S.shadow = clamp(float(S.shadow) + 0.25 * e, 0.0, 3.0)
		"border":
			S.screen_border = not S.screen_border
		"bordercol":
			S.border_col = wrapi(int(S.border_col) + e, 0, Store.BORDER_COLS.size())
		"pwr":
			var idx = 0
			for i in range(Store.PWR_PRESETS.size()):
				if Store.PWR_PRESETS[i][0] == str(S.pwr):
					idx = i
			S.pwr = Store.PWR_PRESETS[wrapi(idx + e, 0, Store.PWR_PRESETS.size())][0]
		"bgkind":
			S.bg_kind = wrapi(int(S.bg_kind) + e, 0, Store.BG_KINDS.size())
			if S.bg_kind == 4 and S.bg_pic == "":
				_pick_picture()
		"bggrad":
			S.bg_grad = wrapi(int(S.bg_grad) + e, 0, Store.BG_GRADS.size())
		"bgshape":
			S.bg_shape = wrapi(int(S.bg_shape) + e, 0, Store.BG_SHAPES.size())
		"bgangle":
			S.bg_angle = wrapi(int(S.bg_angle) + 15 * e, 0, 360)
		"bgpattern":
			S.bg_pattern = wrapi(int(S.bg_pattern) + e, 0, Store.BG_PATTERNS.size())
		"bgscheme":
			S.bg_scheme = wrapi(int(S.bg_scheme) + e, 0, Store.BG_SCHEMES.size())
		"bgsize":
			S.bg_size = clamp(float(S.bg_size) + 0.25 * e, 0.5, 4.0)
		"bgstyle":
			S.bg_style = wrapi(int(S.bg_style) + e, 0, Store.BG_STYLES.size())
		"bgpixel":
			S.bg_pixel = int(clamp(int(S.bg_pixel) + e, 1, 8))
		"bgseed":
			S.bg_seed = randi() % 99999 + 1
		"bgpick":
			_pick_picture()
			return
		"bgfit":
			S.bg_fit = wrapi(int(S.bg_fit) + e, 0, Store.BG_FITS.size())
		"bgpicscale":
			S.bg_pic_scale = int(clamp(int(S.bg_pic_scale) + 10 * e, 10, 400))
		"bgpix":
			S.bg_pix = not S.bg_pix
		"bgpixsize":
			S.bg_pix_size = int(clamp(int(S.bg_pix_size) + e, 1, 16))
		"bgdither":
			S.bg_dither = not S.bg_dither
		"bgdim":
			S.bg_dim = int(clamp(int(S.bg_dim) + 5 * e, 0, 80))
	menu_sel = int(min(menu_sel, device_items().size() - 1))
	Store.save()
	Store.emit_signal("changed")


func ask_clear_file() -> void:
	if mode == "off":
		return
	sync_file()
	ask = {"title": "Clear file %d?" % (int(Store.S.active) + 1),
		"lines": ["This erases everything in it.", "Y = yes, N = no"], "yes": "clear_file"}
	mode = "ask"
	_redraw()


func clear_file() -> void:
	writer.set_text("", 0)
	mode = "word"
	sync_file()
	flash("File %d cleared" % (int(Store.S.active) + 1))


func ask_reset() -> void:
	ask = {"title": "Factory reset?", "lines": ["Erases all 8 files and settings.", "Y = yes, N = no"], "yes": "do_reset"}
	mode = "ask"
	_redraw()


func do_reset() -> void:
	Store.factory_reset()
	load_file()
	mode = "word"
	_mark_file()
	_redraw()


# ---------- system ----------

func _notification(what) -> void:
	if what == MainLoop.NOTIFICATION_WM_QUIT_REQUEST or what == MainLoop.NOTIFICATION_APP_PAUSED:
		sync_file()
		Store._write()
	elif what == MainLoop.NOTIFICATION_WM_GO_BACK_REQUEST:
		# Android back button: backs out of menus like Esc, and does nothing in the writer
		if mode != "word" and mode != "off" and mode != "logo":
			_back_out()


# Tapping the screen brings up the on-screen keyboard on phones and tablets without a keyboard.
func _gui_input(event) -> void:
	if event is InputEventScreenTouch and event.pressed and OS.has_virtual_keyboard() and mode == "word":
		OS.show_virtual_keyboard("")


# ---------- keyboard ----------

# Esc, Backspace or Android's back button: one menu level up
func _back_out() -> void:
	if mode == "device":
		mode = "control"
		menu_sel = _control_index("deved")
	else:
		mode = "applets" if mode == "control" or mode == "about" else "word"
		menu_sel = 0
	_redraw()


func _control_index(id: String) -> int:
	var items = control_items()
	for i in range(items.size()):
		if items[i][0] == id:
			return i
	return 0


func _input(event) -> void:
	if pic_dialog and pic_dialog.visible:
		return                     # the picture chooser has the keyboard
	if not (event is InputEventKey) or not event.pressed:
		return
	get_tree().set_input_as_handled()
	var sc = event.scancode
	if sc == KEY_F10:
		if not event.echo:
			toggle_power()
		return
	if mode == "off":
		return
	last_activity = OS.get_ticks_msec()
	if powering_off:              # a key during the closing logo keeps it on
		powering_off = false
		mode = "word"
		_redraw()
		return
	if mode == "logo":
		return
	if Store.S.sound and not event.echo:
		click.play()
	lcd.cursor_on = true
	# file keys work everywhere
	if sc >= KEY_F1 and sc <= KEY_F8:
		switch_file(sc - KEY_F1)
		return
	if event.alt and not event.control and sc >= KEY_1 and sc <= KEY_8:
		switch_file(sc - KEY_1)
		return
	if sc == KEY_F9:
		if mode == "word":
			open_applets()
		else:
			mode = "word"
			_redraw()
		return
	if mode == "word":
		_word_key(event)
	else:
		_menu_key(event)


func _menu_key(event) -> void:
	var sc = event.scancode
	if mode == "ask":
		if sc == KEY_Y:
			call(ask.yes)
		elif sc == KEY_N or sc == KEY_ESCAPE or sc == KEY_BACKSPACE:
			mode = "word"
			_redraw()
		return
	if sc == KEY_ESCAPE or sc == KEY_BACKSPACE:
		_back_out()
		return
	if mode == "about":
		return
	var n = applet_items().size() if mode == "applets" else (device_items().size() if mode == "device" else control_items().size())
	match sc:
		KEY_UP:
			menu_sel = (menu_sel - 1 + n) % n
		KEY_DOWN:
			menu_sel = (menu_sel + 1) % n
		KEY_LEFT:
			if mode == "control":
				control_step(-1)
			elif mode == "device":
				device_step(-1)
		KEY_RIGHT:
			if mode == "control":
				control_step(1)
			elif mode == "device":
				device_step(1)
		KEY_ENTER, KEY_KP_ENTER:
			if mode == "applets":
				match applet_items()[menu_sel]:
					"Writer":
						mode = "word"
					"Control Panel":
						mode = "control"
						menu_sel = 0
					"About":
						mode = "about"
			elif mode == "device":
				var did = device_items()[menu_sel][0]
				device_step(0 if did == "bgpick" or did == "bgseed" else 1)
			else:
				var id = control_items()[menu_sel][0]
				control_step(0 if id == "reset" or id == "deved" else 1)
	_redraw()


func _word_key(event) -> void:
	var sc = event.scancode
	var ctrl = event.control or event.command
	var sh = event.shift
	var w = writer
	var edited = true
	match sc:
		KEY_LEFT:
			w.left(sh, ctrl)
			edited = false
		KEY_RIGHT:
			w.right(sh, ctrl)
			edited = false
		KEY_UP:
			w.vertical(-1, sh)
			edited = false
		KEY_DOWN:
			w.vertical(1, sh)
			edited = false
		KEY_PAGEUP:
			w.vertical(-lcd.lines_n, sh)
			edited = false
		KEY_PAGEDOWN:
			w.vertical(lcd.lines_n, sh)
			edited = false
		KEY_HOME:
			w.home(sh, ctrl)
			edited = false
		KEY_END:
			w.end(sh, ctrl)
			edited = false
		KEY_BACKSPACE:
			w.backspace(ctrl)
		KEY_DELETE:
			w.delete(ctrl)
		KEY_ENTER, KEY_KP_ENTER:
			w.type_text("\n")
		KEY_TAB:
			w.type_text("    ")
		KEY_INSERT:
			if ctrl or sh:
				return
			w.overtype = not w.overtype
			flash("Typing over text" if w.overtype else "Inserting text")
			return
		KEY_ESCAPE:
			return
		_:
			if ctrl and not event.alt:
				match sc:
					KEY_A:
						w.select_all()
						edited = false
					KEY_C:
						w.copy()
						edited = false
					KEY_X:
						w.cut()
					KEY_V:
						var n = w.paste()
						if n > 0:
							if n >= 500:
								flash("Pasted %d characters" % n)
					KEY_Z:
						if sh:
							w.redo()
						else:
							w.undo()
					KEY_Y:
						w.redo()
					_:
						return
			elif event.unicode >= 32:
				w.type_text(char(event.unicode))
			else:
				return
	if edited:
		sync_file()
	else:
		Store.file().cur = w.caret
	lcd.update()

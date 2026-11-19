extends Control
# The LCD. It draws one of four things: nothing (switched off), the logo, the writer, or a list of rows
# (menus and messages). Sizes are worked out so one font pixel is a whole number of screen pixels.

var writer                     # writer.gd
var mode = "off"              # off | logo | word | rows
var rows = []                 # for "rows": [{"t": text, "inv": bool, "r": right-aligned hint}]
var msg = ""                  # shown on the bottom line in the writer for a moment
var logo_text = "plainwrite"
var cursor_on = true          # blink phase

var dot = 2                   # screen pixels per font pixel
var lines_n = 4               # lines of text on screen
var top = 0                   # first visible wrapped line in the writer
var font: Font
var _inner = Rect2()


func _ready() -> void:
	connect("resized", self, "relayout")
	Store.connect("changed", self, "relayout")
	relayout()


func relayout() -> void:
	var size_info: Dictionary = Store.SIZES[Store.S.text_size]
	lines_n = size_info.lines
	var pad = 10.0
	var inner_h = rect_size.y - pad * 2
	var inner_w = rect_size.x - pad * 2
	# biggest whole-pixel scale that fits the lines down and about the right number of characters across
	var by_h = int(inner_h / (Store.face_line() * lines_n))
	var by_w = int(inner_w / (size_info.cols * Store.face_cw()))
	dot = int(max(1, min(by_h, by_w)))
	font = Store.font(dot)
	var used_h = Store.face_line() * dot * lines_n
	_inner = Rect2(pad, pad + (inner_h - used_h) / 2.0, inner_w, used_h)
	if writer:
		writer.font = font
		writer.max_w = inner_w
	update()


func line_h() -> int:
	return Store.face_line() * dot


func _draw() -> void:
	var c: Array = Store.colors()      # [background, unlit/border, ink]
	var bg: Color = c[0]
	var off: Color = c[1]
	var ink: Color = c[2]
	draw_rect(Rect2(Vector2.ZERO, rect_size), off if Store.palette().has("classic") else off.darkened(0.15))
	draw_rect(Rect2(Vector2(4, 4), rect_size - Vector2(8, 8)), off if mode == "off" else bg)
	if mode == "off":
		return
	if mode == "logo":
		_draw_logo(ink)
		return
	if mode == "rows":
		for i in range(int(min(rows.size(), lines_n))):
			_draw_row(i, rows[i], bg, ink)
		return
	_draw_writer(bg, ink)
	if msg != "":
		_draw_row(lines_n - 1, {"t": msg, "inv": true}, bg, ink)


func _row_y(i: int) -> float:
	return _inner.position.y + i * line_h()


func _baseline(i: int) -> float:
	return _row_y(i) + font.get_ascent()


func _shown(s: String) -> String:
	return s.replace("\t", " ").replace("\n", "")


func _draw_row(i: int, row: Dictionary, bg: Color, ink: Color) -> void:
	var y = _row_y(i)
	var fg = ink
	if row.get("inv", false):
		draw_rect(Rect2(_inner.position.x - dot, y, _inner.size.x + dot * 2, line_h()), ink)
		fg = bg
	draw_string(font, Vector2(_inner.position.x, _baseline(i)), row.t, fg)
	var r: String = row.get("r", "")
	if r != "":
		# a hint like "Esc to exit" sits at the right edge, and is left out if it doesn't fit
		var rw = font.get_string_size(r).x
		var tw = font.get_string_size(row.t).x
		if tw + rw + font.get_string_size("  ").x <= _inner.size.x:
			draw_string(font, Vector2(_inner.end.x - rw, _baseline(i)), r, fg)


func _draw_logo(ink: Color) -> void:
	var big = Store.font(int(max(2, dot * 2)))
	var w1 = big.get_string_size("plain").x
	var w2 = big.get_string_size(logo_text.substr(5)).x
	var x = rect_size.x / 2.0 - (w1 + w2) / 2.0
	var y = rect_size.y / 2.0 + big.get_ascent() / 2.0 - dot * 2
	draw_string(big, Vector2(x, y), "plain", ink)
	draw_string(big, Vector2(x + max(1, dot), y), "plain", ink)    # "plain" in bold
	draw_string(big, Vector2(x + w1 + max(1, dot), y), logo_text.substr(5), ink)


func _draw_writer(bg: Color, ink: Color) -> void:
	var w = writer
	var ls: Array = w.lines()
	var li: int = w.line_of(w.caret, ls)
	if li < top:
		top = li
	if li >= top + lines_n:
		top = li - lines_n + 1
	top = int(clamp(top, 0, max(0, ls.size() - 1)))
	var a: int = w.sel_from()
	var b: int = w.sel_to()
	var gap: bool = Store.S.sel_gap
	var hl = line_h() - (dot if gap else 0)       # selection height: with gaps it stops a pixel short
	for r in range(lines_n):
		var i = top + r
		if i >= ls.size():
			break
		var s: int = ls[i][0]
		var e: int = ls[i][1]
		var t: String = w.text.substr(s, e - s)
		var x0 = _inner.position.x
		var y = _row_y(r)
		var base = _baseline(r)
		draw_string(font, Vector2(x0, base), _shown(t), ink)
		# selected part, drawn the other way round
		var sa = int(max(a, s))
		var sb = int(min(b, e))
		if sb > sa:
			var x = x0 + w.width(w.text.substr(s, sa - s))
			var seg: String = w.text.substr(sa, sb - sa)
			var sw: float = w.width(seg)
			if sb == e and e < w.text.length() and w.text[e] == "\n":
				sw += w.cw(" ")
			draw_rect(Rect2(x, y, sw, hl), ink)
			draw_string(font, Vector2(x, base), _shown(seg), bg)
		# cursor
		if i == li and not w.has_sel() and cursor_on:
			_draw_cursor(w, s, base, y, bg, ink)


func _draw_cursor(w, s: int, base: float, y: float, bg: Color, ink: Color) -> void:
	var x = _inner.position.x + w.width(w.text.substr(s, w.caret - s))
	var ch = " "
	if w.caret < w.text.length() and w.text[w.caret] != "\n":
		ch = w.text[w.caret]
	var cw: float = w.cw(ch if ch != "\t" else " ")
	var style: String = Store.S.cursor
	# typing over text shows the block, or the underscore if the block is already your cursor
	if w.overtype:
		style = "under" if style == "block" else "block"
	var thick = float(max(2, dot))
	match style:
		"line":
			draw_rect(Rect2(x, y, thick, line_h()), ink)
		"under":
			draw_rect(Rect2(x, y + line_h() - thick, cw, thick), ink)
		_:
			draw_rect(Rect2(x, y, cw, line_h() - (dot if Store.S.sel_gap else 0)), ink)
			draw_string(font, Vector2(x, base), _shown(ch), bg)

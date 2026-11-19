extends Reference
# The text being edited: the words, the caret and selection, word wrap by on-screen width,
# moving around, typing (inserting or typing over), deleting, clipboard and undo.
# It knows nothing about drawing; lcd.gd draws it.

var text = ""
var caret = 0          # where the cursor is
var anchor = 0         # other end of the selection (== caret when nothing is selected)
var overtype = false   # Insert key: type over the letters instead of pushing them along

var font: Font          # set by the screen, used to measure widths for word wrap
var max_w = 100.0      # usable width of a line in screen pixels

var _goal_x = null      # ↑ ↓ remember the spot you started from, even through shorter lines
var _vert_caret = -1
var _undo = []
var _redo = []
var _last_edit_ms = 0
var _lines = []        # cached wrap
var _lines_for = ""
var _dirty = true


func set_text(t: String, cur: int) -> void:
	text = t
	caret = int(clamp(cur, 0, text.length()))
	anchor = caret
	_undo.clear()
	_redo.clear()
	_dirty = true


# ---------- measuring and wrapping ----------

func cw(ch: String) -> float:
	if ch == "\t":
		ch = " "
	return font.get_char_size(ord(ch)).x if font else 8.0


func width(s: String) -> float:
	var w = 0.0
	for i in range(s.length()):
		w += cw(s[i])
	return w


# Lines as [start, end) pairs. Long lines break after the last space that fits;
# a word longer than the whole line is broken where it runs out of room.
func lines() -> Array:
	var key = "%f|%s" % [max_w, str(font)]
	if not _dirty and _lines_for == key:
		return _lines
	var out = []
	var n = text.length()
	var p = 0
	while true:
		var nl = text.find("\n", p)
		var para_end = n if nl == -1 else nl
		var s = p
		if s == para_end:
			out.append([s, s])
		while s < para_end:
			var w = 0.0
			var i = s
			var last_space = -1
			while i < para_end:
				var c = cw(text[i])
				if w + c > max_w and i > s:
					break
				if text[i] == " ":
					last_space = i
				w += c
				i += 1
			if i >= para_end:
				out.append([s, para_end])
				s = para_end
			elif last_space >= s:
				out.append([s, last_space + 1])
				s = last_space + 1
			else:
				out.append([s, i])
				s = i
		if nl == -1:
			break
		p = nl + 1
	_lines = out
	_lines_for = key
	_dirty = false
	return out


func line_of(pos: int, ls: Array) -> int:
	var k = 0
	for i in range(ls.size()):
		if ls[i][0] <= pos:
			k = i
		else:
			break
	return k


# last caret position on a line (before a soft-wrap space it's the end of the line's text)
func line_end(ls: Array, i: int) -> int:
	var L: Array = ls[i]
	if i + 1 < ls.size() and ls[i + 1][0] == L[1] and L[1] > L[0]:
		return L[1] - 1
	return L[1]


# ---------- selection ----------

func has_sel() -> bool:
	return caret != anchor


func sel_from() -> int:
	return int(min(caret, anchor))


func sel_to() -> int:
	return int(max(caret, anchor))


func selected() -> String:
	return text.substr(sel_from(), sel_to() - sel_from())


func move_to(p: int, extend: bool) -> void:
	caret = int(clamp(p, 0, text.length()))
	if not extend:
		anchor = caret


# ---------- moving ----------

func left(extend: bool, word: bool) -> void:
	if has_sel() and not extend:
		move_to(sel_from(), false)
		return
	var p = caret - 1
	if word:
		while p > 0 and text[p] == " ":
			p -= 1
		while p > 0 and text[p - 1] != " " and text[p - 1] != "\n":
			p -= 1
	move_to(p, extend)


func right(extend: bool, word: bool) -> void:
	if has_sel() and not extend:
		move_to(sel_to(), false)
		return
	var p = caret + 1
	if word:
		while p < text.length() and text[p - 1] != " " and text[p - 1] != "\n":
			p += 1
		while p < text.length() and text[p] == " ":
			p += 1
	move_to(p, extend)


# ↑ ↓ go to the letter under the same spot on screen (by width, so proportional fonts line up)
func vertical(d: int, extend: bool) -> void:
	var ls = lines()
	var li = line_of(caret, ls)
	if caret != _vert_caret or _goal_x == null:
		_goal_x = width(text.substr(ls[li][0], caret - ls[li][0]))
	var t = li + d
	var p: int
	if t < 0:
		p = 0
	elif t >= ls.size():
		p = text.length()
	else:
		p = _pos_at_x(ls, t, _goal_x)
	move_to(p, extend)
	_vert_caret = caret


func _pos_at_x(ls: Array, t: int, x: float) -> int:
	var s: int = ls[t][0]
	var e = line_end(ls, t)
	var w = 0.0
	for p in range(s, e):
		var c = cw(text[p])
		if w + c / 2.0 > x:
			return p
		w += c
	return e


func home(extend: bool, doc: bool) -> void:
	if doc:
		move_to(0, extend)
		return
	var ls = lines()
	move_to(ls[line_of(caret, ls)][0], extend)


func end(extend: bool, doc: bool) -> void:
	if doc:
		move_to(text.length(), extend)
		return
	var ls = lines()
	move_to(line_end(ls, line_of(caret, ls)), extend)


func select_all() -> void:
	anchor = 0
	caret = text.length()


# ---------- editing ----------

func _snapshot(coalesce: bool) -> void:
	var now = OS.get_ticks_msec()
	if coalesce and now - _last_edit_ms < 1000 and _undo.size() > 0:
		_last_edit_ms = now
		return
	_last_edit_ms = now
	_undo.append([text, caret, anchor])
	if _undo.size() > 200:
		_undo.pop_front()
	_redo.clear()


func _replace(from: int, to: int, s: String) -> void:
	text = text.substr(0, from) + s + text.substr(to)
	_dirty = true
	caret = from + s.length()
	anchor = caret


func type_text(s: String) -> void:
	_snapshot(s.length() == 1 and s != "\n")
	var from = sel_from()
	var to = sel_to()
	if overtype and not has_sel():
		# replace as many letters as are typed, but never the line break
		var e = caret
		while e < text.length() and e - caret < s.length() and text[e] != "\n":
			e += 1
		to = e
	_replace(from, to, s)


func backspace(word: bool) -> void:
	if has_sel():
		_snapshot(false)
		_replace(sel_from(), sel_to(), "")
		return
	if caret == 0:
		return
	_snapshot(true)
	var p = caret - 1
	if word:
		while p > 0 and text[p - 1] == " ":
			p -= 1
		while p > 0 and text[p - 1] != " " and text[p - 1] != "\n":
			p -= 1
	_replace(p, caret, "")


func delete(word: bool) -> void:
	if has_sel():
		_snapshot(false)
		_replace(sel_from(), sel_to(), "")
		return
	if caret >= text.length():
		return
	_snapshot(true)
	var e = caret + 1
	if word:
		while e < text.length() and text[e] != " " and text[e] != "\n":
			e += 1
	var c = caret
	_replace(c, e, "")


func copy() -> void:
	if has_sel():
		OS.clipboard = selected()


func cut() -> void:
	if has_sel():
		copy()
		_snapshot(false)
		_replace(sel_from(), sel_to(), "")


func paste() -> int:
	var s: String = OS.clipboard.replace("\r\n", "\n").replace("\r", "\n")
	if s == "":
		return 0
	_snapshot(false)
	_replace(sel_from(), sel_to(), s)
	return s.length()


func undo() -> void:
	if _undo.empty():
		return
	_redo.append([text, caret, anchor])
	var u: Array = _undo.pop_back()
	text = u[0]
	_dirty = true
	caret = u[1]
	anchor = u[2]
	_last_edit_ms = 0


func redo() -> void:
	if _redo.empty():
		return
	_undo.append([text, caret, anchor])
	var r: Array = _redo.pop_back()
	text = r[0]
	_dirty = true
	caret = r[1]
	anchor = r[2]
	_last_edit_ms = 0


func word_count() -> int:
	var n = 0
	var in_word = false
	for i in range(text.length()):
		var sp: bool = text[i] == " " or text[i] == "\n" or text[i] == "\t"
		if not sp and not in_word:
			n += 1
		in_word = not sp
	return n

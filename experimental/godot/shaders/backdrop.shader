shader_type canvas_item;
// What shows behind the device (Control Panel → Device editor → Background). One shader draws every kind:
// kind 0 plain colour, 1 gradient, 2 vector pattern, 3 generated pattern, 4 your own picture.
// Written for GLES2: no integer bit tricks, no arrays, no switch.

uniform vec2 size = vec2(1024.0, 600.0);   // the window, in pixels
uniform int kind = 0;
uniform int sub = 0;            // gradient shape (0 straight, 1 round, 2 sweep), pattern number or style number
uniform vec4 c1 : hint_color = vec4(0.07, 0.08, 0.09, 1.0);
uniform vec4 c2 : hint_color = vec4(0.23, 0.25, 0.29, 1.0);
uniform vec4 c3 : hint_color = vec4(0.1, 0.1, 0.1, 1.0);
uniform float three = 1.0;
uniform float angle = 2.79;     // radians, CSS style: 0 = up, clockwise
uniform float scale = 1.0;      // pattern size, or pixel size for generated ones
uniform float seed = 1.0;
uniform float dim = 0.0;        // 0–0.8: darkens whatever is drawn
uniform sampler2D pic;
uniform vec2 pic_size = vec2(1.0, 1.0);
uniform int fit = 0;            // 0 fill, 1 fit inside, 2 stretch, 3 centre, 4 tile
uniform float pic_scale = 1.0;  // for centre and tile
uniform float pix = 0.0;        // pixel rendering: size of one big pixel (0 = off)
uniform float dither = 0.0;     // with pixel rendering, 1 = ordered dither (5 levels per colour)

const float TAU = 6.28318530718;

float hash(vec2 p) {
	p = mod(p, 4096.0);
	return fract(sin(dot(p, vec2(127.1, 311.7)) + seed * 17.13) * 43758.5453);
}

vec4 ramp3(float t) {
	t = clamp(t, 0.0, 1.0);
	if (three > 0.5) {
		return t < 0.5 ? mix(c1, c2, t * 2.0) : mix(c2, c3, (t - 0.5) * 2.0);
	}
	return mix(c1, c2, t);
}

vec4 gradient(vec2 p) {
	vec2 c = size * 0.5;
	if (sub == 1) {          // round, from a little above the middle out to the farthest corner
		vec2 o = size * vec2(0.5, 0.4);
		float far = length(max(o, size - o));
		return ramp3(length(p - o) / far);
	}
	if (sub == 2) {          // sweep around the middle, back to the first colour
		vec2 d = p - c;
		float a = atan(d.x, -d.y) - angle;
		float t = fract(a / TAU);
		if (three > 0.5) {
			if (t < 1.0 / 3.0) { return mix(c1, c2, t * 3.0); }
			if (t < 2.0 / 3.0) { return mix(c2, c3, t * 3.0 - 1.0); }
			return mix(c3, c1, t * 3.0 - 2.0);
		}
		return t < 0.5 ? mix(c1, c2, t * 2.0) : mix(c2, c1, t * 2.0 - 1.0);
	}
	vec2 dir = vec2(sin(angle), -cos(angle));
	float ext = abs(c.x * dir.x) + abs(c.y * dir.y);
	return ramp3(dot(p - c, dir) / (2.0 * ext) + 0.5);
}

// vector patterns on a 24-unit tile; true where the pattern colour goes
bool pattern(vec2 p) {
	vec2 q = mod(p / scale, 24.0);
	vec2 m = q - vec2(12.0);
	if (sub == 0) { return length(m) < 3.2; }                                   // dots
	if (sub == 1) { return q.x < 1.0 || q.y < 1.0; }                            // grid
	if (sub == 2) { return q.y < 9.0; }                                         // stripes
	if (sub == 3) { return mod(q.x + q.y, 24.0) < 5.0; }                        // diagonal
	if (sub == 4) { return (q.x < 12.0) != (q.y < 12.0); }                      // checker
	if (sub == 5) { return abs(q.y - 8.0 - abs(mod(q.x, 12.0) - 6.0) * 1.33) < 1.6; }   // zigzag
	if (sub == 6) { return abs(q.y - 12.0 - 4.0 * sin(q.x / 24.0 * TAU)) < 1.3; }      // waves
	if (sub == 7) { return abs(m.x) + abs(m.y) < 10.0; }                        // diamonds
	if (sub == 8) { return (abs(m.x) < 2.0 && abs(m.y) < 7.0) || (abs(m.y) < 2.0 && abs(m.x) < 7.0); }   // plus
	if (sub == 9) {                                                             // bricks
		if (q.y < 1.5 || abs(q.y - 12.75) < 0.75) { return true; }
		return q.y < 12.0 ? q.x < 1.5 : abs(q.x - 12.75) < 0.75;
	}
	if (sub == 10) { float d = length(m); return abs(d - 10.0) < 1.0 || abs(d - 4.5) < 1.0; }   // rings
	if (sub == 11) { return q.y > 2.0 && q.y < 22.0 && abs(m.x) < (q.y - 2.0) * 0.6; }        // triangles
	return abs(abs(m.x) - abs(m.y)) < 1.2 && max(abs(m.x), abs(m.y)) < 5.0;                    // crosses
}

float plasma(vec2 pp, float big) {
	float v = 0.0;
	for (int i = 0; i < 6; i++) {
		float fi = float(i);
		float a = hash(vec2(fi, 1.0)) * 0.12 + 0.02;
		float b = hash(vec2(fi, 2.0)) * 0.12 + 0.02;
		float ph = hash(vec2(fi, 3.0)) * TAU;
		float qh = hash(vec2(fi, 4.0)) * TAU;
		float s = 280.0 / big;
		v += sin(pp.x * a * s + ph) + sin(pp.y * b * s + qh) + sin((pp.x + pp.y) * a * s * 0.5 + qh);
	}
	return (v / 18.0 + 1.0) * 0.5;
}

float bayer2(vec2 v) { return mod(v.x * 2.0 + v.y * 3.0, 4.0); }

vec4 generated(vec2 p) {
	vec2 pp = floor(p / scale);                 // chunky pixels
	vec2 grid = floor(size / scale);
	float big = max(grid.x, grid.y);
	if (sub == 0) {                              // static
		float r = hash(pp);
		return mix(c1, c2, r * hash(pp + 7.0) * 1.6 > 0.5 ? 1.0 : r * 0.25);
	}
	if (sub == 1) {                              // plasma
		return mix(c1, c2, 0.5 + 0.5 * sin(plasma(pp, big) * TAU * 2.0));
	}
	if (sub == 2) {                              // starfield
		float r = hash(pp);
		return r > 0.997 ? mix(c1, c2, 0.35 + 0.65 * hash(pp + 3.0)) : c1;
	}
	if (sub == 3) {                              // 10 PRINT maze
		vec2 cell = floor(pp / 8.0);
		vec2 l = mod(pp, 8.0);
		float y = hash(cell) > 0.5 ? l.y : 7.0 - l.y;
		return abs(l.x - y) < 1.0 ? c2 : c1;
	}
	if (sub == 4) {                              // Truchet tiles
		vec2 cell = floor(pp / 16.0);
		vec2 l = mod(pp, 16.0) + 0.5;
		float d;
		if (hash(cell) > 0.5) {
			d = min(abs(length(l) - 8.0), abs(length(l - vec2(16.0)) - 8.0));
		} else {
			d = min(abs(length(l - vec2(16.0, 0.0)) - 8.0), abs(length(l - vec2(0.0, 16.0)) - 8.0));
		}
		return d < 1.5 ? c2 : c1;
	}
	if (sub == 5) {                              // ordered dither, top to bottom
		float m = 4.0 * bayer2(mod(pp, 2.0)) + bayer2(mod(floor(pp / 2.0), 2.0));
		return (pp.y / grid.y) * 16.0 > m + 0.5 ? c2 : c1;
	}
	if (sub == 6) {                              // topography lines
		return fract(plasma(pp, big) * 14.0) < 0.12 ? c2 : c1;
	}
	// cells
	vec2 g = pp / 40.0;
	vec2 gi = floor(g);
	vec2 gf = fract(g);
	float d1 = 9.0;
	float d2 = 9.0;
	float k = 0.0;
	for (int j = -1; j <= 1; j++) {
		for (int i = -1; i <= 1; i++) {
			vec2 o = vec2(float(i), float(j));
			vec2 pt = o + vec2(hash(gi + o), hash(gi + o + 19.0));
			float d = length(gf - pt);
			if (d < d1) { d2 = d1; d1 = d; k = hash(gi + o + 41.0); }
			else if (d < d2) { d2 = d; }
		}
	}
	return (d2 - d1) * 40.0 < 1.6 ? mix(c1, vec4(0.0, 0.0, 0.0, 1.0), 0.45) : mix(c1, c2, k);
}

vec4 picture(vec2 p) {
	vec2 uv;
	if (fit == 2) {
		uv = p / size;
	} else if (fit == 4) {
		uv = fract(p / (pic_size * pic_scale));
	} else {
		float k;
		if (fit == 0) { k = max(size.x / pic_size.x, size.y / pic_size.y); }
		else if (fit == 1) { k = min(size.x / pic_size.x, size.y / pic_size.y); }
		else { k = pic_scale; }
		vec2 shown = pic_size * k;
		uv = (p - (size - shown) * 0.5) / shown;
		if (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) { return vec4(0.0, 0.0, 0.0, 1.0); }
	}
	return texture(pic, uv);
}

void fragment() {
	vec2 p = UV * size;
	vec2 cell = floor(p / max(pix, 1.0));
	if (pix > 0.0 && kind != 3) { p = (cell + 0.5) * pix; }   // one sample per big pixel
	vec4 col = c1;
	if (kind == 1) { col = gradient(p); }
	else if (kind == 2) { col = pattern(p) ? c2 : c1; }
	else if (kind == 3) { col = generated(p); }
	else if (kind == 4) { col = picture(p); }
	if (pix > 0.0 && dither > 0.5 && kind == 1) {
		float m = 4.0 * bayer2(mod(cell, 2.0)) + bayer2(mod(floor(cell / 2.0), 2.0));
		vec3 st = vec3(0.25);
		col.rgb = clamp(floor(col.rgb / st + (m + 0.5) / 16.0) * st, 0.0, 1.0);
	}
	COLOR = vec4(col.rgb * (1.0 - dim), 1.0);
}

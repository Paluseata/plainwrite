shader_type canvas_item;
// The device body: a rounded box filled with a two- or three-colour gradient, over a soft drop shadow.
// The ColorRect this runs on is bigger than the body, to leave room for the shadow.

uniform vec2 size = vec2(100.0, 100.0);      // this rect, in pixels
uniform vec2 box_pos = vec2(0.0, 0.0);       // the body inside this rect
uniform vec2 box_size = vec2(100.0, 100.0);
uniform float radius = 16.0;
uniform vec4 c1 : hint_color = vec4(0.19, 0.21, 0.24, 1.0);
uniform vec4 c2 : hint_color = vec4(0.12, 0.13, 0.15, 1.0);
uniform vec4 c3 : hint_color = vec4(0.12, 0.13, 0.15, 1.0);
uniform float three = 0.0;                   // 1 = c1 → c2 → c3, 0 = c1 → c2 (reached at 70%)
uniform float angle = 2.967;                 // radians, CSS style: 0 = up, clockwise
uniform float shadow = 1.0;                  // 0 = none, 1 = standard, up to 3

float box_sdf(vec2 p, vec2 c, vec2 half_size, float r) {
	vec2 q = abs(p - c) - half_size + vec2(r);
	return length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0) - r;
}

vec4 ramp(float t) {
	t = clamp(t, 0.0, 1.0);
	if (three > 0.5) {
		return t < 0.5 ? mix(c1, c2, t * 2.0) : mix(c2, c3, (t - 0.5) * 2.0);
	}
	return mix(c1, c2, clamp(t / 0.7, 0.0, 1.0));
}

void fragment() {
	vec2 p = UV * size;
	vec2 hs = box_size * 0.5;
	vec2 c = box_pos + hs;
	float d = box_sdf(p, c, hs, radius);
	// shadow: dropped 24px and blurred over 60px at strength 1, like the web app's box-shadow
	float blur = 60.0 * max(shadow, 0.01);
	float ds = box_sdf(p, c + vec2(0.0, 24.0 * shadow), hs, radius);
	float sh = clamp(0.55 * shadow, 0.0, 1.0) * (1.0 - smoothstep(-blur * 0.5, blur * 0.5, ds));
	if (shadow <= 0.0) { sh = 0.0; }
	vec2 dir = vec2(sin(angle), -cos(angle));
	float ext = abs(hs.x * dir.x) + abs(hs.y * dir.y);
	vec4 body = ramp(dot(p - c, dir) / (2.0 * ext) + 0.5);
	float a = clamp(0.5 - d, 0.0, 1.0);
	vec4 shade_col = vec4(0.0, 0.0, 0.0, sh);
	COLOR = vec4(mix(shade_col.rgb, body.rgb, a), a + sh * (1.0 - a));
}

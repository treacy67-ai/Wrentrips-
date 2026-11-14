import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ai_tag, ease, wren

OUT = "/home/claude/wren/ep4"
os.makedirs(OUT, exist_ok=True)

CX, GY, S = 400, 1700, 0.95           # Wren position and scale
TABLE_Y = 1560                        # table top
BOWL = (640, 1435)                    # broth centre
JAR_C = (590, 1215)                   # jar centre while held
HAND_JAR_W = (540, 1265)              # world position of Wren's hand holding the jar
L_MOUTH, L_REST, L_THUMB = (2, -512), (150, -300), (190, -548)
DARK, RED = hexc('#22223b'), '#e63946'

def ell(ctx, x, y, rx, ry, col, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(rx, ry); circle(ctx, 0, 0, 1, col); ctx.restore()

def bobv(t): return math.sin(t * 2 * math.pi * 1.1) * 5
def hand_local(wx, wy, t): return ((wx - CX) / S, (wy - GY) / S - bobv(t))
def hand_world(hl, t, cx=CX): return (cx + S * hl[0], GY + S * (hl[1] + bobv(t)))

def hand_path(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            k = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1
            return (p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k)
    return keys[-1][1]

# ---------- set pieces ----------
def room(ctx, t):
    mv.vgrad(ctx, '#ffd9b3', '#ffe9cf')
    ctx.set_line_width(2); ctx.set_source_rgba(1, 1, 1, 0.4)
    for x in range(0, W, 90): ctx.move_to(x, 620); ctx.line_to(x, 1300); ctx.stroke()
    for y in range(620, 1300, 90): ctx.move_to(0, y); ctx.line_to(W, y); ctx.stroke()
    rrect(ctx, 700, 750, 240, 110, 20); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    mv.font(ctx, 78); e = ctx.text_extents("PHO"); ctx.move_to(820 - e.x_advance / 2, 838); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text("PHO")
    ctx.rectangle(-200, 1640, W + 400, 700); ctx.set_source_rgba(*hexc('#c9ada7')); ctx.fill()

def lights(ctx, t):
    ctx.set_line_width(3); ctx.set_source_rgba(0.15, 0.12, 0.12, 0.9)
    ctx.move_to(-20, 60); ctx.curve_to(W / 3, 160, 2 * W / 3, 160, W + 20, 60); ctx.stroke()
    for k in range(8):
        u = (k + 0.5) / 8; x = u * W; y = 60 + 100 * 0.75 * 4 * u * (1 - u) + 14
        g = cairo.RadialGradient(x, y + 12, 3, x, y + 12, 55); g.add_color_stop_rgba(0, 1, 0.85, 0.4, 0.6); g.add_color_stop_rgba(1, 1, 0.85, 0.4, 0)
        ctx.set_source(g); ctx.arc(x, y + 12, 55, 0, 2 * math.pi); ctx.fill()
        circle(ctx, x, y + 12, 11, hexc('#ffe08a'))

def begin_set(ctx):
    ctx.save(); ctx.translate(540, 1700); ctx.scale(1.2, 1.2); ctx.translate(-540, -1700)

def end_set(ctx):
    ctx.restore()

def aunty(ctx, x, base, t, mood="smile", jar_out=False):
    ctx.save(); ctx.translate(x, base + math.sin(t * 2 * math.pi * 0.9) * 3)
    SK = hexc('#d9a066')
    rrect(ctx, -72, -175, 144, 175, 30); ctx.set_source_rgba(*hexc('#f4a261')); ctx.fill()
    rrect(ctx, -52, -130, 104, 130, 14); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    if jar_out:
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(36); ctx.set_source_rgba(*hexc('#f4a261'))
        ctx.move_to(-58, -150); ctx.line_to(-122, -200); ctx.stroke(); circle(ctx, -122, -200, 21, SK)
        jar(ctx, -150, -245, math.radians(-12 + 4 * math.sin(t * 6)), 1.0, True, scale=0.8)
    circle(ctx, 0, -225, 64, SK)
    ctx.arc(0, -232, 66, math.radians(188), math.radians(352)); ctx.close_path(); ctx.set_source_rgba(*hexc('#e76f51')); ctx.fill()
    circle(ctx, -64, -250, 13, hexc('#e76f51')); circle(ctx, 64, -250, 13, hexc('#e76f51'))
    circle(ctx, -36, -204, 11, hexc('#f28b82', 0.5)); circle(ctx, 36, -204, 11, hexc('#f28b82', 0.5))
    ph = (t + 0.7) % 3.4; sy = 0.12 if ph < 0.12 else 1.0
    for ex in (-22, 22):
        ctx.save(); ctx.translate(ex, -226); ctx.scale(1, sy); circle(ctx, 0, 0, 7, hexc('#2b2d42')); ctx.restore()
    ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#7a3e2b'))
    if mood == "sly":
        ctx.arc(0, -214, 28, math.radians(10), math.radians(170)); ctx.stroke()
        ctx.set_line_width(5); ctx.move_to(-34, -250); ctx.line_to(-12, -258); ctx.stroke(); ctx.move_to(12, -252); ctx.line_to(34, -246); ctx.stroke()
    else:
        ctx.arc(0, -214, 22, math.radians(25), math.radians(155)); ctx.stroke()
    ctx.restore()

def counter(ctx, t):
    # bowl stack + steaming pot sit on the counter
    for k in range(3):
        ell(ctx, 700, 1270 - k * 16, 44, 12, hexc('#f1f3f5')); rrect(ctx, 656, 1262 - k * 16, 88, 8, 4); ctx.set_source_rgba(*hexc('#4361ee')); ctx.fill()
    rrect(ctx, 940, 1190, 120, 90, 12); ctx.set_source_rgba(*hexc('#adb5bd')); ctx.fill()
    ell(ctx, 1000, 1190, 66, 12, hexc('#ced4da')); circle(ctx, 1000, 1176, 9, hexc('#6c757d'))
    for k in range(3):
        ph = (t * 0.7 + k / 3) % 1
        ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(1, 1, 1, 0.75 * (1 - ph))
        bx = 975 + k * 25; by = 1170 - ph * 150
        ctx.move_to(bx, by); ctx.curve_to(bx + 14, by - 20, bx - 14, by - 40, bx, by - 60); ctx.stroke()
    rrect(ctx, 520, 1290, 600, 160, 14); ctx.set_source_rgba(*hexc('#8d5524')); ctx.fill()
    rrect(ctx, 510, 1278, 620, 20, 8); ctx.set_source_rgba(*hexc('#b5835a')); ctx.fill()

def table(ctx):
    rrect(ctx, 110, TABLE_Y - 4, 880, 28, 12); ctx.set_source_rgba(*hexc('#5aa9ff')); ctx.fill()
    ctx.rectangle(130, TABLE_Y + 24, 840, 120); ctx.set_source_rgba(*hexc('#3a7bd5')); ctx.fill()
    ctx.rectangle(130, TABLE_Y + 24, 840, 10); ctx.set_source_rgba(0, 0, 0, 0.12); ctx.fill()

MOUNT = []
_r = random.Random(4)
for _i in range(170):
    h = _r.random() ** 1.35; mw = 138 * (1 - h) + 8
    MOUNT.append((h, _r.uniform(-mw, mw), -h * 135 + _r.uniform(-5, 5), _r.uniform(0, math.pi),
                  _r.choice(['#d62828', '#e63946', '#f77f00', '#c1121f', '#ef233c'])))
MOUNT.sort(key=lambda m: m[0])

def bowl(ctx, x, y, g, t, steam=True):
    ctx.save(); ctx.translate(x, y)
    ctx.move_to(-160, 0); ctx.curve_to(-152, 100, -70, 128, 0, 128); ctx.curve_to(70, 128, 152, 100, 160, 0); ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 1); ctx.fill_preserve(); ctx.save(); ctx.clip()
    ctx.rectangle(-170, 52, 340, 16); ctx.set_source_rgba(*hexc('#4361ee')); ctx.fill(); ctx.restore()
    rrect(ctx, -60, 122, 120, 16, 6); ctx.set_source_rgba(*hexc('#e9ecef')); ctx.fill()
    ell(ctx, 0, 0, 160, 38, hexc('#f1f3f5')); ell(ctx, 0, 2, 146, 31, hexc('#f6bd60'))
    ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(1, 0.97, 0.88, 1)
    for k in range(5):
        ctx.move_to(-90 + k * 40, -8); ctx.curve_to(-70 + k * 40, 12, -40 + k * 40, -14, -22 + k * 40, 8); ctx.stroke()
    for gx, gy_ in ((-60, 6), (20, 12), (70, -4), (-20, -10)): circle(ctx, gx, gy_, 6, hexc('#80b918'))
    n = int(g * len(MOUNT))
    for h, fx, fy, ang, col in MOUNT[:n]: ell(ctx, fx, fy, 14, 5.5, hexc(col), ang)
    if steam and g < 0.98:
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1
            ctx.set_line_width(7); ctx.set_source_rgba(1, 1, 1, 0.7 * (1 - ph))
            bx = -60 + k * 60; by = -40 - ph * 120 - g * 120
            ctx.move_to(bx, by); ctx.curve_to(bx + 14, by - 20, bx - 14, by - 40, bx, by - 60); ctx.stroke()
    ctx.restore()

def jar(ctx, x, y, theta, fill, lid=True, scale=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(theta); ctx.scale(scale, scale)
    rrect(ctx, -50, -70, 100, 140, 18); ctx.set_source_rgba(0.85, 0.95, 1, 0.9); ctx.fill()
    if fill > 0.02:
        hh = 128 * fill; rrect(ctx, -45, 66 - hh, 90, hh, 12); ctx.set_source_rgba(*hexc('#d62828')); ctx.fill()
    rrect(ctx, -34, -20, 68, 46, 8); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    mv.font(ctx, 26); e = ctx.text_extents("HOT"); ctx.move_to(-e.x_advance / 2, 14); ctx.set_source_rgba(*hexc('#c1121f')); ctx.show_text("HOT")
    ctx.set_line_width(4); ctx.set_source_rgba(0.55, 0.65, 0.7, 1); rrect(ctx, -50, -70, 100, 140, 18); ctx.stroke()
    if lid:
        rrect(ctx, -54, -96, 108, 30, 8); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill()
    ctx.restore()

def bubble(ctx, cx, cy, text, size, a, tail_to):
    if a <= 0: return
    mv.font(ctx, size); e = ctx.text_extents(text); w = e.x_advance + 70; h = size * 1.15 + 40
    ctx.save(); ctx.translate(0, (1 - a) * 20)
    rrect(ctx, cx - w / 2, cy - h / 2, w, h, h / 2); ctx.set_source_rgba(1, 1, 1, 0.97 * a); ctx.fill()
    tx, ty = tail_to
    ctx.move_to(cx - 22, cy + h / 2 - 4); ctx.line_to(tx, ty); ctx.line_to(cx + 22, cy + h / 2 - 4); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.97 * a); ctx.fill()
    ctx.move_to(cx - e.x_advance / 2, cy + size * 0.35); ctx.set_source_rgba(*hexc('#22223b', a)); ctx.show_text(text)
    ctx.restore()

def flame(ctx, x, y, t, lvl):
    if lvl <= 0: return
    for k, phi in enumerate((55, 90, 125)):
        L = 190 * lvl * (0.82 + 0.18 * math.sin(t * 32 + k * 2))
        for col, f in ((hexc('#ff6b00'), 1.0), (hexc('#ffd60a'), 0.6)):
            ctx.save(); ctx.translate(x, y); ctx.rotate(math.radians(phi)); l = L * f
            ctx.move_to(0, -22 * f); ctx.curve_to(l * 0.5, -48 * f, l * 0.9, -16 * f, l, 0)
            ctx.curve_to(l * 0.9, 16 * f, l * 0.5, 48 * f, 0, 22 * f); ctx.close_path()
            ctx.set_source_rgba(*col); ctx.fill(); ctx.restore()

def glass(ctx, x, y, tilt):
    ctx.save(); ctx.translate(x, y); ctx.rotate(tilt)
    rrect(ctx, -26, -44, 52, 88, 8); ctx.set_source_rgba(0.75, 0.9, 1, 0.65); ctx.fill()
    rrect(ctx, -22, -14, 44, 54, 6); ctx.set_source_rgba(*hexc('#4cc9f0', 0.8)); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(0.5, 0.65, 0.8, 1); rrect(ctx, -26, -44, 52, 88, 8); ctx.stroke(); ctx.restore()

def chopsticks(ctx, hw, t, strands):
    tx, ty = BOWL[0], BOWL[1] - 60
    vx, vy = tx - hw[0], ty - hw[1]; n = math.hypot(vx, vy) or 1; vx, vy = vx / n, vy / n
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#8b5a2b'))
    for off in (-7, 7):
        ctx.move_to(hw[0] - vy * off, hw[1] + vx * off); ctx.line_to(hw[0] + vx * 120 - vy * off * 0.4, hw[1] + vy * 120 + vx * off * 0.4); ctx.stroke()
    if strands:
        ex, ey = hw[0] + vx * 120, hw[1] + vy * 120
        ctx.set_line_width(5); ctx.set_source_rgba(1, 0.96, 0.85, 1)
        for k in range(4):
            sx = ex - 9 + k * 6; ctx.move_to(sx, ey); ctx.curve_to(sx + 6 * math.sin(t * 5 + k), ey + 20, sx - 6, ey + 40, sx + 3, ey + 60); ctx.stroke()

def thumb(ctx, hw):
    rrect(ctx, hw[0] - 9, hw[1] - 64, 18, 44, 9); ctx.set_source_rgba(*hexc('#f2c9a5')); ctx.fill()

def chilli(ctx, x, y, s, ang):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.move_to(-10, -50); ctx.curve_to(40, -30, 30, 40, -30, 70); ctx.curve_to(-10, 20, -30, -20, -10, -50); ctx.close_path()
    ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    rrect(ctx, -22, -66, 24, 22, 8); ctx.set_source_rgba(*hexc('#2d6a4f')); ctx.fill(); ctx.restore()

def top_box(ctx, a=1.0, h=360):
    rrect(ctx, 60, 140, W - 120, h, 40); ctx.set_source_rgba(1, 1, 1, 0.93 * a); ctx.fill()

def icon_rice(ctx):
    ell(ctx, 0, 14, 52, 14, hexc('#e9ecef'))
    ctx.move_to(-52, 14); ctx.curve_to(-50, 66, 50, 66, 52, 14); ctx.close_path(); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill()
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#4361ee')); ctx.move_to(-48, 36); ctx.line_to(48, 36); ctx.stroke()
    ctx.move_to(-46, 10); ctx.curve_to(-30, -46, 30, -46, 46, 10); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.set_line_width(3); ctx.set_source_rgba(0.8, 0.8, 0.8, 1)
    for k in range(-2, 3): ctx.move_to(k * 14, -20); ctx.line_to(k * 14 + 5, -6); ctx.stroke()

def icon_bread(ctx):
    ctx.save(); ctx.scale(1, 0.32); circle(ctx, 0, 0, 82, hexc('#d9a05b')); ctx.restore()
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#b5762d'))
    for i in range(-2, 3): ctx.move_to(i * 30 - 10, -12); ctx.line_to(i * 30 + 10, -4); ctx.stroke()

def icon_milk(ctx):
    rrect(ctx, -34, -50, 68, 96, 6); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.move_to(-34, -50); ctx.line_to(0, -76); ctx.line_to(34, -50); ctx.close_path(); ctx.set_source_rgba(*hexc('#4cc9f0')); ctx.fill()
    rrect(ctx, -26, -18, 52, 36, 6); ctx.set_source_rgba(*hexc('#4cc9f0')); ctx.fill()
    mv.font(ctx, 22); e = ctx.text_extents("MILK"); ctx.move_to(-e.x_advance / 2, 7); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text("MILK")

# ---------- scenes ----------
def s0(ctx, t, d):
    begin_set(ctx); room(ctx, t); aunty(ctx, 830, 1290, t); counter(ctx, t)
    hl = hand_local(HAND_JAR_W[0] + 2 * math.sin(t * 22), HAND_JAR_W[1], t)
    wren(ctx, CX, GY, S, t, "point", hand=hl)
    table(ctx); bowl(ctx, *BOWL, 0, t)
    jar(ctx, *JAR_C, math.radians(8 + 3 * math.sin(t * 3)), 1.0, True)
    end_set(ctx); lights(ctx, t)
    a = ease(t / 0.3); top_box(ctx, a, 380)
    ctext(ctx, "I only wanted a little chilli.", 245, 64, hexc('#22223b', a), maxw=900)
    ctext(ctx, "The lid had other plans.", 450, 54, hexc(RED, ease((t - 1.7) / 0.4)), maxw=900)
    ai_tag(ctx, y=1860)

def s1(ctx, t, d):
    begin_set(ctx); room(ctx, t); aunty(ctx, 830, 1290, t); counter(ctx, t)
    k = ease(t / 0.7); th = math.radians(8 + 117 * k)
    hl = hand_local(*HAND_JAR_W, t)
    wren(ctx, CX, GY, S, t, "point", hand=hl, expr="shock" if t > 0.7 else "happy")
    table(ctx)
    g = ease((t - 0.75) / 2.6)
    bowl(ctx, *BOWL, g, t)
    lid_on = t < 0.55
    jar(ctx, *JAR_C, th, 1 - g * 0.95, lid_on)
    mx, my = JAR_C[0] + 70 * math.sin(math.radians(125)), JAR_C[1] - 70 * math.cos(math.radians(125))
    if not lid_on:
        tau = t - 0.55; ly = my - 1500 * tau + 1100 * tau * tau; lx = mx + 140 * tau
        rot = tau * 9
        if ly >= TABLE_Y - 14: ly, lx, rot = TABLE_Y - 14, mx + 140 * 1.54, 0.25
        ctx.save(); ctx.translate(lx, ly); ctx.rotate(rot); rrect(ctx, -54, -15, 108, 30, 8); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill(); ctx.restore()
    if t > 0.75 and g < 0.99:
        top_y = BOWL[1] - g * 135
        for i in range(26):
            p = ((t * 2.6 + i * 0.0385) % 1); fx = mx + (i % 7 - 3) * 7 * p; fy = my + p * (top_y - my)
            ell(ctx, fx, fy, 8, 3.5, hexc(['#d62828', '#f77f00', '#e63946'][i % 3]), i)
    end_set(ctx); lights(ctx, t)
    a = ease((t - 0.2) / 0.3); top_box(ctx, a, 380)
    ctext(ctx, "Then the lid fell off.", 245, 66, hexc('#22223b', a), maxw=900)
    ctext(ctx, "The. Whole. Jar.", 450, 62, hexc(RED, ease((t - 1.9) / 0.35)), maxw=900)
    ai_tag(ctx, y=1860)

def s2(ctx, t, d):
    begin_set(ctx); room(ctx, t); aunty(ctx, 830, 1290, t); counter(ctx, t)
    keys = [(0, L_REST), (0.8, L_MOUTH), (1.5, L_MOUTH), (2.2, L_REST), (2.9, L_MOUTH), (3.5, L_MOUTH), (4.2, L_REST)]
    hl = hand_path(t, keys)
    fl = max(0.0, min(1.0, (t - 2.9) / 1.0)); ex = "ouch" if t >= 3.2 else "happy"
    sh = math.sin(t * 45) * 3 if t > 3.4 else 0
    wren(ctx, CX + sh, GY, S, t, "point", hand=hl, flush=fl, expr=ex)
    table(ctx); bowl(ctx, *BOWL, 1.0, t, steam=False)
    hw = hand_world(hl, t, CX + sh)
    chopsticks(ctx, hw, t, strands=(hl[1] < -330 and t < 3.6))
    end_set(ctx); lights(ctx, t)
    a = ease((t - 0.2) / 0.3); top_box(ctx, a, 380)
    ctext(ctx, "Bite one: lovely.", 245, 62, hexc('#22223b', a), maxw=900)
    ctext(ctx, "Bite two: I can see through time.", 345, 54, hexc(RED, ease((t - 1.9) / 0.4)), maxw=880, lh=1.2)
    ai_tag(ctx, y=1860)

def s3(ctx, t, d):
    begin_set(ctx); room(ctx, t); aunty(ctx, 830, 1290, t); counter(ctx, t)
    keys = [(0, L_REST), (0.5, L_MOUTH), (0.9, L_MOUTH), (1.4, L_REST)]
    hl = hand_path(t, keys)
    fl = 1.0 if t < 3.2 else max(0.5, 1 - (t - 3.2) / 1.6)
    ex = "ouch" if t < 3.9 else "happy"
    sh = math.sin(t * 45) * 3 if t < 3.2 else 0
    wren(ctx, CX + sh, GY, S, t, "point", hand=hl, flush=fl, expr=ex)
    table(ctx); bowl(ctx, *BOWL, 1.0, t, steam=False)
    hw = hand_world(hl, t, CX + sh)
    glass(ctx, hw[0] + 12, hw[1] - 12, -0.5 if 0.45 < t < 1.0 else -0.1)
    lvl = 0.0
    if 0.95 < t < 2.1: lvl = math.sin((t - 0.95) / 1.15 * math.pi) ** 0.6
    mxw, myw = CX + sh, GY + S * (-505 + bobv(t))
    flame(ctx, mxw, myw + 8, t, lvl)
    end_set(ctx); lights(ctx, t)
    a = ease(t / 0.3); top_box(ctx, a, 380)
    ctext(ctx, "THE FIX", 215, 44, hexc(RED, a), maxw=900)
    if t < 2.0:
        ctext(ctx, "Water makes it worse.", 300, 66, hexc('#22223b', a * (1 - ease((t - 1.8) / 0.2))), maxw=900)
    else:
        ctext(ctx, "Rice, bread or milk.", 300, 66, hexc('#22223b', ease((t - 2.0) / 0.3)), maxw=900)
    for i, (fn, label, x) in enumerate(((icon_rice, "Rice", 250), (icon_bread, "Bread", 540), (icon_milk, "Milk", 830))):
        p = ease((t - 2.2 - i * 0.5) / 0.4)
        if p <= 0: continue
        y = 805 - (1 - p) * 40
        circle(ctx, x, y, 100 * p, (1, 1, 1, 0.92))
        ctx.save(); ctx.translate(x, y); ctx.scale(1.15 * p, 1.15 * p); fn(ctx); ctx.restore()
        if p > 0.9:
            mv.font(ctx, 34); e = ctx.text_extents(label); ctx.move_to(x - e.x_advance / 2, y + 150); ctx.set_source_rgba(*DARK); ctx.show_text(label)
    ai_tag(ctx, y=1860)

def s4(ctx, t, d):
    begin_set(ctx); room(ctx, t); aunty(ctx, 830, 1290, t, "sly", True); counter(ctx, t)
    keys = [(0, L_REST), (1.8, L_REST), (2.3, L_THUMB)]
    hl = hand_path(t, keys); sh = math.sin(t * 38) * 2
    wren(ctx, CX + sh, GY, S, t, "point", hand=hl, flush=0.75, expr="happy")
    table(ctx); bowl(ctx, *BOWL, 1.0, t, steam=False)
    if t > 2.1: thumb(ctx, hand_world(hl, t, CX + sh))
    bubble(ctx, 800, 935, "More?", 52, ease((t - 0.5) / 0.3), (800, 1010))
    bubble(ctx, 300, 960, "Yes, please!", 48, ease((t - 2.0) / 0.3), (385, 1085))
    end_set(ctx); lights(ctx, t)
    a = ease(t / 0.3); top_box(ctx, a, 400)
    ctext(ctx, "The aunty asked: ‘More?’", 240, 58, hexc('#22223b', a), maxw=900)
    ctext(ctx, "I said yes.", 340, 64, hexc(RED, ease((t - 2.0) / 0.35)), maxw=900)
    ctext(ctx, "Pride is a spice, too.", 430, 48, hexc('#5c2a1e', ease((t - 2.9) / 0.35)), bold=False, maxw=900)
    ai_tag(ctx, y=1860)

def s5(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    for i in range(5):
        chilli(ctx, (i * 260 + t * 120) % (W + 260) - 130, 1790 - abs(math.sin(t * 5 + i)) * 40, 0.8, 0.5 + 0.2 * math.sin(t * 3 + i))
    pop = ease(t / 0.5)
    wren(ctx, 540, 1640, 1.1 * (0.9 + 0.1 * pop), t, "wave", flush=0.45)
    a = ease((t - 0.2) / 0.4)
    ctext(ctx, "Send this to the friend who ‘can handle spicy’", 210 - (1 - a) * 30, 58, hexc('#22223b', a), maxw=900, lh=1.2)
    a2 = ease((t - 1.1) / 0.4)
    mv.font(ctx, 54); s2_ = "@wrentrips"; e = ctx.text_extents(s2_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 500, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 568); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s2_)
    ctext(ctx, "Follow for the next disaster", 690, 44, hexc('#5c2a1e', ease((t - 1.7) / 0.4)), bold=False)
    ai_tag(ctx, y=1890, dark=True)

SCENES = [(s0, 3.5), (s1, 4.5), (s2, 5.5), (s3, 5.0), (s4, 4.5), (s5, 4.5)]

def frame(fn, t, d):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    fn(ctx, t, d)
    a_in = 0 if fn is s0 else 1 - t / 0.25
    a_out = (t - (d - 0.6)) / 0.6 if fn is s5 else (t - (d - 0.2)) / 0.2
    a = max(a_in, a_out, 0)
    if a > 0:
        ctx.set_source_rgba(*hexc('#fff3e0', min(1, ease(a)))); ctx.paint()
    return surf

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        from PIL import Image
        picks = [(s0, 2.6), (s1, 0.45), (s1, 2.8), (s2, 1.1), (s2, 4.6), (s3, 1.5), (s3, 3.4), (s4, 3.6), (s5, 3.0), (s2, 3.3)]
        ims = []
        dmap = {fn: d for fn, d in SCENES}
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((324, 576)))
        c = Image.new("RGB", (334 * 5, 586 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 5) * 334, (i // 5) * 586))
        c.save(f"{OUT}/contact.png")
    else:
        files = []
        for i, (fn, d) in enumerate(SCENES):
            tmp, final = f"{OUT}/s{i}_tmp.mp4", f"{OUT}/s{i}.mp4"
            p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                                  "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp],
                                 stdin=subprocess.PIPE)
            for k in range(int(round(d * 30))):
                p.stdin.write(bytes(frame(fn, k / 30, d).get_data()))
            p.stdin.close()
            if p.wait() == 0: os.replace(tmp, final)
            files.append(final)
        with open(f"{OUT}/list.txt", "w") as f:
            for fl in files: f.write(f"file '{fl}'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy", f"{OUT}/video_only.mp4"], check=True)
        print("video done")

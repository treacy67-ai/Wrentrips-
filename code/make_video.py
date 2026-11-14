import cairo, math, random, subprocess, os, sys, wave
import numpy as np

W, H, FPS = 1080, 1920, 30
OUT = "/home/claude/wren"
random.seed(7)

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

def vgrad(ctx, top, bottom):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *hexc(top)[:3]); g.add_color_stop_rgb(1, *hexc(bottom)[:3])
    ctx.set_source(g); ctx.paint()

def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()

def circle(ctx, x, y, r, col):
    ctx.arc(x, y, r, 0, 2 * math.pi); ctx.set_source_rgba(*col); ctx.fill()

def font(ctx, size, bold=True):
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def wrap(ctx, text, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if ctx.text_extents(t).x_advance > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur); return lines

def ctext(ctx, text, y, size, col, bold=True, shadow=False, maxw=940, lh=1.25):
    font(ctx, size, bold)
    lines = wrap(ctx, text, maxw)
    for i, ln in enumerate(lines):
        e = ctx.text_extents(ln); x = (W - e.x_advance) / 2; yy = y + i * size * lh
        if shadow:
            ctx.move_to(x + 4, yy + 5); ctx.set_source_rgba(0, 0, 0, 0.25 * col[3]); ctx.show_text(ln)
        ctx.move_to(x, yy); ctx.set_source_rgba(*col); ctx.show_text(ln)
    return len(lines)

def caption(ctx, t, label, text, y=1480, delay=0.6):
    a = ease((t - delay) / 0.5)
    if a <= 0: return
    off = (1 - a) * 40
    font(ctx, 54); lines = wrap(ctx, text, 820)
    h = 120 + len(lines) * 68
    rrect(ctx, 90, y + off, W - 180, h, 44); ctx.set_source_rgba(1, 1, 1, 0.93 * a); ctx.fill()
    font(ctx, 34); e = ctx.text_extents(label)
    rrect(ctx, (W - e.x_advance) / 2 - 26, y + off + 26, e.x_advance + 52, 56, 28)
    ctx.set_source_rgba(*hexc('#e63946', a)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, y + off + 66); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    ctext(ctx, text, y + off + 150, 52, hexc('#22223b', a), maxw=820, lh=1.3)

def ai_tag(ctx, y=1850, dark=False):
    font(ctx, 26, False); s = "AI-generated character"
    e = ctx.text_extents(s); x = (W - e.x_advance) / 2
    rrect(ctx, x - 20, y - 36, e.x_advance + 40, 50, 25)
    ctx.set_source_rgba(0, 0, 0, 0.35) if not dark else ctx.set_source_rgba(1, 1, 1, 0.6); ctx.fill()
    ctx.move_to(x, y); ctx.set_source_rgba(1, 1, 1, 1) if not dark else ctx.set_source_rgba(0.15, 0.15, 0.2, 1)
    ctx.show_text(s)

# ---------- Wren, the character ----------
SKIN, HAIR, COAT, SCARF, PACK = hexc('#f2c9a5'), hexc('#dfe3ea'), hexc('#2a9d8f'), hexc('#e63946'), hexc('#c47a3a')

def limb(ctx, sx, sy, ang, side, length, col, width=44, hand=True):
    dx, dy = side * math.sin(ang) * length, math.cos(ang) * length
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(width)
    ctx.move_to(sx, sy); ctx.line_to(sx + dx, sy + dy); ctx.set_source_rgba(*col); ctx.stroke()
    if hand: circle(ctx, sx + dx, sy + dy, 24, SKIN)
    return sx + dx, sy + dy

def mixc(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(4))

def wren(ctx, cx, gy, s, t, mode="wave", blink_seed=0.0, flush=0.0, expr="happy", hand=(180, -300)):
    ctx.save(); ctx.translate(cx, gy); ctx.scale(s, s)
    bob = math.sin(t * 2 * math.pi * 1.1) * 5
    # shadow
    ctx.save(); ctx.scale(1, 0.18); circle(ctx, 0, 0, 170, (0, 0, 0, 0.15)); ctx.restore()
    # legs + shoes
    for lx in (-42, 42):
        ctx.set_line_width(38); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(lx, -190); ctx.line_to(lx, -25); ctx.set_source_rgba(*hexc('#3b3b58')); ctx.stroke()
        ctx.save(); ctx.translate(lx + (8 if lx > 0 else -8), -14); ctx.scale(1.6, 0.8)
        circle(ctx, 0, 0, 26, hexc('#7a3e2b')); ctx.restore()
    ctx.translate(0, bob)
    # backpack peeking out
    rrect(ctx, -150, -440, 300, 250, 50); ctx.set_source_rgba(*PACK); ctx.fill()
    # arms behind coat for down poses
    sh_y = -405
    if mode == "wave":
        a = math.radians(150 + 22 * math.sin(t * 2 * math.pi * 1.6))
        limb(ctx, -96, sh_y, math.radians(14), -1, 175, COAT)
    elif mode == "cheer":
        a = None
    elif mode == "lantern":
        a = None
    elif mode == "point":
        a = None
    # coat
    ctx.move_to(-92, -440); ctx.line_to(92, -440); ctx.line_to(128, -170)
    ctx.curve_to(60, -150, -60, -150, -128, -170); ctx.close_path(); ctx.set_source_rgba(*COAT); ctx.fill()
    for by in (-370, -310, -250):
        circle(ctx, 0, by, 9, hexc('#f4d35e'))
    # straps
    ctx.set_line_width(18); ctx.set_source_rgba(*hexc('#8a5226'))
    for sx in (-55, 55):
        ctx.move_to(sx, -440); ctx.line_to(sx * 1.25, -300); ctx.stroke()
    # arms in front
    if mode == "wave":
        limb(ctx, 96, sh_y, a, 1, 175, COAT)
    elif mode == "cheer":
        w = 10 * math.sin(t * 2 * math.pi * 2)
        limb(ctx, -96, sh_y, math.radians(155 + w), -1, 175, COAT)
        limb(ctx, 96, sh_y, math.radians(155 - w), 1, 175, COAT)
    elif mode == "point":
        limb(ctx, -96, sh_y, math.radians(14), -1, 175, COAT)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(44)
        ctx.move_to(96, sh_y); ctx.line_to(hand[0], hand[1]); ctx.set_source_rgba(*COAT); ctx.stroke()
        circle(ctx, hand[0], hand[1], 24, SKIN)
    elif mode == "lantern":
        limb(ctx, -96, sh_y, math.radians(14), -1, 175, COAT)
        hx, hy = limb(ctx, 96, sh_y, math.radians(70), 1, 170, COAT)
        sw = math.sin(t * 2 * math.pi * 0.8) * 0.15
        lx, ly = hx + math.sin(sw) * 90, hy + math.cos(sw) * 90
        ctx.set_line_width(4); ctx.set_source_rgba(0.2, 0.2, 0.2, 1); ctx.move_to(hx, hy); ctx.line_to(lx, ly); ctx.stroke()
        lantern(ctx, lx, ly + 50, 1.0, '#ff7b39')
    # scarf
    ctx.save(); ctx.translate(0, -445); ctx.scale(1.0, 0.42); circle(ctx, 0, 0, 92, SCARF); ctx.restore()
    tail = math.sin(t * 2 * math.pi * 0.9) * 10
    ctx.move_to(30, -430); ctx.line_to(78 + tail, -320); ctx.line_to(42 + tail, -310); ctx.line_to(8, -430)
    ctx.close_path(); ctx.set_source_rgba(*SCARF); ctx.fill()
    # head
    hy = -545
    skin_h = mixc(SKIN, hexc('#e5483f'), 0.8 * flush)
    circle(ctx, -86, hy + 5, 20, skin_h); circle(ctx, 86, hy + 5, 20, skin_h)
    circle(ctx, 0, hy, 88, skin_h)
    # hair: bun, cap, side puffs
    circle(ctx, 0, hy - 108, 46, HAIR)
    ctx.arc(0, hy, 92, math.radians(190), math.radians(350)); ctx.close_path(); ctx.set_source_rgba(*HAIR); ctx.fill()
    for px, py in ((-78, hy - 30), (78, hy - 30), (-50, hy - 70), (50, hy - 70), (0, hy - 84)):
        circle(ctx, px, py, 30, HAIR)
    # cheeks
    circle(ctx, -50, hy + 32, 17, hexc('#f28b82', 0.55)); circle(ctx, 50, hy + 32, 17, hexc('#f28b82', 0.55))
    # eyes (blink)
    ph = (t + blink_seed) % 3.2
    sy = 0.12 if ph < 0.12 else 1.0
    if expr == "ouch":
        ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgba(*hexc('#2b2d42'))
        for sg in (-1, 1):
            ctx.move_to(sg * 43, hy - 8); ctx.line_to(sg * 25, hy + 2); ctx.line_to(sg * 43, hy + 12); ctx.stroke()
    elif expr == "shock":
        for ex in (-33, 33):
            circle(ctx, ex, hy + 2, 14, (1, 1, 1, 1)); circle(ctx, ex, hy + 2, 5.5, hexc('#2b2d42'))
    else:
        for ex in (-33, 33):
            ctx.save(); ctx.translate(ex, hy + 2); ctx.scale(1, sy); circle(ctx, 0, 0, 8, hexc('#2b2d42')); ctx.restore()
    # glasses
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#5c4033'))
    for ex in (-33, 33):
        ctx.arc(ex, hy + 2, 27, 0, 2 * math.pi); ctx.stroke()
    ctx.move_to(-6, hy); ctx.line_to(6, hy); ctx.stroke()
    # smile
    if expr == "ouch" or expr == "shock":
        ry = (17 + 4 * math.sin(t * 14)) if expr == "ouch" else 15
        rx = 24 if expr == "ouch" else 11
        ctx.save(); ctx.translate(0, hy + 44); ctx.scale(rx, ry); circle(ctx, 0, 0, 1, hexc('#7a1f2b')); ctx.restore()
        if expr == "ouch":
            ctx.save(); ctx.translate(0, hy + 54); ctx.scale(13, 7); circle(ctx, 0, 0, 1, hexc('#ff8fa3')); ctx.restore()
    else:
        ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.arc(0, hy + 30, 26, math.radians(25), math.radians(155)); ctx.set_source_rgba(*hexc('#7a3e2b')); ctx.stroke()
    if flush > 0.45 and expr == "ouch":
        for sg in (-1, 1):
            for k in range(2):
                ph = (t * 1.4 + k * 0.5 + (0.25 if sg > 0 else 0)) % 1
                ctx.save(); ctx.translate(sg * (40 + ph * 4), hy + 24 + ph * 85); ctx.scale(6, 9)
                circle(ctx, 0, 0, 1, hexc('#5ec8ff', 1 - ph * 0.9)); ctx.restore()
    if flush > 0.3:
        lvl = min(1, (flush - 0.3) / 0.4)
        for sg in (-1, 1):
            for k in range(3):
                ph = (t * 1.1 + k / 3 + (0.17 if sg > 0 else 0)) % 1
                circle(ctx, sg * (96 + ph * 22 + 8 * math.sin(ph * 8 + k)), hy - 5 - ph * 170, 16 + ph * 26, (1, 1, 1, (1 - ph) * 0.9 * lvl))
    ctx.restore()

def lantern(ctx, x, y, s, col):
    g = cairo.RadialGradient(x, y, 5, x, y, 130 * s)
    r, gg, b, _ = hexc(col); g.add_color_stop_rgba(0, r, gg, b, 0.45); g.add_color_stop_rgba(1, r, gg, b, 0)
    ctx.set_source(g); ctx.arc(x, y, 130 * s, 0, 2 * math.pi); ctx.fill()
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.save(); ctx.scale(1, 1.15); circle(ctx, 0, 0, 42, hexc(col)); ctx.restore()
    circle(ctx, -10, -10, 18, (1, 1, 0.8, 0.35))
    for yy in (-50, 46):
        rrect(ctx, -22, yy - 6, 44, 12, 4); ctx.set_source_rgba(*hexc('#5c3d1e')); ctx.fill()
    ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#ffd166'))
    ctx.move_to(0, 52); ctx.line_to(0, 80); ctx.stroke()
    ctx.restore()

def cloud(ctx, x, y, s, a=0.95):
    for dx, dy, r in ((0, 0, 60), (55, -25, 70), (115, 0, 55), (60, 15, 60)):
        circle(ctx, x + dx * s, y + dy * s, r * s, (1, 1, 1, a))

def suitcase(ctx, x, y, s, t):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#2b2d42'))
    rrect(ctx, -45, -330, 90, 70, 20); ctx.stroke()
    rrect(ctx, -110, -280, 220, 280, 30); ctx.set_source_rgba(*hexc('#457b9d')); ctx.fill()
    for i, (sx, sy, c) in enumerate(((-55, -210, '#f4d35e'), (40, -160, '#e63946'), (-40, -90, '#ffffff'), (50, -60, '#90be6d'))):
        ctx.save(); ctx.translate(sx, sy); ctx.rotate(0.3 * (i - 1.5))
        rrect(ctx, -32, -24, 64, 48, 12); ctx.set_source_rgba(*hexc(c)); ctx.fill(); ctx.restore()
    ctx.restore()

def plane(ctx, x, y, s, ang, t):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.move_to(-120, -10); ctx.line_to(-170, -110); ctx.line_to(-120, -110); ctx.line_to(-50, -20); ctx.close_path()
    ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    ctx.save(); ctx.scale(1, 0.26); circle(ctx, 0, 0, 200, (1, 1, 1, 1)); ctx.restore()
    ctx.move_to(-30, 10); ctx.line_to(-110, 120); ctx.line_to(-60, 120); ctx.line_to(60, 10); ctx.close_path()
    ctx.set_source_rgba(*hexc('#8d99ae')); ctx.fill()
    for wx in range(-90, 150, 34):
        circle(ctx, wx, -10, 9, hexc('#457b9d'))
    # Wren peeking from a big window
    circle(ctx, 150, -6, 30, hexc('#bde0fe'))
    circle(ctx, 150, -4, 18, SKIN); circle(ctx, 150, -24, 10, HAIR)
    ctx.restore()

# ---------- scenes ----------
def scene_intro(ctx, t, d):
    vgrad(ctx, '#ffb385', '#ffe5c4')
    circle(ctx, 820, 520, 150, hexc('#fff1c1', 0.9))
    cloud(ctx, -60 + t * 25, 600, 1.0); cloud(ctx, 640 - t * 15, 760, 0.7, 0.8)
    ctx.rectangle(0, 1380, W, H); ctx.set_source_rgba(*hexc('#f4a261')); ctx.fill()
    ctx.rectangle(0, 1380, W, 14); ctx.set_source_rgba(*hexc('#e76f51')); ctx.fill()
    pop = max(0.02, ease(t / 0.6))
    suitcase(ctx, 800, 1400, 0.95 * pop, t)
    wren(ctx, 430, 1400, 1.05 * (0.85 + 0.15 * pop), t, "wave")
    a = ease((t - 0.3) / 0.5)
    ctext(ctx, "Meet Wren.", 250 - (1 - a) * 30, 130, (1, 1, 1, a), shadow=True)
    a2 = ease((t - 1.1) / 0.5)
    ctext(ctx, "72. Retired teacher. Full-time wanderer.", 380, 52, hexc('#5c2a1e', a2), maxw=860)
    a3 = ease((t - 2.4) / 0.5)
    ctx.save(); ctx.set_source_rgba(1, 1, 1, 0)
    rrect(ctx, 140, 1530 + (1 - a3) * 30, 800, 130, 65); ctx.set_source_rgba(1, 1, 1, 0.92 * a3); ctx.fill()
    ctext(ctx, "“I didn’t retire. I re-routed.”", 1612 + (1 - a3) * 30, 46, hexc('#22223b', a3), maxw=760)
    ctx.restore()
    ai_tag(ctx)

def scene_flight(ctx, t, d):
    vgrad(ctx, '#6cb4e4', '#e3f4ff')
    for i, (x0, y0, sp, sc) in enumerate(((100, 300, 40, 1.2), (700, 520, 70, 0.8), (300, 1150, 110, 1.4), (850, 1000, 55, 1.0), (-200, 800, 90, 0.9))):
        cloud(ctx, (x0 - t * sp) % (W + 500) - 250, y0, sc, 0.9)
    p = t / d
    x = -250 + p * (W + 500); y = 820 - math.sin(p * math.pi) * 120 - p * 100
    ang = -0.12 + 0.18 * (p - 0.5)
    ctx.set_line_width(10); ctx.set_dash([28, 22]); ctx.set_source_rgba(1, 1, 1, 0.85)
    ctx.move_to(-260, 820)
    for k in range(1, 41):
        q = p * k / 40; ctx.line_to(-250 + q * (W + 500) - 200, 820 - math.sin(q * math.pi) * 120 - q * 100)
    ctx.stroke(); ctx.set_dash([])
    plane(ctx, x, y, 1.15, ang, t)
    a = ease((t - 0.2) / 0.5)
    ctext(ctx, "First stop: wherever the cheap flight goes", 260, 60, (1, 1, 1, a), shadow=True, maxw=880)
    caption(ctx, t, "DAY 1", "Packed light. Mostly snacks.", delay=1.0)
    ai_tag(ctx)

def scene_mountain(ctx, t, d):
    vgrad(ctx, '#ff8c69', '#6d597a')
    circle(ctx, 540, 720 + t * 28, 170, hexc('#ffd56b', 0.95))
    layers = (('#b5838d', 900, 0.0021, 160), ('#6d597a', 1050, 0.0034, 120), ('#355070', 1220, 0.0052, 90))
    for col, base, f, amp in layers:
        ctx.move_to(0, H)
        for x in range(0, W + 20, 20):
            ctx.line_to(x, base - amp * abs(math.sin(x * f + base)) - 30 * math.sin(x * f * 3))
        ctx.line_to(W, H); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    # ledge
    ctx.move_to(520, 1330); ctx.curve_to(700, 1290, 950, 1290, W, 1310); ctx.line_to(W, H); ctx.line_to(480, H); ctx.close_path()
    ctx.set_source_rgba(*hexc('#22223b')); ctx.fill()
    # birds
    ctx.set_line_width(5); ctx.set_source_rgba(0.15, 0.1, 0.2, 0.7)
    for i in range(4):
        bx = 120 + i * 90 + t * 60; by = 520 + i * 35 + math.sin(t * 3 + i) * 10; fl = 14 + 8 * math.sin(t * 9 + i)
        ctx.move_to(bx - 22, by - fl); ctx.line_to(bx, by); ctx.line_to(bx + 22, by - fl); ctx.stroke()
    mode = "cheer" if t > 2.2 else "wave"
    wren(ctx, 790, 1312, 0.62, t, mode)
    # walking stick
    if mode == "wave":
        pass
    a = ease((t - 0.2) / 0.5)
    ctext(ctx, "Sunset hike, 4 km", 260, 66, (1, 1, 1, a), shadow=True)
    caption(ctx, t, "DAY 4", "Made it to the lookout. Slowly. Proudly.", delay=1.0)
    ai_tag(ctx)

def scene_lanterns(ctx, t, d):
    vgrad(ctx, '#1d1b3a', '#4a2f63')
    random.seed(3)
    for i in range(40):
        circle(ctx, random.uniform(0, W), random.uniform(0, 700), random.uniform(1.5, 3.5), (1, 1, 1, 0.4 + 0.4 * math.sin(t * 3 + i)))
    for bx, bw, bh in ((0, 260, 900), (240, 220, 760), (800, 280, 940), (600, 220, 700)):
        ctx.rectangle(bx, H - bh, bw, bh); ctx.set_source_rgba(*hexc('#2d2347')); ctx.fill()
        for wy in range(H - bh + 60, H - 300, 130):
            for wx in range(bx + 40, bx + bw - 40, 90):
                rrect(ctx, wx, wy, 46, 64, 8); ctx.set_source_rgba(*hexc('#ffb86b', 0.75)); ctx.fill()
    cols = ['#ff4d4d', '#ff9f1c', '#ffd166', '#ff7b39', '#ef476f']
    for row, (y0, sag) in enumerate(((560, 90), (760, 70))):
        ctx.set_line_width(3); ctx.set_source_rgba(0.1, 0.08, 0.1, 1)
        ctx.move_to(-20, y0)
        ctx.curve_to(W / 3, y0 + sag, 2 * W / 3, y0 + sag, W + 20, y0); ctx.stroke()
        for k in range(7):
            u = (k + 0.5 + row * 0.5) / 7.5; x = u * W
            yy = y0 + sag * 0.75 * 4 * u * (1 - u)
            sw = math.sin(t * 2.2 + k + row) * 0.12
            lx, ly = x + math.sin(sw) * 40, yy + math.cos(sw) * 40
            ctx.set_line_width(2); ctx.move_to(x, yy); ctx.line_to(lx, ly); ctx.stroke()
            lantern(ctx, lx, ly + 40, 0.75, cols[(k + row) % 5])
    ctx.rectangle(0, 1420, W, H); ctx.set_source_rgba(*hexc('#3a2a4f')); ctx.fill()
    wren(ctx, 430, 1430, 0.85, t, "lantern")
    for i in range(14):
        sx = (i * 83 + t * 30) % W; sy = 1300 - ((t * 60 + i * 97) % 700)
        circle(ctx, sx, sy, 4, hexc('#ffd166', 0.6))
    a = ease((t - 0.2) / 0.5)
    ctext(ctx, "Lantern night", 260, 76, (1, 1, 1, a), shadow=True)
    caption(ctx, t, "DAY 7", "Best night of my life (so far).", y=1530, delay=1.0)
    ai_tag(ctx)

def scene_outro(ctx, t, d):
    vgrad(ctx, '#fff3e0', '#ffd6a5')
    ctx.set_line_width(8); ctx.set_dash([24, 18]); ctx.set_source_rgba(*hexc('#e63946', 0.5))
    ctx.move_to(100, 1650); ctx.curve_to(300, 1100, 800, 1500, 980, 900); ctx.stroke(); ctx.set_dash([])
    for px, py in ((100, 1650), (980, 900)):
        circle(ctx, px, py - 30, 28, hexc('#e63946')); circle(ctx, px, py - 30, 11, (1, 1, 1, 1))
    pop = ease(t / 0.5)
    wren(ctx, 540, 1640, 1.15 * (0.9 + 0.1 * pop), t, "cheer" if t < 1.6 else "wave")
    a = ease((t - 0.3) / 0.5)
    ctext(ctx, "Age is just a boarding pass.", 230 - (1 - a) * 30, 96, hexc('#22223b', a), maxw=900, lh=1.15)
    a2 = ease((t - 1.2) / 0.5)
    font(ctx, 54); s = "@wrentrips"; e = ctx.text_extents(s)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 520, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc('#e63946', a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 588); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s)
    a3 = ease((t - 1.8) / 0.5)
    ctext(ctx, "Follow for the next stop", 700, 44, hexc('#5c2a1e', a3), bold=False)
    ai_tag(ctx, dark=True)

SCENES = [(scene_intro, 5.0), (scene_flight, 4.5), (scene_mountain, 5.0), (scene_lanterns, 5.0), (scene_outro, 4.5)]

def frame(fn, t, d):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    fn(ctx, t, d)
    # soft dip transitions
    a = max(1 - t / 0.3, (t - (d - 0.25)) / 0.25 if fn is not scene_outro else (t - (d - 0.6)) / 0.6, 0)
    if a > 0:
        ctx.set_source_rgba(*hexc('#fff3e0', min(1, ease(a)))); ctx.paint()
    return surf

def preview():
    for i, (fn, d) in enumerate(SCENES):
        frame(fn, d * 0.75, d).write_to_png(f"{OUT}/preview_{i}.png")

def render():
    files = []
    for i, (fn, d) in enumerate(SCENES):
        tmp, final = f"{OUT}/s{i}_tmp.mp4", f"{OUT}/s{i}.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                              "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        for k in range(int(round(d * FPS))):
            p.stdin.write(bytes(frame(fn, k / FPS, d).get_data()))
        p.stdin.close()
        if p.wait() == 0: os.replace(tmp, final)
        files.append(final)
    with open(f"{OUT}/list.txt", "w") as f:
        for fl in files: f.write(f"file '{fl}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy", f"{OUT}/video_only.mp4"], check=True)

def music(total):
    sr = 44100; n = int(total * sr); out = np.zeros(n)
    bpm = 96; beat = 60 / bpm
    def note(f, start, dur, amp, dec=3.0):
        i0 = int(start * sr); m = min(int(dur * sr), n - i0)
        if m <= 0: return
        tt = np.arange(m) / sr
        w = (np.sin(2 * np.pi * f * tt) + 0.45 * np.sin(4 * np.pi * f * tt) * np.exp(-2 * tt) + 0.2 * np.sin(6 * np.pi * f * tt) * np.exp(-4 * tt))
        env = np.exp(-dec * tt) * np.minimum(1, tt / 0.005)
        out[i0:i0 + m] += amp * w * env
    mid = lambda m: 440 * 2 ** ((m - 69) / 12)
    chords = [[60, 64, 67, 72], [65, 69, 72, 77], [57, 60, 64, 69], [55, 59, 62, 67]]
    bass = [36, 41, 33, 31]
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]
    t = 0.0; bar = 0
    while t < total:
        ch = chords[bar % 4]
        note(mid(bass[bar % 4]), t, beat * 4, 0.35, 1.2)
        for k, idx in enumerate(pattern):
            note(mid(ch[idx]), t + k * beat / 2, beat * 2, 0.16, 3.5)
        if bar % 2 == 1:
            note(mid(ch[3] + 12), t + beat * 3, beat * 1.5, 0.08, 2.5)
        t += beat * 4; bar += 1
    rng = np.random.default_rng(1)
    for k in range(int(total / (beat / 2))):
        if k % 2 == 1:
            i0 = int(k * beat / 2 * sr); m = min(int(0.06 * sr), n - i0)
            if m > 0: out[i0:i0 + m] += 0.05 * rng.standard_normal(m) * np.exp(-np.arange(m) / sr * 60)
    fade = int(1.5 * sr); out[-fade:] *= np.linspace(1, 0, fade)
    out[:int(0.05 * sr)] *= np.linspace(0, 1, int(0.05 * sr))
    out = out / np.max(np.abs(out)) * 0.8
    with wave.open(f"{OUT}/music.wav", "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        preview()
    else:
        render()
        total = sum(d for _, d in SCENES)
        music(total)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/video_only.mp4", "-i", f"{OUT}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest",
                        f"{OUT}/wren_wanders_reel.mp4"], check=True)
        print("done")

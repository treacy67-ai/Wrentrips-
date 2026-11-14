import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = "/home/claude/wren/ep13"
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'
INK = '#1f3552'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))

WX, LX, AX, GY = 190, 540, 885, 1640

# ------------------------------------------------------------ Andy
def andy(ctx, cx, gy, s, t, expr="smile", flush=0.0, flex=0.0):
    ctx.save(); ctx.translate(cx, gy); ctx.scale(s, s); ctx.translate(0, math.sin(t * 2 * math.pi * 1.0) * 4)
    SK = hexc('#d9a27a'); ink = hexc(INK)
    # torso (tank top)
    rrect(ctx, -130, -455, 260, 340, 64); ctx.set_source_rgba(*hexc('#1b1b2b')); ctx.fill()
    ctx.move_to(-48, -455); ctx.line_to(48, -455); ctx.line_to(0, -350); ctx.close_path(); ctx.set_source_rgba(*SK); ctx.fill()          # neckline
    circle(ctx, -4, -400, 17, hexc('#c1121f')); circle(ctx, -4, -400, 8, hexc('#ff6b6b'))
    ctx.set_line_width(5); ctx.set_source_rgba(*ink); ctx.arc(-4, -400, 18, 0, 6.3); ctx.stroke()
    # arms with sleeve tattoos
    def limb(sx, sy, hx, hy):
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_width(68); ctx.set_source_rgba(*SK); ctx.move_to(sx, sy); ctx.line_to(hx, hy); ctx.stroke()
        dx, dy = hx - sx, hy - sy; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
        ctx.set_line_cap(cairo.LINE_CAP_BUTT); ctx.set_line_width(7); ctx.set_source_rgba(*ink)
        for p in (0.62, 0.72):
            px, py = sx + dx * p, sy + dy * p; ctx.move_to(px - nx * 30, py - ny * 30); ctx.line_to(px + nx * 30, py + ny * 30); ctx.stroke()
        mx, my = sx + dx * 0.4, sy + dy * 0.4
        circle(ctx, mx, my, 15, hexc('#c1121f')); circle(ctx, mx, my, 7, hexc('#ffd166'))
        ctx.set_line_width(4); ctx.arc(mx, my, 16, 0, 6.3); ctx.stroke()
        circle(ctx, hx, hy, 36, SK)
    limb(-128, -418, -190, -190)
    limb(128, -418, 190 + 40 * flex, -190 - 330 * flex)
    # neck + head
    rrect(ctx, -44, -520, 88, 80, 20); ctx.set_source_rgba(*SK); ctx.fill()
    skin_h = SK if flush <= 0 else tuple(a * (1 - 0.45 * flush) + b * 0.45 * flush for a, b in zip(SK, hexc('#ef6f6c')))
    circle(ctx, -96, -585, 22, SK); circle(ctx, 96, -585, 22, SK)
    ctx.set_line_width(6); ctx.set_source_rgba(*ink); ctx.arc(-96, -570, 12, 0, 6.3); ctx.stroke(); ctx.arc(96, -570, 12, 0, 6.3); ctx.stroke()
    circle(ctx, 0, -590, 98, skin_h)
    HAIRC = hexc('#e6e9ef')
    ctx.move_to(-96, -596); ctx.curve_to(-104, -700, 104, -700, 96, -596); ctx.curve_to(70, -650, 40, -664, 0, -652); ctx.curve_to(-40, -664, -70, -650, -96, -596)
    ctx.set_source_rgba(*HAIRC); ctx.fill()
    for hx_, hy_, r_ in ((-92, -610, 22), (92, -610, 22), (-56, -666, 28), (0, -678, 32), (56, -666, 28)): circle(ctx, hx_, hy_, r_, HAIRC)
    ctx.set_line_width(3); ctx.set_source_rgba(0.6, 0.64, 0.72, 0.8)
    for k in range(5): ctx.move_to(-48 + k * 24, -700); ctx.curve_to(-40 + k * 24, -680, -36 + k * 24, -668, -30 + k * 24, -660); ctx.stroke()
    # age lines
    ctx.set_line_width(4); ctx.set_source_rgba(0.55, 0.36, 0.25, 0.55)
    for yy in (-640, -626): ctx.move_to(-40, yy); ctx.curve_to(-14, yy - 6, 14, yy - 6, 40, yy); ctx.stroke()
    for sg in (-1, 1):
        for dy in (-6, 6): ctx.move_to(sg * 62, -594 + dy); ctx.line_to(sg * 80, -594 + dy * 1.8); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(9); ctx.set_source_rgba(*hexc('#b8bec9'))
    ctx.move_to(-62, -625); ctx.line_to(-18, -632); ctx.stroke(); ctx.move_to(18, -632); ctx.line_to(62, -625); ctx.stroke()   # brows
    ex_style = "wide" if expr == "nervous" else ("closed" if expr == "touched" else "open")
    for ex in (-36, 36):
        if ex_style == "wide":
            circle(ctx, ex, -598, 17, (1, 1, 1, 1)); circle(ctx, ex + (3 if t % 1.6 < 0.8 else -3), -598, 7, hexc('#2b2d42'))
        elif ex_style == "closed":
            ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#2b2d42')); ctx.arc(ex, -602, 13, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
        else: circle(ctx, ex, -598, 8, hexc('#2b2d42'))
    circle(ctx, -58, -560, 15, hexc('#f28b82', 0.35 + 0.4 * flush)); circle(ctx, 58, -560, 15, hexc('#f28b82', 0.35 + 0.4 * flush))
    ctx.move_to(-52, -552); ctx.curve_to(-30, -566, -12, -560, 0, -552); ctx.curve_to(12, -560, 30, -566, 52, -552)         # moustache
    ctx.curve_to(30, -534, 12, -540, 0, -538); ctx.curve_to(-12, -540, -30, -534, -52, -552); ctx.set_source_rgba(*hexc('#e1e4ea')); ctx.fill()
    ctx.move_to(-34, -520); ctx.curve_to(-30, -480, 30, -480, 34, -520); ctx.curve_to(10, -508, -10, -508, -34, -520); ctx.set_source_rgba(*hexc('#e1e4ea')); ctx.fill()  # goatee
    if expr == "nervous":
        ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#7a3e2b')); ctx.move_to(-22, -528); ctx.curve_to(-10, -538, 0, -520, 10, -532); ctx.curve_to(16, -538, 20, -530, 24, -528); ctx.stroke()
        for k in range(3):
            ph = (t * 1.3 + k / 3) % 1; circle(ctx, 84 + k * 6, -640 + ph * 90, 9, hexc('#7fc4ee', 1 - ph))
    else:
        ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#7a3e2b')); ctx.arc(0, -545, 22, 0.2 * math.pi, 0.8 * math.pi); ctx.stroke()
    ctx.restore()

# ------------------------------------------------------------ restaurant
def restaurant(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, 1500); g.add_color_stop_rgb(0, *hexc('#2b1230')[:3]); g.add_color_stop_rgb(1, *hexc('#5a2340')[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1500); ctx.fill()
    for k in range(6):                                                # wall panels
        rrect(ctx, 40 + k * 170, 760, 140, 560, 14); ctx.set_source_rgba(1, 1, 1, 0.04); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(1, 0.9, 0.6, 0.5); ctx.move_to(-20, 640); ctx.curve_to(300, 720, 780, 720, 1100, 640); ctx.stroke()   # string lights
    for k in range(12):
        x = 10 + k * 90; y = 646 + 62 * math.sin((x / 1080) * math.pi)
        tw = 0.65 + 0.35 * math.sin(t * 4 + k * 1.7)
        gl = cairo.RadialGradient(x, y, 2, x, y, 46); gl.add_color_stop_rgba(0, 1, 0.85, 0.45, 0.8 * tw); gl.add_color_stop_rgba(1, 1, 0.85, 0.45, 0)
        ctx.set_source(gl); ctx.rectangle(x - 50, y - 50, 100, 100); ctx.fill(); circle(ctx, x, y, 8, hexc('#fff3b0'))
    for k, (bx, by, bw, bh) in enumerate(((90, 830, 190, 140), (445, 810, 190, 170), (800, 830, 190, 140))):          # framed pictures
        rrect(ctx, bx, by, bw, bh, 8); ctx.set_source_rgba(*hexc('#a0622d')); ctx.fill()
        rrect(ctx, bx + 12, by + 12, bw - 24, bh - 24, 4); ctx.set_source_rgba(*hexc(['#e9c46a', '#8ecae6', '#f4a261'][k], 0.85)); ctx.fill()
        ctx.move_to(bx + 12, by + bh - 12); ctx.line_to(bx + bw * 0.4, by + bh * 0.45); ctx.line_to(bx + bw * 0.62, by + bh * 0.7); ctx.line_to(bx + bw - 12, by + bh * 0.4); ctx.line_to(bx + bw - 12, by + bh - 12)
        ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.fill()

def table(ctx, t, spaghetti=False, strand=None):
    ctx.rectangle(0, 1500, W, H - 1500); ctx.set_source_rgba(*hexc('#8b1e2d')); ctx.fill()
    for k in range(14): ctx.move_to(k * 80, 1500); ctx.arc(k * 80 + 40, 1500, 40, math.pi, 0)
    ctx.set_source_rgba(*hexc('#8b1e2d')); ctx.fill()
    ctx.rectangle(0, 1500, W, 18); ctx.set_source_rgba(0, 0, 0, 0.15); ctx.fill()
    ctx.rectangle(0, 1580, W, 40); ctx.set_source_rgba(1, 1, 1, 0.16); ctx.fill()
    for px in (WX + 20, AX - 10):                                           # plates
        e4.ell(ctx, px, 1560, 150, 38, hexc('#f8f9fa')); e4.ell(ctx, px, 1556, 112, 26, hexc('#e9ecef'))
        if spaghetti:
            e4.ell(ctx, px, 1544, 74, 24, hexc('#ffd166'))
            circle(ctx, px - 20, 1530, 14, hexc('#c1121f')); circle(ctx, px + 24, 1534, 12, hexc('#c1121f'))
    e4.ell(ctx, LX - 100, 1566, 70, 18, hexc('#f8f9fa'))                    # Leo's juice box
    rrect(ctx, LX - 20, 1488, 56, 70, 8); ctx.set_source_rgba(*hexc('#ffb703')); ctx.fill()
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#ffb703')); ctx.move_to(LX + 8, 1488); ctx.line_to(LX + 8, 1450); ctx.line_to(LX + 24, 1450); ctx.stroke()
    # candle
    cx = 700
    rrect(ctx, cx - 16, 1450, 32, 90, 8); ctx.set_source_rgba(*hexc('#fff3d6')); ctx.fill()
    fl = 1 + 0.12 * math.sin(t * 17)
    gl = cairo.RadialGradient(cx, 1430, 6, cx, 1430, 200); gl.add_color_stop_rgba(0, 1, 0.8, 0.4, 0.5); gl.add_color_stop_rgba(1, 1, 0.8, 0.4, 0)
    ctx.set_source(gl); ctx.rectangle(cx - 220, 1230, 440, 400); ctx.fill()
    ctx.save(); ctx.translate(cx, 1428); ctx.scale(1, fl)
    ctx.move_to(0, -34); ctx.curve_to(18, -8, 14, 14, 0, 14); ctx.curve_to(-14, 14, -18, -8, 0, -34); ctx.set_source_rgba(*hexc('#ffb703')); ctx.fill()
    ctx.restore()

def approval(ctx, pct, t=0.0):
    rrect(ctx, 90, 524, 900, 74, 37); ctx.set_source_rgba(*hexc('#10132b', 0.92)); ctx.fill()
    mv.font(ctx, 27); ctx.move_to(122, 572); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text("LEO'S APPROVAL")
    bx, bw = 420, 390
    rrect(ctx, bx, 546, bw, 28, 14); ctx.set_source_rgba(1, 1, 1, 0.16); ctx.fill()
    col = '#ff4d5a' if pct < 40 else ('#ffd60a' if pct < 80 else '#4ade80')
    rrect(ctx, bx, 546, max(28, bw * pct / 100.0), 28, 14); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    mv.font(ctx, 32); s_ = "%d%%" % pct; e = ctx.text_extents(s_); ctx.move_to(960 - e.x_advance, 573); ctx.set_source_rgba(*hexc(col)); ctx.show_text(s_)

def trio(ctx, t, wexpr="happy", wflush=0.0, lexpr="flat", aexpr="smile", aflush=0.0, wmode="point", lhand=(0, -150), flex=0.0, wh=(110, -110), lgy=-20):
    wren(ctx, WX, GY, 0.85, t, wmode, flush=wflush, expr=wexpr, hand=wh)
    andy(ctx, AX, GY, 0.82, t, aexpr, aflush, flex)
    kid(ctx, LX, GY + lgy, 1.0, t, lexpr, lhand)

# ------------------------------------------------------------ tattoo icons
def tat_heart(ctx, x, y):
    ctx.save(); ctx.translate(x, y)
    ctx.move_to(0, 50); ctx.curve_to(-110, -20, -50, -90, 0, -40); ctx.curve_to(50, -90, 110, -20, 0, 50); ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc(INK)); ctx.move_to(0, 50); ctx.curve_to(-110, -20, -50, -90, 0, -40); ctx.curve_to(50, -90, 110, -20, 0, 50); ctx.stroke()
    rrect(ctx, -70, -8, 140, 44, 8); ctx.set_source_rgba(1, 0.97, 0.88, 1); ctx.fill(); ctx.set_source_rgba(*hexc(INK)); ctx.set_line_width(4); rrect(ctx, -70, -8, 140, 44, 8); ctx.stroke()
    mv.font(ctx, 34); e = ctx.text_extents("MUM"); ctx.move_to(-e.x_advance / 2, 26); ctx.set_source_rgba(*hexc(INK)); ctx.show_text("MUM"); ctx.restore()

def tat_cat(ctx, x, y):
    ctx.save(); ctx.translate(x, y)
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc(INK))
    ctx.move_to(-62, -34); ctx.line_to(-62, -86); ctx.line_to(-24, -58); ctx.move_to(62, -34); ctx.line_to(62, -86); ctx.line_to(24, -58); ctx.stroke()
    circle(ctx, 0, -10, 66, hexc('#ffb86b')); ctx.arc(0, -10, 66, 0, 6.3); ctx.stroke()
    for sx in (-26, 26): circle(ctx, sx, -22, 7, hexc(INK))
    ctx.move_to(-8, 4); ctx.line_to(8, 4); ctx.line_to(0, 14); ctx.close_path(); ctx.set_source_rgba(*hexc('#ff6b81')); ctx.fill()
    ctx.set_source_rgba(*hexc(INK)); ctx.set_line_width(3)
    for sy in (0, 12): ctx.move_to(-30, sy + 4); ctx.line_to(-78, sy - 2); ctx.move_to(30, sy + 4); ctx.line_to(78, sy - 2)
    ctx.stroke()
    ctx.restore()

def tat_cup(ctx, x, y, t):
    ctx.save(); ctx.translate(x, y)
    ctx.move_to(-56, -40); ctx.line_to(56, -40); ctx.curve_to(52, 40, -52, 40, -56, -40); ctx.set_source_rgba(*hexc('#8ecae6')); ctx.fill()
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc(INK)); ctx.move_to(-56, -40); ctx.line_to(56, -40); ctx.curve_to(52, 40, -52, 40, -56, -40); ctx.stroke()
    ctx.arc(66, -10, 20, -math.pi / 2, math.pi / 2); ctx.stroke()
    for k in range(2):
        ph = (t * 0.8 + k * 0.5) % 1; ctx.move_to(-14 + k * 28, -50); ctx.curve_to(-30 + k * 28, -70 - ph * 12, 0 + k * 28, -90, -14 + k * 28, -110); ctx.set_source_rgba(*hexc(INK, 0.7)); ctx.stroke()
    ctx.restore()

def flash_card(ctx, t, a=1.0):
    if a <= 0: return
    ctx.save(); ctx.translate(0, (1 - a) * -30)
    rrect(ctx, 66, 636, 948, 330, 40); ctx.set_source_rgba(0, 0, 0, 0.14 * a); ctx.fill()
    rrect(ctx, 60, 628, 948, 330, 40); ctx.set_source_rgba(1, 0.98, 0.92, 0.97 * a); ctx.fill()
    items = [(0.3, tat_heart, "Mum"), (1.0, tat_cat, "Biscuit the cat"), (1.7, None, "Tea")]
    for k, (t0, fn, cap) in enumerate(items):
        p = ramp(t, t0, t0 + 0.3)
        if p <= 0: continue
        cx = 230 + k * 306; ctx.save(); ctx.translate(cx, 780); s = 0.6 + 0.4 * p; ctx.scale(s, s); ctx.translate(-cx, -780)
        if k == 0: tat_heart(ctx, cx, 780)
        elif k == 1: tat_cat(ctx, cx, 790)
        else: tat_cup(ctx, cx, 790, t)
        ctx.restore()
        mv.font(ctx, 32); e = ctx.text_extents(cap); ctx.move_to(cx - e.x_advance / 2, 915); ctx.set_source_rgba(*hexc('#22223b', p)); ctx.show_text(cap)
    ctx.restore()

def stamp(ctx, t, t0):
    k = ease((t - t0) / 0.12)
    if k <= 0: return
    sc = 1 + 1.4 * max(0.0, 1 - (t - t0) / 0.18)
    ctx.save(); ctx.translate(540, 940); ctx.rotate(-0.16); ctx.scale(sc, sc)
    mv.font(ctx, 118); e = ctx.text_extents("APPROVED"); w = e.x_advance + 70
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#1f9d6b', k)); rrect(ctx, -w / 2, -88, w, 150, 24); ctx.stroke()
    ctx.move_to(-e.x_advance / 2, 28); ctx.set_source_rgba(*hexc('#1f9d6b', k)); ctx.show_text("APPROVED"); ctx.restore()

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    restaurant(ctx, t); trio(ctx, t, wexpr="happy", wflush=0.2, lexpr="flat", aexpr="smile"); table(ctx, t)
    header(ctx, ease(t / 0.2 + 1), "WREN'S DATE", "Andy, 72, has tattoos.", "Wren brought Leo.", -0.3, t, main_size=56)
    approval(ctx, int(lerp(5, 8, t / d)), t); wm(ctx)

def s1(ctx, t, d):
    restaurant(ctx, t); nerv = t > 0.9
    trio(ctx, t, wexpr="shock" if t > 0.9 else "happy", wflush=0.5, lexpr="flat", aexpr="nervous" if nerv else "smile", aflush=0.4 if nerv else 0.0)
    table(ctx, t)
    bubble_ml(ctx, 540, 1000, ["What are your", "intentions?"], 46, ramp(t, 0.3, 0.5) * (1 - ramp(t, 1.8, 2.0)), (LX, 1230))
    bubble_ml(ctx, 790, 1000, ["...Share a pizza?"], 42, ramp(t, 2.0, 2.2), (AX - 10, 1130))
    header(ctx, ease(t / 0.2), "THE INTERVIEW", "Leo has questions.", "Andy is sweating.", 1.2, t)
    approval(ctx, int(lerp(8, 25, ramp(t, 2.2, 2.9))), t); wm(ctx)

def s2(ctx, t, d):
    restaurant(ctx, t)
    trio(ctx, t, wexpr="happy", wflush=0.3, lexpr="flat" if t < 2.0 else "smile", aexpr="touched" if t > 1.5 else "smile", aflush=0.3, flex=ramp(t, 0.3, 0.8) * (1 - ramp(t, 2.6, 3.0)))
    table(ctx, t)
    flash_card(ctx, t, ease(t / 0.25))
    header(ctx, ease(t / 0.2), "THE TATTOOS", "Not what Leo expected.", "Mum. Biscuit. Tea.", 2.0, t, main_size=52)
    approval(ctx, int(lerp(25, 72, ramp(t, 0.8, 2.6))), t); wm(ctx)

def strand(ctx, t, bite, snap):
    # a long spaghetti strand between Wren's and Andy's mouths
    x0, y0, x1, y1 = WX + 35, 1215, AX - 20, 1150
    sag = 120 * (1 - 0.5 * snap)
    if bite < 1:
        ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#ffd166'))
        ctx.move_to(x0, y0); ctx.curve_to(x0 + 150, y0 + sag * 1.7, x1 - 150, y1 + sag * 1.7, x1, y1); ctx.stroke()
    else:
        k = clamp01((t - snap_t) / 0.4)
        for sx, ex, ey, c1 in ((x0, 455, 1380, 1), (x1, 625, 1380, -1)):
            ctx.set_line_width(9); ctx.set_source_rgba(*hexc('#ffd166')); ctx.move_to(sx, y0 if c1 == 1 else y1)
            ctx.curve_to(sx + c1 * 60, y0 + 100 * k, ex - c1 * 30, ey - 60, lerp(ex, sx + c1 * 90, k * 0.8), lerp(ey, 1400, k)); ctx.stroke()

snap_t = 1.55
def s3(ctx, t, d):
    restaurant(ctx, t)
    popped = ramp(t, 1.0, 1.35) * (1 - ramp(t, 2.3, 2.6))
    trio(ctx, t, wexpr="happy", wflush=0.6, lexpr="smug" if t > 1.5 else "flat", aexpr="touched", aflush=0.5, lhand=(0, -150), lgy=-20 - 40 * popped)
    table(ctx, t, spaghetti=True)
    # strand then Leo pops up between and bites it
    if t < snap_t: strand(ctx, t, 0, 0)
    else: strand(ctx, t, 1, 1)
    if t > snap_t - 0.05 and t < snap_t + 0.3: burst(ctx, LX + 12, 1300, 1 - (t - snap_t) / 0.3, 70)
    for k in range(3):                                                    # floating hearts
        if t < 1.3:
            ph = (t * 0.7 + k / 3) % 1; ctx.save(); ctx.translate(AX - 330 + k * 120, 1250 - ph * 260); ctx.scale(0.5, 0.5)
            ctx.move_to(0, 22); ctx.curve_to(-44, -10, -20, -40, 0, -18); ctx.curve_to(20, -40, 44, -10, 0, 22); ctx.set_source_rgba(*hexc('#ff6b81', 1 - ph)); ctx.fill(); ctx.restore()
    stamp(ctx, t, 2.2)
    header(ctx, ease(t / 0.2), "DINNER", "The spaghetti moment", "Leo had other plans.", 1.4, t, main_size=54)
    approval(ctx, int(lerp(72, 100, ramp(t, 2.2, 2.6))), t); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave", flush=0.35)
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “Best date ever.”", 205 - (1 - a) * 20, 60, hexc('#22223b', a), maxw=940)
    ctext(ctx, "Leo: “Andy's approved.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Would you bring a chaperone? Comment below", 625, 36, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

SCENES = [(s0, 2.6), (s1, 3.0), (s2, 3.2), (s3, 3.4), (s4, 2.6)]

def frame(fn, t, d):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    fn(ctx, t, d)
    a_in = 0 if fn is s0 else 1 - t / 0.1
    a_out = (t - (d - 0.5)) / 0.5 if fn is s4 else (t - (d - 0.1)) / 0.1
    a = max(a_in, a_out, 0)
    if a > 0:
        ctx.set_source_rgba(*hexc('#fff3e0' if fn is s4 or fn is s0 and False else '#fff3e0', min(1, ease(a)))); ctx.paint()
    return surf

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        from PIL import Image
        picks = [(s0, 1.8), (s1, 1.2), (s1, 2.6), (s2, 0.5), (s2, 1.6), (s2, 2.6), (s3, 0.8), (s3, 1.8), (s3, 2.8), (s4, 2.0)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((300, 533)))
        c = Image.new("RGB", (310 * 5, 543 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 5) * 310, (i // 5) * 543))
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

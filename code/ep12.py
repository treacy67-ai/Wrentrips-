import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = "/home/claude/wren/ep12"
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))

# ------------------------------------------------------------ shared bits
def bunting(ctx, t, y=0):
    for k, x in enumerate(range(-30, W + 80, 84)):
        sw = 6 * math.sin(t * 2 + k)
        ctx.move_to(x, y + 10 + 16 * math.sin(x * 0.015)); ctx.line_to(x + 76, y + 10 + 16 * math.sin((x + 76) * 0.015)); ctx.line_to(x + 38 + sw, y + 100)
        ctx.close_path(); ctx.set_source_rgba(*hexc(['#e63946', '#ffd166', '#4361ee', '#2a9d8f', '#f72585'][k % 5])); ctx.fill()

def palm(ctx, x, base, h, t, col='#2f8f4e', trunk='#8a5a2b'):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(h * 0.07); ctx.set_source_rgba(*hexc(trunk))
    ctx.move_to(x, base); ctx.curve_to(x + h * 0.06, base - h * 0.4, x - h * 0.05, base - h * 0.7, x + h * 0.02, base - h); ctx.stroke()
    tx, ty = x + h * 0.02, base - h
    for k in range(7):
        a = math.radians(-160 + k * 50) + 0.05 * math.sin(t * 1.5 + k)
        ex, ey = tx + math.cos(a) * h * 0.55, ty + math.sin(a) * h * 0.4 + h * 0.12
        ctx.move_to(tx, ty); ctx.curve_to(tx + math.cos(a) * h * 0.3, ty + math.sin(a) * h * 0.5 - h * 0.1, ex - 10, ey - 30, ex, ey)
        ctx.curve_to(ex - 10, ey - 10, tx + math.cos(a) * h * 0.3, ty + math.sin(a) * h * 0.5, tx, ty)
        ctx.set_source_rgba(*hexc(col)); ctx.fill()
    circle(ctx, tx, ty + 8, h * 0.035, hexc('#6b4423'))

def vibe(ctx, pct, a=1.0, t=0.0, pop_t=None):
    if a <= 0: return
    rrect(ctx, 90, 524, 900, 74, 37); ctx.set_source_rgba(*hexc('#10132b', 0.9 * a)); ctx.fill()
    mv.font(ctx, 27); ctx.move_to(122, 572); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text("VACATION VIBES")
    bx, bw = 420, 390
    rrect(ctx, bx, 546, bw, 28, 14); ctx.set_source_rgba(1, 1, 1, 0.16 * a); ctx.fill()
    rrect(ctx, bx, 546, max(28, bw * pct / 100.0), 28, 14); ctx.set_source_rgba(*hexc('#ffb703' if pct < 100 else '#4ade80', a)); ctx.fill()
    mv.font(ctx, 32); s_ = "%d%%" % pct; e = ctx.text_extents(s_); ctx.move_to(960 - e.x_advance, 573); ctx.set_source_rgba(*hexc('#ffb703' if pct < 100 else '#4ade80', a)); ctx.show_text(s_)

# ------------------------------------------------------------ jeepney exterior
def jeep(ctx, cx, base, t):
    ctx.save(); ctx.translate(0, math.sin(t * 15) * 3)
    e4.ell(ctx, cx, base + 6, 460, 20, (0, 0, 0, 0.22))
    for wx in (cx - 270, cx + 250):
        circle(ctx, wx, base - 62, 64, hexc('#15171c')); circle(ctx, wx, base - 62, 36, hexc('#c8ced8'))
        ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#6c7380'))
        for k in range(5):
            a = k * 2 * math.pi / 5 + t * 40; ctx.move_to(wx, base - 62); ctx.line_to(wx + 34 * math.cos(a), base - 62 + 34 * math.sin(a)); ctx.stroke()
    rrect(ctx, cx - 440, base - 230, 880, 160, 22); ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()                  # lower body
    ctx.rectangle(cx - 440, base - 150, 880, 28); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    ctx.rectangle(cx - 440, base - 118, 880, 14); ctx.set_source_rgba(*hexc('#4361ee')); ctx.fill()
    for k in range(8):
        sx = cx - 400 + k * 110 + (0 if k % 2 == 0 else 0)
        ctx.save(); ctx.translate(sx, base - 188)
        for j in range(5):
            a = j * 2 * math.pi / 5 - math.pi / 2; ctx.line_to(math.cos(a) * 16, math.sin(a) * 16); a2 = a + math.pi / 5; ctx.line_to(math.cos(a2) * 7, math.sin(a2) * 7)
        ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill(); ctx.restore()
    rrect(ctx, cx - 400, base - 410, 760, 190, 26); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()                  # cabin
    rrect(ctx, cx - 420, base - 440, 800, 38, 16); ctx.set_source_rgba(*hexc('#4361ee')); ctx.fill()                  # roof
    for k in range(9): circle(ctx, cx - 360 + k * 90, base - 458, 12, hexc(['#ffd60a', '#ff6b6b'][k % 2]))
    ctx.save(); rrect(ctx, cx - 360, base - 392, 560, 150, 18); ctx.clip()
    ctx.set_source_rgba(*hexc('#3a2a4a')); ctx.paint()
    wren(ctx, cx - 240, base - 15, 0.46, t, "wave")
    kid(ctx, cx - 70, base - 78, 0.58, t, "smile", (0, -150))
    ctx.restore()
    ctx.set_line_width(10); ctx.set_source_rgba(*hexc('#c1583a')); rrect(ctx, cx - 360, base - 392, 560, 150, 18); ctx.stroke()
    rrect(ctx, cx + 215, base - 392, 130, 150, 14); ctx.set_source_rgba(*hexc('#cfe8f7')); ctx.fill()                  # driver window
    rrect(ctx, cx + 400, base - 250, 70, 190, 18); ctx.set_source_rgba(*hexc('#d0d4dc')); ctx.fill()                  # chrome front
    for k in range(4): ctx.rectangle(cx + 408, base - 232 + k * 40, 54, 8)
    ctx.set_source_rgba(*hexc('#8d96a5')); ctx.fill()
    circle(ctx, cx + 452, base - 196, 18, hexc('#fff3b0'))
    mv.font(ctx, 52); s_ = "WRENTRIPS"; ctx.move_to(cx - 190, base - 82); ctx.set_source_rgba(1, 0.95, 0.7, 1); ctx.show_text(s_)
    ctx.restore()

def street_bg(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, 1300); g.add_color_stop_rgb(0, *hexc('#7fd0ff')[:3]); g.add_color_stop_rgb(1, *hexc('#f1fbff')[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1400); ctx.fill()
    circle(ctx, 880, 700, 80, hexc('#fff3b0', 0.9))
    sp = 260.0; off = (t * sp) % 1200
    rng = random.Random(8)
    for rep in (-1, 0, 1):                                     # far buildings
        for k in range(7):
            x = k * 190 - off * 0.35 + rep * 1330; bw = 160 + (k * 37) % 40; bh = 260 + (k * 97) % 280
            ctx.rectangle(x, 1330 - bh, bw, bh); ctx.set_source_rgba(*hexc(['#f4a261', '#2a9d8f', '#e9c46a', '#e76f51'][k % 4], 0.85)); ctx.fill()
            for wy in range(int(1330 - bh + 30), 1290, 62):
                for wx in range(int(x + 20), int(x + bw - 30), 50):
                    ctx.rectangle(wx, wy, 26, 34); ctx.set_source_rgba(1, 1, 1, 0.6); ctx.fill()
    for k in range(4):                                         # palms (parallax)
        x = (k * 380 - off * 0.9) % 1500 - 200
        palm(ctx, x, 1400, 520, t)
    ctx.rectangle(0, 1380, W, 60); ctx.set_source_rgba(*hexc('#c9c2b4')); ctx.fill()
    ctx.rectangle(0, 1440, W, H - 1440); ctx.set_source_rgba(*hexc('#4a4e58')); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.7)
    for k in range(6): ctx.rectangle((k * 260 - t * 700) % 1560 - 200, 1790, 150, 14)
    ctx.fill()

# ------------------------------------------------------------ interior
def coin(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    circle(ctx, 0, 0, 22, hexc('#c98f00')); circle(ctx, 0, 0, 19, hexc('#ffd60a')); circle(ctx, -5, -5, 6, (1, 1, 1, 0.6))
    ctx.restore()

def interior(ctx, t):
    ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(*hexc('#ffd9a0')); ctx.fill()
    for k in range(0, W, 120): ctx.rectangle(k, 600, 60, 1000); ctx.set_source_rgba(1, 1, 1, 0.12); ctx.fill()
    ctx.save(); rrect(ctx, 70, 640, 940, 290, 24); ctx.clip()                                      # window with scrolling palms
    g = cairo.LinearGradient(0, 640, 0, 930); g.add_color_stop_rgb(0, *hexc('#8fd8ff')[:3]); g.add_color_stop_rgb(1, *hexc('#e6f8ff')[:3]); ctx.set_source(g); ctx.paint()
    off = (t * 300) % 1200
    for k in range(4): palm(ctx, (k * 360 - off) % 1440 - 180, 960, 380, t)
    ctx.restore()
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#c1583a')); rrect(ctx, 70, 640, 940, 290, 24); ctx.stroke()
    for k in range(18):                                                                                 # tassels
        x = 40 + k * 58; ctx.move_to(x, 560); ctx.line_to(x, 610 + 14 * math.sin(t * 5 + k)); ctx.set_line_width(7)
        ctx.set_source_rgba(*hexc(['#e63946', '#4361ee', '#2a9d8f', '#f72585'][k % 4])); ctx.stroke()
    ctx.rectangle(0, 540, W, 26); ctx.set_source_rgba(*hexc('#c1583a')); ctx.fill()

def bench_front(ctx):
    ctx.rectangle(0, 1400, W, 140); ctx.set_source_rgba(*hexc('#a0622d')); ctx.fill()
    ctx.rectangle(0, 1396, W, 16); ctx.set_source_rgba(*hexc('#c98a52')); ctx.fill()
    for k in range(1, 8): ctx.rectangle(k * 135, 1412, 6, 128); ctx.set_source_rgba(0, 0, 0, 0.12); ctx.fill()
    ctx.rectangle(0, 1540, W, H - 1540); ctx.set_source_rgba(*hexc('#4f3b2b')); ctx.fill()

def driver(ctx, t, hand_out):
    ctx.save(); ctx.translate(960, 0)
    rrect(ctx, -70, 1190, 140, 220, 40); ctx.set_source_rgba(*hexc('#2a9d8f')); ctx.fill()
    circle(ctx, 0, 1150, 56, hexc('#c68b59')); ctx.arc(0, 1142, 60, math.pi, 2 * math.pi); ctx.close_path(); ctx.set_source_rgba(*hexc('#1d1d2b')); ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(34); ctx.set_source_rgba(*hexc('#2a9d8f'))
    hx = -70 - 60 * hand_out; ctx.move_to(-40, 1250); ctx.line_to(hx, 1270); ctx.stroke(); circle(ctx, hx, 1270, 20, hexc('#c68b59'))
    ctx.restore()

# ------------------------------------------------------------ cafe
def cafe_bg(ctx, t):
    ctx.rectangle(0, 0, W, 1560); ctx.set_source_rgba(*hexc('#bfe9d9')); ctx.fill()
    for yy in range(600, 1560, 90):
        for xx in range(0, W, 90):
            ctx.rectangle(xx + 2, yy + 2, 86, 86); ctx.set_source_rgba(1, 1, 1, 0.22 if ((xx // 90) + (yy // 90)) % 2 else 0.1); ctx.fill()
    for k in range(10):                                         # awning
        ctx.move_to(k * 112, 520); ctx.line_to(k * 112 + 112, 520); ctx.line_to(k * 112 + 112, 600); ctx.arc(k * 112 + 56, 600, 56, 0, math.pi); ctx.close_path()
        ctx.set_source_rgba(*hexc('#e63946' if k % 2 == 0 else '#ffffff')); ctx.fill()
    rrect(ctx, 700, 700, 300, 170, 14); ctx.set_source_rgba(*hexc('#2d3a35')); ctx.fill()                  # chalkboard
    ctx.set_line_width(8); ctx.set_source_rgba(*hexc('#a0622d')); rrect(ctx, 700, 700, 300, 170, 14); ctx.stroke()
    mv.font(ctx, 46); ctx.move_to(722, 775); ctx.set_source_rgba(1, 1, 1, 0.95); ctx.show_text("HALO-HALO")
    mv.font(ctx, 30, False); ctx.move_to(722, 825); ctx.set_source_rgba(1, 0.85, 0.5, 0.95); ctx.show_text("ube • flan • ice")
    for k in range(3): palm(ctx, 60 + k * 0, 1560, 0, t) if False else None

def sundae(ctx, cx, base, t, level=1.0):
    ctx.save(); ctx.translate(cx, base)
    ctx.move_to(-150, -460); ctx.curve_to(-150, -250, -70, -140, -26, -110); ctx.line_to(-26, -40); ctx.line_to(-80, -20); ctx.line_to(80, -20); ctx.line_to(26, -40); ctx.line_to(26, -110)
    ctx.curve_to(70, -140, 150, -250, 150, -460); ctx.close_path(); ctx.set_source_rgba(*hexc('#e8f6ff', 0.55)); ctx.fill()
    ctx.save(); ctx.move_to(-150, -460); ctx.curve_to(-150, -250, -70, -140, -26, -110); ctx.line_to(26, -110); ctx.curve_to(70, -140, 150, -250, 150, -460); ctx.close_path(); ctx.clip()
    for y0, y1, col in ((-130, -230, '#f7d6e0'), (-230, -300, '#9d4edd'), (-300, -370, '#fff3d6'), (-370, -460, '#e8f6ff')):
        ctx.rectangle(-160, y1, 320, y0 - y1); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    rng = random.Random(3)
    for k in range(14):
        x = rng.uniform(-110, 110); y = rng.uniform(-285, -150)
        circle(ctx, x, y, 11, hexc(rng.choice(['#8b1a2b', '#6b3fa0', '#ff8fa3', '#7fd8a6'])))
    ctx.restore()
    ctx.set_line_width(6); ctx.set_source_rgba(0.6, 0.7, 0.8, 0.9)
    ctx.move_to(-150, -460); ctx.curve_to(-150, -250, -70, -140, -26, -110); ctx.line_to(-26, -40); ctx.line_to(-80, -20); ctx.line_to(80, -20); ctx.line_to(26, -40); ctx.line_to(26, -110)
    ctx.curve_to(70, -140, 150, -250, 150, -460); ctx.stroke()
    e4.ell(ctx, 0, -470, 160, 40, hexc('#ffffff'))                                               # shaved ice dome + toppings
    ctx.arc(0, -470, 150, math.pi, 2 * math.pi); ctx.set_source_rgba(*hexc('#ffffff')); ctx.fill()
    circle(ctx, 0, -560 + (1 - level) * 40, 66 * (0.4 + 0.6 * level), hexc('#9d4edd')); circle(ctx, -22, -584, 14, (1, 1, 1, 0.5))
    ctx.save(); ctx.translate(-92, -520); ctx.rotate(-0.4); rrect(ctx, -44, -22, 88, 44, 10); ctx.set_source_rgba(*hexc('#ffb703')); ctx.fill(); ctx.restore()
    ctx.restore()

def spoon(ctx, x, y, ang=0.6, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(9); ctx.set_source_rgba(*hexc('#c8ced8')); ctx.move_to(0, 0); ctx.line_to(0, 70); ctx.stroke()
    e4.ell(ctx, 0, -8, 20, 14, hexc('#c8ced8')); circle(ctx, 0, -16, 9, hexc('#9d4edd'))
    ctx.restore()

def snowflake(ctx, x, y, r, a, rot):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(0.75, 0.92, 1, a)
    for k in range(3):
        ang = k * math.pi / 3; ctx.move_to(-math.cos(ang) * r, -math.sin(ang) * r); ctx.line_to(math.cos(ang) * r, math.sin(ang) * r); ctx.stroke()
    ctx.restore()

# ------------------------------------------------------------ bay
def bay_bg(ctx, t, sun_k):
    top, mid = ('#ff9e5e', '#ff5d8f'), None
    g = cairo.LinearGradient(0, 0, 0, 1180); g.add_color_stop_rgb(0, *hexc('#6a3fa0')[:3]); g.add_color_stop_rgb(0.5, *hexc('#ff5d8f')[:3]); g.add_color_stop_rgb(1, *hexc('#ffb86b')[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1180); ctx.fill()
    sy = lerp(1000, 1140, sun_k)
    ctx.save(); ctx.rectangle(0, 0, W, 1180); ctx.clip(); circle(ctx, 540, sy, 150, hexc('#fff0a0')); circle(ctx, 540, sy, 190, hexc('#ffd166', 0.25)); ctx.restore()
    for cxx, cyy, s in ((220, 760, 1.0), (820, 700, 1.2), (560, 860, 0.8)):
        for dx, dy, r in ((0, 0, 60), (60, 14, 50), (-60, 18, 46), (20, -22, 44)): circle(ctx, cxx + dx * s + 10 * math.sin(t * 0.5), cyy + dy * s, r * s, hexc('#ffc4d6', 0.75))
    g2 = cairo.LinearGradient(0, 1180, 0, 1580); g2.add_color_stop_rgb(0, *hexc('#ff9e6b')[:3]); g2.add_color_stop_rgb(1, *hexc('#5a3a8a')[:3])
    ctx.set_source(g2); ctx.rectangle(0, 1180, W, 400); ctx.fill()
    for k in range(14):                                          # sun reflection
        y = 1190 + k * 26; w = (240 - k * 11) * (0.9 + 0.1 * math.sin(t * 3 + k))
        ctx.rectangle(540 - w / 2, y, w, 8); ctx.set_source_rgba(1, 0.95, 0.6, 0.55 - k * 0.03); ctx.fill()
    bx = 180 + 40 * math.sin(t * 0.4)                             # sailboat
    ctx.move_to(bx, 1215); ctx.line_to(bx, 1105); ctx.line_to(bx + 70, 1215); ctx.close_path(); ctx.set_source_rgba(*hexc('#3a1f5c')); ctx.fill()
    ctx.move_to(bx - 12, 1220); ctx.line_to(bx + 90, 1220); ctx.line_to(bx + 70, 1245); ctx.line_to(bx + 6, 1245); ctx.close_path(); ctx.fill()
    ctx.rectangle(0, 1560, W, H - 1560); ctx.set_source_rgba(*hexc('#8c7a96')); ctx.fill()                  # promenade
    ctx.rectangle(0, 1560, W, 26); ctx.set_source_rgba(*hexc('#6d5c78')); ctx.fill()
    for pxx, ph in ((60, 620), (1010, 700)): palm(ctx, pxx, 1580, ph, t, col='#2b1b45', trunk='#2b1b45')

def cup(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-26, -50); ctx.line_to(26, -50); ctx.line_to(20, 40); ctx.line_to(-20, 40); ctx.close_path(); ctx.set_source_rgba(*hexc('#ffe08a', 0.95)); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.8); ctx.stroke()
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#2a9d8f')); ctx.move_to(8, -50); ctx.line_to(18, -84); ctx.stroke()
    circle(ctx, -4, -52, 14, hexc('#9fdc5a')); ctx.restore()

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    street_bg(ctx, t); bunting(ctx, t); jeep(ctx, 540, 1700, t)
    header(ctx, ease(t / 0.2 + 1), "WELCOME TO MANILA", "Mabuhay!", "Vacation mode: ON", -0.3, t)
    vibe(ctx, int(lerp(10, 30, ramp(t, 0.3, 2.2))), 1.0, t)
    wm(ctx)

def s1(ctx, t, d):
    interior(ctx, t)
    pts = [(255, 1295), (480, 1275), (730, 1265), (885, 1262)]
    driver(ctx, t, ramp(t, 1.2, 1.5) * (1 - ramp(t, 1.9, 2.1)))
    wren(ctx, 190, 1520, 0.72, t, "cheer" if t > 2.8 else "wave")
    kid(ctx, 425, 1520, 0.88, t, "smile", (0, -150))
    e4.aunty(ctx, 690, 1480, t, "smile")
    bench_front(ctx)
    # coin hops hand to hand, then returns
    seq = [(0.4, 0.8, 0, 1), (0.8, 1.2, 1, 2), (1.2, 1.6, 2, 3), (2.0, 2.3, 3, 2), (2.3, 2.6, 2, 1), (2.6, 2.9, 1, 0)]
    cp = None
    for a, b, i, j in seq:
        if a <= t < b:
            k = (t - a) / (b - a); cp = (lerp(pts[i][0], pts[j][0], k), lerp(pts[i][1], pts[j][1], k) - 80 * math.sin(math.pi * k))
    if cp is None:
        cp = pts[0] if t < 0.4 else (pts[3] if t < 2.0 else pts[0])
    if t >= 0.2: coin(ctx, cp[0], cp[1])
    for a, b, i, j in seq:
        if 0 <= t - b < 0.25: burst(ctx, pts[j][0], pts[j][1] - 20, 1 - (t - b) / 0.25, 46 * (0.5 + (t - b) * 3))
    bubble_ml(ctx, 360, 1040, ["Bayad po!"], 42, ramp(t, 0.15, 0.35) * (1 - ramp(t, 1.5, 1.7)), (210, 1150))
    bubble_ml(ctx, 400, 1040, ["It came back!"], 42, ramp(t, 2.9, 3.1), (210, 1150))
    header(ctx, ease(t / 0.2), "RIDE 1: JEEPNEY", "Pass the fare along", "Everyone helps.", 1.6, t, main_size=56)
    vibe(ctx, int(lerp(30, 55, ramp(t, 0.3, 3.0))), 1.0, t)
    wm(ctx)

def s2(ctx, t, d):
    cafe_bg(ctx, t)
    frz = t > 1.7
    bite = ramp(t, 0.6, 1.3)
    # Wren digs in from the left; Leo calmly eats from the right
    ctx.save()
    if frz: ctx.push_group()
    whand = (lerp(270, 280, bite) if t < 1.3 else 40, lerp(-330, -420, math.sin(min(1, t / 1.3) * math.pi)) if t < 1.3 else -520)
    wren(ctx, 230, 1490, 0.85, t, "point", expr="ouch" if frz else "happy", hand=whand)
    if frz:
        ctx.set_operator(cairo.OPERATOR_ATOP); ctx.set_source_rgba(0.35, 0.65, 1.0, 0.38); ctx.paint(); ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.pop_group_to_source(); ctx.paint()
    ctx.restore()
    kid(ctx, 850, 1490, 1.05, t, "smug" if frz else "smile", (-110, -210))
    sundae(ctx, 540, 1500, t, level=1.0 if t < 1.1 else 0.8)
    # spoons
    wx = 230 + whand[0] * 0.85; wy = 1490 + whand[1] * 0.85
    spoon(ctx, wx, wy - 4, 0.5 if t < 1.3 else -0.2)
    spoon(ctx, 850 - 110 * 1.05, 1490 - 210 * 1.05 - 4, -0.5)
    # table
    rrect(ctx, 40, 1500, 1000, 34, 14); ctx.set_source_rgba(*hexc('#a0622d')); ctx.fill()
    for k in range(20):
        for j in range(3):
            ctx.rectangle(40 + k * 50, 1534 + j * 36, 50, 36); ctx.set_source_rgba(*hexc('#e63946' if (k + j) % 2 == 0 else '#ffffff')); ctx.fill()
    ctx.rectangle(0, 1642, W, H - 1642); ctx.set_source_rgba(*hexc('#d9c7a8')); ctx.fill()
    if frz:
        for k in range(5):
            snowflake(ctx, 230 + 130 * math.cos(t * 4 + k * 1.26), 1020 + 60 * math.sin(t * 4 + k * 1.26), 24, 0.9, t * 2 + k)
    header(ctx, ease(t / 0.2), "SNACK STOP", "Halo-halo!", "Brain freeze: instant.", 1.9, t)
    vibe(ctx, int(lerp(55, 80, ramp(t, 0.3, 3.0))), 1.0, t)
    wm(ctx)

def s3(ctx, t, d):
    bay_bg(ctx, t, ramp(t, 0.0, 3.4))
    clink = t > 1.6
    wren(ctx, 330, 1650, 0.9, t, "point", hand=(190, -440 + 6 * math.sin(t * 3)))
    kid(ctx, 760, 1650, 1.2, t, "smile", (-150, -308))
    cup(ctx, 330 + 190 * 0.9 + 8, 1650 - 440 * 0.9 + 6 * math.sin(t * 3) - 40, 1.0)
    cup(ctx, 760 - 150 * 1.2 - 10, 1650 - 308 * 1.2 - 40, 1.0)
    if clink and t < 2.3: burst(ctx, 545, 1150, 1 - (t - 1.6) / 0.7, 90 * (0.6 + (t - 1.6)))
    bubble_ml(ctx, 540, 940, ["Cheers to Manila!"], 44, ramp(t, 1.5, 1.7), (460, 1090))
    header(ctx, ease(t / 0.2), "MANILA BAY", "Sunset. Calamansi juice.", "Perfect day.", 1.0, t, main_size=54)
    vibe(ctx, int(lerp(80, 100, ramp(t, 0.3, 2.6))), 1.0, t)
    wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    a = ease(t / 0.3)
    ctext(ctx, "Wren's review: Manila 10/10.", 205 - (1 - a) * 20, 56, hexc('#22223b', a), maxw=960)
    ctext(ctx, "Halo-halo: 11/10.", 290, 62, hexc(RED, ease((t - 0.5) / 0.3)), maxw=900)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Where should they go next? Comment below", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=960)

SCENES = [(s0, 2.6), (s1, 3.2), (s2, 3.4), (s3, 3.4), (s4, 2.6)]

def frame(fn, t, d):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    fn(ctx, t, d)
    a_in = 0 if fn is s0 else 1 - t / 0.1
    a_out = (t - (d - 0.5)) / 0.5 if fn is s4 else (t - (d - 0.1)) / 0.1
    a = max(a_in, a_out, 0)
    if a > 0:
        ctx.set_source_rgba(*hexc('#fff3e0', min(1, ease(a)))); ctx.paint()
    return surf

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        from PIL import Image
        picks = [(s0, 1.4), (s1, 0.9), (s1, 2.0), (s1, 3.0), (s2, 0.9), (s2, 1.5), (s2, 2.6), (s3, 0.8), (s3, 1.9), (s4, 2.0)]
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

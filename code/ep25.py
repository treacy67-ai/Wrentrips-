"""ep25 - Country road trip: the GPS sends Wren round the same roundabout 7 times, then into a field of sheep. Wren unfolds the paper map. Nobody can refold it."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep25"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; NAVY = '#1d3557'; CAR = '#2a9d8f'; CAR_D = '#21867a'; PAPER = '#f6e7c1'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
ROAD = 1590                      # tyre contact line
CX = 600                         # car centre
WS, KS = 0.62, 0.66              # Wren / Leo scale inside the car

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

def ftext(ctx, s, cx, y, size, col, maxw, bold=True):
    mv.font(ctx, size, bold); e = ctx.text_extents(s)
    while e.x_advance > maxw and size > 12:
        size -= 1; mv.font(ctx, size, bold); e = ctx.text_extents(s)
    ctx.move_to(cx - e.x_advance / 2, y); ctx.set_source_rgba(*col); ctx.show_text(s)

# ------------------------------------------------------------ GPS screen
def gps(ctx, text, a, kind="recalc", t=0.0):
    if a <= 0: return
    ctx.save(); ctx.translate(0, (1 - a) * -16)
    rrect(ctx, 150, 612, 780, 104, 30); ctx.set_source_rgba(*hexc('#0b2545', 0.95 * a)); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#4cc9f0', 0.8 * a)); rrect(ctx, 150, 612, 780, 104, 30); ctx.stroke()
    ix, iy = 222, 664
    if kind == "recalc":                                   # spinning arrow
        ctx.save(); ctx.translate(ix, iy); ctx.rotate(t * 6)
        ctx.set_line_width(9); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.arc(0, 0, 26, 0.4, 2 * math.pi - 0.3); ctx.stroke()
        ctx.move_to(30, -6); ctx.line_to(18, 14); ctx.line_to(40, 12); ctx.close_path(); ctx.fill(); ctx.restore()
    elif kind == "turn":                                   # 'take exit' arrow
        circle(ctx, ix, iy, 34, hexc('#3a86ff', a))
        ctx.set_line_width(9); ctx.set_source_rgba(1, 1, 1, a); ctx.arc(ix, iy, 16, -math.pi * 0.9, math.pi * 0.6); ctx.stroke()
    else:                                                  # chequered flag
        ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, a); ctx.move_to(ix - 20, iy + 30); ctx.line_to(ix - 20, iy - 32); ctx.stroke()
        for i in range(4):
            for j in range(3):
                ctx.rectangle(ix - 18 + i * 11, iy - 32 + j * 11, 11, 11)
                ctx.set_source_rgba(*(hexc('#ffffff', a) if (i + j) % 2 else hexc('#2a9d8f', a))); ctx.fill()
    mv.font(ctx, 46); e = ctx.text_extents(text); size = 46
    while e.x_advance > 640: size -= 1; mv.font(ctx, size); e = ctx.text_extents(text)
    ctx.move_to(276, 682); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(text)
    ctx.restore()

# ------------------------------------------------------------ background: rolling countryside
def country(ctx, t, scroll=0.0, sheep_field=False):
    mv.vgrad(ctx, '#bde0fe', '#e9f5ff')
    circle(ctx, 880, 860, 70, hexc('#ffe08a'))
    for cx_, cy_ in ((180, 800), (640, 760), (980, 1000)):
        x = (cx_ - scroll * 0.1) % 1300 - 110
        for dx, r in ((-40, 34), (0, 48), (46, 32)): circle(ctx, x + dx, cy_, r, (1, 1, 1, 0.9))
    for k, (base, amp, col, sp) in enumerate(((1120, 70, '#95d5b2', 0.25), (1190, 50, '#74c69d', 0.5), (1280, 40, '#52b788', 0.8))):
        ctx.move_to(0, H)
        for x in range(0, W + 20, 20):
            ctx.line_to(x, base - amp * math.sin((x + scroll * sp) / (260 + 60 * k) + k) - 20 * math.sin((x + scroll * sp) / 90 + k))
        ctx.line_to(W, H); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    # hedgerow trees
    for i in range(7):
        x = (i * 190 - scroll * 0.8) % 1330 - 120
        ctx.set_source_rgba(*hexc('#6f4e37')); ctx.rectangle(x - 8, 1260, 16, 70); ctx.fill()
        circle(ctx, x, 1240, 46, hexc('#2d6a4f')); circle(ctx, x - 26, 1262, 30, hexc('#2d6a4f')); circle(ctx, x + 28, 1260, 32, hexc('#2d6a4f'))
    # fence
    ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#a47148'))
    off = scroll % 120
    for i in range(11):
        x = i * 120 - off; ctx.move_to(x, 1440); ctx.line_to(x, 1370); ctx.stroke()
    ctx.move_to(0, 1385); ctx.line_to(W, 1385); ctx.stroke(); ctx.move_to(0, 1415); ctx.line_to(W, 1415); ctx.stroke()
    # road
    ctx.rectangle(0, 1450, W, 240); ctx.set_source_rgba(*hexc('#6c757d')); ctx.fill()
    ctx.rectangle(0, 1450, W, 10); ctx.set_source_rgba(*hexc('#adb5bd')); ctx.fill()
    off = (scroll * 1.6) % 200
    for i in range(8):
        rrect(ctx, i * 200 - off, 1612, 110, 14, 7); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.fill()
    ctx.rectangle(0, 1690, W, H - 1690); ctx.set_source_rgba(*hexc('#52b788')); ctx.fill()
    for i in range(30):
        x = (i * 41 - scroll * 1.6) % 1140 - 30
        ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#2d6a4f')); ctx.move_to(x, 1700 + (i % 3) * 60); ctx.line_to(x + 8, 1680 + (i % 3) * 60); ctx.stroke()

def cow(ctx, x, base, s=1.0):
    ctx.save(); ctx.translate(x, base); ctx.scale(s, s)
    for dx in (-50, -30, 34, 54): rrect(ctx, dx - 9, -60, 18, 60, 6); ctx.set_source_rgba(*hexc('#3d3d3d')); ctx.fill()
    rrect(ctx, -80, -130, 170, 84, 40); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    for (dx, dy, r) in ((-40, -100, 20), (20, -80, 16), (52, -110, 13)): circle(ctx, dx, dy, r, hexc('#222222'))
    rrect(ctx, -126, -150, 66, 64, 26); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    rrect(ctx, -132, -110, 52, 30, 14); ctx.set_source_rgba(*hexc('#ffafcc')); ctx.fill()
    circle(ctx, -104, -130, 6, hexc('#222222'))
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#e9c46a')); ctx.move_to(-112, -150); ctx.line_to(-120, -168); ctx.stroke(); ctx.move_to(-78, -150); ctx.line_to(-70, -168); ctx.stroke()
    ctx.restore()

def sheep(ctx, x, base, s=1.0, t=0.0, seed=0, face=-1):
    ctx.save(); ctx.translate(x, base + 3 * math.sin(t * 7 + seed)); ctx.scale(s * (1 if face < 0 else -1), s)
    for dx in (-30, -12, 16, 32): rrect(ctx, dx - 6, -40, 12, 40, 5); ctx.set_source_rgba(*hexc('#2b2b2b')); ctx.fill()
    for (dx, dy, r) in ((-30, -60, 30), (0, -72, 34), (30, -60, 30), (-14, -46, 28), (16, -46, 28), (0, -88, 24)):
        circle(ctx, dx, dy, r, hexc('#fbfbf7'))
    e4.ell(ctx, -56, -66, 20, 26, hexc('#2b2b2b'))
    circle(ctx, -62, -72, 5, (1, 1, 1, 1)); circle(ctx, -62, -72, 2.5, hexc('#000000'))
    e4.ell(ctx, -42, -86, 10, 6, hexc('#2b2b2b'), -0.4)
    ctx.restore()

def roundabout_sign(ctx, x, base):
    ctx.set_source_rgba(*hexc('#8d99ae')); ctx.rectangle(x - 7, base - 260, 14, 260); ctx.fill()
    circle(ctx, x, base - 300, 64, (1, 1, 1, 1)); circle(ctx, x, base - 300, 56, hexc('#3a86ff'))
    ctx.set_line_width(9); ctx.set_source_rgba(1, 1, 1, 1)
    for k in range(3):
        a0 = k * 2 * math.pi / 3
        ctx.arc(x, base - 300, 30, a0, a0 + 1.5); ctx.stroke()
        ax, ay = x + 30 * math.cos(a0 + 1.6), base - 300 + 30 * math.sin(a0 + 1.6)
        ctx.move_to(ax + 12 * math.cos(a0 + 1.6 + 1.57), ay + 12 * math.sin(a0 + 1.6 + 1.57)); ctx.line_to(ax - 10 * math.cos(a0 + 1.6), ay - 10 * math.sin(a0 + 1.6))
        ctx.line_to(ax - 12 * math.cos(a0 + 1.6 + 1.57), ay - 12 * math.sin(a0 + 1.6 + 1.57)); ctx.close_path(); ctx.fill()

# ------------------------------------------------------------ the little convertible
def car_back(ctx, cx):
    for sx in (cx - 210, cx + 30):                         # seat backs
        rrect(ctx, sx - 70, 1250, 140, 140, 30); ctx.set_source_rgba(*hexc('#6d4c41')); ctx.fill()

def car_front(ctx, cx, t, moving=True):
    bob = 3 * math.sin(t * 18) if moving else 0
    ctx.save(); ctx.translate(0, bob)
    ctx.move_to(cx - 330, 1530); ctx.line_to(cx - 330, 1400); ctx.curve_to(cx - 330, 1370, cx - 310, 1360, cx - 280, 1360)
    ctx.line_to(cx + 150, 1360); ctx.line_to(cx + 190, 1400); ctx.line_to(cx + 320, 1410)
    ctx.curve_to(cx + 350, 1414, cx + 360, 1440, cx + 360, 1470); ctx.line_to(cx + 360, 1530); ctx.close_path()
    ctx.set_source_rgba(*hexc(CAR)); ctx.fill()
    rrect(ctx, cx - 340, 1500, 710, 40, 20); ctx.set_source_rgba(*hexc('#ced4da')); ctx.fill()        # bumper strip
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc(CAR_D)); ctx.move_to(cx - 80, 1372); ctx.line_to(cx - 80, 1500); ctx.stroke()
    rrect(ctx, cx - 50, 1420, 46, 12, 6); ctx.set_source_rgba(*hexc('#e9ecef')); ctx.fill()           # door handle
    circle(ctx, cx + 340, 1440, 18, hexc('#ffd166')); circle(ctx, cx - 316, 1430, 12, hexc(RED))     # lights
    # windscreen
    ctx.set_line_width(8); ctx.set_source_rgba(*hexc('#adb5bd')); ctx.move_to(cx + 150, 1362); ctx.line_to(cx + 110, 1240); ctx.stroke()
    ctx.move_to(cx + 150, 1362); ctx.line_to(cx + 110, 1240); ctx.line_to(cx + 128, 1240); ctx.line_to(cx + 166, 1362); ctx.close_path()
    ctx.set_source_rgba(*hexc('#caf0f8', 0.5)); ctx.fill()
    # steering wheel
    ctx.set_line_width(10); ctx.set_source_rgba(*hexc('#343a40')); ctx.save(); ctx.translate(cx + 96, 1318); ctx.scale(0.45, 1); ctx.arc(0, 0, 44, 0, 2 * math.pi); ctx.restore(); ctx.stroke()
    # L-plate style rental sticker
    rrect(ctx, cx - 300, 1410, 120, 60, 8); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ftext(ctx, "RENTAL", cx - 240, 1450, 24, hexc(NAVY), 104)
    ctx.restore()
    for wx in (cx - 210, cx + 220):
        circle(ctx, wx, ROAD - 62, 62, hexc('#212529')); circle(ctx, wx, ROAD - 62, 30, hexc('#ced4da'))
        ang = -t * 14 if moving else 0
        ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#6c757d'))
        for k in range(3):
            a = ang + k * 2.09; ctx.move_to(wx, ROAD - 62); ctx.line_to(wx + 28 * math.cos(a), ROAD - 62 + 28 * math.sin(a)); ctx.stroke()

STEER = (CX + 96, 1318)
def riders(ctx, t, cx, wexpr="happy", kexpr="smile", whand=None, wmode="point", kh=(-60, -170)):
    wx = cx + 20; wgy = 1600
    if whand is None:
        hx, hy = STEER[0] - CX + cx, STEER[1]
        whand = ((hx - wx) / WS, (hy - wgy) / WS)
    ctx.save(); ctx.rectangle(0, 0, W, 1470); ctx.clip()
    kid(ctx, cx - 200, 1520, KS, t, kexpr, kh)
    wren(ctx, wx, wgy, WS, t, wmode, expr=wexpr, hand=whand)
    ctx.restore()

G = 1.25                                                     # car group scale (pivot on the road under the car)
def gin(ctx, cx):
    ctx.save(); ctx.translate(cx, ROAD); ctx.scale(G, G); ctx.translate(-cx, -ROAD)
def gpt(cx, x, y): return (cx + (x - cx) * G, ROAD + (y - ROAD) * G)

# ------------------------------------------------------------ paper map
def paper_map(ctx, x0, y0, w, h, a=1.0, folds=(4, 3)):
    if w < 4 or h < 4 or a <= 0: return
    ctx.save(); ctx.rectangle(x0, y0, w, h); ctx.clip()
    ctx.rectangle(x0, y0, w, h); ctx.set_source_rgba(*hexc(PAPER, a)); ctx.fill()
    for (fx, fy, r, c) in ((0.2, 0.3, 0.16, '#b7e4c7'), (0.7, 0.65, 0.2, '#b7e4c7'), (0.55, 0.2, 0.1, '#d8f3dc'), (0.85, 0.25, 0.12, '#b7e4c7')):
        circle(ctx, x0 + fx * w, y0 + fy * h, r * max(w, h), hexc(c, a))
    ctx.set_line_width(max(2, w / 90)); ctx.set_source_rgba(*hexc('#4cc9f0', a))
    ctx.move_to(x0, y0 + h * 0.8); ctx.curve_to(x0 + w * 0.3, y0 + h * 0.5, x0 + w * 0.6, y0 + h * 1.0, x0 + w, y0 + h * 0.7); ctx.stroke()
    ctx.set_line_width(max(2, w / 120)); ctx.set_source_rgba(*hexc(RED, a))
    ctx.move_to(x0 + w * 0.05, y0 + h * 0.15); ctx.line_to(x0 + w * 0.45, y0 + h * 0.45); ctx.line_to(x0 + w * 0.9, y0 + h * 0.4); ctx.stroke()
    ctx.move_to(x0 + w * 0.45, y0 + h * 0.45); ctx.line_to(x0 + w * 0.6, y0 + h * 0.9); ctx.stroke()
    ctx.set_line_width(max(2, w / 160)); ctx.set_source_rgba(*hexc('#e9c46a', a))
    ctx.move_to(x0 + w * 0.1, y0 + h * 0.6); ctx.line_to(x0 + w * 0.8, y0 + h * 0.1); ctx.stroke()
    # little X on the tea room
    if w > 300:
        cx_, cy_ = x0 + w * 0.82, y0 + h * 0.36; ctx.set_line_width(7); ctx.set_source_rgba(*hexc(RED, a))
        ctx.move_to(cx_ - 14, cy_ - 14); ctx.line_to(cx_ + 14, cy_ + 14); ctx.stroke(); ctx.move_to(cx_ + 14, cy_ - 14); ctx.line_to(cx_ - 14, cy_ + 14); ctx.stroke()
    ctx.set_line_width(2); ctx.set_source_rgba(*hexc('#9c8b6e', 0.8 * a))
    nx, ny = folds
    for i in range(1, nx): ctx.move_to(x0 + w * i / nx, y0); ctx.line_to(x0 + w * i / nx, y0 + h); ctx.stroke()
    for j in range(1, ny): ctx.move_to(x0, y0 + h * j / ny); ctx.line_to(x0 + w, y0 + h * j / ny); ctx.stroke()
    ctx.restore()
    ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#9c8b6e', a)); ctx.rectangle(x0, y0, w, h); ctx.stroke()

def crumple(ctx, cx, cy, r, seed, a=1.0):
    rnd = random.Random(seed); n = 11
    ctx.move_to(cx + r, cy)
    for k in range(1, n + 1):
        ang = k * 2 * math.pi / n; rr = r * rnd.uniform(0.7, 1.15)
        ctx.line_to(cx + rr * math.cos(ang), cy + rr * math.sin(ang) * 0.75)
    ctx.close_path(); ctx.set_source_rgba(*hexc(PAPER, a)); ctx.fill_preserve()
    ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#9c8b6e', a)); ctx.stroke()
    ctx.set_line_width(3)
    for _ in range(4):
        ctx.move_to(cx + rnd.uniform(-r, r) * 0.6, cy + rnd.uniform(-r, r) * 0.45); ctx.line_to(cx + rnd.uniform(-r, r) * 0.6, cy + rnd.uniform(-r, r) * 0.45)
        ctx.set_source_rgba(*hexc(RED if rnd.random() < 0.4 else '#9c8b6e', 0.8 * a)); ctx.stroke()

def teacup(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    e4.ell(ctx, 0, 6, 46, 10, hexc('#ffffff'))
    ctx.move_to(-32, -40); ctx.line_to(32, -40); ctx.curve_to(30, -4, 20, 4, 0, 4); ctx.curve_to(-20, 4, -30, -4, -32, -40); ctx.close_path()
    ctx.set_source_rgba(*hexc('#ffffff')); ctx.fill()
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#ffffff')); ctx.arc(36, -24, 12, -1.6, 1.6); ctx.stroke()
    for k in (-14, 0, 14): circle(ctx, k, -24, 4, hexc('#e76f51'))
    ctx.restore()

def tearoom(ctx):
    rrect(ctx, 620, 960, 440, 420, 8); ctx.set_source_rgba(*hexc('#fffaf0')); ctx.fill()
    ctx.move_to(590, 980); ctx.line_to(840, 820); ctx.line_to(1090, 980); ctx.close_path(); ctx.set_source_rgba(*hexc('#c9a227')); ctx.fill()
    ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#a0821d'))
    for k in range(6): ctx.move_to(620 + k * 80, 980); ctx.line_to(700 + k * 60, 880 - (k % 2) * 10); ctx.stroke()
    for wx_ in (680, 940):
        rrect(ctx, wx_, 1040, 90, 90, 6); ctx.set_source_rgba(*hexc('#caf0f8')); ctx.fill()
        ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#6f4e37')); rrect(ctx, wx_, 1040, 90, 90, 6); ctx.stroke()
    rrect(ctx, 790, 1060, 100, 160, 8); ctx.set_source_rgba(*hexc('#6f4e37')); ctx.fill()
    rrect(ctx, 700, 990, 280, 46, 10); ctx.set_source_rgba(*hexc(NAVY)); ctx.fill()
    ftext(ctx, "TEA ROOM", 840, 1024, 30, (1, 1, 1, 1), 260)
    for k in range(5): circle(ctx, 640 + k * 100, 1000 - 14, 9, hexc('#ff8fab'))

# ------------------------------------------------------------ scenes
P = 0.46                                                    # one lap of the roundabout
def s0(ctx, t, d):
    scroll = t * 520
    country(ctx, t, scroll)
    ph = ((t + 0.12) % P) / P                                # the SAME cow and sign keep coming round
    lap = min(7, 1 + int((t + 0.12) / P))
    cow(ctx, 1220 - ph * 1500, 1320, 0.9)
    roundabout_sign(ctx, 1400 - ph * 1500, 1450)
    gin(ctx, CX); car_back(ctx, CX)
    riders(ctx, t, CX, "shock" if lap >= 6 else "happy", "flat" if lap >= 4 else "smile", kh=(-40, -150))
    car_front(ctx, CX, t); ctx.restore()
    if lap < 3: gps(ctx, "Take the 3rd exit.", 1.0, "turn", t)
    else: gps(ctx, "Recalculating…", 1.0, "recalc", t)
    bubble_ml(ctx, 330, 900, ["Lovely cow.", "Again."], 44, ramp(t, 2.3, 2.5), gpt(CX, CX + 20, 1150))
    header(ctx, ease(t / 0.2 + 1), "COUNTRY ROAD TRIP", "GPS: “Take the 3rd exit.”", "Lap 7. Same cow.", -0.3, t, main_size=54)
    meter(ctx, "TIMES ROUND THE ROUNDABOUT", "%d" % lap); wm(ctx)

SHEEP = [(1000, 1500, 0.9), (930, 1700, 1.0), (1040, 1640, 0.85), (250, 1700, 0.95), (120, 1520, 0.8), (380, 1480, 0.75),
         (60, 1360, 0.6), (200, 1350, 0.6), (820, 1350, 0.6), (980, 1340, 0.55), (560, 1340, 0.55), (700, 1690, 0.9), (470, 1720, 0.85), (990, 1400, 0.6)]
def s1(ctx, t, d):
    country(ctx, t, 2000)
    n = 0
    for k, (sx, sy, ss) in enumerate(SHEEP):
        if sy < 1450:
            tk = 0.2 + k * 0.12; pop = ramp(t, tk, tk + 0.2)
            if pop > 0: sheep(ctx, sx, sy, ss * pop, t, k, -1 if k % 2 else 1); n += 1
    gin(ctx, CX); car_back(ctx, CX)
    riders(ctx, t, CX, "shock" if t < 2.6 else "happy", "flat", kh=(-40, -150))
    car_front(ctx, CX, t, moving=False); ctx.restore()
    for k, (sx, sy, ss) in enumerate(SHEEP):
        if sy >= 1450:
            tk = 0.2 + k * 0.12; pop = ramp(t, tk, tk + 0.2)
            if pop > 0: sheep(ctx, sx, sy, ss * pop, t, k, -1 if k % 2 else 1); n += 1
    gps(ctx, "You have arrived.", ramp(t, 0.0, 0.2), "flag", t)
    bubble_ml(ctx, 340, 880, ["We have NOT", "arrived."], 44, ramp(t, 0.9, 1.1) * (1 - ramp(t, 2.6, 2.75)), gpt(CX, CX - 200, 1175))
    bubble_ml(ctx, 720, 880, ["They seem", "very welcoming."], 42, ramp(t, 2.85, 3.05), gpt(CX, CX + 20, 1150))
    header(ctx, ease(t / 0.2), "THEN", "GPS: “You have arrived.”", "It's a field of sheep.", 0.8, t, main_size=54)
    meter(ctx, "SHEEP AROUND THE CAR", "%d" % n); wm(ctx)

STAGES = [(80, 60)]
for _k in range(12):
    w_, h_ = STAGES[-1]; STAGES.append((w_ * 1.45, h_) if _k % 2 == 0 else (w_, h_ * 1.38))
MAXW = 940
def s2(ctx, t, d):
    country(ctx, t, 2000)
    nf = clamp01((t - 0.3) / 2.4) * 12; n = int(nf)
    gin(ctx, CX); car_back(ctx, CX)
    riders(ctx, t, CX, "happy", "flat", wmode="cheer", kh=(-40, -150))
    car_front(ctx, CX, t, moving=False); ctx.restore()
    w0, h0 = STAGES[n]; w1, h1 = STAGES[min(12, n + 1)]; k = ease(nf - n)
    w, h = lerp(w0, w1, k), lerp(h0, h1, k)
    f = MAXW / STAGES[12][0]; w, h = max(90, w * f), max(66, min(380, h * f * 1.25))
    bottom = 1000; x0 = min(max(70, CX + 25 - w / 2), 1010 - w)
    sway = 6 * math.sin(t * 5)
    paper_map(ctx, x0, bottom - h + sway, w, h, 1.0, (max(1, (n + 2) // 2), max(1, (n + 1) // 2)))
    bubble_ml(ctx, 300, 880, ["Is that map", "from 1974?"], 40, ramp(t, 1.4, 1.6) * (1 - ramp(t, 2.8, 2.95)), gpt(CX, CX - 200, 1175))
    bubble_ml(ctx, 700, 860, ["Maps never", "lose signal."], 44, ramp(t, 3.0, 3.2), gpt(CX, CX + 20, 1150))
    header(ctx, ease(t / 0.2), "WREN'S FIX", "The emergency paper map.", "It unfolds. And unfolds.", 0.9, t, main_size=52)
    meter(ctx, "FOLDS OPENED", "%d / 12" % n); wm(ctx)

C3 = 720
def s3(ctx, t, d):
    country(ctx, t, 2600)
    tearoom(ctx)
    att = min(9, int(clamp01((t - 0.3) / 2.6) * 9) + 1)
    gin(ctx, C3); car_back(ctx, C3)
    ctx.save(); ctx.rectangle(0, 0, W, 1470); ctx.clip()
    kid(ctx, C3 + 20, 1475, KS, t, "flat", (-40, -150)); ctx.restore()
    for j in range(3):                                         # tangled in the map
        crumple(ctx, C3 + 20 + (j - 1) * 62, 1362 + (j % 2) * 16, 62 - j * 4, att * 7 + j)
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc(PAPER)); ctx.move_to(C3 - 70, 1330); ctx.curve_to(C3 + 10, 1300, C3 - 10, 1400, C3 + 120, 1350); ctx.stroke()
    car_front(ctx, C3, t, moving=False); ctx.restore()
    wren(ctx, 410, 1700, 0.85, t, "point", expr="happy", hand=(150, -330))
    teacup(ctx, 410 + 150 * 0.85, 1700 - 330 * 0.85 - 18, 0.9)
    bubble_ml(ctx, 780, 830, ["Help. It has", "13 folds now."], 40, ramp(t, 0.8, 1.0) * (1 - ramp(t, 2.5, 2.65)), gpt(C3, C3 + 20, 1170))
    bubble_ml(ctx, 400, 860, ["Nobody refolds", "a map, love."], 44, ramp(t, 2.7, 2.9), (410, 1060))
    header(ctx, ease(t / 0.2), "THE CATCH", "Tea room: found in 20 min.", "Refolding it: 2 hours.", 0.9, t, main_size=52)
    meter(ctx, "REFOLD ATTEMPTS", "%d" % att); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 470, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    crumple(ctx, 830, 1520 + 6 * math.sin(t * 3), 110, 99)
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “Paper never loses signal.”", 205 - (1 - a) * 20, 56, hexc('#22223b', a), maxw=1000)
    ctext(ctx, "Leo: “It never folds back, either.”", 290, 56, hexc(RED, ease((t - 0.5) / 0.3)), maxw=1000)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "GPS or paper map? Comment below!", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

SCENES = [(s0, 3.8), (s1, 4.4), (s2, 4.4), (s3, 4.0), (s4, 3.2)]   # 19.8s

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
        picks = [(s0, 0.0), (s0, 1.5), (s0, 3.3), (s1, 0.6), (s1, 1.8), (s1, 3.9), (s2, 1.0), (s2, 2.0), (s2, 3.9), (s3, 1.0), (s3, 2.0), (s3, 3.7), (s4, 1.0), (s4, 2.6)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((300, 533)))
        c = Image.new("RGB", (310 * 7, 543 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 7) * 310, (i // 7) * 543))
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

"""ep22 - Hotel pool sunbeds: Leo gets up at 6, 5, then 4 AM to beat the towels. Wren just buys a flamingo."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep22")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; PINK = '#ff7eb6'; PINK_D = '#e85a9b'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1700
WX, LX = 440, 880
BEDS = [130 + i * 165 for i in range(6)]; BED_Y = 930
TOWELS = ['#e63946', '#4361ee', '#ffd60a', '#2a9d8f', '#ff8c42', '#b388ff']

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

# ------------------------------------------------------------ hotel pool
SKY = {'dawn': ('#ffb88a', '#ffe6c7'), 'predawn': ('#6a5acd', '#f7b7a3'), 'night': ('#101a3c', '#2b3a6b'), 'day': ('#4db8ff', '#d6f3ff')}
SHADE = {'dawn': ('#ff9e6d', 0.10), 'predawn': ('#3b2f7a', 0.28), 'night': ('#0b1230', 0.50), 'day': None}
random.seed(22); STARS = [(random.uniform(20, 1060), random.uniform(600, 750), random.uniform(2, 5)) for _ in range(40)]

def palm(ctx, x, base, h, t, flip=1):
    ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#8a5a2b'))
    ctx.move_to(x, base); ctx.curve_to(x + 20 * flip, base - h * 0.4, x - 10 * flip, base - h * 0.8, x + 14 * flip, base - h); ctx.stroke()
    tx, ty = x + 14 * flip, base - h
    for k in range(6):
        a = -math.pi / 2 + (k - 2.5) * 0.62 + 0.05 * math.sin(t * 1.6 + k)
        ex, ey = tx + math.cos(a) * 150, ty + math.sin(a) * 110 + 60
        ctx.set_line_width(24); ctx.set_source_rgba(*hexc('#2f9e44' if k % 2 else '#38b24f'))
        ctx.move_to(tx, ty); ctx.curve_to(tx + math.cos(a) * 80, ty + math.sin(a) * 110, ex, ey - 70, ex, ey); ctx.stroke()
    circle(ctx, tx - 8, ty + 14, 13, hexc('#6b4423')); circle(ctx, tx + 12, ty + 16, 13, hexc('#6b4423'))

def sunbed(ctx, x, base, s=1.0, towel=None, drop=1.0):
    """side view, head end on the left. towel = colour or None; drop 0..1 = towel falling in."""
    ctx.save(); ctx.translate(x, base); ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(8); ctx.set_source_rgba(*hexc('#9aa5b1'))
    for lx in (-52, 52): ctx.move_to(lx, -30); ctx.line_to(lx, 0); ctx.stroke()
    ctx.set_line_width(16); ctx.set_source_rgba(1, 1, 1, 1); ctx.move_to(-66, -36); ctx.line_to(-108, -108); ctx.stroke()
    rrect(ctx, -72, -44, 144, 16, 8); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#cfd6de')); ctx.move_to(-66, -28); ctx.line_to(66, -28); ctx.stroke()
    if towel and drop > 0:
        dy = -(1 - drop) * 330; ctx.translate(0, dy)
        ctx.set_line_width(20); ctx.set_source_rgba(*hexc(towel)); ctx.move_to(-66, -42); ctx.line_to(-104, -106); ctx.stroke()
        rrect(ctx, -70, -52, 138, 18, 8); ctx.fill()
        rrect(ctx, 50, -52, 18, 44, 8); ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.75)
        for k in range(4): ctx.rectangle(-48 + k * 30, -52, 10, 18); ctx.fill()
        ctx.rectangle(50, -20, 18, 6); ctx.fill()
    ctx.restore()

def pool_bg(ctx, t, tod='dawn', n_towels=6, drops=None, props=False):
    top, bot = SKY[tod]
    g = cairo.LinearGradient(0, 0, 0, 800); g.add_color_stop_rgb(0, *hexc(top)[:3]); g.add_color_stop_rgb(1, *hexc(bot)[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 800); ctx.fill()
    if tod == 'night':
        for i, (sx, sy, r) in enumerate(STARS): circle(ctx, sx, sy, r, (1, 1, 1, 0.55 + 0.4 * math.sin(t * 3 + i)))
        circle(ctx, 250, 680, 52, hexc('#fff6d6')); circle(ctx, 274, 666, 46, hexc('#16224a'))
    elif tod == 'day':
        circle(ctx, 240, 690, 80, hexc('#fff3b0', 0.45)); circle(ctx, 240, 690, 54, hexc('#ffd60a'))
        for cx, cy in ((720, 660), (420, 720)):
            x = (cx + t * 10) % 1300 - 110
            for dx, dy, r in ((-60, 10, 36), (0, -8, 50), (60, 10, 38)): circle(ctx, x + dx, cy + dy, r, (1, 1, 1, 0.9))
    else:
        sy = 750 if tod == 'dawn' else 800
        circle(ctx, 540, sy, 120, hexc('#fff3b0', 0.4)); circle(ctx, 540, sy, 74, hexc('#ffd166'))
    # hedge, palms, back deck
    for k in range(13): circle(ctx, k * 90, 790, 55, hexc('#3a8f5c'))
    palm(ctx, 40, 810, 170, t, 1); palm(ctx, 1040, 810, 185, t + 1, -1)
    ctx.rectangle(0, 790, W, 180); ctx.set_source_rgba(*hexc('#f1dfc0')); ctx.fill()
    for i, bx in enumerate(BEDS):
        d = 1.0 if drops is None else drops[i]
        sunbed(ctx, bx, BED_Y, 1.0, TOWELS[i] if i < n_towels else None, d)
    if props:
        e4.ell(ctx, BEDS[1] + 6, BED_Y - 60, 34, 9, hexc('#f4d58d')); ctx.arc(BEDS[1] + 6, BED_Y - 62, 18, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc('#f4d58d')); ctx.fill()
        circle(ctx, BEDS[3] + 4, BED_Y - 66, 16, hexc('#ffd60a')); circle(ctx, BEDS[3] + 18, BED_Y - 82, 10, hexc('#ffd60a')); rrect(ctx, BEDS[3] + 24, BED_Y - 84, 12, 6, 3); ctx.set_source_rgba(*hexc('#ff8c42')); ctx.fill()
        rrect(ctx, BEDS[4] - 20, BED_Y - 62, 44, 10, 3); ctx.set_source_rgba(*hexc('#4361ee')); ctx.fill(); rrect(ctx, BEDS[4] - 16, BED_Y - 70, 44, 10, 3); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    # pool
    g = cairo.LinearGradient(0, 960, 0, 1420); g.add_color_stop_rgb(0, *hexc('#48cae4')[:3]); g.add_color_stop_rgb(1, *hexc('#0096c7')[:3])
    ctx.set_source(g); ctx.rectangle(0, 960, W, 460); ctx.fill()
    ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(1, 1, 1, 0.35)
    for r in range(5):
        for k in range(5):
            x = (k * 250 + r * 110 + t * (18 + 6 * r)) % 1240 - 80; y = 1010 + r * 84
            ctx.move_to(x, y); ctx.curve_to(x + 25, y - 12, x + 50, y + 12, x + 80, y); ctx.stroke()
    ctx.rectangle(0, 948, W, 18); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.rectangle(0, 1410, W, 22); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    # front deck
    ctx.rectangle(0, 1432, W, H - 1432); ctx.set_source_rgba(*hexc('#ecd9b8')); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#dcc59c'))
    for k in range(4): ctx.move_to(0, 1520 + k * 120); ctx.line_to(W, 1520 + k * 120); ctx.stroke()
    for k in range(7): ctx.move_to(k * 180 - 40, 1432); ctx.line_to(k * 200 - 120, H); ctx.stroke()
    if SHADE[tod]:
        c, a = SHADE[tod]; ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(*hexc(c, a)); ctx.fill()

def teacup(ctx, cx, cy):
    rrect(ctx, cx - 30, cy - 50, 60, 50, 12); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill(); e4.ell(ctx, cx, cy + 4, 50, 9, (1, 1, 1, 1))

def towel_roll(ctx, x, y, col=RED):
    rrect(ctx, x - 62, y - 26, 124, 52, 26); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.8)
    for k in range(3): ctx.rectangle(x - 34 + k * 30, y - 26, 10, 52); ctx.fill()

def alarm(ctx, x, y, t, ring=True):
    sh = 7 * math.sin(t * 60) if ring else 0
    ctx.save(); ctx.translate(x + sh, y)
    for sg in (-1, 1): circle(ctx, sg * 34, -44, 20, hexc('#ffd166'))
    circle(ctx, 0, 0, 52, hexc(RED)); circle(ctx, 0, 0, 40, (1, 1, 1, 1))
    ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#22223b')); ctx.move_to(0, 0); ctx.line_to(0, -26); ctx.stroke(); ctx.move_to(0, 0); ctx.line_to(18, 10); ctx.stroke()
    ctx.restore()
    if ring:
        ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#22223b', 0.7))
        for sg in (-1, 1):
            for r in (78, 100): ctx.arc(x, y, r, (-0.5 if sg > 0 else math.pi - 0.5), (0.5 if sg > 0 else math.pi + 0.5)); ctx.stroke()

def umbrella(ctx, hx, hy, k):
    if k <= 0: return
    top = hy - 330
    ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#5c4033')); ctx.move_to(hx, hy + 20); ctx.line_to(hx, top - 10); ctx.stroke()
    r = 250 * (0.2 + 0.8 * k)
    ctx.save(); ctx.translate(hx, top + 150); ctx.scale(1, 0.62)
    for i in range(6):
        a0 = math.pi + i * math.pi / 6; ctx.move_to(0, 0); ctx.arc(0, 0, r, a0, a0 + math.pi / 6); ctx.close_path()
        ctx.set_source_rgba(*hexc('#ffd60a' if i % 2 else RED)); ctx.fill()
    ctx.restore()

def rain(ctx, t, a):
    if a <= 0: return
    ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#bfe3ff', 0.75 * a))
    for k in range(70):
        x = (k * 137.5) % 1120 - 20; y = 700 + ((k * 211.3 + t * 1500) % 1240)
        ctx.move_to(x, y); ctx.line_to(x - 10, y + 44); ctx.stroke()

def storm_cloud(ctx, x, y):
    for dx, dy, r in ((-150, 20, 80), (-60, -30, 110), (60, -20, 120), (160, 20, 86), (0, 40, 100)): circle(ctx, x + dx, y + dy, r, hexc('#5b6478'))
    for dx, dy, r in ((-60, -40, 80), (60, -34, 90)): circle(ctx, x + dx, y + dy, r, hexc('#727c92'))

def flamingo_back(ctx, x, y, s):
    e4.ell(ctx, x, y + 34 * s, 250 * s, 34 * s, (1, 1, 1, 0.35))
    e4.ell(ctx, x - 190 * s, y - 34 * s, 70 * s, 36 * s, hexc(PINK_D), -0.5)
    e4.ell(ctx, x, y, 210 * s, 70 * s, hexc(PINK)); e4.ell(ctx, x, y - 10 * s, 130 * s, 34 * s, hexc(PINK_D))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(50 * s); ctx.set_source_rgba(*hexc(PINK))
    ctx.move_to(x + 170 * s, y - 10 * s); ctx.curve_to(x + 300 * s, y - 90 * s, x + 150 * s, y - 190 * s, x + 236 * s, y - 286 * s); ctx.stroke()
    hx, hy = x + 244 * s, y - 296 * s
    ctx.move_to(hx + 30 * s, hy - 26 * s); ctx.line_to(hx + 112 * s, hy + 6 * s); ctx.line_to(hx + 84 * s, hy + 46 * s); ctx.line_to(hx + 26 * s, hy + 26 * s); ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    ctx.move_to(hx + 80 * s, hy - 6 * s); ctx.line_to(hx + 112 * s, hy + 6 * s); ctx.line_to(hx + 84 * s, hy + 46 * s); ctx.line_to(hx + 64 * s, hy + 38 * s); ctx.close_path(); ctx.set_source_rgba(*hexc('#22223b')); ctx.fill()
    circle(ctx, hx, hy, 48 * s, hexc(PINK)); circle(ctx, hx + 14 * s, hy - 10 * s, 13 * s, (1, 1, 1, 1)); circle(ctx, hx + 17 * s, hy - 10 * s, 6 * s, hexc('#22223b'))

def flamingo_front(ctx, x, y, s):
    ctx.save(); ctx.rectangle(x - 260 * s, y - 2 * s, 520 * s, 120 * s); ctx.clip()
    e4.ell(ctx, x, y, 210 * s, 70 * s, hexc(PINK)); ctx.restore()
    ctx.set_line_width(8 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(1, 1, 1, 0.55)
    ctx.arc(x, y - 14 * s, 190 * s, math.radians(60), math.radians(110)); ctx.stroke()
    ctx.set_line_width(6); ctx.set_source_rgba(1, 1, 1, 0.6)
    for sg in (-1, 1): ctx.move_to(x + sg * 150 * s, y + 66 * s); ctx.curve_to(x + sg * 200 * s, y + 80 * s, x + sg * 250 * s, y + 60 * s, x + sg * 290 * s, y + 72 * s); ctx.stroke()

def drink(ctx, x, y):
    ctx.move_to(x - 30, y - 70); ctx.line_to(x + 30, y - 70); ctx.line_to(x + 20, y); ctx.line_to(x - 20, y); ctx.close_path(); ctx.set_source_rgba(*hexc('#ff8c42', 0.95)); ctx.fill()
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc(RED)); ctx.move_to(x + 6, y - 60); ctx.line_to(x + 26, y - 118); ctx.stroke()
    ctx.arc(x - 16, y - 100, 34, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd60a')); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#5c4033')); ctx.move_to(x - 16, y - 100); ctx.line_to(x - 12, y - 62); ctx.stroke()

def wren_afloat(ctx, x, t, s=0.78):
    yf = 1330 + 7 * math.sin(t * 3)
    flamingo_back(ctx, x, yf, 1.0)
    hand = (195, -300)
    ctx.save(); ctx.rectangle(0, 0, W, yf + 4); ctx.clip()
    wren(ctx, x - 10, yf + 200 * s, s, t, "point", expr="happy", hand=hand); ctx.restore()
    drink(ctx, x - 10 + hand[0] * s + 4, yf + 200 * s + hand[1] * s - 14)
    flamingo_front(ctx, x, yf, 1.0)
    return yf

# ------------------------------------------------------------ scenes
T0 = [0.45 + i * 0.36 for i in range(6)]            # towel landing times in s0
def s0(ctx, t, d):
    drops = [ease(clamp01((t - (T0[i] - 0.22)) / 0.22)) for i in range(6)]
    pool_bg(ctx, t, 'dawn', 6, drops)
    for i in range(6):
        if 0 < t - T0[i] < 0.25: burst(ctx, BEDS[i], BED_Y - 60, 1 - (t - T0[i]) / 0.25, 70)
    landed = sum(1 for x in T0 if t >= x)
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy", hand=(150, -330)); teacup(ctx, WX + 150 * 1.1 + 6, GY - 330 * 1.1)
    run = ramp(t, 0.0, 0.9); lx = lerp(1010, LX, run)
    kid(ctx, lx, GY, 0.95, t * (2.5 if run < 1 else 1), "smile" if landed < 3 else "flat", (-10, -190))
    towel_roll(ctx, lx - 10 * 0.95, GY - 190 * 0.95 - 30)
    bubble_ml(ctx, 800, 1150, ["It's SIX A.M.!"], 46, ramp(t, 2.6, 2.8), (LX, GY - 395))
    header(ctx, ease(t / 0.2 + 1), "HOTEL POOL. 6 AM.", "Leo wants a sunbed.", "Every one has a towel.", -0.3, t, main_size=56)
    meter(ctx, "FREE SUNBEDS", "%d" % (6 - landed)); wm(ctx)

def s1(ctx, t, d):
    pool_bg(ctx, t, 'predawn', 6, None, props=True)
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy", hand=(150, -330)); teacup(ctx, WX + 150 * 1.1 + 6, GY - 330 * 1.1)
    run = ramp(t, 0.1, 0.9); lx = lerp(1250, LX, run)
    ringing = t < 2.0
    kid(ctx, lx, GY, 0.95, t * (2.5 if run < 1 else 1), "flat", (-10, -200))
    alarm(ctx, lx - 10 * 0.95, GY - 200 * 0.95 - 46, t, ringing)
    bubble_ml(ctx, 790, 1130, ["Who gets up", "before FIVE?!"], 42, ramp(t, 1.1, 1.3) * (1 - ramp(t, 2.7, 2.85)), (LX, GY - 395))
    bubble_ml(ctx, 800, 1110, ["Towels are", "early risers, dear."], 42, ramp(t, 2.95, 3.15), (WX + 125, GY - 600))
    header(ctx, ease(t / 0.2), "DAY TWO. 5 AM.", "Leo gets up earlier.", "So did the towels.", 1.0, t, main_size=56)
    meter(ctx, "LEO'S ALARM", "5:00 AM"); wm(ctx)

def s2(ctx, t, d):
    pool_bg(ctx, t, 'night', 6, None, props=True)
    wet = ramp(t, 2.3, 2.7)
    cx = lerp(1420, 760, ramp(t, 1.7, 2.4)); storm_cloud(ctx, cx, 690)
    rain(ctx, t, wet)
    up = ramp(t, 2.5, 2.9)
    hand = (lerp(150, 130, up), lerp(-330, -430, up))
    hx, hy = WX + hand[0] * 1.1, GY + hand[1] * 1.1
    if up > 0: umbrella(ctx, hx, hy, up)
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy", hand=hand)
    if up <= 0: teacup(ctx, hx + 6, hy)
    run = ramp(t, 0.0, 0.55); lx = lerp(1250, 850, run)
    win = 0.6 < t < 2.3
    kid(ctx, lx, GY - 10, 0.95, t * (2.5 if run < 1 else 1), "smug" if win else ("smile" if t < 0.6 else "flat"), (0, -430) if win else (0, -150))
    claimed = ramp(t, 0.5, 0.7)
    sunbed(ctx, 850, GY + 40, 2.1, RED, claimed)
    if 0.7 < t < 1.0: burst(ctx, 850, GY - 80, 1 - (t - 0.7) / 0.3, 150)
    if wet > 0.5:
        for k in range(3):
            ph = (t * 1.6 + k / 3) % 1; circle(ctx, lx - 50 + k * 50, GY - 250 + 60 * ph, 9, hexc('#8fd3ff', 1 - ph))
    if 2.2 < t < 2.4: ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(1, 1, 1, 0.55 * (1 - (t - 2.2) / 0.2)); ctx.fill()
    bubble_ml(ctx, 850, 1090, ["MINE.", "All day."], 46, ramp(t, 0.9, 1.1) * (1 - ramp(t, 2.2, 2.35)), (850, GY - 480))
    bubble_ml(ctx, 840, 1130, ["Forecast said", "rain, dear."], 42, ramp(t, 3.1, 3.3), (WX + 125, GY - 600))
    header(ctx, ease(t / 0.2), "DAY THREE. 4 AM.", "Leo finally gets one.", "Then the weather arrives.", 1.9, t, main_size=56)
    meter(ctx, "LEO'S SUNBEDS", "1" if t > 0.6 else "0"); wm(ctx)

def s3(ctx, t, d):
    pool_bg(ctx, t, 'day', 6, None, props=True)
    fx = lerp(-320, 310, ramp(t, 0.1, 1.5)) + 25 * ramp(t, 1.5, 4.0)
    yf = wren_afloat(ctx, fx, t)
    if 0.2 < t < 1.5:
        for k in range(4): circle(ctx, fx - 260 - k * 34, yf + 40 - 30 * abs(math.sin(t * 9 + k)), 12 - 2 * k, (1, 1, 1, 0.8))
    kid(ctx, LX, GY, 0.95, t, "flat", (0, -150))
    e4.ell(ctx, LX, GY + 6, 120, 20, hexc('#8fd3ff', 0.55))
    for k in range(2):
        ph = (t * 1.3 + k / 2) % 1; circle(ctx, LX - 46 + k * 92, GY - 230 + 70 * ph, 8, hexc('#8fd3ff', 1 - ph))
    bubble_ml(ctx, 860, 1200, ["Where did you", "GET that?"], 42, ramp(t, 1.3, 1.5) * (1 - ramp(t, 2.6, 2.75)), (LX, GY - 395))
    bubble_ml(ctx, fx + 30, 868, ["Gift shop.", "Opens at nine."], 44, ramp(t, 2.85, 3.05), (fx - 10, yf - 392))
    header(ctx, ease(t / 0.2), "WREN'S FIX", "No sunbed. A flamingo.", "“Nobody reserves the pool.”", 1.2, t, main_size=56)
    meter(ctx, "WREN'S ALARM", "9:30 AM"); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 470, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    flamingo_back(ctx, 820, 1600 + 5 * math.sin(t * 3), 0.6); flamingo_front(ctx, 820, 1600 + 5 * math.sin(t * 3), 0.6)
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “Nobody reserves the pool.”", 205 - (1 - a) * 20, 50, hexc('#22223b', a), maxw=1040)
    ctext(ctx, "Leo: “I got up at 4 AM.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Tag the sunbed-towel person you know", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 1.3), (s0, 3.3), (s1, 0.6), (s1, 2.0), (s1, 3.9), (s2, 0.4), (s2, 1.5), (s2, 2.5), (s2, 3.9), (s3, 0.8), (s3, 2.1), (s3, 3.6), (s4, 2.6)]
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

"""ep28 - Seaside taverna: Leo orders with a translate app. 'Surprise Legs' arrives: an octopus that waves at him. Wren just points at the next table's plate. Served in seconds. The octopus keeps Leo's phone."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep28"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; BLUE = '#1d5fa8'; SEA = '#2a8fc9'; PURP = '#9b5de5'; PURP_D = '#6a3fb0'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1600                         # characters' ground line (kept above the @wrentrips watermark)
FLOOR = 1300

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

def ftext(ctx, s, x, y, size, col, maxw, bold=True, center=False):
    mv.font(ctx, size, bold); e = ctx.text_extents(s)
    while e.x_advance > maxw and size > 12:
        size -= 1; mv.font(ctx, size, bold); e = ctx.text_extents(s)
    ctx.move_to(x - (e.x_advance / 2 if center else 0), y); ctx.set_source_rgba(*col); ctx.show_text(s)

# ------------------------------------------------------------ background: whitewashed seaside taverna terrace
def house(ctx, x, y, w, h, dome=False, door=True):
    rrect(ctx, x, y, w, h, 8); ctx.set_source_rgba(*hexc('#fbfbf7')); ctx.fill()
    ctx.rectangle(x + w - 10, y + 6, 10, h - 6); ctx.set_source_rgba(*hexc('#e3e6ea')); ctx.fill()
    if dome:
        ctx.arc(x + w / 2, y + 4, w * 0.36, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc(BLUE)); ctx.fill()
        ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#fbfbf7')); ctx.move_to(x + w / 2, y + 4 - w * 0.36); ctx.line_to(x + w / 2, y + 4 - w * 0.36 - 26); ctx.stroke()
        ctx.move_to(x + w / 2 - 9, y + 4 - w * 0.36 - 16); ctx.line_to(x + w / 2 + 9, y + 4 - w * 0.36 - 16); ctx.stroke()
    if door:
        rrect(ctx, x + w * 0.38, y + h - h * 0.45, w * 0.24, h * 0.45, 6); ctx.set_source_rgba(*hexc(BLUE)); ctx.fill()
    rrect(ctx, x + w * 0.12, y + h * 0.18, w * 0.16, w * 0.16, 3); ctx.set_source_rgba(*hexc('#2f7fc1')); ctx.fill()

def terrace(ctx, t, lights=True):
    g = cairo.LinearGradient(0, 0, 0, 900); g.add_color_stop_rgb(0, *hexc('#5ab8f0')[:3]); g.add_color_stop_rgb(1, *hexc('#cdeeff')[:3])
    ctx.rectangle(0, 0, W, 900); ctx.set_source(g); ctx.fill()
    circle(ctx, 880, 700, 60, hexc('#fff3b0'))
    ctx.rectangle(0, 880, W, 140); ctx.set_source_rgba(*hexc(SEA)); ctx.fill()                       # sea
    ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.5)
    for k in range(7):
        x = (k * 170 + t * 30) % (W + 100) - 50; y = 910 + (k % 3) * 34
        ctx.move_to(x, y); ctx.curve_to(x + 15, y - 8, x + 30, y - 8, x + 45, y); ctx.stroke()
    # boat
    bx = 160 + 6 * math.sin(t * 1.2)
    ctx.move_to(bx - 50, 930); ctx.line_to(bx + 50, 930); ctx.line_to(bx + 34, 952); ctx.line_to(bx - 34, 952); ctx.close_path(); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    ctx.move_to(bx, 928); ctx.line_to(bx, 870); ctx.line_to(bx + 36, 922); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    # village on the hill (left and right)
    ctx.move_to(0, 1040); ctx.curve_to(150, 930, 330, 960, 420, 1040); ctx.close_path(); ctx.set_source_rgba(*hexc('#d9c6a5')); ctx.fill()
    house(ctx, 20, 930, 120, 110, dome=True, door=False); house(ctx, 150, 960, 110, 90, door=False); house(ctx, 270, 990, 100, 60, door=False)
    ctx.move_to(W, 1040); ctx.curve_to(W - 150, 940, W - 320, 970, W - 400, 1040); ctx.close_path(); ctx.set_source_rgba(*hexc('#d9c6a5')); ctx.fill()
    house(ctx, W - 140, 940, 120, 100, door=False); house(ctx, W - 260, 975, 110, 70, dome=True, door=False)
    # terrace wall + bougainvillea
    ctx.rectangle(0, 1030, W, FLOOR - 1030); ctx.set_source_rgba(*hexc('#fbfbf7')); ctx.fill()
    ctx.rectangle(0, 1030, W, 16); ctx.set_source_rgba(*hexc('#e3e6ea')); ctx.fill()
    rnd = random.Random(28)
    for k in range(26):
        x = rnd.uniform(-20, 300) if k < 13 else rnd.uniform(W - 300, W + 20); y = rnd.uniform(990, 1110)
        circle(ctx, x, y, rnd.uniform(16, 30), hexc(rnd.choice(['#e0218a', '#f15bb5', '#c9184a'])))
    for k in range(8):
        x = rnd.uniform(0, 280) if k < 4 else rnd.uniform(W - 280, W); circle(ctx, x, rnd.uniform(1000, 1100), 12, hexc('#3a8f5c'))
    # string lights
    if lights:
        ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#4a4a4a')); ctx.move_to(-10, 640); ctx.curve_to(300, 760, 780, 760, W + 10, 640); ctx.stroke()
        for k in range(11):
            u = k / 10; x = (1 - u) ** 3 * -10 + 3 * (1 - u) ** 2 * u * 300 + 3 * (1 - u) * u * u * 780 + u ** 3 * (W + 10)
            y = (1 - u) ** 3 * 640 + 3 * (1 - u) ** 2 * u * 760 + 3 * (1 - u) * u * u * 760 + u ** 3 * 640
            tw = 0.75 + 0.25 * math.sin(t * 4 + k)
            circle(ctx, x, y + 14, 11, (1, 0.85, 0.4, tw))
    # terracotta floor
    ctx.rectangle(0, FLOOR, W, H - FLOOR); ctx.set_source_rgba(*hexc('#d98b5f')); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#c27449'))
    for r in range(9):
        y = FLOOR + r * 80; ctx.move_to(0, y); ctx.line_to(W, y); ctx.stroke()
        for k in range(9):
            x = k * 130 + (r % 2) * 65; ctx.move_to(x, y); ctx.line_to(x, y + 80); ctx.stroke()

def table(ctx, cx, top, w=360, legs=300):
    for dx in (-w / 2 + 40, w / 2 - 40): rrect(ctx, cx + dx - 12, top, 24, legs, 6); ctx.set_source_rgba(*hexc('#6b4423')); ctx.fill()
    rrect(ctx, cx - w / 2, top - 14, w, 28, 10); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.rectangle(cx - w / 2, top, w, 90); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()                  # checked cloth
    sq = w / 12
    for i in range(12):
        for j in range(3):
            if (i + j) % 2 == 0: ctx.rectangle(cx - w / 2 + i * sq, top + j * 30, sq, 30); ctx.set_source_rgba(*hexc('#3d7dd8')); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 1)
    for i in range(12):
        x = cx - w / 2 + i * sq; ctx.arc(x + sq / 2, top + 90, sq / 2, 0, math.pi); ctx.set_source_rgba(*hexc('#3d7dd8' if i % 2 else '#ffffff')); ctx.fill()

def plate(ctx, x, y, s=1.0):
    e4.ell(ctx, x, y, 110 * s, 24 * s, (1, 1, 1, 1)); e4.ell(ctx, x, y - 2, 80 * s, 15 * s, hexc('#e8edf2'))

def pie_plate(ctx, x, y, s=1.0):                                                # golden pie + salad
    plate(ctx, x, y, s)
    ctx.move_to(x - 70 * s, y - 6 * s); ctx.line_to(x + 10 * s, y - 6 * s); ctx.line_to(x - 20 * s, y - 56 * s); ctx.close_path(); ctx.set_source_rgba(*hexc('#e9a83a')); ctx.fill()
    ctx.set_line_width(3 * s); ctx.set_source_rgba(*hexc('#c27c1e')); ctx.move_to(x - 56 * s, y - 16 * s); ctx.line_to(x - 4 * s, y - 16 * s); ctx.stroke()
    for k, c in enumerate(('#e63946', '#7ac143', '#ffffff', '#7ac143', '#e63946')):
        circle(ctx, x + (24 + k * 12) * s, y - (14 + 10 * (k % 2)) * s, 11 * s, hexc(c))
    circle(ctx, x + 44 * s, y - 34 * s, 8 * s, hexc('#2b2d42'))

def steam(ctx, x, y, t):
    for k in range(3):
        ph = (t * 0.8 + k / 3) % 1; circle(ctx, x - 25 + k * 25 + 6 * math.sin(t * 3 + k), y - ph * 80, 9 + 7 * ph, (1, 1, 1, 0.55 * (1 - ph)))

def menu_card(ctx, x, y, ang=0.0, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    rrect(ctx, -60, -80, 120, 160, 8); ctx.set_source_rgba(*hexc('#fdf6e3')); ctx.fill()
    ctx.set_line_width(3); ctx.set_source_rgba(*hexc(BLUE)); rrect(ctx, -52, -72, 104, 144, 6); ctx.stroke()
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#5a5a6e'))
    for k in range(6):
        yy = -48 + k * 22; ctx.move_to(-38, yy)
        for j in range(5): ctx.curve_to(-38 + j * 15 + 4, yy - 6, -38 + j * 15 + 10, yy + 6, -38 + (j + 1) * 15, yy)
        ctx.stroke()
    ctx.restore()

def phone(ctx, x, y, ang=0.0, s=1.0, screen='#bde0fe'):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    rrect(ctx, -26, -46, 52, 92, 10); ctx.set_source_rgba(*hexc('#1a1c2e')); ctx.fill()
    rrect(ctx, -20, -38, 40, 70, 6); ctx.set_source_rgba(*hexc(screen)); ctx.fill()
    ctx.restore()

# ------------------------------------------------------------ the octopus ("Surprise Legs")
def octopus(ctx, x, y, s, t, wave=1.0, holds_phone=False, expr="happy"):
    """Body centre (x, y). Tentacles drape over the plate and wave."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(8):
        side = -1 if k < 4 else 1; j = k % 4
        base_x = side * (20 + j * 16); ang0 = side * (0.4 + j * 0.35)
        wav = math.sin(t * 4 + k * 0.9) * 0.35 * wave
        L = 140 - j * 8
        if k == 7 and holds_phone:                      # this one is busy scrolling
            pts = [(base_x, 40), (base_x + 60, 10), (base_x + 110, -60 + 6 * math.sin(t * 6))]
        elif k == 6 and wave > 0.5:                     # this one waves hello
            pts = [(base_x, 40), (base_x + 50, -30), (base_x + 70 + 30 * math.sin(t * 7), -120)]
        else:
            pts = [(base_x, 40), (base_x + side * L * 0.5 * math.cos(ang0 * 0.6), 70 + L * 0.15 + 20 * wav), (base_x + side * L * math.cos(ang0 * 0.4) + 30 * wav * side, 70 + 30 * math.sin(t * 3 + k) * wave)]
        ctx.set_line_width(30); ctx.set_source_rgba(*hexc(PURP_D))
        ctx.move_to(*pts[0]); ctx.curve_to(pts[1][0], pts[1][1], pts[1][0], pts[1][1], pts[2][0], pts[2][1]); ctx.stroke()
        ctx.set_line_width(24); ctx.set_source_rgba(*hexc(PURP))
        ctx.move_to(*pts[0]); ctx.curve_to(pts[1][0], pts[1][1], pts[1][0], pts[1][1], pts[2][0], pts[2][1]); ctx.stroke()
        circle(ctx, pts[2][0], pts[2][1], 13, hexc(PURP))
        if k == 7 and holds_phone: phone(ctx, pts[2][0] + 10, pts[2][1] - 20, 0.25 + 0.05 * math.sin(t * 3), 0.9, '#ffb3b8')
    # head
    ctx.save(); ctx.scale(1, 1.15); circle(ctx, 0, -20, 78, hexc(PURP)); ctx.restore()
    for dx, dy, r in ((-30, -70, 10), (20, -86, 7), (40, -40, 9)): circle(ctx, dx, dy, r, hexc('#c39bff'))
    for ex in (-26, 26):
        circle(ctx, ex, 0, 19, (1, 1, 1, 1))
        circle(ctx, ex + (4 if not holds_phone else 8), 2 + (6 if holds_phone else 0), 8, hexc('#1b1b2f'))
    circle(ctx, -46, 26, 10, hexc('#f28b82', 0.6)); circle(ctx, 46, 26, 10, hexc('#f28b82', 0.6))
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#3b1f6b'))
    ctx.arc(0, 26, 16, math.radians(20), math.radians(160)); ctx.stroke()
    ctx.restore()

def cloche(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.arc(0, 0, 120, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc('#dfe5ea')); ctx.fill()
    ctx.arc(-30, -40, 60, math.pi * 1.1, math.pi * 1.5); ctx.set_line_width(10); ctx.set_source_rgba(1, 1, 1, 0.8); ctx.stroke()
    circle(ctx, 0, -124, 16, hexc('#b8c0c8')); e4.ell(ctx, 0, 0, 130, 12, hexc('#b8c0c8'))
    ctx.restore()

def waiter(ctx, x, gy, t, walk=True):
    b = 4 * math.sin(t * 6) if walk else 0
    for dx in (-26, 26): rrect(ctx, x + dx - 18, gy - 260, 36, 250, 14); ctx.set_source_rgba(*hexc('#22223b')); ctx.fill()
    for dx in (-30, 30): e4.ell(ctx, x + dx, gy - 6, 36, 16, hexc('#111111'))
    rrect(ctx, x - 78, gy - 520 + b, 156, 290, 40); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()               # white shirt
    rrect(ctx, x - 66, gy - 400 + b, 132, 190, 20); ctx.set_source_rgba(*hexc(BLUE)); ctx.fill()             # apron
    circle(ctx, x, gy - 600 + b, 76, hexc('#d9a074'))
    ctx.arc(x, gy - 618 + b, 78, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc('#3b2a20')); ctx.fill()
    ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#3b2a20'))      # moustache
    ctx.move_to(x - 30, gy - 572 + b); ctx.curve_to(x - 10, gy - 586 + b, x + 10, gy - 586 + b, x + 30, gy - 572 + b); ctx.stroke()
    for dx in (-26, 26): circle(ctx, x + dx, gy - 606 + b, 8, hexc('#22223b'))
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#22223b')); ctx.arc(x, gy - 562 + b, 18, 0.3, math.pi - 0.3); ctx.stroke()

def thumbs(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -30, -10, 60, 56, 14); ctx.set_source_rgba(*hexc('#d9a074')); ctx.fill()
    rrect(ctx, -14, -60, 26, 60, 12); ctx.fill()
    ctx.restore()

def app_inset(ctx, a, n_show, t, hi=-1):
    """Leo's translate app on the menu: literal translations."""
    if a <= 0: return
    x, y, w, h = 380, 640, 400, 600
    ctx.save(); ctx.translate(0, (1 - a) * 40)
    rrect(ctx, x, y, w, h, 46); ctx.set_source_rgba(*hexc('#1b1b2f', a)); ctx.fill()
    rrect(ctx, x + 16, y + 56, w - 32, h - 96, 18); ctx.set_source_rgba(*hexc('#f8f9fa', a)); ctx.fill()
    mv.font(ctx, 24); ctx.move_to(x + 36, y + 40); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text("Translate")
    circle(ctx, x + w - 46, y + 32, 10, hexc('#ff595e', a * (0.5 + 0.5 * math.sin(t * 8))))
    items = [("Angry Bread", "$4"), ("Sad Little Fish", "$11"), ("Grandmother's Feet", "$9"),
             ("Cheese That Shouts", "$7"), ("Surprise Legs", "$16"), ("Soup of Regret", "$6")]
    for k, (name, price) in enumerate(items):
        if k >= n_show: continue
        yy = y + 112 + k * 80
        if k == hi:
            rrect(ctx, x + 26, yy - 40, w - 52, 62, 14); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.fill()
        ftext(ctx, name, x + 40, yy, 28, hexc("#22223b", a), 240)
        ftext(ctx, price, x + w - 44 - 50, yy, 28, hexc(RED, a), 50)
    ctx.restore()

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    terrace(ctx, t)
    table(ctx, 540, 1330, 360, 270)
    menu_card(ctx, 470, 1270, -0.2, 0.8)
    wren(ctx, 250, GY, 1.05, t, "point", expr="happy", hand=(150, -320))
    menu_card(ctx, 250 + 150 * 1.05 + 10, GY - 320 * 1.05 - 40, 0.15, 1.0)
    kid(ctx, 840, GY, 0.95, t, "smug", (-60, -250))
    phone(ctx, 840 - 60 * 0.95, GY - 250 * 0.95 - 34, -0.1, 1.0, '#bde0fe')
    if int(t * 3) % 2 == 0: circle(ctx, 840 - 60 * 0.95, GY - 250 * 0.95 - 40, 30, (1, 1, 1, 0.35))
    bubble_ml(ctx, 760, 820, ["Relax, Grandma.", "The app's got this."], 40, ramp(t, 1.4, 1.6), (830, GY - 390))
    header(ctx, ease(t / 0.2 + 1), "ORDERING ABROAD", "Leo has a translate app.", "What could go wrong?", -0.3, t, main_size=56)
    meter(ctx, "LEO'S CONFIDENCE", "100%"); wm(ctx)

def s1(ctx, t, d):
    terrace(ctx, t)
    table(ctx, 540, 1330, 360, 270)
    wren(ctx, 220, GY, 1.05, t, "point", expr="happy" if t < 1.8 else "shock", hand=(150, -320))
    menu_card(ctx, 220 + 150 * 1.05 + 10, GY - 320 * 1.05 - 40, 0.15, 1.0)
    kid(ctx, 870, GY, 0.95, t, "smile" if t < 1.6 else "flat", (-60, -250))
    phone(ctx, 870 - 60 * 0.95, GY - 250 * 0.95 - 34, -0.1, 1.0)
    n = int(clamp01((t - 0.3) / 1.4) * 6.99)
    app_inset(ctx, ramp(t, 0.1, 0.4) * (1 - ramp(t, 2.9, 3.1)), n, t, hi=4 if t > 2.0 else -1)
    if 2.0 < t < 2.3: burst(ctx, 580, 1032, 1 - (t - 2.0) / 0.3, 60)
    bubble_ml(ctx, 760, 820, ["One Surprise Legs,", "please!"], 40, ramp(t, 3.1, 3.3), (860, GY - 390))
    header(ctx, ease(t / 0.2), "THE APP TRANSLATES", "Every dish. Literally.", "Leo picks one anyway.", 1.6, t, main_size=56)
    meter(ctx, "LEO'S CONFIDENCE", "%d%%" % int(100 - 55 * ramp(t, 0.4, 2.0))); wm(ctx)

def s2(ctx, t, d):
    terrace(ctx, t)
    # waiter walks in and sets the dish down
    wx = lerp(1250, 990, ramp(t, 0.0, 0.7))
    waiter(ctx, wx, GY, t, walk=t < 0.7)
    table(ctx, 500, 1330, 380, 270)
    kid(ctx, 790, GY, 0.95, t, "smile" if t < 1.5 else ("flat" if t < 2.6 else "shock"), (0, -160) if t < 1.5 else (-10, -260))
    wren(ctx, 200, GY, 1.05, t, "point", expr="happy" if t < 1.5 else "shock", hand=(140, -300))
    plate(ctx, 500, 1310, 1.4)
    lift = ramp(t, 1.2, 1.6)
    if lift > 0.05:
        octopus(ctx, 500, 1190, 0.85, t, wave=ramp(t, 1.6, 2.2))
    if lift < 1.0:
        cloche(ctx, 500, 1306 - 380 * lift, 1.05)
    if 1.5 < t < 1.9: burst(ctx, 500, 1180, 1 - (t - 1.5) / 0.4, 200)
    bubble_ml(ctx, 790, 800, ["It's waving", "at me."], 44, ramp(t, 2.4, 2.6), (790, GY - 390))
    header(ctx, ease(t / 0.2), "THE ORDER ARRIVES", "“Surprise Legs.”", "Eight of them.", 1.7, t, main_size=56)
    meter(ctx, "LEGS ON THE PLATE", "%d" % int(8 * ramp(t, 1.5, 2.2))); wm(ctx)

def s3(ctx, t, d):
    terrace(ctx, t)
    # neighbouring table on the right with a lovely golden pie
    table(ctx, 930, 1360, 260, 240)
    pie_plate(ctx, 930, 1340, 0.95); steam(ctx, 920, 1270, t)
    if 0.5 < t < 1.6:
        a = ramp(t, 0.5, 0.7) * (1 - ramp(t, 1.4, 1.6))
        ctx.set_line_width(8); ctx.set_source_rgba(*hexc('#ffd166', a))
        for k in range(6):
            ang = -math.pi / 2 + (k - 2.5) * 0.4; ctx.move_to(930 + math.cos(ang) * 120, 1260 + math.sin(ang) * 120); ctx.line_to(930 + math.cos(ang) * 170, 1260 + math.sin(ang) * 170); ctx.stroke()
    table(ctx, 470, 1330, 380, 270)
    # the octopus has moved in and taken the phone
    plate(ctx, 410, 1310, 1.1); octopus(ctx, 400, 1200, 0.7, t, wave=0.3, holds_phone=True)
    pop = ramp(t, 1.9, 2.3)
    if pop > 0:
        pie_plate(ctx, 590, 1316, 0.9 * pop)
        if t < 2.5: burst(ctx, 590, 1270, 1 - (t - 1.9) / 0.6, 140)
    wren(ctx, 190, GY, 1.05, t, "point", expr="happy", hand=(190, -380) if t < 1.8 else (140, -260))
    kid(ctx, 700, GY, 0.9, t, "flat", (0, -160))
    bubble_ml(ctx, 360, 760, ["Two of those,", "please."], 44, ramp(t, 0.5, 0.7) * (1 - ramp(t, 2.3, 2.45)), (230, GY - 680))
    bubble_ml(ctx, 760, 800, ["It took my", "phone, Grandma."], 40, ramp(t, 2.5, 2.7), (700, GY - 380))
    header(ctx, ease(t / 0.2), "WREN'S METHOD", "Point at the next table.", "Served in 4 seconds.", 1.2, t, main_size=56)
    meter(ctx, "TIME TO ORDER", "%.1f sec" % (4.0 * ramp(t, 0.4, 1.9))); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 420, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    plate(ctx, 820, 1520, 1.1); octopus(ctx, 820, 1400, 0.8, t, wave=1.0, holds_phone=True)
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “Pointing works in every language.”", 205 - (1 - a) * 20, 44, hexc('#22223b', a), maxw=1000)
    ctext(ctx, "Leo: “The octopus kept my phone.”", 290, 44, hexc(RED, ease((t - 0.5) / 0.3)), maxw=1000)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Team app or team pointing? Comment below!", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 2.5), (s1, 1.0), (s1, 2.4), (s1, 3.8), (s2, 0.5), (s2, 1.4), (s2, 2.0), (s2, 3.6), (s3, 1.0), (s3, 2.2), (s3, 3.6), (s4, 0.2), (s4, 2.6)]
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

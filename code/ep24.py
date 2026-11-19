"""ep24 - Airport security: Wren packed 2 litres of soup. Limit is 100 ml. She decants it into 20 tiny bottles, then feeds the queue."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep24"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; NAVY = '#1d3557'; SOUP = '#f3722c'; SOUP_D = '#d35400'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1700
WX, LX = 420, 1000
HAND = (180, -320)
HX, HY = WX + HAND[0] * 1.1, GY + HAND[1] * 1.1          # Wren's hand on screen
TABLE_Y = 1390

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

def ftext(ctx, s, cx, y, size, col, maxw):
    mv.font(ctx, size); e = ctx.text_extents(s)
    while e.x_advance > maxw and size > 12:
        size -= 1; mv.font(ctx, size); e = ctx.text_extents(s)
    ctx.move_to(cx - e.x_advance / 2, y); ctx.set_source_rgba(*col); ctx.show_text(s)

def heart(ctx, x, y, s, a):
    if a <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(0, 12); ctx.curve_to(-30, -8, -16, -34, 0, -16); ctx.curve_to(16, -34, 30, -8, 0, 12); ctx.close_path()
    ctx.set_source_rgba(*hexc(RED, a)); ctx.fill(); ctx.restore()

# ------------------------------------------------------------ props
def jar(ctx, x, base, s=1.0, level=1.0, label=True):
    """Big glass soup jar standing on y=base."""
    ctx.save(); ctx.translate(x, base); ctx.scale(s, s)
    rrect(ctx, -62, -170, 124, 170, 26); ctx.set_source_rgba(*hexc('#dff3ff', 0.75)); ctx.fill()
    if level > 0.01:
        h = 150 * level
        ctx.save(); rrect(ctx, -56, -164, 112, 158, 22); ctx.clip()
        ctx.rectangle(-60, -6 - h, 120, h); ctx.set_source_rgba(*hexc(SOUP)); ctx.fill()
        for (dx, dy) in ((-24, 30), (14, 60), (-6, 100), (28, 120)):
            if -6 - h < -dy: circle(ctx, dx, -dy, 7, hexc('#90be6d'))
        ctx.restore()
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#8ecae6')); rrect(ctx, -62, -170, 124, 170, 26); ctx.stroke()
    rrect(ctx, -54, -196, 108, 32, 8); ctx.set_source_rgba(*hexc(RED)); ctx.fill()                  # lid
    for k in range(5): circle(ctx, -40 + k * 20, -180, 4, (1, 1, 1, 0.9))                          # gingham dots
    if label:
        rrect(ctx, -42, -112, 84, 46, 8); ctx.set_source_rgba(1, 1, 1, 0.95); ctx.fill()
        ftext(ctx, "2 L", 0, -78, 30, hexc('#22223b'), 76)
    ctx.restore()

def bottle(ctx, x, base, s=1.0, fill=1.0, a=1.0):
    """Tiny 100 ml travel bottle."""
    if a <= 0 or s <= 0: return
    ctx.save(); ctx.translate(x, base); ctx.scale(s, s)
    rrect(ctx, -14, -50, 28, 50, 8); ctx.set_source_rgba(*hexc('#ffffff', 0.85 * a)); ctx.fill()
    if fill > 0:
        ctx.save(); rrect(ctx, -12, -48, 24, 46, 7); ctx.clip()
        ctx.rectangle(-14, -2 - 44 * fill, 28, 44 * fill); ctx.set_source_rgba(*hexc(SOUP, a)); ctx.fill(); ctx.restore()
    ctx.set_line_width(2.5); ctx.set_source_rgba(*hexc('#8d99ae', a)); rrect(ctx, -14, -50, 28, 50, 8); ctx.stroke()
    rrect(ctx, -8, -64, 16, 16, 4); ctx.set_source_rgba(*hexc('#3a86ff', a)); ctx.fill()
    ctx.restore()

def flower_bag(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_line_width(10); ctx.set_source_rgba(*hexc('#6d2e46')); ctx.arc(0, -96, 46, math.pi, 0); ctx.stroke()
    rrect(ctx, -90, -100, 180, 100, 24); ctx.set_source_rgba(*hexc('#c9184a')); ctx.fill()
    random.seed(5)
    for _ in range(9):
        fx, fy = random.uniform(-70, 70), random.uniform(-84, -16)
        for k in range(5):
            a = k * 2 * math.pi / 5; circle(ctx, fx + 7 * math.cos(a), fy + 7 * math.sin(a), 5, hexc('#ffccd5'))
        circle(ctx, fx, fy, 4, hexc('#ffd166'))
    ctx.restore()

def tray(ctx, x, y):
    ctx.move_to(x - 120, y - 40); ctx.line_to(x + 120, y - 40); ctx.line_to(x + 106, y); ctx.line_to(x - 106, y); ctx.close_path()
    ctx.set_source_rgba(*hexc('#6c757d')); ctx.fill()

def person(ctx, x, gy, s, t, shirt, skin, hair, hand=None, officer=False, sip=0.0, smile=True):
    """Generic adult (traveller or security officer). hand = absolute (x, y) for the right hand."""
    ctx.save(); ctx.translate(x, gy); ctx.scale(s, s)
    b = 3 * math.sin(t * 5 + x)
    for dx in (-26, 26): rrect(ctx, dx - 18, -250, 36, 240, 14); ctx.set_source_rgba(*hexc('#2b2d42')); ctx.fill()
    for dx in (-30, 30): e4.ell(ctx, dx, -6, 36, 16, hexc('#111111'))
    rrect(ctx, -82, -520 + b, 164, 300, 44); ctx.set_source_rgba(*hexc(shirt)); ctx.fill()
    if officer:
        rrect(ctx, 26, -470 + b, 40, 30, 6); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()           # badge
        ctx.rectangle(-82, -330 + b, 164, 22); ctx.set_source_rgba(*hexc('#0b132b')); ctx.fill()         # belt
    circle(ctx, 0, -600 + b, 74, hexc(skin))
    for sg in (-1, 1): circle(ctx, sg * 72, -596 + b, 16, hexc(skin))
    if officer:
        ctx.arc(0, -630 + b, 76, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc(NAVY)); ctx.fill()
        rrect(ctx, -96, -640 + b, 192, 22, 10); ctx.set_source_rgba(*hexc('#0b132b')); ctx.fill()
        circle(ctx, 0, -680 + b, 12, hexc('#ffd166'))
    else:
        ctx.arc(0, -612 + b, 78, math.pi * 1.05, -0.05); ctx.close_path(); ctx.set_source_rgba(*hexc(hair)); ctx.fill()
    for dx in (-26, 26):
        if sip > 0.5:
            ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#1d1d2c')); ctx.arc(dx, -596 + b, 10, math.pi + 0.3, -0.3); ctx.stroke()
        else: circle(ctx, dx, -600 + b, 8, hexc('#1d1d2c'))
    circle(ctx, -44, -572 + b, 12, hexc('#f28b82', 0.5)); circle(ctx, 44, -572 + b, 12, hexc('#f28b82', 0.5))
    ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#1d1d2c'))
    if smile: ctx.arc(0, -578 + b, 22, 0.2, math.pi - 0.2); ctx.stroke()
    else: ctx.move_to(-18, -566 + b); ctx.line_to(18, -566 + b); ctx.stroke()
    ctx.restore()
    # right arm to hand (absolute coords)
    sx, sy = x + 70 * s * (-1), gy + (-470 + b) * s
    if hand is None: hand = (x - 120 * s, gy - 380 * s)
    ctx.set_line_width(36 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc(shirt))
    ctx.move_to(sx, sy); ctx.line_to(*hand); ctx.stroke(); circle(ctx, hand[0], hand[1], 20 * s, hexc(skin))

# ------------------------------------------------------------ background: airport security hall
def hall(ctx, t):
    mv.vgrad(ctx, '#e7eef8', '#d3dff0')
    # big window with runway + plane
    ctx.save(); rrect(ctx, 40, 620, 1000, 420, 18); ctx.clip()
    g = cairo.LinearGradient(0, 620, 0, 1040); g.add_color_stop_rgb(0, *hexc('#8ecae6')[:3]); g.add_color_stop_rgb(1, *hexc('#e0f4ff')[:3]); ctx.set_source(g); ctx.paint()
    for cx_, cy_ in ((200, 720), (720, 690)):
        for dx, r in ((-40, 34), (0, 46), (44, 32)): circle(ctx, cx_ + dx + (t * 8) % 60, cy_, r, (1, 1, 1, 0.85))
    ctx.rectangle(40, 960, 1000, 80); ctx.set_source_rgba(*hexc('#adb5bd')); ctx.fill()
    px = 300 + t * 30                                                     # parked plane
    rrect(ctx, px - 220, 890, 440, 70, 35); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.move_to(px + 140, 900); ctx.line_to(px + 210, 800); ctx.line_to(px + 240, 800); ctx.line_to(px + 220, 905); ctx.close_path(); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    for k in range(8): circle(ctx, px - 160 + k * 38, 918, 7, hexc('#5c677d'))
    ctx.restore()
    ctx.set_line_width(10); ctx.set_source_rgba(*hexc('#9aa5b1'))
    for x in (40, 373, 706, 1040): ctx.move_to(x, 620); ctx.line_to(x, 1040); ctx.stroke()
    ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(*hexc('#e7eef8', 0.25)); ctx.fill()
    # floor
    ctx.rectangle(0, 1420, W, H - 1420); ctx.set_source_rgba(*hexc('#eef1f4')); ctx.fill()
    for i in range(10):
        for j in range(5):
            if (i + j) % 2: ctx.rectangle(i * 120 - 20, 1420 + j * 110, 120, 110); ctx.set_source_rgba(*hexc('#dde3ea')); ctx.fill()
    # queue stanchions in the back
    ctx.set_line_width(8); ctx.set_source_rgba(*hexc('#8d99ae'))
    for x in (70, 250):
        ctx.move_to(x, 1440); ctx.line_to(x, 1300); ctx.stroke(); circle(ctx, x, 1296, 10, hexc('#8d99ae'))
    ctx.set_line_width(10); ctx.set_source_rgba(*hexc('#3a86ff', 0.8)); ctx.move_to(70, 1310); ctx.curve_to(130, 1340, 190, 1340, 250, 1310); ctx.stroke()

def xray(ctx, t, bag_x, alarm=False):
    # monitor on a pole
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#5c677d')); ctx.move_to(840, 930); ctx.line_to(840, 1110); ctx.stroke()
    rrect(ctx, 640, 640, 400, 290, 20); ctx.set_source_rgba(*hexc('#2b2d42')); ctx.fill()
    rrect(ctx, 656, 656, 368, 258, 10); ctx.set_source_rgba(*hexc('#0b2545')); ctx.fill()
    # x-ray image of the bag, revealed left to right as it passes
    rev = clamp01((bag_x - 700) / 220)
    ctx.save(); ctx.rectangle(656, 656, 368 * rev, 258); ctx.clip()
    rrect(ctx, 700, 720, 280, 150, 30); ctx.set_source_rgba(*hexc('#4cc9f0', 0.35)); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#4cc9f0', 0.9)); rrect(ctx, 700, 720, 280, 150, 30); ctx.stroke()
    ctx.set_line_width(5); ctx.move_to(730, 860); ctx.line_to(800, 760); ctx.stroke(); ctx.move_to(746, 860); ctx.line_to(816, 760); ctx.stroke()  # knitting needles
    on = alarm and int(t * 6) % 2 == 0
    col = hexc(RED if alarm else '#f8961e', 1.0 if on or not alarm else 0.7)
    rrect(ctx, 870, 740, 80, 112, 18); ctx.set_source_rgba(*col); ctx.fill()                       # the jar
    rrect(ctx, 864, 728, 92, 18, 6); ctx.fill()
    ctx.restore()
    if alarm:
        rrect(ctx, 676, 668, 210, 44, 10); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
        ftext(ctx, "LIQUID!", 781, 702, 30, (1, 1, 1, 1), 190)
    # machine body + tunnel
    rrect(ctx, 680, 1110, 330, 280, 30); ctx.set_source_rgba(*hexc('#adb5bd')); ctx.fill()
    rrect(ctx, 700, 1200, 290, 190, 16); ctx.set_source_rgba(*hexc('#343a40')); ctx.fill()
    rrect(ctx, 720, 1130, 120, 40, 10); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    ftext(ctx, "X-RAY", 780, 1162, 26, hexc('#22223b'), 110)
    lamp = alarm and int(t * 6) % 2 == 0
    circle(ctx, 960, 1150, 22, hexc(RED if lamp else '#6c757d'))
    # belt
    rrect(ctx, 560, 1390, 520, 30, 10); ctx.set_source_rgba(*hexc('#212529')); ctx.fill()
    ctx.rectangle(560, 1420, 520, 120); ctx.set_source_rgba(*hexc('#8d99ae')); ctx.fill()
    # tray + bag (hidden while inside the tunnel)
    ctx.save(); ctx.rectangle(0, 0, 700, H); ctx.rectangle(990, 0, W - 990, H); ctx.clip()
    tray(ctx, bag_x, 1390); flower_bag(ctx, bag_x, 1350, 0.8)
    ctx.restore()
    # lead curtain strips at the tunnel mouth
    for k in range(6):
        sw = 6 * math.sin(t * 9 + k) if 600 < bag_x < 780 else 0
        rrect(ctx, 702 + k * 12 + sw, 1206, 10, 180, 4); ctx.set_source_rgba(*hexc('#495057', 0.9)); ctx.fill()

def table(ctx):
    rrect(ctx, 560, TABLE_Y, 520, 26, 8); ctx.set_source_rgba(*hexc('#ced4da')); ctx.fill()
    ctx.rectangle(580, TABLE_Y + 26, 480, 300); ctx.set_source_rgba(*hexc('#adb5bd')); ctx.fill()
    rrect(ctx, 640, TABLE_Y + 70, 360, 50, 10); ctx.set_source_rgba(*hexc(NAVY)); ctx.fill()
    ftext(ctx, "BAG CHECK", 820, TABLE_Y + 106, 30, (1, 1, 1, 1), 330)

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    hall(ctx, t)
    bag_x = lerp(640, 850, ramp(t, 0.15, 1.15))
    alarm = t >= 1.2
    xray(ctx, t, bag_x, alarm)
    wren(ctx, WX, GY, 1.1, t, "point", expr="shock" if 1.25 < t < 2.2 else "happy", hand=HAND)
    if 1.2 < t < 1.5: burst(ctx, 960, 1150, 1 - (t - 1.2) / 0.3, 90)
    kid(ctx, LX, GY, 0.85, t, "flat" if alarm else "smile", (-60, -200))
    bubble_ml(ctx, 330, 790, ["It's only", "my soup!"], 46, ramp(t, 2.2, 2.4), (WX, 950))
    header(ctx, ease(t / 0.2 + 1), "AIRPORT SECURITY", "Wren's bag hits the X-ray.", "It's 2 litres of soup.", -0.3, t, main_size=56)
    meter(ctx, "LIQUID IN WREN'S BAG", "2,000 ml" if alarm else "scanning…"); wm(ctx)

OFF_X = 830
def s1(ctx, t, d):
    hall(ctx, t)
    up = ramp(t, 0.3, 0.8)
    hand = (lerp(OFF_X - 100, 680, up), lerp(1360, 1215, up))
    person(ctx, OFF_X, GY, 1.0, t, NAVY, '#c68642', '#1b1b1b', hand=hand, officer=True, smile=False)
    bottle(ctx, hand[0], hand[1] - 14, 1.3 * up, 0.0, up)
    table(ctx)
    jar(ctx, 975, TABLE_Y, 1.0)
    wren(ctx, WX, GY, 1.1, t, "point", expr="shock" if t < 2.3 else "happy", hand=HAND)
    bubble_ml(ctx, 830, 860, ["100 ml max,", "madam."], 42, ramp(t, 0.5, 0.7) * (1 - ramp(t, 2.3, 2.45)), (OFF_X, 1010))
    bubble_ml(ctx, 330, 790, ["Challenge", "accepted."], 46, ramp(t, 2.6, 2.8), (WX, 950))
    header(ctx, ease(t / 0.2), "THE RULE", "Liquids: 100 ml per bottle.", "Wren's jar: 20 times that.", 1.0, t, main_size=54)
    meter(ctx, "OVER THE LIMIT BY", "1,900 ml"); wm(ctx)

BX0, BSP = 742, 33
def s2(ctx, t, d):
    hall(ctx, t)
    table(ctx)
    n_f = clamp01((t - 0.35) / 2.4) * 20
    n = int(n_f)
    jar(ctx, 640, TABLE_Y, 0.85, level=1 - n_f / 20, label=False)
    for i in range(20):                                                   # back row first, then front row
        row, col = (1, i - 10) if i >= 10 else (0, i)
        if i > n: continue
        pop = ramp(t, 0.35 + i * 0.12, 0.35 + i * 0.12 + 0.12)
        fill = 1.0 if i < n else n_f - n
        base = TABLE_Y - 34 if row == 1 else TABLE_Y
        bottle(ctx, BX0 + col * BSP + (16 if row else 0), base, 0.9 * pop if row else pop, fill)
    # pour stream from jar to the bottle being filled
    if 0.35 < t < 2.75:
        i = min(n, 19); row, col = (1, i - 10) if i >= 10 else (0, i)
        tx = BX0 + col * BSP + (16 if row else 0); ty = (TABLE_Y - 34 if row else TABLE_Y) - 60
        ctx.set_line_width(7); ctx.set_source_rgba(*hexc(SOUP, 0.9)); ctx.move_to(680, TABLE_Y - 150); ctx.curve_to(tx - 30, ty - 120, tx, ty - 60, tx, ty); ctx.stroke()
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy", hand=HAND)
    kid(ctx, LX, GY, 0.85, t, "flat", (0, -150))
    bubble_ml(ctx, 815, 1140, ["Where were those", "HIDING?!"], 38, ramp(t, 0.9, 1.1) * (1 - ramp(t, 2.7, 2.85)), (LX, 1378))
    bubble_ml(ctx, 330, 790, ["Grandma always", "packs spares."], 44, ramp(t, 2.95, 3.15), (WX, 950))
    header(ctx, ease(t / 0.2), "WREN'S FIX", "Twenty tiny bottles.", "100 ml each. Legal!", 1.2, t, main_size=56)
    meter(ctx, "BOTTLES FILLED", "%d / 20" % n); wm(ctx)

PEOPLE = [(665, '#9b5de5', '#8d5524', '#1b1b1b', False), (800, '#2a9d8f', '#f1c27d', '#c9a227', False), (945, NAVY, '#c68642', '#1b1b1b', True)]
def s3(ctx, t, d):
    hall(ctx, t)
    for k, (px, sh, sk, hr, off) in enumerate(PEOPLE):
        tk = 0.5 + k * 0.55; got = t > tk
        hy = 1700 - 300 * 0.8
        hand = (px - 72, lerp(hy + 40, 1700 - 470 * 0.8, ramp(t, tk + 0.25, tk + 0.6)))
        sip = 1.0 if (off and t > 2.2) else 0.0
        if off: hand = (lerp(hand[0], px - 52, ramp(t, 1.9, 2.2)), lerp(hand[1], 1240, ramp(t, 1.9, 2.2)))
        person(ctx, px, GY, 0.8, t, sh, sk, hr, hand=hand, officer=off, sip=sip)
        if got: bottle(ctx, hand[0], hand[1] - 12, 1.0, 0.0 if (off and t > 2.2) else 1.0)
        heart(ctx, px + 40, 1150 - 120 * ramp(t, tk + 0.3, tk + 1.3), 1.2, (1 - ramp(t, tk + 0.9, tk + 1.3)) if t > tk + 0.3 else 0)
    served = int(clamp01((t - 0.4) / 2.0) * 10)
    # Wren serves from a little tray
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy", hand=HAND)
    rrect(ctx, HX - 70, HY - 12, 140, 16, 6); ctx.set_source_rgba(*hexc('#6c757d')); ctx.fill()
    left = 3 - sum(1 for k in range(3) if t > 0.5 + k * 0.55)
    for k in range(left): bottle(ctx, HX - 40 + k * 40, HY - 12, 0.8, 1.0)
    bubble_ml(ctx, 820, 960, ["Is this...", "pumpkin?"], 40, ramp(t, 2.3, 2.5), (945, 1150))
    bubble_ml(ctx, 330, 790, ["Seconds", "are free."], 46, ramp(t, 2.9, 3.1), (WX, 950))
    header(ctx, ease(t / 0.2), "THE CATCH", "Only 10 fit in the bag.", "So Wren serves the rest.", 1.0, t, main_size=56)
    meter(ctx, "SOUP SERVED", "%d / 10" % served); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 470, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    jar(ctx, 810, 1620, 1.25 + 0.03 * math.sin(t * 3), level=0.0)
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “No soup left behind.”", 205 - (1 - a) * 20, 58, hexc('#22223b', a), maxw=1000)
    ctext(ctx, "Leo: “Security had seconds.”", 290, 58, hexc(RED, ease((t - 0.5) / 0.3)), maxw=960)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Weirdest thing you've packed? Comment!", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 0.8), (s0, 3.3), (s1, 0.3), (s1, 1.6), (s1, 3.9), (s2, 1.2), (s2, 2.0), (s2, 3.9), (s3, 1.0), (s3, 2.6), (s3, 3.7), (s4, 1.0), (s4, 2.6)]
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

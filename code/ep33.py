"""ep33 - Theme park ride photo: Leo wants ONE good rollercoaster photo. #1 mid-scream, #2 a seagull, #3 his cap, #4 asleep from the 6-hour queue. Wren looks perfect in all four. Then she sticks his face through the face-in-the-hole board: one try, free. She still bought all four, for the fridge."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep33"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; YEL = '#ffd166'; GREEN = '#2ecc71'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1700

def meter(ctx, label, val, a=1.0, col=YEL):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc(col, a)); ctx.show_text(val)

def txt(ctx, s, x, y, size, col, center=True, bold=True):
    mv.font(ctx, size, bold); e = ctx.text_extents(s); ctx.move_to(x - (e.x_advance / 2 if center else 0), y); ctx.set_source_rgba(*col); ctx.show_text(s)

def sfx(ctx, s, x, y, a, col=RED, size=50, rot=-0.1):
    if a <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); txt(ctx, s, 0, 0, size, hexc(col, a)); ctx.restore()

# ------------------------------------------------------------ Leo's photo faces
def seagull(ctx, x, y, s, t):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    fl = math.sin(t * 14) * 0.35
    ctx.set_source_rgba(*hexc('#adb5bd'))
    for sg in (-1, 1):
        ctx.move_to(0, -6); ctx.curve_to(sg * 40, -50 - 30 * fl, sg * 80, -40 - 40 * fl, sg * 110, -60 - 50 * fl)
        ctx.curve_to(sg * 70, -10, sg * 30, 0, 0, 8); ctx.close_path(); ctx.fill()
    e4.ell(ctx, 0, 0, 46, 28, (1, 1, 1, 1))
    circle(ctx, 34, -16, 22, (1, 1, 1, 1))
    ctx.move_to(52, -20); ctx.line_to(82, -12); ctx.line_to(52, -6); ctx.close_path(); ctx.set_source_rgba(*hexc('#ff9f1c')); ctx.fill()
    circle(ctx, 40, -22, 4.5, hexc('#22223b'))
    ctx.restore()

def leo_fx(ctx, x, gy, s, t, kind):
    """draws on top of kid() with the same transform (incl. its bob)"""
    if kind == "smile": return
    ctx.save(); ctx.translate(x, gy); ctx.scale(s, s); ctx.translate(0, math.sin(t * 2 * math.pi * 1.6) * 3)
    skin = hexc('#c68642')
    if kind == "scream":
        for ex in (-20, 20): circle(ctx, ex, -307, 13, (1, 1, 1, 1)); circle(ctx, ex, -305, 5.5, hexc('#2b2d42'))
        circle(ctx, 0, -280, 22, skin)
        ctx.save(); ctx.translate(0, -274); ctx.scale(17, 22); circle(ctx, 0, 0, 1, hexc('#7a1f2b')); ctx.restore()
        ctx.save(); ctx.translate(0, -262); ctx.scale(10, 7); circle(ctx, 0, 0, 1, hexc('#ff8fa3')); ctx.restore()
    elif kind == "sleep":
        for ex in (-20, 20): circle(ctx, ex, -306, 10, skin)
        circle(ctx, 0, -284, 22, skin)
        ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#2b2d42'))
        for ex in (-20, 20): ctx.arc(ex, -308, 9, math.radians(20), math.radians(160)); ctx.stroke()
        circle(ctx, 0, -280, 7, hexc('#7a3e2b'))
        for k, (zx, zy, zs) in enumerate(((70, -360, 30), (100, -400, 38))):
            txt(ctx, "z", zx, zy, zs, hexc('#4361ee'))
    elif kind == "cap":
        ctx.save(); ctx.translate(0, -296); ctx.rotate(0.12)
        e4.ell(ctx, 0, 0, 66, 56, hexc('#2a9d8f'))
        rrect(ctx, -70, 30, 140, 22, 11); ctx.set_source_rgba(*hexc('#1f7a70')); ctx.fill()
        circle(ctx, 0, -50, 9, hexc('#1f7a70'))
        ctx.restore()
    elif kind == "bird":
        seagull(ctx, -6, -296, 0.95, t)
    ctx.restore()

# ------------------------------------------------------------ coaster car
def ride_car(ctx, x, y, s, ang, t, leo="smile"):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    wren(ctx, -110, 40, 0.55, t, "cheer", expr="happy")
    kid(ctx, 118, -10, 0.62, t, "flat" if leo == "sleep" else "smile", hands=(0, -440) if leo != "sleep" else (0, -200))
    leo_fx(ctx, 118, -10, 0.62, t, leo)
    rrect(ctx, -240, -150, 480, 200, 40); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    ctx.move_to(236, -150); ctx.line_to(300, -70); ctx.line_to(300, -10); ctx.line_to(236, 20); ctx.close_path(); ctx.set_source_rgba(*hexc('#c1121f')); ctx.fill()
    ctx.rectangle(-240, -98, 500, 22); ctx.set_source_rgba(*hexc(YEL)); ctx.fill()
    rrect(ctx, -250, -160, 500, 22, 11); ctx.set_source_rgba(*hexc('#3d405b')); ctx.fill()        # lap bar
    circle(ctx, -40, -40, 26, hexc('#ffffff')); txt(ctx, "7", -40, -27, 34, hexc(RED))
    for wx in (-170, 170): circle(ctx, wx, 52, 28, hexc('#22223b')); circle(ctx, wx, 52, 10, hexc('#adb5bd'))
    ctx.restore()

# ------------------------------------------------------------ coaster park
PEAK, BOT, X0, X1 = 1200, 1580, 160, 880
def track_y(x):
    if x < X0: return PEAK
    if x > X1: return BOT
    return PEAK + (BOT - PEAK) * (1 - math.cos(math.pi * (x - X0) / (X1 - X0))) / 2
def track_ang(x):
    if x < X0 or x > X1: return 0.0
    return math.atan((BOT - PEAK) * math.pi / (2 * (X1 - X0)) * math.sin(math.pi * (x - X0) / (X1 - X0)))

def sky(ctx, x0=0, y0=0, w=W, h=H, clouds=True, t=0.0):
    g = cairo.LinearGradient(0, y0, 0, y0 + h); g.add_color_stop_rgb(0, *hexc('#74c0fc')[:3]); g.add_color_stop_rgb(1, *hexc('#e7f5ff')[:3])
    ctx.set_source(g); ctx.rectangle(x0, y0, w, h); ctx.fill()

def park_bg(ctx, t):
    sky(ctx)
    for cx, cy, s in ((180, 700, 0.9), (820, 640, 0.7)): mv.cloud(ctx, cx + 10 * math.sin(t * 0.5), cy, s)
    # distant big wheel
    ctx.set_line_width(8); ctx.set_source_rgba(*hexc('#9775fa', 0.55)); ctx.arc(860, 1120, 230, 0, 2 * math.pi); ctx.stroke()
    for k in range(8):
        a = k * math.pi / 4 + t * 0.15; ctx.move_to(860, 1120); ctx.line_to(860 + 230 * math.cos(a), 1120 + 230 * math.sin(a)); ctx.stroke()
        circle(ctx, 860 + 230 * math.cos(a), 1120 + 230 * math.sin(a), 22, hexc(['#ff8fa3', '#ffd166', '#74c0fc', '#8ce99a'][k % 4], 0.7))
    ctx.rectangle(0, 1600, W, H - 1600); ctx.set_source_rgba(*hexc('#8fd18a')); ctx.fill()
    # supports (lattice)
    ctx.set_line_width(10); ctx.set_source_rgba(*hexc('#f8f9fa'))
    xs = list(range(-40, W + 80, 120))
    for x in xs: ctx.move_to(x, track_y(x) + 20); ctx.line_to(x, 1610); ctx.stroke()
    ctx.set_line_width(5)
    for x in xs[:-1]:
        ctx.move_to(x, track_y(x) + 40); ctx.line_to(x + 120, 1600); ctx.stroke()
    # rails
    for dy, col, lw in ((0, '#c1121f', 16), (22, '#9d0208', 10)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*hexc(col))
        for i, x in enumerate(range(-60, W + 60, 10)):
            ctx.line_to(x, track_y(x) + dy) if i else ctx.move_to(x, track_y(x) + dy)
        ctx.stroke()

def camera_post(ctx, t, flash=0.0):
    ctx.set_line_width(16); ctx.set_source_rgba(*hexc('#495057')); ctx.move_to(1000, 760); ctx.line_to(1000, 1610); ctx.stroke()
    ctx.save(); ctx.translate(990, 730); ctx.rotate(0.45)
    rrect(ctx, -60, -40, 120, 80, 14); ctx.set_source_rgba(*hexc('#22223b')); ctx.fill()
    circle(ctx, -60, 0, 30, hexc('#495057')); circle(ctx, -60, 0, 18, hexc('#74c0fc'))
    if flash > 0: circle(ctx, -40, -50, 40 * flash + 10, hexc('#fff3b0', flash))
    ctx.restore()
    rrect(ctx, 880, 830, 180, 66, 14); ctx.set_source_rgba(*hexc(YEL)); ctx.fill()
    txt(ctx, "SMILE!", 970, 877, 38, hexc(RED))

# ------------------------------------------------------------ photos
def photo(ctx, x, y, w, h, leo, t, label=None, a=1.0, rot=0.0, price=False):
    if a <= 0: return
    ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.rotate(rot); sc = 0.6 + 0.4 * a; ctx.scale(sc, sc); ctx.translate(-w / 2, -h / 2)
    rrect(ctx, -12, -12, w + 24, h + 24, 16); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.save(); ctx.rectangle(0, 0, w, h); ctx.clip()
    sky(ctx, 0, 0, w, h)
    k = h / 400.0; sc = h / 270.0
    ride_car(ctx, w / 2 - 4 * sc, h + 110 * sc, sc, 0.0, t, leo)
    ctx.restore()
    if label:
        rrect(ctx, 6, 6, 110 * max(k, 0.7), 46 * max(k, 0.7), 12); ctx.set_source_rgba(*hexc('#10132b', 0.9)); ctx.fill()
        txt(ctx, label, 6 + 55 * max(k, 0.7), 6 + 34 * max(k, 0.7), int(30 * max(k, 0.7)), hexc(YEL))
    if price:
        ctx.save(); ctx.translate(w - 70, 60); ctx.rotate(0.2); circle(ctx, 0, 0, 58, hexc(RED)); txt(ctx, "$25", 0, 14, 40, (1, 1, 1, 1)); ctx.restore()
    ctx.restore()

def kiosk_bg(ctx, t):
    mv.vgrad(ctx, '#e5dbff', '#d0bfff')
    for k in range(9):                                                     # bunting
        x = k * 130 - 20; ctx.move_to(x, 600); ctx.line_to(x + 130, 600); ctx.line_to(x + 65, 640); ctx.close_path()
        ctx.set_source_rgba(*hexc(['#e63946', '#ffd166', '#4cc9f0'][k % 3])); ctx.fill()
    ctx.rectangle(0, 1600, W, H - 1600); ctx.set_source_rgba(*hexc('#b197fc')); ctx.fill()
    for x in range(-40, W, 140): ctx.rectangle(x, 1600, 5, H - 1600); ctx.set_source_rgba(*hexc('#9775fa')); ctx.fill()

# ------------------------------------------------------------ face-in-the-hole board
BX, BY, BW, BH = 180, 1000, 520, 640
HOLE = (440, 1345, 76)
def board(ctx, t):
    hx, hy, hr = HOLE
    for lx in (BX + 150, BX + BW - 150): ctx.rectangle(lx - 12, BY + BH - 10, 24, GY - BY - BH + 10); ctx.set_source_rgba(*hexc('#8a5a2b')); ctx.fill()
    ctx.save()
    rrect(ctx, BX, BY, BW, BH, 26); ctx.arc(hx, hy, hr, 0, 2 * math.pi); ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); ctx.clip()
    sky(ctx, BX, BY, BW, BH)
    # painted hero body: striped shirt, huge flexing arms
    skin = hexc('#e0a36a')
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for sg in (-1, 1):
        ctx.set_line_width(70); ctx.set_source_rgba(*skin)
        ctx.move_to(hx + sg * 90, hy + 130); ctx.line_to(hx + sg * 190, hy + 40); ctx.line_to(hx + sg * 170, hy - 90); ctx.stroke()
        circle(ctx, hx + sg * 190, hy + 30, 56, skin)                     # biceps
        circle(ctx, hx + sg * 170, hy - 110, 42, skin)                    # fist
    rrect(ctx, hx - 130, hy + 70, 260, 260, 60); ctx.set_source_rgba(*hexc('#ffffff')); ctx.fill()
    for k in range(5): ctx.rectangle(hx - 130, hy + 90 + k * 46, 260, 20); ctx.set_source_rgba(*hexc('#4361ee')); ctx.fill()
    # painted coaster front
    rrect(ctx, BX - 20, BY + BH - 190, BW + 40, 220, 40); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    ctx.rectangle(BX, BY + BH - 140, BW, 24); ctx.set_source_rgba(*hexc(YEL)); ctx.fill()
    txt(ctx, "WORLD'S BRAVEST", hx, BY + 70, 34, hexc(RED))
    txt(ctx, "RIDER", hx, BY + 122, 46, hexc(RED))
    ctx.restore()
    ctx.set_line_width(12); ctx.set_source_rgba(*hexc('#8a5a2b')); rrect(ctx, BX, BY, BW, BH, 26); ctx.stroke()
    ctx.arc(hx, hy, hr, 0, 2 * math.pi); ctx.set_line_width(6); ctx.stroke()

def board_scene(ctx, t, leo_expr="smile"):
    kid(ctx, HOLE[0], GY, 1.1, t, leo_expr, (0, -200))
    board(ctx, t)

def phone(ctx, x, y, flash=0.0):
    rrect(ctx, x - 30, y - 50, 60, 100, 12); ctx.set_source_rgba(*hexc('#1a1c2e')); ctx.fill()
    rrect(ctx, x - 22, y - 40, 44, 78, 6); ctx.set_source_rgba(*hexc('#74c0fc')); ctx.fill()
    if flash > 0: circle(ctx, x - 14, y - 34, 12 + 50 * flash, hexc('#fff3b0', flash))

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    park_bg(ctx, t)
    flash_t = 2.25
    tt = min(t, flash_t)                                             # freeze-frame at the flash
    k = clamp01((tt - 0.6) / 1.65); x = lerp(260, 740, k * k)
    leo = "smile" if x < 330 else "scream"
    s = 1.45
    ride_car(ctx, x, track_y(x) - 66 * s, s, track_ang(x) * 0.8, tt, leo)
    fl = ramp(t, flash_t, flash_t + 0.05) * (1 - ramp(t, flash_t + 0.1, flash_t + 0.6))
    camera_post(ctx, t, fl)
    sfx(ctx, "AAAAAH!", 330, 1500, ramp(t, 1.2, 1.4), RED, 56, -0.12)
    bubble_ml(ctx, 690, 900, ["Big smile...", "big smile..."], 40, ramp(t, 0.15, 0.35) * (1 - ramp(t, 0.95, 1.1)), (480, 820))
    if fl > 0: ctx.set_source_rgba(1, 1, 1, 0.85 * fl); ctx.paint()
    sfx(ctx, "CLICK!", 770, 980, ramp(t, flash_t, flash_t + 0.15), '#22223b', 60, -0.08)
    header(ctx, ease(t / 0.2 + 1), "THEME PARK RIDE PHOTO", "Leo wants ONE good photo.", "The camera has other plans.", -0.3, t, main_size=54)
    meter(ctx, "RIDE PHOTO PRICE", "$25"); wm(ctx)

def s1(ctx, t, d):
    kiosk_bg(ctx, t)
    rrect(ctx, 96, 662, 888, 436, 24); ctx.set_source_rgba(*hexc('#22223b')); ctx.fill()           # monitor
    photo(ctx, 130, 690, 820, 380, "scream", 0.0, "#1", ramp(t, 0.1, 0.5), price=True)
    wren(ctx, 440, GY, 0.95, t, "point" if t < 2.6 else "wave", expr="happy", hand=(140, -380))
    kid(ctx, 820, GY, 1.0, t, "flat", (0, -150))
    bubble_ml(ctx, 760, 1190, ["I look like a", "screaming potato."], 40, ramp(t, 0.8, 1.0) * (1 - ramp(t, 2.5, 2.65)), (820, 1330))
    bubble_ml(ctx, 760, 1190, ["A lovely", "potato, dear."], 42, ramp(t, 2.8, 3.0), (520, 1140))
    header(ctx, ease(t / 0.2), "PHOTO #1", "Leo: mid-scream.", "Wren: flawless.", 0.9, t, main_size=56)
    meter(ctx, "GOOD PHOTOS OF LEO", "0"); wm(ctx)

CELLS = [(100, 640, 420, 240), (560, 640, 420, 240), (100, 905, 420, 240), (560, 905, 420, 240)]
def s2(ctx, t, d):
    kiosk_bg(ctx, t)
    kinds = ["scream", "bird", "cap", "sleep"]
    for i, (cx, cy, cw, ch) in enumerate(CELLS):
        t0 = [-1, 0.8, 1.7, 2.6][i]
        a = 1.0 if i == 0 else ramp(t, t0, t0 + 0.3)
        photo(ctx, cx, cy, cw, ch, kinds[i], t if kinds[i] == "bird" else 0.0, "#%d" % (i + 1), a, rot=[-0.03, 0.03, 0.02, -0.025][i])
        if i and t0 < t < t0 + 0.3: burst(ctx, cx + cw / 2, cy + ch / 2, 1 - (t - t0) / 0.3, 140)
    wren(ctx, 440, GY, 0.85, t, "point", expr="happy", hand=(140, -380))
    kid(ctx, 830, GY, 0.95, t, "smile" if t < 1.0 else "flat", (0, -150) if t > 1.0 else (0, -420))
    bubble_ml(ctx, 790, 1270, ["ONE more go!"], 42, ramp(t, 0.1, 0.3) * (1 - ramp(t, 0.85, 1.0)), (830, 1380))
    bubble_ml(ctx, 790, 1270, ["Is that a", "SEAGULL?!"], 42, ramp(t, 1.05, 1.25) * (1 - ramp(t, 2.4, 2.55)), (830, 1380))
    bubble_ml(ctx, 790, 1270, ["I fell asleep", "in the queue."], 40, ramp(t, 2.95, 3.15), (830, 1380))
    header(ctx, ease(t / 0.2), "RIDE AGAIN. AND AGAIN.", "4 rides. 4 disasters.", "Wren: perfect every time.", 1.4, t, main_size=56)
    meter(ctx, "TIME IN QUEUES", "%.1f HRS" % lerp(1.5, 6.0, ramp(t, 0.6, 3.0))); wm(ctx)

def park_path_bg(ctx, t):
    park_bg_light = '#d3f9d8'
    sky(ctx)
    for cx, cy, s in ((820, 700, 0.8),): mv.cloud(ctx, cx + 10 * math.sin(t * 0.5), cy, s)
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#c1121f', 0.35))         # coaster in the distance
    for i, x in enumerate(range(0, W + 10, 10)):
        y = 1000 - 140 * math.sin(x / 170.0) * math.exp(-((x - 700) / 600.0) ** 2)
        ctx.line_to(x, y) if i else ctx.move_to(x, y)
    ctx.stroke()
    ctx.rectangle(0, 1560, W, H - 1560); ctx.set_source_rgba(*hexc('#ffe8cc')); ctx.fill()
    ctx.rectangle(0, 1540, W, 30); ctx.set_source_rgba(*hexc('#8fd18a')); ctx.fill()

def s3(ctx, t, d):
    park_path_bg(ctx, t)
    flash_t = 2.0
    happy = t > flash_t + 0.4
    board_scene(ctx, t, "smile")
    WX, WS = 885, 0.95
    ctx.save(); ctx.translate(WX, 0); ctx.scale(-1, 1); wren(ctx, 0, GY, WS, t, "point", expr="happy", hand=(150, -330)); ctx.restore()
    fl = ramp(t, flash_t, flash_t + 0.05) * (1 - ramp(t, flash_t + 0.1, flash_t + 0.5))
    phone(ctx, WX - 150 * WS - 6, GY - 330 * WS, fl)
    if fl > 0: ctx.set_source_rgba(1, 1, 1, 0.45 * fl); ctx.paint()
    pa = ramp(t, flash_t + 0.3, flash_t + 0.6)
    if pa > 0:                                                                # the photo pops up
        ctx.save(); ctx.translate(320, 820); ctx.rotate(-0.06); sc = 0.6 + 0.4 * pa; ctx.scale(sc, sc)
        rrect(ctx, -190, -175, 380, 360, 14); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        ctx.save(); ctx.rectangle(-170, -155, 340, 270); ctx.clip()
        ctx.translate(-170, -155); ctx.scale(0.5, 0.5); ctx.translate(-180, -980)
        sky(ctx, 0, 0, W, H); board_scene(ctx, 0.4, "smug")
        ctx.restore()
        txt(ctx, "PERFECT!", 0, 160, 38, hexc(RED))
        ctx.restore()
    bubble_ml(ctx, 790, 880, ["Face in the", "hole, love."], 42, ramp(t, 0.4, 0.6) * (1 - ramp(t, 1.75, 1.9)), (WX - 20, 1110))
    bubble_ml(ctx, 790, 880, ["That's actually", "great."], 42, ramp(t, 2.8, 3.0), (520, 1270))
    header(ctx, ease(t / 0.2), "PLAN GRANDMA", "The face-in-the-hole board.", "One try. Free.", 0.9, t, main_size=52)
    meter(ctx, "GOOD PHOTOS OF LEO", "1  ·  $0" if t > flash_t + 0.2 else "0", col=GREEN if t > flash_t + 0.2 else YEL); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    ctx.save(); ctx.translate(810, 1400); ctx.rotate(0.12 + 0.04 * math.sin(t * 3))          # fridge-magnet photo
    photo(ctx, -110, -80, 220, 150, "scream", 0.0)
    circle(ctx, 0, -92, 16, hexc(RED)); ctx.restore()
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “I bought all four.”", 205 - (1 - a) * 20, 60, hexc('#22223b', a), maxw=940)
    ctext(ctx, "Leo: “For the FRIDGE.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Tag your worst ride-photo face", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 1.6), (s0, 2.6), (s1, 1.5), (s1, 3.6), (s2, 1.6), (s2, 3.8), (s3, 1.0), (s3, 2.05), (s3, 3.5), (s4, 2.6)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((300, 533)))
        c = Image.new("RGB", (310 * 6, 543 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 6) * 310, (i // 6) * 543))
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

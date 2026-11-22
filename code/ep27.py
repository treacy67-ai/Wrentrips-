"""ep27 - Art gallery: Leo queued two hours for the famous painting and sees only phones. 214 jump-photos, zero painting. Wren buys the $12 gift-shop poster. The crowd turns round and photographs HER."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep27"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; GOLD = '#d4a017'; GOLD_D = '#9c7410'; WALL = '#7d2433'; WALL_D = '#5e1a26'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1600                         # characters' ground line (kept above the @wrentrips watermark)
FLOOR = 1340

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

def ftext(ctx, s, cx, y, size, col, maxw, bold=True):
    mv.font(ctx, size, bold); e = ctx.text_extents(s)
    while e.x_advance > maxw and size > 12:
        size -= 1; mv.font(ctx, size, bold); e = ctx.text_extents(s)
    ctx.move_to(cx - e.x_advance / 2, y); ctx.set_source_rgba(*col); ctx.show_text(s)

# ------------------------------------------------------------ the (invented) famous painting: a smug duck in a beret
def duck_art(ctx, x, y, w, h, frame=True, label=True):
    """Painting with top-left (x, y), size w x h (inside of frame)."""
    if frame:
        fw = max(10, w * 0.08)
        rrect(ctx, x - fw, y - fw, w + 2 * fw, h + 2 * fw, fw * 0.5); ctx.set_source_rgba(*hexc(GOLD)); ctx.fill()
        ctx.set_line_width(max(2, fw * 0.25)); ctx.set_source_rgba(*hexc(GOLD_D)); rrect(ctx, x - fw * 0.45, y - fw * 0.45, w + fw * 0.9, h + fw * 0.9, fw * 0.3); ctx.stroke()
        for cx_, cy_ in ((x - fw * 0.5, y - fw * 0.5), (x + w + fw * 0.5, y - fw * 0.5), (x - fw * 0.5, y + h + fw * 0.5), (x + w + fw * 0.5, y + h + fw * 0.5)):
            circle(ctx, cx_, cy_, fw * 0.55, hexc('#f1c84b'))
    g = cairo.RadialGradient(x + w * 0.5, y + h * 0.45, w * 0.05, x + w * 0.5, y + h * 0.5, w * 0.8)
    g.add_color_stop_rgb(0, *hexc('#5a7d4f')[:3]); g.add_color_stop_rgb(1, *hexc('#1f3324')[:3])
    ctx.rectangle(x, y, w, h); ctx.set_source(g); ctx.fill()
    s = w / 300.0
    ctx.save(); ctx.translate(x + w / 2, y + h * 0.58); ctx.scale(s, s)
    e4.ell(ctx, 0, 70, 120, 80, hexc('#f4efe1'))                                 # body
    e4.ell(ctx, -60, 60, 60, 40, hexc('#e0d8c2'), -0.3)                         # wing
    ctx.rectangle(-36, -40, 72, 90); ctx.set_source_rgba(*hexc('#f4efe1')); ctx.fill()   # neck
    circle(ctx, 0, -60, 62, hexc('#f4efe1'))                                      # head
    for k in range(7):                                                            # lace ruff collar
        ang = math.pi * (k / 6.0); circle(ctx, math.cos(ang) * 58 - 0, 10 + math.sin(ang) * 10, 20, hexc('#ffffff'))
    e4.ell(ctx, 60, -48, 46, 16, hexc('#f4a300'))                                 # beak
    ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#b36b00')); ctx.move_to(26, -48); ctx.line_to(100, -48); ctx.stroke()
    circle(ctx, 18, -74, 9, hexc('#1b1b1b'))                                       # smug half-closed eye
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#1b1b1b')); ctx.move_to(4, -84); ctx.line_to(34, -82); ctx.stroke()
    circle(ctx, -14, -56, 10, hexc('#f28b82', 0.5))
    ctx.save(); ctx.translate(-8, -116); ctx.rotate(-0.25); e4.ell(ctx, 0, 0, 64, 22, hexc('#c1121f')); circle(ctx, 0, -14, 9, hexc('#c1121f')); ctx.restore()  # beret
    ctx.restore()
    if label:
        lw = w * 0.5
        rrect(ctx, x + w / 2 - lw / 2, y + h + w * 0.12, lw, w * 0.09, 4); ctx.set_source_rgba(*hexc('#f1e3c0')); ctx.fill()
        ftext(ctx, "THE DUCK, 1622", x + w / 2, y + h + w * 0.12 + w * 0.068, max(10, int(w * 0.055)), hexc('#3b2a14'), lw * 0.9)

# ------------------------------------------------------------ background: grand gallery room
def small_frame(ctx, x, y, w, h, kind):
    fw = 14
    rrect(ctx, x - fw, y - fw, w + 2 * fw, h + 2 * fw, 6); ctx.set_source_rgba(*hexc(GOLD_D)); ctx.fill()
    if kind == 0:                                                                 # landscape
        ctx.rectangle(x, y, w, h); ctx.set_source_rgba(*hexc('#9ad1d4')); ctx.fill()
        ctx.move_to(x, y + h); ctx.line_to(x + w * 0.35, y + h * 0.45); ctx.line_to(x + w * 0.6, y + h * 0.75); ctx.line_to(x + w * 0.8, y + h * 0.5); ctx.line_to(x + w, y + h); ctx.close_path()
        ctx.set_source_rgba(*hexc('#52796f')); ctx.fill(); circle(ctx, x + w * 0.78, y + h * 0.25, w * 0.1, hexc('#ffd166'))
    else:                                                                         # bowl of fruit
        ctx.rectangle(x, y, w, h); ctx.set_source_rgba(*hexc('#3d2c2e')); ctx.fill()
        for k, c in enumerate(('#e63946', '#ffb703', '#8ac926')): circle(ctx, x + w * (0.32 + 0.18 * k), y + h * 0.55, w * 0.12, hexc(c))
        e4.ell(ctx, x + w / 2, y + h * 0.7, w * 0.36, h * 0.1, hexc('#c9b79c'))

def gallery(ctx, t, art=True, art_x=380, art_w=320, art_y=760):
    g = cairo.LinearGradient(0, 0, 0, FLOOR); g.add_color_stop_rgb(0, *hexc(WALL_D)[:3]); g.add_color_stop_rgb(1, *hexc(WALL)[:3])
    ctx.rectangle(0, 0, W, FLOOR); ctx.set_source(g); ctx.fill()
    for k in range(9):                                                            # damask-ish pattern
        for j in range(8):
            circle(ctx, 60 + k * 120 + (j % 2) * 60, 640 + j * 90, 8, hexc('#9a3445', 0.5))
    ctx.rectangle(0, FLOOR - 140, W, 140); ctx.set_source_rgba(*hexc('#4a1520')); ctx.fill()      # wainscot
    ctx.rectangle(0, FLOOR - 146, W, 10); ctx.set_source_rgba(*hexc(GOLD_D)); ctx.fill()
    small_frame(ctx, 40, 740, 200, 150, 0); small_frame(ctx, 860, 720, 170, 210, 1)
    if art:
        ah = art_w * 0.9
        for k in range(3):                                                        # spotlight
            ctx.move_to(art_x + art_w / 2 - 30, 600); ctx.line_to(art_x - 60 - k * 20, art_y + ah + 40); ctx.line_to(art_x + art_w + 60 + k * 20, art_y + ah + 40); ctx.close_path()
            ctx.set_source_rgba(1, 0.95, 0.75, 0.05); ctx.fill()
        duck_art(ctx, art_x, art_y, art_w, ah)
    # parquet floor
    ctx.rectangle(0, FLOOR, W, H - FLOOR); ctx.set_source_rgba(*hexc('#b98352')); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#a06d40'))
    for r in range(8):
        y = FLOOR + r * 75; ctx.move_to(0, y); ctx.line_to(W, y); ctx.stroke()
        for k in range(10):
            x = k * 140 + (r % 2) * 70; ctx.move_to(x, y); ctx.line_to(x, y + 75); ctx.stroke()

def rope(ctx, x0, x1, y):
    for x in (x0, x1):
        rrect(ctx, x - 8, y - 120, 16, 120, 6); ctx.set_source_rgba(*hexc(GOLD)); ctx.fill()
        e4.ell(ctx, x, y, 34, 10, hexc(GOLD_D)); circle(ctx, x, y - 124, 14, hexc('#f1c84b'))
    ctx.set_line_width(12); ctx.set_source_rgba(*hexc('#a4161a')); ctx.move_to(x0, y - 110); ctx.curve_to(x0 + 60, y - 50, x1 - 60, y - 50, x1, y - 110); ctx.stroke()

# ------------------------------------------------------------ crowd (generic tourists, seen from behind, phones up)
CROWD_COLS = ['#264653', '#2a9d8f', '#e9c46a', '#6d597a', '#457b9d', '#bc6c25', '#3a5a40', '#b5838d', '#1d3557', '#9c6644']
HAIR_COLS = ['#2b1d14', '#6b4423', '#c9a66b', '#1b1b1b', '#8d8d8d', '#a0522d']
def phone(ctx, x, y, ang, flash=0.0, s=1.0, screen='#bde0fe'):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    rrect(ctx, -24, -40, 48, 80, 9); ctx.set_source_rgba(*hexc('#1b1b2f')); ctx.fill()
    rrect(ctx, -19, -34, 38, 66, 6); ctx.set_source_rgba(*hexc(screen)); ctx.fill()
    ctx.restore()
    if flash > 0:
        circle(ctx, x, y, 60 * flash + 20, (1, 1, 1, 0.75 * flash))
        ctx.set_line_width(6); ctx.set_source_rgba(1, 1, 0.85, flash)
        for k in range(8):
            a = k * math.pi / 4; ctx.move_to(x + math.cos(a) * 30, y + math.sin(a) * 30); ctx.line_to(x + math.cos(a) * (60 + 50 * flash), y + math.sin(a) * (60 + 50 * flash)); ctx.stroke()

def tourist_back(ctx, x, base, s, i, t, aim=None, flash=0.0, sway=1.0):
    """Generic tourist from behind, arms up holding a phone. aim = (px, py) phone position, else straight up."""
    col = hexc(CROWD_COLS[i % len(CROWD_COLS)]); hair = hexc(HAIR_COLS[(i * 7) % len(HAIR_COLS)])
    b = math.sin(t * 3 + i * 1.3) * 4 * sway
    ctx.save(); ctx.translate(x, base); ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(36); ctx.set_source_rgba(*hexc('#2b2d42'))
    for lx in (-26, 26): ctx.move_to(lx, -170); ctx.line_to(lx, -16); ctx.stroke()
    rrect(ctx, -72, -430 + b, 144, 280, 42); ctx.set_source_rgba(*col); ctx.fill()
    px, py = aim if aim else (10 * math.sin(i), -640)
    ctx.set_line_width(30); ctx.set_source_rgba(*col)
    for sg in (-1, 1): ctx.move_to(sg * 58, -400 + b); ctx.line_to(px + sg * 14, py + 40 + b); ctx.stroke()
    circle(ctx, 0, -490 + b, 62, hair)                                           # back of head
    if i % 3 == 0: circle(ctx, 0, -548 + b, 24, hair)                            # bun
    if i % 4 == 1: ctx.arc(0, -500 + b, 66, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc('#f4a261')); ctx.fill()   # cap
    ctx.restore()
    phone(ctx, x + px * s, base + (py + b) * s, 0.05 * math.sin(i), flash, s)

def tourist_flash(t, i, rate=1.0):
    ph = (t * rate * 1.3 + i * 0.37) % 1.0
    return clamp01(1 - ph / 0.12) if ph < 0.12 else 0.0

CROWD = [(150, 0.92), (300, 1.0), (450, 0.95), (600, 1.05), (740, 0.95), (890, 1.0), (380, 0.85), (680, 0.88)]
def crowd_wall(ctx, t, base=1500, rate=1.0, n=8):
    order = sorted(range(n), key=lambda k: CROWD[k][1])                       # small (far) first
    for k in order:
        x, s = CROWD[k]
        tourist_back(ctx, x, base - (40 if s < 0.9 else 0), s, k, t, flash=tourist_flash(t, k, rate))

# ------------------------------------------------------------ props
def guide(ctx, x, y):                                                             # audio guide handset
    rrect(ctx, x - 14, y - 60, 28, 80, 8); ctx.set_source_rgba(*hexc('#1b1b2f')); ctx.fill(); circle(ctx, x, y - 44, 6, hexc('#4cc9f0'))

def poster(ctx, x, y, w, unroll):
    """Gift-shop poster, top-left (x, y), width w, unroll 0..1 (rolls down)."""
    h = w * 1.25 * unroll
    if unroll < 0.98:
        ctx.save(); ctx.rectangle(x, y, w, max(1, h)); ctx.clip()
        duck_art(ctx, x + w * 0.08, y + w * 0.08, w * 0.84, w * 0.84 * 0.9 * 1.0, frame=False, label=False)
        ctx.restore()
    else:
        rrect(ctx, x, y, w, h, 6); ctx.set_source_rgba(*hexc('#fbf6ea')); ctx.fill()
        duck_art(ctx, x + w * 0.08, y + w * 0.08, w * 0.84, w * 0.84 * 0.9, frame=False, label=False)
        ftext(ctx, "THE DUCK", x + w / 2, y + h - w * 0.13, int(w * 0.11), hexc('#3b2a14'), w * 0.8)
        ftext(ctx, "GIFT SHOP  $12", x + w / 2, y + h - w * 0.04, int(w * 0.055), hexc(RED), w * 0.8, bold=False)
    if unroll < 0.98:
        if unroll > 0.02:
            ctx.rectangle(x, y, w, h); ctx.set_source_rgba(*hexc('#fbf6ea', 0.0)); ctx.fill()
        rrect(ctx, x - 6, y + h - 22, w + 12, 44, 22); ctx.set_source_rgba(*hexc('#e9dcc0')); ctx.fill()   # the roll
        ctx.set_line_width(4); ctx.set_source_rgba(*hexc(RED)); ctx.move_to(x + w * 0.3, y + h - 22); ctx.line_to(x + w * 0.3, y + h + 22); ctx.stroke()
        e4.ell(ctx, x + w + 4, y + h, 10, 20, hexc('#c9b79c'))

def bench(ctx, x, y, w=420):
    rrect(ctx, x - w / 2, y - 26, w, 52, 14); ctx.set_source_rgba(*hexc('#5c3b22')); ctx.fill()
    rrect(ctx, x - w / 2 + 6, y - 22, w - 12, 18, 9); ctx.set_source_rgba(*hexc('#a4161a')); ctx.fill()
    for dx in (-w / 2 + 40, w / 2 - 40): rrect(ctx, x + dx - 14, y + 20, 28, 110, 6); ctx.set_source_rgba(*hexc('#3e2716')); ctx.fill()

def phone_inset(ctx, a, n_show, t):
    """Leo's camera roll: a grid of thumbnails, every one is phones and the backs of heads."""
    if a <= 0: return
    x, y, w, h = 120, 640, 470, 640
    ctx.save(); ctx.translate(0, (1 - a) * 40)
    rrect(ctx, x, y, w, h, 46); ctx.set_source_rgba(*hexc('#1b1b2f', a)); ctx.fill()
    rrect(ctx, x + 18, y + 60, w - 36, h - 110, 18); ctx.set_source_rgba(*hexc('#f8f9fa', a)); ctx.fill()
    mv.font(ctx, 24); ctx.move_to(x + 40, y + 42); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text("Photos")
    cols, rows = 4, 5; tw = (w - 36 - 10 * (cols + 1)) / cols; th = (h - 110 - 10 * (rows + 1)) / rows
    for r in range(rows):
        for c in range(cols):
            k = r * cols + c
            if k >= n_show: continue
            tx = x + 18 + 10 + c * (tw + 10); ty = y + 60 + 10 + r * (th + 10)
            ctx.save(); ctx.rectangle(tx, ty, tw, th); ctx.clip()
            ctx.rectangle(tx, ty, tw, th); ctx.set_source_rgba(*hexc(WALL)); ctx.fill()
            circle(ctx, tx + tw * 0.5, ty + th * 1.05, tw * 0.48, hexc(HAIR_COLS[k % len(HAIR_COLS)]))        # back of a head
            rrect(ctx, tx + tw * (0.2 + 0.1 * (k % 3)), ty + th * 0.12, tw * 0.3, th * 0.5, 4); ctx.set_source_rgba(*hexc('#1b1b2f')); ctx.fill()  # someone's phone
            rrect(ctx, tx + tw * (0.24 + 0.1 * (k % 3)), ty + th * 0.16, tw * 0.22, th * 0.4, 3); ctx.set_source_rgba(*hexc('#bde0fe')); ctx.fill()
            if k % 5 == 2: e4.ell(ctx, tx + tw * 0.8, ty + th * 0.5, tw * 0.16, th * 0.24, hexc('#f4c7a1'))   # an elbow
            ctx.restore()
    mv.font(ctx, 26); s_ = "0 of 214 show a painting"; e = ctx.text_extents(s_)
    ctx.move_to(x + w / 2 - e.x_advance / 2, y + h - 18); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(s_)
    ctx.restore()

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    gallery(ctx, t, art_y=920)
    rope(ctx, 300, 780, 1360)
    crowd_wall(ctx, t, rate=1.0)
    tip = 22 * abs(math.sin(t * 4.2))                                            # Leo on tiptoe, bobbing
    kid(ctx, 560, GY - tip, 0.95, t, "flat", (0, -170))
    wren(ctx, 880, GY, 1.0, t, "point", expr="happy", hand=(150, -330))
    guide(ctx, 880 + 150 + 2, GY - 330)
    bubble_ml(ctx, 470, 1100, ["I can't see", "a thing!"], 44, ramp(t, 1.6, 1.8), (545, GY - 390))
    header(ctx, ease(t / 0.2 + 1), "THE FAMOUS PAINTING", "Leo queued 2 hours.", "He can see… phones.", -0.3, t, main_size=56)
    meter(ctx, "PAINTING VISIBLE", "0%"); wm(ctx)

def s1(ctx, t, d):
    gallery(ctx, t, art_y=920)
    rope(ctx, 300, 780, 1360)
    crowd_wall(ctx, t, rate=1.4)
    jumping = 0.2 < t < 2.4
    jy = 120 * abs(math.sin(t * 5.0)) if jumping else 0
    lx = 760
    kid(ctx, lx, GY - jy, 0.95, t, "smile" if jumping else "flat", (0, -470) if jumping else (-20, -200))
    if jumping: phone(ctx, lx, GY - jy - 470 * 0.95 - 30, 0.0, 1.0 if (int(t * 10) % 3 == 0) else 0.0, 0.95)
    # Wren slips away to the right at the start
    wx = lerp(960, 1350, ramp(t, 0.9, 2.0))
    if wx < 1300:
        wren(ctx, wx, GY, 1.0, t, "wave" if t < 0.9 else "point", expr="happy", hand=(150, -330))
    bubble_ml(ctx, 560, 1080, ["Back in a", "minute, love."], 40, ramp(t, 0.1, 0.3) * (1 - ramp(t, 1.1, 1.25)), (900, GY - 700))
    photos = int(214 * ramp(t, 0.3, 2.4))
    phone_inset(ctx, ramp(t, 2.5, 2.8), 20, t)
    bubble_ml(ctx, 790, 790, ["214 photos of", "the back of heads."], 38, ramp(t, 3.0, 3.2), (lx + 10, GY - 390))
    header(ctx, ease(t / 0.2), "PLAN B", "Jump. Phone up. Click.", "Zero painting.", 1.6, t, main_size=56)
    meter(ctx, "PHOTOS TAKEN", "%d" % photos); wm(ctx)

def s2(ctx, t, d):
    gallery(ctx, t, art=True, art_y=920)
    crowd_wall(ctx, t, base=1420, rate=1.0)
    wx = lerp(1250, 250, ramp(t, 0.0, 0.8))
    hand = (150, -330)
    wren(ctx, wx, GY, 1.05, t, "point", expr="happy", hand=hand)
    hx, hy = wx + 150 * 1.05, GY - 330 * 1.05
    un = ramp(t, 1.0, 1.6)
    pw = 380
    poster(ctx, hx + 10, hy - 260, pw, max(0.03, un))
    if 1.6 < t < 2.0: burst(ctx, hx + 10 + pw / 2, hy - 260 + pw * 0.6, 1 - (t - 1.6) / 0.4, 300)
    kid(ctx, 960, GY, 0.9, t, "flat" if t < 1.7 else "smile", (-20, -200))
    bubble_ml(ctx, 790, 1020 - 60, ["It's… a duck?!"], 44, ramp(t, 1.9, 2.1) * (1 - ramp(t, 2.9, 3.05)), (950, GY - 360))
    bubble_ml(ctx, 330, 760, ["A very famous", "duck, love."], 42, ramp(t, 3.0, 3.2), (250, GY - 720))
    header(ctx, ease(t / 0.2), "WREN'S TURN", "Gift shop. $12 poster.", "Full view. No elbows.", 1.4, t, main_size=56)
    meter(ctx, "PAINTING VISIBLE", "%d%%" % int(100 * un)); wm(ctx)

def s3(ctx, t, d):
    gallery(ctx, t, art=True, art_x=110, art_w=300)
    bench(ctx, 780, 1480)
    # Wren stands on the bench, holding the poster up beside her
    wy = 1460
    wren(ctx, 700, wy, 0.95, t, "point", expr="happy" if t < 2.5 else "shock", hand=(150, -380))
    hx, hy = 700 + 150 * 0.95, wy - 380 * 0.95
    poster(ctx, hx - 10, hy - 200, 230, 1.0)
    # the crowd has turned round: phones aimed at Wren, flashes going off
    turn = ramp(t, 0.3, 1.0)
    rate = 1.0 + 2.0 * ramp(t, 1.0, 2.0)
    n_on = int(lerp(0, 8, turn))
    for k, (x, s) in enumerate([(470, 0.9), (1010, 0.95), (600, 1.02), (880, 1.05), (760, 1.1), (1080, 0.85), (520, 1.12), (980, 1.15)]):
        if k >= n_on: continue
        ax = (700 - x) / s * 0.35; aim = (ax, -620)
        tourist_back(ctx, x, 1760 if s > 1.0 else 1700, s, k + 2, t, aim=aim, flash=tourist_flash(t, k, rate))
    # Leo alone at the real painting
    kid(ctx, 260, GY, 0.95, t, "smile" if t < 1.3 else "smug", (-10, -200))
    bubble_ml(ctx, 300, 1130, ["Best view ever!"], 42, ramp(t, 1.4, 1.6), (270, GY - 380))
    bubble_ml(ctx, 820, 700, ["No flash, please."], 42, ramp(t, 2.6, 2.8), (690, wy - 690))
    header(ctx, ease(t / 0.2), "PLOT TWIST", "The crowd turns around.", "Leo gets the duck.", 1.0, t, main_size=56)
    meter(ctx, "PHONES POINTED AT WREN", "%d" % int(38 * ramp(t, 0.3, 2.2))); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 420, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    ctx.save(); ctx.translate(820, 1300); ctx.rotate(0.06 * math.sin(t * 2)); poster(ctx, -130, -160, 260, 1.0); ctx.restore()
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “The gift shop has the best view.”", 205 - (1 - a) * 20, 44, hexc('#22223b', a), maxw=1000)
    ctext(ctx, "Leo: “Now SHE's the famous painting.”", 290, 44, hexc(RED, ease((t - 0.5) / 0.3)), maxw=1000)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Crowd or gift shop? Comment below!", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 2.5), (s1, 0.6), (s1, 1.8), (s1, 3.6), (s2, 0.5), (s2, 1.3), (s2, 2.4), (s2, 3.9), (s3, 0.6), (s3, 2.0), (s3, 3.6), (s4, 0.2), (s4, 2.6)]
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

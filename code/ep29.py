"""ep29 - Hotel corridor at night: Leo's key card flashes red. He blows on it, presses it to his forehead, makes 4 trips to reception. Then the door opens from the inside. Wren reads the sleeve: their room is 412, Leo was at 421. Green, first try."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep29"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; GREEN = '#2ecc71'; WOOD = '#7a4b2a'; WOOD_D = '#5a3720'; BRASS = '#d4a843'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1600                         # characters' ground line (kept above the @wrentrips watermark)
FLOOR = 1440                      # wall meets carpet
D1 = (110, 430)                   # door 421 (left) x-range
D2 = (650, 970)                   # door 412 (right) x-range
DTOP = 740

def meter(ctx, label, val, a=1.0, col='#ffd166'):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc(col, a)); ctx.show_text(val)

def ftext(ctx, s, x, y, size, col, maxw, bold=True, center=False):
    mv.font(ctx, size, bold); e = ctx.text_extents(s)
    while e.x_advance > maxw and size > 12:
        size -= 1; mv.font(ctx, size, bold); e = ctx.text_extents(s)
    ctx.move_to(x - (e.x_advance / 2 if center else 0), y); ctx.set_source_rgba(*col); ctx.show_text(s)

# ------------------------------------------------------------ background: hotel corridor at night
def sconce(ctx, x, y, t):
    g = cairo.RadialGradient(x, y, 10, x, y, 190); g.add_color_stop_rgba(0, 1, 0.86, 0.55, 0.55); g.add_color_stop_rgba(1, 1, 0.86, 0.55, 0)
    ctx.arc(x, y, 190, 0, 2 * math.pi); ctx.set_source(g); ctx.fill()
    rrect(ctx, x - 8, y + 10, 16, 50, 6); ctx.set_source_rgba(*hexc(BRASS)); ctx.fill()
    ctx.move_to(x - 36, y + 14); ctx.line_to(x + 36, y + 14); ctx.line_to(x + 24, y - 40); ctx.line_to(x - 24, y - 40); ctx.close_path()
    ctx.set_source_rgba(*hexc('#fff1cf')); ctx.fill()

def door(ctx, x0, x1, num, t, led=None, open_k=0.0, dnd=False, room_light=False):
    w = x1 - x0; h = FLOOR - DTOP
    rrect(ctx, x0 - 18, DTOP - 18, w + 36, h + 18, 6); ctx.set_source_rgba(*hexc(WOOD_D)); ctx.fill()     # frame
    if open_k > 0:
        # dark (or lamp-lit) room behind
        ctx.rectangle(x0, DTOP, w, h); ctx.set_source_rgba(*hexc('#2b2440')); ctx.fill()
        if room_light:
            g = cairo.RadialGradient(x0 + w * 0.7, DTOP + 260, 10, x0 + w * 0.7, DTOP + 260, 320)
            g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.9); g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0.0)
            ctx.rectangle(x0, DTOP, w, h); ctx.set_source(g); ctx.fill()
            rrect(ctx, x0 + 40, DTOP + 420, w - 80, 120, 16); ctx.set_source_rgba(*hexc('#f7f1e3')); ctx.fill()     # bed
            rrect(ctx, x0 + 60, DTOP + 396, 90, 40, 14); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
            rrect(ctx, x0 + 40, DTOP + 470, w - 80, 70, 12); ctx.set_source_rgba(*hexc('#c0392b')); ctx.fill()
        # door slab swung inward (narrow parallelogram on hinge side = left)
        sw = w * (1 - open_k * 0.82)
        ctx.move_to(x0, DTOP); ctx.line_to(x0 + sw, DTOP + 40 * open_k); ctx.line_to(x0 + sw, FLOOR - 30 * open_k); ctx.line_to(x0, FLOOR); ctx.close_path()
        ctx.set_source_rgba(*hexc(WOOD)); ctx.fill()
        return
    ctx.rectangle(x0, DTOP, w, h); ctx.set_source_rgba(*hexc(WOOD)); ctx.fill()
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc(WOOD_D))
    rrect(ctx, x0 + 40, DTOP + 50, w - 80, 250, 10); ctx.stroke()
    rrect(ctx, x0 + 40, DTOP + 350, w - 80, 300, 10); ctx.stroke()
    # number plate
    rrect(ctx, x0 + w / 2 - 70, DTOP + 120, 140, 70, 12); ctx.set_source_rgba(*hexc(BRASS)); ctx.fill()
    ftext(ctx, num, x0 + w / 2, DTOP + 172, 46, hexc('#3b2a10'), 120, center=True)
    circle(ctx, x0 + w / 2, DTOP + 240, 9, hexc('#222222'))                                               # peephole
    # lever handle + key card reader
    rrect(ctx, x1 - 70, DTOP + 470, 70, 18, 9); ctx.set_source_rgba(*hexc('#c9c9c9')); ctx.fill()
    rrect(ctx, x1 - 66, DTOP + 380, 40, 70, 8); ctx.set_source_rgba(*hexc('#1b1b2f')); ctx.fill()
    lc = {'red': '#ff3b3b', 'green': GREEN}.get(led, '#55556a')
    if led: circle(ctx, x1 - 46, DTOP + 400, 18, hexc(lc, 0.35))
    circle(ctx, x1 - 46, DTOP + 400, 9, hexc(lc))
    if dnd:
        sw_ = 0.08 * math.sin(t * 3)
        ctx.save(); ctx.translate(x1 - 40, DTOP + 470); ctx.rotate(sw_); ctx.scale(0.75, 0.75)
        rrect(ctx, -60, 20, 120, 190, 12); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
        circle(ctx, 0, 42, 16, hexc(WOOD))
        for i, ln in enumerate(("DO", "NOT", "DISTURB")): ftext(ctx, ln, 0, 100 + i * 34, 26, (1, 1, 1, 1), 100, center=True)
        ctx.restore()

def corridor(ctx, t, d1="closed", d2_led=None, d2_open=0.0, d1_led=None, d1_open=0.0, dnd=False):
    ctx.rectangle(0, 0, W, FLOOR); ctx.set_source_rgba(*hexc('#e8d3a8')); ctx.fill()                    # wallpaper
    for k in range(0, W, 90):
        ctx.rectangle(k, 0, 40, FLOOR); ctx.set_source_rgba(*hexc('#dcc38f')); ctx.fill()
    for k in range(12):
        for r in range(9): circle(ctx, k * 90 + 65, 90 + r * 150 + (k % 2) * 75, 6, hexc('#c9a86a'))
    ctx.rectangle(0, 0, W, 120); ctx.set_source_rgba(*hexc('#3d2b22')); ctx.fill()                      # cornice
    ctx.rectangle(0, 120, W, 16); ctx.set_source_rgba(*hexc(BRASS)); ctx.fill()
    ctx.rectangle(0, 1300, W, FLOOR - 1300); ctx.set_source_rgba(*hexc('#6b4226')); ctx.fill()         # wainscot
    ctx.rectangle(0, 1296, W, 10); ctx.set_source_rgba(*hexc(BRASS)); ctx.fill()
    sconce(ctx, 540, 820, t); sconce(ctx, -40, 820, t); sconce(ctx, W + 40, 820, t)
    door(ctx, D1[0], D1[1], "421", t, led=d1_led, open_k=d1_open, dnd=dnd)
    door(ctx, D2[0], D2[1], "412", t, led=d2_led, open_k=d2_open, room_light=True)
    # carpet
    ctx.rectangle(0, FLOOR, W, H - FLOOR); ctx.set_source_rgba(*hexc('#8e1f2f')); ctx.fill()
    ctx.rectangle(0, FLOOR, W, 14); ctx.set_source_rgba(*hexc('#3d2b22')); ctx.fill()
    for r in range(5):
        y = FLOOR + 70 + r * 100
        for k in range(10):
            x = k * 120 + (r % 2) * 60
            ctx.move_to(x, y - 22); ctx.line_to(x + 22, y); ctx.line_to(x, y + 22); ctx.line_to(x - 22, y); ctx.close_path()
            ctx.set_source_rgba(*hexc('#d4a843', 0.55)); ctx.fill()

def card(ctx, x, y, ang=0.0, s=1.0, col='#ffffff'):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    rrect(ctx, -36, -24, 72, 48, 6); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    ctx.rectangle(-36, -10, 72, 12); ctx.set_source_rgba(*hexc('#1d5fa8')); ctx.fill()
    ctx.set_line_width(2); ctx.set_source_rgba(0, 0, 0, 0.25); rrect(ctx, -36, -24, 72, 48, 6); ctx.stroke()
    ctx.restore()

def red_flash(ctx, x, y, t, t0):
    if t0 <= t < t0 + 0.45:
        a = 1 - (t - t0) / 0.45
        circle(ctx, x, y, 30 + 60 * (1 - a), (1, 0.2, 0.2, 0.5 * a))
        ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(1, 0.2, 0.2, a)
        ctx.move_to(x + 40, y - 70); ctx.line_to(x + 80, y - 30); ctx.move_to(x + 80, y - 70); ctx.line_to(x + 40, y - 30); ctx.stroke()

def guest(ctx, x, gy, s, t, glare=1.0):
    """Sleepy fictional guest in a bathrobe with a sleep mask pushed up."""
    ctx.save(); ctx.translate(x, gy); ctx.scale(s, s)
    for dx in (-30, 30): e4.ell(ctx, dx, -10, 40, 16, hexc('#9aa5b1'))                     # slippers
    ctx.move_to(-110, -470); ctx.line_to(110, -470); ctx.line_to(130, -30); ctx.line_to(-130, -30); ctx.close_path()
    ctx.set_source_rgba(*hexc('#f4f4f6')); ctx.fill()
    ctx.move_to(-60, -470); ctx.line_to(0, -360); ctx.line_to(60, -470); ctx.close_path(); ctx.set_source_rgba(*hexc('#e0ac85')); ctx.fill()
    ctx.set_line_width(10); ctx.set_source_rgba(*hexc('#d6d6dc')); ctx.move_to(-60, -470); ctx.line_to(10, -200); ctx.move_to(60, -470); ctx.line_to(-10, -200); ctx.stroke()
    rrect(ctx, -125, -260, 250, 26, 10); ctx.set_source_rgba(*hexc('#4361ee')); ctx.fill()          # belt
    # arms crossed
    rrect(ctx, -120, -400, 240, 64, 30); ctx.set_source_rgba(*hexc('#e9e9ee')); ctx.fill()
    circle(ctx, -96, -368, 22, hexc('#e0ac85')); circle(ctx, 96, -368, 22, hexc('#e0ac85'))
    # head
    hy = -560
    circle(ctx, 0, hy, 82, hexc('#e0ac85'))
    rnd = random.Random(7)
    for k in range(9):
        a = math.pi + k * math.pi / 8; circle(ctx, math.cos(a) * 78, hy + math.sin(a) * 74 - 10, 28 + rnd.uniform(-4, 8), hexc('#8d8d99'))
    rrect(ctx, -84, hy - 64, 168, 38, 16); ctx.set_source_rgba(*hexc('#ff8fab')); ctx.fill()     # sleep mask on forehead
    for ex in (-38, 38): e4.ell(ctx, ex, hy - 45, 26, 12, hexc('#ffc2d1'))
    for ex in (-30, 30): circle(ctx, ex, hy + 6, 7, hexc('#22223b'))
    ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#4a4a55'))
    ctx.move_to(-48, hy - 16 + 0 * glare); ctx.line_to(-14, hy - 6 + 4 * glare); ctx.stroke()
    ctx.move_to(48, hy - 16); ctx.line_to(14, hy - 6 + 4 * glare); ctx.stroke()
    ctx.set_line_width(6); ctx.arc(0, hy + 52, 18, math.radians(200), math.radians(340)); ctx.stroke()
    ctx.restore()

def sleeve_inset(ctx, a):
    """Wren's key-card sleeve: the receptionist's handwriting."""
    if a <= 0: return
    ctx.save(); ctx.translate(0, (1 - a) * 40)
    x, y, w, h = 260, 640, 560, 330
    rrect(ctx, x, y, w, h, 24); ctx.set_source_rgba(*hexc('#fdf6e3', a)); ctx.fill()
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc(BRASS, a)); rrect(ctx, x + 14, y + 14, w - 28, h - 28, 18); ctx.stroke()
    ftext(ctx, "GRAND HOTEL  ·  WELCOME", x + w / 2, y + 70, 28, hexc('#8a6d3b', a), w - 80, center=True)
    ftext(ctx, "YOUR ROOM", x + w / 2, y + 140, 34, hexc('#22223b', a), w - 80, center=True)
    ftext(ctx, "412", x + w / 2, y + 270, 120, hexc(RED, a), w - 80, center=True)
    ctx.restore()

def card_pile(ctx, x, y, n):
    for k in range(n):
        card(ctx, x + (k % 3) * 18 - 18, y - k * 9, (k * 0.7) % 0.6 - 0.3, 0.9)

# ------------------------------------------------------------ scenes
LX = 230; RX = (D1[1] - 46, DTOP + 400)      # Leo's spot and door-421 reader
def leo_at_reader(ctx, t, expr):
    kid(ctx, LX, GY, 0.95, t, expr, ((RX[0] - LX) / 0.95 - 10, (RX[1] - GY) / 0.95 + 26))

def s0(ctx, t, d):
    taps = (0.5, 1.5, 2.5)
    corridor(ctx, t, d1_led='red' if any(tp <= t < tp + 0.45 for tp in taps) else None)
    wren(ctx, 650, GY, 1.0, t, "point", expr="happy", hand=(-40, -230))
    card(ctx, 650 - 40, GY - 230 - 20, 0.2, 0.9)                                       # Wren holds her sleeve casually
    leo_at_reader(ctx, t, "smug" if t < 1.5 else "flat")
    card(ctx, RX[0] - 8, RX[1] + 30, -0.3, 1.0)
    for tp in taps: red_flash(ctx, RX[0], RX[1], t, tp)
    bubble_ml(ctx, 260, 960, ["Come ON!"], 44, ramp(t, 2.6, 2.8), (240, GY - 360))
    n = sum(1 for tp in taps if t >= tp)
    header(ctx, ease(t / 0.2 + 1), "HOTEL KEY CARDS", "Leo's key card won't work.", "Red light. Every time.", -0.3, t, main_size=56)
    meter(ctx, "ATTEMPTS", "%d" % max(1, n)); wm(ctx)

def s1(ctx, t, d):
    flashes = (0.9, 2.1, 3.3)
    corridor(ctx, t, d1_led='red' if any(tp <= t < tp + 0.45 for tp in flashes) else None)
    wren(ctx, 650, GY, 1.0, t, "point", expr="happy", hand=(-40, -230))
    card(ctx, 610, GY - 250, 0.2, 0.9)
    n_cards = 1 + int(clamp01(t / 3.6) * 4.99)
    card_pile(ctx, 420, GY - 20, n_cards)
    if t < 1.2:                                  # trick 1: blow on the card
        kid(ctx, LX, GY, 0.95, t, "flat", (20, -300))
        card(ctx, LX + 20, GY - 300, 0.1, 1.0)
        for k in range(3):
            ph = (t * 2 + k / 3) % 1; circle(ctx, LX + 30 + ph * 60, GY - 290 - ph * 30, 8 + 10 * ph, (1, 1, 1, 0.7 * (1 - ph)))
        label = "Blow on it"
    elif t < 2.4:                                # trick 2: forehead
        kid(ctx, LX, GY, 0.95, t, "flat", (0, -330))
        card(ctx, LX, GY - 352, 0.0, 0.9)
        label = "Forehead scan"
    else:                                        # trick 3: angry fast swipe
        leo_at_reader(ctx, t, "flat")
        for k in range(4):
            ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.8); ctx.move_to(RX[0] - 90 - k * 10, RX[1] + 10 + k * 14); ctx.line_to(RX[0] - 30 - k * 10, RX[1] + 10 + k * 14); ctx.stroke()
        card(ctx, RX[0] - 8, RX[1] + 30, -0.3, 1.0)
        label = "Swipe it angrily"
    for tp in flashes: red_flash(ctx, RX[0], RX[1], t, tp)
    # little trick label above Leo
    a = 1.0 if t > 0.1 else t / 0.1
    mv.font(ctx, 34); e = ctx.text_extents(label)
    rrect(ctx, LX - e.x_advance / 2 - 26, 1000, e.x_advance + 52, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.85 * a)); ctx.fill()
    ftext(ctx, label, LX, 1042, 34, (1, 1, 1, a), 400, center=True)
    header(ctx, ease(t / 0.2), "PLAN B, C, D...", "4 trips to reception.", "5 new cards. All red.", 1.4, t, main_size=56)
    meter(ctx, "NEW KEY CARDS", "%d" % n_cards); wm(ctx)

def s2(ctx, t, d):
    op = ramp(t, 0.6, 1.1)
    corridor(ctx, t, d1_open=op)
    if op > 0.05:
        guest(ctx, (D1[0] + D1[1]) / 2 + 20, FLOOR + 40, 0.92, t)
    if 0.6 < t < 1.0: burst(ctx, (D1[0] + D1[1]) / 2, 1000, 1 - (t - 0.6) / 0.4, 220)
    kid(ctx, 520, GY, 0.95, t, "smile" if t < 0.6 else "flat", (40, -200))
    card(ctx, 560, GY - 200, 0.3, 1.0)
    wren(ctx, 800, GY, 1.0, t, "point", expr="happy" if t < 0.7 else "shock", hand=(-40, -230))
    card(ctx, 760, GY - 250, 0.2, 0.9)
    bubble_ml(ctx, 290, 790, ["Do you know", "what time it is?"], 42, ramp(t, 1.4, 1.6), (300, 930))
    header(ctx, ease(t / 0.2), "THEN THE DOOR OPENS", "From the inside.", "It's not their room.", 1.8, t, main_size=56)
    meter(ctx, "LEO'S DIGNITY", "%d%%" % int(100 - 100 * ramp(t, 0.8, 2.6)), col=RED); wm(ctx)

def s3(ctx, t, d):
    unlock = 2.0
    corridor(ctx, t, dnd=True, d2_led='green' if t >= unlock else None, d2_open=ramp(t, unlock + 0.4, unlock + 1.0))
    kid(ctx, 220, GY, 0.95, t, "flat", (0, -170))
    card_pile(ctx, 420, GY - 20, 5)
    hx = lerp(-40, 250, ramp(t, 1.4, 1.9)); hy = lerp(-230, -400, ramp(t, 1.4, 1.9))
    wren(ctx, 640, GY, 1.0, t, "point", expr="happy", hand=(hx, hy))
    card(ctx, 640 + hx + 10, GY + hy - 20, 0.2, 0.9)
    if unlock <= t < unlock + 0.5: burst(ctx, D2[1] - 46, DTOP + 400, 1 - (t - unlock) / 0.5, 120)
    sleeve_inset(ctx, ramp(t, 0.2, 0.5) * (1 - ramp(t, 1.3, 1.5)))
    bubble_ml(ctx, 620, 770, ["412, love. Not 421."], 40, ramp(t, 1.5, 1.7) * (1 - ramp(t, 2.9, 3.0)), (640, 860))
    bubble_ml(ctx, 250, 1030, ["Don't tell Mum."], 40, ramp(t, 3.0, 3.2), (230, GY - 360))
    header(ctx, ease(t / 0.2), "WREN READS THE SLEEVE", "Room 412. Not 421.", "Green. First try.", unlock, t, main_size=56)
    meter(ctx, "WREN'S ATTEMPTS", "1", col=GREEN); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 420, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    # stack of red-light cards vs one green-light card
    card_pile(ctx, 800, 1600, 5)
    ctx.save(); ctx.translate(820, 1360 + 10 * math.sin(t * 3)); ctx.scale(1.5, 1.5)
    rrect(ctx, -50, -80, 100, 150, 14); ctx.set_source_rgba(*hexc('#1b1b2f')); ctx.fill()
    circle(ctx, 0, -40, 34, hexc(GREEN, 0.35)); circle(ctx, 0, -40, 18, hexc(GREEN))
    ctx.restore()
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “Right card. Wrong door.”", 205 - (1 - a) * 20, 50, hexc('#22223b', a), maxw=1000)
    ctext(ctx, "Leo: “Reception knows my name now.”", 290, 44, hexc(RED, ease((t - 0.5) / 0.3)), maxw=1000)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Ever tried the wrong hotel door? Comment below!", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 2.7), (s1, 0.6), (s1, 1.8), (s1, 3.4), (s2, 0.3), (s2, 1.2), (s2, 2.6), (s2, 4.0), (s3, 0.8), (s3, 1.8), (s3, 2.6), (s3, 3.6), (s4, 2.6)]
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

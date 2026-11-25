"""ep30 - Old-town walking tour: the guide says 'Follow the yellow umbrella.' There are 7 of them. Leo joins a wrong tour, a wedding photo, and a man with his own rain cloud. Lost. Then a pineapple on a stick rises above the crowd: Wren brought her own flag. 38 strangers follow her too."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep30"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; YEL = '#ffd60a'; YEL_D = '#e0b400'; GREEN = '#2ecc71'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1600                         # main characters' ground line (watermark sits below / left of it)
CROWD_GY = 1450                   # background crowd ground line

def meter(ctx, label, val, a=1.0, col='#ffd166'):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc(col, a)); ctx.show_text(val)

def ftext(ctx, s, x, y, size, col, maxw, bold=True, center=False):
    mv.font(ctx, size, bold); e = ctx.text_extents(s)
    while e.x_advance > maxw and size > 12:
        size -= 1; mv.font(ctx, size, bold); e = ctx.text_extents(s)
    ctx.move_to(x - (e.x_advance / 2 if center else 0), y); ctx.set_source_rgba(*col); ctx.show_text(s)

# ------------------------------------------------------------ background: sunny old-town piazza
FACADES = [(-40, 250, 640, '#e9b872'), (210, 230, 700, '#d9764a'), (440, 220, 600, '#f2a7a0'),
           (660, 220, 680, '#f6d37a'), (880, 260, 620, '#b5c99a')]
def piazza(ctx, t):
    mv.vgrad(ctx, '#7cc8f5', '#e6f6ff')
    circle(ctx, 930, 640, 70, hexc('#fff3b0'))
    rnd = random.Random(30)
    for x0, w, top, col in FACADES:
        ctx.rectangle(x0, top, w, 1400 - top); ctx.set_source_rgba(*hexc(col)); ctx.fill()
        ctx.rectangle(x0 - 8, top - 22, w + 16, 30); ctx.set_source_rgba(*hexc('#8a5a3b')); ctx.fill()     # cornice
        for r in range(4):
            wy = top + 60 + r * 160
            if wy > 1180: break
            for c in range(2):
                wx = x0 + 40 + c * (w - 120) / 1
                if wx + 60 > x0 + w: continue
                rrect(ctx, wx, wy, 60, 96, 26); ctx.set_source_rgba(*hexc('#3d3a4b')); ctx.fill()
                ctx.rectangle(wx - 18, wy + 10, 16, 86); ctx.rectangle(wx + 62, wy + 10, 16, 86)
                ctx.set_source_rgba(*hexc('#3f7d5a')); ctx.fill()                                                # shutters
                if rnd.random() < 0.35:                                                                            # flower box
                    ctx.rectangle(wx - 10, wy + 96, 80, 14); ctx.set_source_rgba(*hexc('#8a5a3b')); ctx.fill()
                    for k in range(4): circle(ctx, wx - 2 + k * 22, wy + 92, 9, hexc(rnd.choice(('#e63946', '#ff8fab', '#ffffff'))))
    # cafe awning on the right
    for k in range(6):
        ctx.rectangle(860 + k * 40, 1180, 40, 70); ctx.set_source_rgba(*hexc('#e63946' if k % 2 == 0 else '#ffffff')); ctx.fill()
    for k in range(6):
        ctx.arc(880 + k * 40, 1250, 20, 0, math.pi); ctx.set_source_rgba(*hexc('#e63946' if k % 2 == 0 else '#ffffff')); ctx.fill()
    # bunting across the square
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#5c4033')); ctx.move_to(0, 760); ctx.curve_to(300, 850, 760, 850, W, 760); ctx.stroke()
    for k in range(14):
        u = (k + 0.5) / 14; x = u * W; y = 760 + 4 * 90 * u * (1 - u) * 0.95 + 4
        ctx.move_to(x - 20, y); ctx.line_to(x + 20, y); ctx.line_to(x, y + 44 + 4 * math.sin(t * 4 + k)); ctx.close_path()
        ctx.set_source_rgba(*hexc(('#e63946', '#ffd60a', '#4361ee', '#2ecc71')[k % 4])); ctx.fill()
    # cobbles
    ctx.rectangle(0, 1380, W, H - 1380); ctx.set_source_rgba(*hexc('#cdb79e')); ctx.fill()
    for r in range(11):
        y = 1400 + r * 48
        for k in range(16):
            x = k * 72 + (r % 2) * 36
            e4.ell(ctx, x, y, 30, 15, hexc('#bea283'))

# ------------------------------------------------------------ props & extras (all fictional)
def umbrella(ctx, x, y, r=100, col=YEL, closed=False):
    if closed:
        ctx.move_to(x, y - 30); ctx.line_to(x - 18, y + 120); ctx.line_to(x + 18, y + 120); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
        return
    ctx.move_to(x - r, y)
    ctx.arc(x, y, r, math.pi, 0)
    n = 4; sw = 2 * r / n
    for k in range(n):
        cx = x + r - sw * (k + 0.5); ctx.arc(cx, y, sw / 2, 0, math.pi)                   # scalloped edge
    ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc(YEL_D))
    for k in (-0.5, 0.5): ctx.move_to(x, y - r); ctx.curve_to(x + k * r * 0.6, y - r * 0.6, x + k * r * 0.5, y - 10, x + k * r, y); ctx.stroke()
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#3b3b3b')); ctx.move_to(x, y - r); ctx.line_to(x, y - r - 22); ctx.stroke()

def rain_cloud(ctx, x, y, t):
    for dx, dy, r in ((-60, 10, 44), (0, -14, 58), (60, 10, 44), (-20, 26, 40), (30, 26, 40)): circle(ctx, x + dx, y + dy, r, hexc('#8d99ae'))
    ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#4cc9f0'))
    for k in range(7):
        ph = (t * 2.4 + k * 0.37) % 1; dx = -80 + k * 27
        ctx.move_to(x + dx, y + 60 + ph * 90); ctx.line_to(x + dx - 4, y + 82 + ph * 90); ctx.stroke()

def pineapple(ctx, x, y, s=1.0, ang=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    for k, a in enumerate((-0.6, -0.3, 0.0, 0.3, 0.6)):                                     # crown
        ctx.save(); ctx.rotate(a); ctx.move_to(-14, -50); ctx.line_to(0, -130 + abs(a) * 60); ctx.line_to(14, -50); ctx.close_path()
        ctx.set_source_rgba(*hexc('#2d9a4b' if k % 2 else '#3cb95b')); ctx.fill(); ctx.restore()
    e4.ell(ctx, 0, 10, 52, 70, hexc('#f4a224'))
    ctx.new_path(); ctx.save(); ctx.translate(0, 10); ctx.scale(52, 70); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore(); ctx.clip()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#c06d12'))
    for k in range(-6, 7):
        ctx.move_to(-80 + k * 26, -80); ctx.line_to(80 + k * 26, 100); ctx.move_to(80 + k * 26, -80); ctx.line_to(-80 + k * 26, 100)
    ctx.stroke(); ctx.reset_clip()
    ctx.restore()

def pineapple_flag(ctx, hx, hy, t, length=300):
    ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#8a5a3b'))
    ctx.move_to(hx, hy + 30); ctx.line_to(hx, hy - length); ctx.stroke()
    pineapple(ctx, hx, hy - length - 50, 0.9, 0.08 * math.sin(t * 5))

PALETTE = [('#4361ee', '#5a3825', '#f1c27d'), ('#2a9d8f', '#d9b26f', '#e0ac85'), ('#f77f00', '#2b2b2b', '#8d5524'),
           ('#9d4edd', '#a0a0a0', '#f1c27d'), ('#06d6a0', '#3d2b1f', '#c68642'), ('#ef476f', '#7a4b2a', '#e0ac85'),
           ('#118ab2', '#e3c16f', '#ffdbac'), ('#8338ec', '#1d1d1d', '#a1665e')]
def tourist(ctx, x, gy, s, t, pal=0, umb=None, hat=False, kind="plain", seed=0, umb_up=1.0):
    """Generic cartoon tourist. umb: None / 'open' / 'closed'. kind: plain / bride / camera."""
    body, hair, skin = PALETTE[pal % len(PALETTE)]
    if kind == "bride": body, hair = '#ffffff', '#6b4226'
    ctx.save(); ctx.translate(x, gy); ctx.scale(s, s); ctx.translate(0, 3 * math.sin(t * 6 + seed))
    ctx.save(); ctx.scale(1, 0.2); circle(ctx, 0, 0, 90, (0, 0, 0, 0.12)); ctx.restore()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if kind == "bride":
        ctx.move_to(-50, -300); ctx.line_to(50, -300); ctx.line_to(110, -10); ctx.line_to(-110, -10); ctx.close_path()
        ctx.set_source_rgba(*hexc('#ffffff')); ctx.fill()
        ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#d8d8e0')); ctx.stroke()
    else:
        ctx.set_line_width(30); ctx.set_source_rgba(*hexc('#3d405b'))
        for lx in (-26, 26): ctx.move_to(lx, -140); ctx.line_to(lx, -22); ctx.stroke()
        for lx in (-26, 26): e4.ell(ctx, lx + (6 if lx > 0 else -6), -12, 28, 13, hexc('#2b2d42'))
        rrect(ctx, -62, -310, 124, 190, 36); ctx.set_source_rgba(*hexc(body)); ctx.fill()
    # left arm down
    ctx.set_line_width(26); ctx.set_source_rgba(*hexc(body if kind != "bride" else '#f6e7d8'))
    ctx.move_to(-56, -285); ctx.line_to(-74, -170); ctx.stroke(); circle(ctx, -74, -165, 15, hexc(skin))
    if kind == "camera":
        rrect(ctx, -30, -250, 60, 42, 8); ctx.set_source_rgba(*hexc('#2b2d42')); ctx.fill(); circle(ctx, 0, -229, 13, hexc('#8ecae6'))
    # right arm: up with umbrella or down
    if umb:
        hx, hy = 80, -470 + (1 - umb_up) * 220
        ctx.set_line_width(26); ctx.set_source_rgba(*hexc(body if kind != "bride" else '#f6e7d8'))
        ctx.move_to(56, -285); ctx.line_to(hx, hy); ctx.stroke(); circle(ctx, hx, hy, 15, hexc(skin))
        ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#3b3b3b'))
        if umb == "open":
            ctx.move_to(hx, hy + 20); ctx.line_to(hx, hy - 190); ctx.stroke()
            umbrella(ctx, hx, hy - 190, 100)
        else:
            umbrella(ctx, hx, hy - 120, closed=True)
    else:
        ctx.set_line_width(26); ctx.set_source_rgba(*hexc(body))
        ctx.move_to(56, -285); ctx.line_to(74, -170); ctx.stroke(); circle(ctx, 74, -165, 15, hexc(skin))
    # head
    hy = -370
    circle(ctx, 0, hy, 56, hexc(skin))
    ctx.arc(0, hy - 8, 58, math.pi * 1.05, math.pi * 1.95); ctx.close_path(); ctx.set_source_rgba(*hexc(hair)); ctx.fill()
    if hat:
        e4.ell(ctx, 0, hy - 46, 84, 16, hexc('#f4e3b5')); ctx.arc(0, hy - 46, 50, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc('#f4e3b5')); ctx.fill()
        ctx.rectangle(-50, hy - 62, 100, 12); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    if kind == "bride":
        ctx.move_to(-40, hy - 50); ctx.curve_to(-120, hy + 40, -110, hy + 200, -70, hy + 260); ctx.line_to(-46, hy + 40); ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.8); ctx.fill()
        for k in range(5): circle(ctx, -36 + k * 18, hy - 56, 8, hexc('#ffb3c6'))
    for ex in (-20, 20): circle(ctx, ex, hy + 2, 6, hexc('#2b2d42'))
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#7a3e2b')); ctx.arc(0, hy + 20, 16, math.radians(25), math.radians(155)); ctx.stroke()
    ctx.restore()

# background crowd: (x, palette, hat, seed)
CROWD = [(60, 0, False, 1), (200, 3, True, 2), (330, 5, False, 3), (470, 1, True, 4), (610, 6, False, 5),
         (750, 2, True, 6), (880, 7, False, 7), (1020, 4, True, 8)]
def crowd(ctx, t, umb_at=None, umb_kind="open", shift=0.0, only=None):
    for i, (x, pal, hat, seed) in enumerate(CROWD):
        if only is not None and i not in only: continue
        u = None
        if umb_at is not None and umb_at[i] is not None and t >= umb_at[i]:
            u = umb_kind
        up = ramp(t, umb_at[i], umb_at[i] + 0.25) if u and umb_at[i] is not None else 1.0
        tourist(ctx, x + shift * (1 if x < 760 else 0.4), CROWD_GY, 0.72, t, pal, umb=u, hat=hat, seed=seed, umb_up=up)
        if u == "open" and umb_at[i] is not None and 0 <= t - umb_at[i] < 0.3:
            burst(ctx, x + 0.72 * 80, CROWD_GY - 0.72 * 760, 1 - (t - umb_at[i]) / 0.3, 70)

def label_chip(ctx, label, x, y, a=1.0):
    mv.font(ctx, 34); e = ctx.text_extents(label)
    rrect(ctx, x - e.x_advance / 2 - 26, y - 42, e.x_advance + 52, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.88 * a)); ctx.fill()
    ftext(ctx, label, x, y, 34, (1, 1, 1, a), 600, center=True)

# ------------------------------------------------------------ scenes
S0_UMB = [1.2, None, 1.5, 2.7, 1.8, 2.1, None, 2.4]          # extra umbrellas popping up behind (+ the guide's = 7)
def s0(ctx, t, d):
    piazza(ctx, t)
    crowd(ctx, t, umb_at=S0_UMB, only=[0, 2, 3, 4, 5, 7])
    tourist(ctx, 880, GY - 10, 1.05, t, 2, umb="open", hat=True, seed=0)                       # the real guide
    wren(ctx, 520, GY, 1.0, t, "wave" if t < 1.2 else "point", expr="happy", hand=(-40, -230))
    kid(ctx, 300, GY, 0.95, t, "smile" if t < 1.6 else "flat", (0, -170))
    n = 1 + sum(1 for u in S0_UMB if u is not None and t >= u)
    bubble_ml(ctx, 470, 700, ["Follow the yellow", "umbrella!"], 40, ramp(t, 0.25, 0.45) * (1 - ramp(t, 1.9, 2.05)), (850, 1150))
    bubble_ml(ctx, 260, 1060, ["Which one?"], 42, ramp(t, 2.7, 2.9), (300, GY - 370))
    header(ctx, ease(t / 0.2 + 1), "WALKING TOUR", "“Follow the yellow umbrella.”", "There are 7 of them.", -0.3, t, main_size=50)
    meter(ctx, "YELLOW UMBRELLAS", "%d" % n); wm(ctx)

def s1(ctx, t, d):
    piazza(ctx, t)
    crowd(ctx, t, umb_at=[0, None, 0, None, 0, 0, None, 0], only=[0, 2, 5, 7])
    if t < 1.45:                                             # tour 1: a different tour, everyone in red caps listening
        for k, xx in enumerate((640, 980)): tourist(ctx, xx, GY - 20, 0.95, t, 3 + k * 2, hat=True, kind="camera", seed=k)
        tourist(ctx, 820, GY - 10, 1.05, t, 0, umb="open", seed=3)
        kid(ctx, 420, GY, 0.95, t, "smile", (0, -170))
        label = "Tour 1: wrong tour"
    elif t < 2.9:                                            # tour 2: a wedding photo with a yellow parasol
        tourist(ctx, 760, GY - 10, 1.05, t, 0, umb="open", kind="bride", seed=4)
        tourist(ctx, 950, GY - 10, 1.05, t, 7, seed=5)
        bx, by = 950, GY - 10 - 1.05 * 300                                         # groom's bow tie
        ctx.move_to(bx, by); ctx.line_to(bx - 30, by - 18); ctx.line_to(bx - 30, by + 18); ctx.close_path()
        ctx.move_to(bx, by); ctx.line_to(bx + 30, by - 18); ctx.line_to(bx + 30, by + 18); ctx.close_path()
        ctx.set_source_rgba(*hexc('#1d1d2c')); ctx.fill()
        kid(ctx, 560, GY, 0.95, t, "smug", (0, -330))             # photobomb pose: hands up
        if 0 <= t - 2.2 < 0.25: ctx.set_source_rgba(1, 1, 1, 0.75 * (1 - (t - 2.2) / 0.25)); ctx.paint()   # camera flash
        label = "Tour 2: a wedding"
    else:                                                    # tour 3: a man with his own rain cloud
        tourist(ctx, 800, GY - 10, 1.05, t, 6, umb="open", seed=6)
        rain_cloud(ctx, 885, 690, t)
        kid(ctx, 560, GY, 0.95, t, "flat", (0, -170))
        label = "Tour 3: just a man. It's raining."
    lx = 420 if t < 1.45 else 560
    label_chip(ctx, label, min(max(lx, 330), 750), 1040, ramp(t % 1.45 if t < 2.9 else t - 2.9, 0.0, 0.12) if t > 0.1 else 1)
    header(ctx, ease(t / 0.2), "LEO PICKS ONE", "Then another. Then another.", "All wrong.", 1.2, t, main_size=54)
    meter(ctx, "TOURS JOINED", "%d" % (1 + (t >= 1.45) + (t >= 2.9))); wm(ctx)

S2_UMB = [0.2, 0.5, 0.8, 1.1, 1.4, 1.7, 2.0, 2.3]
def s2(ctx, t, d):
    piazza(ctx, t)
    crowd(ctx, t, umb_at=S2_UMB)
    # more umbrellas bobbing in from the edges
    for k, (x0, y0, t0) in enumerate(((120, 980, 2.6), (420, 940, 2.8), (700, 990, 3.0), (980, 950, 3.2))):
        if t >= t0:
            umbrella(ctx, x0 + 14 * math.sin(t * 3 + k), y0 + 8 * math.sin(t * 4 + k), 90)
            if t - t0 < 0.3: burst(ctx, x0, y0 - 40, 1 - (t - t0) / 0.3, 70)
    spin = 0.06 * math.sin(t * 9) * ramp(t, 0.8, 1.6)
    ctx.save(); ctx.translate(600, GY + 80); ctx.rotate(spin); ctx.translate(-600, -(GY + 80))
    kid(ctx, 600, GY + 80, 1.0, t, "flat" if t < 1.0 else "shock", (0, -170) if t < 1.6 else (0, -360))
    ctx.restore()
    bubble_ml(ctx, 600, 1215, ["GRANDMA?!"], 46, ramp(t, 1.6, 1.8), (600, GY + 80 - 380))
    header(ctx, ease(t / 0.2), "LEO IS LOST", "15 yellow umbrellas.", "Zero grandmas.", 1.4, t, main_size=56)
    meter(ctx, "PANIC", "%d%%" % int(100 * ramp(t, 0.3, 2.8)), col=RED); wm(ctx)

def s3(ctx, t, d):
    piazza(ctx, t)
    fold = [2.2 + 0.12 * i for i in range(8)]
    for i, (x, pal, hat, seed) in enumerate(CROWD):           # the crowd closes umbrellas and turns to Wren
        follow = ramp(t, fold[i], fold[i] + 0.5)
        tourist(ctx, x + 40 * follow, CROWD_GY, 0.72, t, pal, umb="open" if t < fold[i] else "closed", hat=hat, seed=seed)
    rise = ramp(t, 0.2, 0.9)
    hx, hy = 130, lerp(-230, -620, rise)
    WX = 780
    wren(ctx, WX, GY, 1.0, t, "point", expr="happy", hand=(hx, hy))
    bob = math.sin(t * 2 * math.pi * 1.1) * 5
    pineapple_flag(ctx, WX + hx, GY + hy + bob, t, length=lerp(100, 200, rise))
    if 0.8 <= t < 1.2: burst(ctx, WX + hx, GY + hy - 250, 1 - (t - 0.8) / 0.4, 130)
    lx = lerp(260, 520, ramp(t, 0.9, 1.7))
    kid(ctx, lx, GY, 0.95, t, "shock" if t < 0.9 else "smile", (0, -330) if 0.9 < t < 1.9 else (60, -200))
    bubble_ml(ctx, 360, 1030, ["GRANDMA!"], 44, ramp(t, 1.0, 1.2) * (1 - ramp(t, 2.1, 2.25)), (lx, GY - 370))
    bubble_ml(ctx, 330, 830, ["Grandmas don't", "get lost, love."], 40, ramp(t, 2.3, 2.5), (WX - 140, 1175))
    n = 1 + int(37 * ramp(t, 2.2, 3.6))
    header(ctx, ease(t / 0.2), "THEN HE SEES IT", "A pineapple on a stick.", "Wren brought her own flag.", 1.0, t, main_size=56)
    meter(ctx, "FOLLOWING WREN", "%d" % n, col=GREEN); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 440, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    pineapple_flag(ctx, 800, 1600, t, length=380)
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “Always pack a pineapple.”", 205 - (1 - a) * 20, 52, hexc('#22223b', a), maxw=1000)
    ctext(ctx, "Leo: “38 strangers call her Grandma now.”", 290, 42, hexc(RED, ease((t - 0.5) / 0.3)), maxw=1000)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Your tour group trick? Comment below!", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 1.0), (s0, 3.3), (s1, 0.8), (s1, 2.1), (s1, 3.6), (s2, 0.6),
                 (s2, 2.0), (s2, 3.8), (s3, 0.5), (s3, 1.5), (s3, 3.0), (s3, 3.8), (s4, 2.6)]
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

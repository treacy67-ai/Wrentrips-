import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = "/home/claude/wren/ep17"
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1700
LEI_COLS = ['#ff4d8d', '#ffd60a', '#ffffff', '#ff8c42', '#b86bff']

# ------------------------------------------------------------ shared bits
def hibiscus(ctx, x, y, r, col='#ff4d8d'):
    for k in range(5):
        a = k * 2 * math.pi / 5; circle(ctx, x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6, r * 0.55, hexc(col))
    circle(ctx, x, y, r * 0.28, hexc('#ffd60a'))

def palm(ctx, x, base, h, t, col='#2f8f4e', trunk='#8a5a2b', flip=1):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(h * 0.06); ctx.set_source_rgba(*hexc(trunk))
    ctx.move_to(x, base); ctx.curve_to(x + flip * h * 0.12, base - h * 0.4, x + flip * h * 0.02, base - h * 0.7, x + flip * h * 0.14, base - h); ctx.stroke()
    tx, ty = x + flip * h * 0.14, base - h
    for k in range(7):
        a = math.radians(-165 + k * 52) + 0.06 * math.sin(t * 1.6 + k)
        ex, ey = tx + math.cos(a) * h * 0.55, ty + math.sin(a) * h * 0.38 + h * 0.14
        ctx.move_to(tx, ty); ctx.curve_to(tx + math.cos(a) * h * 0.3, ty + math.sin(a) * h * 0.5 - h * 0.1, ex - 10, ey - 30, ex, ey)
        ctx.curve_to(ex - 10, ey - 8, tx + math.cos(a) * h * 0.3, ty + math.sin(a) * h * 0.5, tx, ty); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    for dx in (-14, 14): circle(ctx, tx + dx, ty + 16, h * 0.03, hexc('#6b4423'))

def sky(ctx, t, top='#4cc9f0', bot='#c8f1ff', h=1250):
    g = cairo.LinearGradient(0, 0, 0, h); g.add_color_stop_rgb(0, *hexc(top)[:3]); g.add_color_stop_rgb(1, *hexc(bot)[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, h); ctx.fill()

def cloud(ctx, x, y, s, a=0.9):
    for dx, dy, r in ((0, 0, 50), (55, 10, 42), (-55, 12, 38), (18, -26, 40)): circle(ctx, x + dx * s, y + dy * s, r * s, (1, 1, 1, a))

def leis(ctx, x, gy, s, n):
    for i in range(n):
        y = gy - (428 + i * 6.2) * s; R = (92 - i * 0.7) * s
        for j in range(11):
            a = math.radians(8 + j * 16.4); px = x + math.cos(a) * R * (1 if j % 2 == 0 else 1); py = y + math.sin(a) * R * 0.30
            hibiscus(ctx, px, py, 11 * s, LEI_COLS[(i + j) % 5]) if (j % 2 == 0) else circle(ctx, px, py, 8 * s, hexc(LEI_COLS[(i + j + 2) % 5]))

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

# ------------------------------------------------------------ scene 0: arrival
def arrival_bg(ctx, t):
    sky(ctx, t, '#ffe6a8', '#fff6dc', 1350)
    for k in range(6):                                                         # hanging flower garland
        ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#2f8f4e'))
    ctx.move_to(-20, 640); ctx.curve_to(300, 760, 780, 760, 1100, 640); ctx.stroke()
    for k in range(13):
        x = k * 85 - 10; y = 646 + 82 * math.sin((x / 1080) * math.pi) ** 1.0
        hibiscus(ctx, x, y, 17, LEI_COLS[k % 5])
    rrect(ctx, 250, 800, 580, 130, 20); ctx.set_source_rgba(*hexc('#2a9d8f')); ctx.fill()
    mv.font(ctx, 74); e = ctx.text_extents("ALOHA"); ctx.move_to(540 - e.x_advance / 2, 893); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text("ALOHA")
    for px, h in ((90, 520), (990, 560)): palm(ctx, px, 1360, h, t, flip=1 if px < 500 else -1)
    ctx.rectangle(0, 1350, W, H - 1350); ctx.set_source_rgba(*hexc('#e8d8b8')); ctx.fill()
    for yy in range(1400, H, 100):
        for xx in range(-100, W + 100, 200): ctx.rectangle(xx + (100 if (yy // 100) % 2 else 0), yy, 200, 100); ctx.set_source_rgba(*hexc('#d9c6a0', 0.6)); ctx.stroke()
    ctx.set_line_width(2)

def s0(ctx, t, d):
    arrival_bg(ctx, t)
    n = int(clamp01((t - 0.3) / 2.4) * 14)
    # flying leis from the sides
    for k in range(n, min(14, n + 2)):
        ph = ((t - 0.3) / 2.4 * 14) % 1; sx = -100 if k % 2 == 0 else 1180
        px = lerp(sx, 540, ease(ph)); py = lerp(1150, 1190, ease(ph)) - 120 * math.sin(math.pi * ph)
        hibiscus(ctx, px, py, 26, LEI_COLS[k % 5])
    wren(ctx, 520, GY, 1.1, t, "wave", expr="happy" if n < 12 else "shock", hand=(110, -140))
    leis(ctx, 520, GY, 1.1, n)
    kid(ctx, 880, GY, 0.95, t, "flat", (0, -150))
    bubble_ml(ctx, 740, 1030, ["Grandma, you're", "a hedge."], 42, ramp(t, 2.8, 3.0), (880, GY - 400))
    header(ctx, ease(t / 0.2 + 1), "WREN LANDS IN HAWAII", "Aloha! Aloha! Aloha!", "Free leis for everyone.", -0.3, t, main_size=56)
    meter(ctx, "LEIS", "%d" % n); wm(ctx)

# ------------------------------------------------------------ scenes 1 & 2: surf
WATER = 1560
def ocean(ctx, t, swell=0.0, curl=0.0):
    sky(ctx, t, '#4cc9f0', '#d8f6ff', 1050)
    cloud(ctx, 250 + 20 * math.sin(t * 0.3), 760, 1.1); cloud(ctx, 800, 640, 0.8)
    circle(ctx, 880, 560, 90, hexc('#fff3b0', 0.9))
    ctx.move_to(0, 1050); ctx.curve_to(200, 900, 420, 900, 560, 1050); ctx.close_path(); ctx.set_source_rgba(*hexc('#2f8f4e', 0.75)); ctx.fill()      # island
    ctx.move_to(520, 1050); ctx.curve_to(700, 860, 900, 840, 1080, 1050); ctx.close_path(); ctx.set_source_rgba(*hexc('#3a6b4a', 0.8)); ctx.fill()
    g = cairo.LinearGradient(0, 1050, 0, H); g.add_color_stop_rgb(0, *hexc('#2ec4d6')[:3]); g.add_color_stop_rgb(1, *hexc('#0a6e8a')[:3])
    ctx.set_source(g); ctx.rectangle(0, 1050, W, H - 1050); ctx.fill()
    for k in range(7):
        y = 1100 + k * 90; ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.22)
        for j in range(5):
            x = (j * 280 + k * 70 + t * 40 * (1 + k % 2)) % 1400 - 150; ctx.move_to(x, y); ctx.curve_to(x + 40, y - 10, x + 80, y + 10, x + 120, y); ctx.stroke()
    if swell > 0:                                                             # big wave rising behind
        top = lerp(1500, 760, swell)
        ctx.move_to(-20, H); ctx.line_to(-20, top + 120)
        ctx.curve_to(260, top - 40 * swell, 620, top - 10, 900, top + 40 + 160 * (1 - swell)); ctx.line_to(1100, top + 200 + 120 * (1 - swell)); ctx.line_to(1100, H); ctx.close_path()
        g2 = cairo.LinearGradient(0, top, 0, H); g2.add_color_stop_rgb(0, *hexc('#4be3e6')[:3]); g2.add_color_stop_rgb(1, *hexc('#0a7da0')[:3]); ctx.set_source(g2); ctx.fill()
        ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(1, 1, 1, 0.95)
        ctx.move_to(-20, top + 120); ctx.curve_to(260, top - 40 * swell, 620, top - 10, 900, top + 40 + 160 * (1 - swell)); ctx.stroke()
        rng = random.Random(4)
        for k in range(26):
            x = rng.uniform(0, W); circle(ctx, x, top + rng.uniform(-30, 60) + 40 * math.sin(t * 5 + k), rng.uniform(8, 20), (1, 1, 1, 0.8))

def board(ctx, x, y, ang=0.0, s=1.0, col='#ff8c42'):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.move_to(-260, 0); ctx.curve_to(-250, -34, 220, -34, 280, 0); ctx.curve_to(220, 34, -250, 34, -260, 0); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    ctx.set_line_width(10); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.move_to(-230, 0); ctx.line_to(250, 0); ctx.stroke()
    ctx.restore()

def spray(ctx, x, y, t, a=1.0):
    rng = random.Random(9)
    for k in range(20):
        ph = (t * 1.6 + k / 20) % 1; circle(ctx, x + rng.uniform(-200, 200) * (0.4 + ph), y - ph * rng.uniform(80, 240), rng.uniform(5, 12), (1, 1, 1, 0.8 * (1 - ph) * a))

def s1(ctx, t, d):
    ocean(ctx, t)
    # Leo's attempts: wobble and fall twice
    def attempt(t0):
        u = t - t0
        if u < 0: return 0.0, 0.0, 0.0
        if u < 0.9: return 0.25 * math.sin(u * 14) * (u / 0.9), 0.0, 0.0
        if u < 1.5: k = (u - 0.9) / 0.6; return 0.25 * math.sin(0.9 * 14) + k * 1.5, k * k * 200, k
        return 1.8, 200, 1.0
    first = t < 2.2
    ang, sink, k = attempt(0.5) if first else attempt(2.3)
    bx = 540
    board(ctx, bx, 1600 + (0 if not first or t < 1.5 else 0), 0.05 * math.sin(t * 9) if k < 0.05 else 0.4 * k, 1.0)
    ctx.save(); ctx.translate(bx + 40 * k, 1600 + sink * 0.5); ctx.rotate(ang); ctx.translate(-bx, -1600)
    kid(ctx, bx, 1600, 1.15, t, "shock" if k > 0.05 else "flat", (-90, -230) if k < 0.05 else (-90, -300))
    ctx.restore()
    if k > 0.4:
        for j in range(3): e4.ell(ctx, bx + 40 + 60 * j, 1625, 50 + 60 * (k - 0.4), 12, (1, 1, 1, 0.5))
        burst(ctx, bx + 40, 1560, clamp01(1 - (k - 0.4) * 2), 150)
    # water overlay
    g = cairo.LinearGradient(0, 1620, 0, H); g.add_color_stop_rgba(0, *hexc('#2ec4d6')[:3], 0.0); g.add_color_stop_rgba(0.3, *hexc('#1aa0bf')[:3], 0.9); g.add_color_stop_rgba(1, *hexc('#0a6e8a')[:3], 1)
    ctx.set_source(g); ctx.rectangle(0, 1620, W, H - 1620); ctx.fill()
    bubble_ml(ctx, 540, 960, ["How hard can it be?"], 44, ramp(t, 0.3, 0.5) * (1 - ramp(t, 1.4, 1.6)), (bx, 1330))
    bubble_ml(ctx, 540, 960, ["Okay, once more."], 44, ramp(t, 2.4, 2.6), (bx, 1330))
    header(ctx, ease(t / 0.2), "SURF LESSON", "Leo goes first.", "Leo goes sideways.", 0.9, t, main_size=56)
    meter(ctx, "LEO'S WAVES", "0"); wm(ctx)

def s2(ctx, t, d):
    sw = ramp(t, 0.0, 1.8)
    ocean(ctx, t, swell=sw)
    ride = ramp(t, 1.6, 3.8)
    bxp = lerp(300, 740, ride) + 40 * math.sin(t * 2.2); byp = lerp(1380, 1620, ride * ride)
    sc = lerp(0.55, 1.1, ride)
    board(ctx, bxp, byp, 0.08 * math.sin(t * 3), sc)
    wren(ctx, bxp, byp + 4, 0.95 * sc, t, "cheer" if t > 2.6 else "point", expr="happy", hand=(120, -150))
    # scarf-flaring spray and speed lines
    spray(ctx, bxp, byp, t, ramp(t, 1.4, 1.8))
    if t > 1.6:
        ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.5)
        for k in range(6): y = 950 + k * 120; xx = (t * 1500 + k * 170) % 1300 - 100; ctx.move_to(xx, y); ctx.line_to(xx + 160, y); ctx.stroke()
    bubble_ml(ctx, 360, 900, ["Wheee!"], 54, ramp(t, 2.0, 2.2) * (1 - ramp(t, 3.4, 3.6)), (bxp, byp - 700 * sc * 0.95))
    # crowd tiny cheering on the right
    for k in range(4):
        cx = 120 + k * 90; cy = 1470 - 6 * abs(math.sin(t * 6 + k));
        if ramp(t, 3.0, 3.3) > 0: circle(ctx, cx, cy, 20, hexc('#d9a27a')); rrect(ctx, cx - 20, cy + 22, 40, 48, 14); ctx.set_source_rgba(*hexc(['#ff4d8d', '#4361ee', '#2a9d8f', '#ffd60a'][k])); ctx.fill()
    header(ctx, ease(t / 0.2), "WREN'S TURN", "A real wave arrives.", "She rides it perfectly.", 2.2, t, main_size=56)
    meter(ctx, "WREN'S WAVES", "1" if t > 2.4 else "0"); wm(ctx)

# ------------------------------------------------------------ scene 3: luau
def luau(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, 1300); g.add_color_stop_rgb(0, *hexc('#5b2a86')[:3]); g.add_color_stop_rgb(0.45, *hexc('#ff5d8f')[:3]); g.add_color_stop_rgb(1, *hexc('#ffb86b')[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1300); ctx.fill()
    circle(ctx, 540, 1200, 150, hexc('#fff0a0')); circle(ctx, 540, 1200, 200, hexc('#ffd166', 0.25))
    ctx.move_to(0, 1300); ctx.line_to(0, 1160); ctx.curve_to(240, 1140, 340, 1010, 440, 960); ctx.line_to(520, 960); ctx.curve_to(640, 1010, 820, 1150, 1080, 1180); ctx.line_to(1080, 1300); ctx.close_path()
    ctx.set_source_rgba(*hexc('#2b1b45')); ctx.fill()                                                         # volcano
    for k in range(5):
        ph = (t * 0.6 + k / 5) % 1; circle(ctx, 480 + 12 * math.sin(t * 3 + k) + k * 10, 950 - ph * 160, 10 + 8 * ph, hexc('#ff8c42', 1 - ph))
    ctx.rectangle(0, 1300, W, H - 1300); ctx.set_source_rgba(*hexc('#f0d9a8')); ctx.fill()
    for px, h, fl in ((70, 700, 1), (1010, 760, -1)): palm(ctx, px, 1330, h, t, col='#1d4d2e', trunk='#3b2a1a', flip=fl)
    for k in range(10):                                                                                       # tiki torches
        pass
    for tx in (260, 820):
        ctx.rectangle(tx - 7, 1180, 14, 300); ctx.set_source_rgba(*hexc('#5a3a1e')); ctx.fill()
        fl = 1 + 0.15 * math.sin(t * 14 + tx)
        ctx.save(); ctx.translate(tx, 1170); ctx.scale(1, fl); ctx.move_to(0, -58); ctx.curve_to(26, -20, 22, 14, 0, 14); ctx.curve_to(-22, 14, -26, -20, 0, -58); ctx.set_source_rgba(*hexc('#ff8c42')); ctx.fill(); ctx.restore()
    # mat
    rrect(ctx, 60, 1560, 960, 260, 30); ctx.set_source_rgba(*hexc('#c1583a')); ctx.fill()
    for k in range(10): rrect(ctx, 90 + k * 96, 1580, 70, 220, 12); ctx.set_source_rgba(*hexc('#e9a05a', 0.55)); ctx.fill()

def grass_skirt(ctx, x, gy, s, t):
    for k in range(17):
        sx = x - 90 * s + k * 11 * s; sw = 12 * math.sin(t * 7 + k * 0.6)
        ctx.set_line_width(9 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#7ac143' if k % 2 else '#4f9d2d'))
        ctx.move_to(sx, gy - 270 * s); ctx.line_to(sx + sw * s, gy - 130 * s); ctx.stroke()

def s3(ctx, t, d):
    luau(ctx, t)
    sway = math.sin(t * 4.5) * 14
    wren(ctx, 400 + sway, GY, 1.05, t, "cheer" if t % 1.0 < 0.5 else "wave", expr="happy", hand=(120, -150))
    grass_skirt(ctx, 400 + sway, GY, 1.05, t)
    leis(ctx, 400 + sway, GY, 1.05, 3)
    kid(ctx, 800, GY, 1.0, t, "smug" if t > 2.0 else "flat", (-100, -190))
    # Leo with coconut drink
    cx, cy = 800 - 100, GY - 190
    ctx.save(); ctx.translate(cx, cy - 40); circle(ctx, 0, 0, 36, hexc('#7a4a2a')); circle(ctx, -8, -8, 12, (1, 1, 1, 0.2))
    ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#e63946')); ctx.move_to(10, -20); ctx.line_to(30, -66); ctx.stroke()
    ctx.move_to(14, -52); ctx.line_to(60, -60); ctx.line_to(36, -36); ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd60a')); ctx.fill(); ctx.restore()
    bubble_ml(ctx, 760, 1010, ["Grandma, people", "are filming you."], 40, ramp(t, 1.0, 1.2) * (1 - ramp(t, 2.6, 2.8)), (800, GY - 400))
    bubble_ml(ctx, 380, 1010, ["Good. Get my", "good side."], 40, ramp(t, 2.8, 3.0), (400, GY - 640))
    header(ctx, ease(t / 0.2), "SUNSET LUAU", "Wren does the hula.", "Leo does the coconut.", 1.0, t, main_size=56)
    meter(ctx, "ALOHA LEVEL", "100%"); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    leis(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), 2)
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “I'm never leaving.”", 205 - (1 - a) * 20, 60, hexc('#22223b', a), maxw=940)
    ctext(ctx, "Leo: “Flight's at 6am.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Where should Wren go next? Comment below", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

SCENES = [(s0, 3.8), (s1, 4.2), (s2, 4.6), (s3, 4.0), (s4, 3.2)]

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
        picks = [(s0, 0.5), (s0, 1.8), (s0, 3.4), (s1, 0.9), (s1, 1.4), (s1, 3.2), (s2, 0.8), (s2, 2.2), (s2, 3.4), (s3, 1.5), (s3, 3.3), (s4, 2.0)]
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

import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ai_tag, ease, wren
import ep4 as e4
from ep5 import CX, GY, S, L_REST, L_HOLD, L_UP, bob, hwp, gate

OUT = "/home/claude/wren/ep6"
os.makedirs(OUT, exist_ok=True)
DARK, RED = hexc('#22223b'), '#e63946'

# ---------- props (all original designs, no logos) ----------
def car(ctx, x, y, s, ang, puff=0.0, t=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    if puff > 0:
        for k in range(5):
            ph = (t * 5 + k * 0.2) % 1; r = 14 + ph * 34; a = (1 - ph) * 0.7 * puff
            circle(ctx, -200 - ph * 130, -52 + (k % 3 - 1) * 8, r, (1, 1, 1, a))
            circle(ctx, -20 + (k % 3 - 1) * 12, -18 + ph * 80, r * 0.8, (1, 1, 1, a * 0.8))
    for wx in (-105, 108): circle(ctx, wx, -30, 31, hexc('#22223b')); circle(ctx, wx, -30, 15, hexc('#adb5bd'))
    ctx.move_to(-178, -36); ctx.line_to(-170, -66); ctx.curve_to(-110, -80, -50, -96, 0, -112)
    ctx.curve_to(60, -122, 110, -96, 145, -72); ctx.line_to(192, -54); ctx.curve_to(200, -42, 190, -32, 172, -32)
    ctx.line_to(-170, -32); ctx.close_path(); ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    ctx.move_to(-35, -96); ctx.curve_to(10, -108, 58, -102, 92, -76); ctx.line_to(-35, -72); ctx.close_path()
    ctx.set_source_rgba(*hexc('#bde0fe')); ctx.fill()
    ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#ffd166'))
    ctx.move_to(-165, -52); ctx.line_to(170, -48); ctx.stroke()
    rrect(ctx, -198, -64, 28, 24, 6); ctx.set_source_rgba(*hexc('#3d405b')); ctx.fill()
    e4.ell(ctx, -60, -62, 16, 6, hexc('#3d405b')); e4.ell(ctx, 40, -66, 16, 6, hexc('#3d405b'))
    ctx.restore()

def parked(ctx, x, y, col):
    for wx in (-26, 28): circle(ctx, x + wx, y - 14, 15, hexc('#22223b'))
    rrect(ctx, x - 48, y - 58, 96, 40, 14); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    rrect(ctx, x - 28, y - 82, 58, 30, 12); ctx.set_source_rgba(*hexc('#dee2e6')); ctx.fill()

def phone_prop(ctx, x, y, rot=-0.15):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    rrect(ctx, -34, -60, 68, 120, 12); ctx.set_source_rgba(*hexc('#1d2433')); ctx.fill()
    rrect(ctx, -29, -54, 58, 108, 8); ctx.set_source_rgba(*hexc('#e8f4ff')); ctx.fill()
    rrect(ctx, -20, 20, 40, 18, 9); ctx.set_source_rgba(*hexc(RED)); ctx.fill(); ctx.restore()

def big_phone(ctx, a, t):
    if a <= 0: return
    x = 640 + (1 - a) * 500; y = 640
    rrect(ctx, x, y, 390, 720, 52); ctx.set_source_rgba(*hexc('#1d2433')); ctx.fill()
    rrect(ctx, x + 18, y + 22, 354, 676, 36); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    mv.font(ctx, 40); e = ctx.text_extents("FLYING CAR"); ctx.move_to(x + 195 - e.x_advance / 2, y + 110); ctx.set_source_rgba(*DARK); ctx.show_text("FLYING CAR")
    car(ctx, x + 205, y + 290, 0.85, 0.0)
    rrect(ctx, x + 60, y + 380, 270, 86, 43); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    mv.font(ctx, 38); e = ctx.text_extents("RESERVE"); ctx.move_to(x + 195 - e.x_advance / 2, y + 436); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text("RESERVE")
    mv.font(ctx, 36); ctx.move_to(x + 60, y + 548); ctx.set_source_rgba(*DARK); ctx.show_text("Delivery: 2028*")
    mv.font(ctx, 28, False); ctx.move_to(x + 60, y + 600); ctx.set_source_rgba(0.45, 0.45, 0.5, 1); ctx.show_text("*no guarantee")
    k = ease((t - 1.1) / 0.4)
    if k > 0:
        ctx.save(); ctx.translate(x + 175, y + 538); ctx.scale(150 * k, 36 * k); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
        ctx.set_line_width(6); ctx.set_source_rgba(*hexc(RED, k)); ctx.stroke()

def mini_head(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    circle(ctx, 0, -16, 30, hexc('#dfe3ea')); circle(ctx, 0, 0, 34, hexc('#f2c9a5'))
    ctx.arc(0, -4, 36, math.radians(190), math.radians(350)); ctx.close_path(); ctx.set_source_rgba(*hexc('#dfe3ea')); ctx.fill()
    ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#5c4033'))
    for ex in (-13, 13): ctx.arc(ex, 0, 10, 0, 2 * math.pi); ctx.stroke()
    ctx.set_line_width(4); ctx.arc(0, 12, 12, math.radians(25), math.radians(155)); ctx.stroke(); ctx.restore()

def bus(ctx, x, y, door_open=False):
    for wx in (-150, 150): circle(ctx, x + wx, y - 40, 44, hexc('#22223b')); circle(ctx, x + wx, y - 40, 20, hexc('#adb5bd'))
    rrect(ctx, x - 250, y - 250, 500, 210, 28); ctx.set_source_rgba(*hexc('#4895ef')); ctx.fill()
    ctx.rectangle(x - 250, y - 120, 500, 18); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.fill()
    for k in range(5):
        rrect(ctx, x - 215 + k * 82, y - 220, 66, 62, 10); ctx.set_source_rgba(*hexc('#d7f0ff')); ctx.fill()
    rrect(ctx, x + 175, y - 225, 60, 140, 8); ctx.set_source_rgba(*hexc('#1f55a8')); ctx.fill()

def share_pill(ctx, t):
    a = ease((t - 1.0) / 0.4)
    if a <= 0: return
    rrect(ctx, 110, 1738, 860, 60, 30); ctx.set_source_rgba(1, 1, 1, 0.9 * a); ctx.fill()
    mv.font(ctx, 30); s_ = "Send this to someone waiting on a flying car"; e = ctx.text_extents(s_)
    ctx.move_to(540 - e.x_advance / 2, 1778); ctx.set_source_rgba(*hexc('#22223b', a)); ctx.show_text(s_)

# ---------- backgrounds ----------
def test_site(ctx, t):
    mv.vgrad(ctx, '#9bd1f5', '#eaf7ff')
    mv.cloud(ctx, 150 + t * 8, 1000, 0.8); mv.cloud(ctx, 700 - t * 6, 1150, 0.6, 0.85)
    ctx.move_to(-200, 1500)
    for x in range(-200, W + 300, 60): ctx.line_to(x, 1470 - 40 * abs(math.sin(x * 0.006)))
    ctx.line_to(W + 300, 1640); ctx.line_to(-200, 1640); ctx.close_path(); ctx.set_source_rgba(*hexc('#e9c46a')); ctx.fill()
    ctx.rectangle(-200, 1590, W + 400, 700); ctx.set_source_rgba(*hexc('#6b705c')); ctx.fill()
    ctx.set_line_width(6); ctx.set_dash([40, 34]); ctx.set_source_rgba(1, 1, 1, 0.5); ctx.move_to(-200, 1650); ctx.line_to(W + 200, 1650); ctx.stroke(); ctx.set_dash([])
    # steel ramp
    ctx.move_to(90, 1600); ctx.curve_to(230, 1600, 300, 1540, 310, 1440); ctx.line_to(335, 1440); ctx.line_to(335, 1600); ctx.close_path()
    ctx.set_source_rgba(*hexc('#8d99ae')); ctx.fill()
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#edf2f4')); ctx.move_to(90, 1600); ctx.curve_to(230, 1600, 300, 1540, 310, 1440); ctx.stroke()

def street(ctx, t):
    mv.vgrad(ctx, '#ffd9b3', '#ffe9cf')
    random.seed(5); x = -30
    while x < W + 100:
        w = random.randint(150, 230); h = random.randint(400, 700)
        ctx.rectangle(x, 1580 - h, w, h); ctx.set_source_rgba(*hexc(random.choice(['#f6bd60', '#84a59d', '#f28482', '#a3c4bc', '#f5cac3']))); ctx.fill()
        for wy in range(1580 - h + 40, 1450, 110):
            rrect(ctx, x + 26, wy, w - 52, 64, 8); ctx.set_source_rgba(*hexc('#5c4d7d', 0.5)); ctx.fill()
        x += w
    ctx.rectangle(-200, 1580, W + 400, 700); ctx.set_source_rgba(*hexc('#c9ada7')); ctx.fill()
    ctx.rectangle(-200, 1580, W + 400, 14); ctx.set_source_rgba(*hexc('#9a8c98')); ctx.fill()
    ctx.rectangle(-200, 1610, W + 400, 160); ctx.set_source_rgba(*hexc('#6b705c')); ctx.fill()
    ctx.set_line_width(7); ctx.set_dash([46, 36]); ctx.set_source_rgba(1, 1, 1, 0.55); ctx.move_to(-200, 1690); ctx.line_to(W + 200, 1690); ctx.stroke(); ctx.set_dash([])

# ---------- scenes ----------
def s0(ctx, t, d):
    e4.begin_set(ctx); gate(ctx, t, "CANCELLED"); mv.suitcase(ctx, 170, 1700, 0.55, t)
    hl = e4.hand_path(t, [(0, L_REST), (0.9, L_HOLD)])
    wren(ctx, CX, GY, S, t, "point", hand=hl, expr="shock" if t < 1.6 else "happy")
    p = hwp(hl, t); phone_prop(ctx, p[0] + 14, p[1] - 36)
    e4.end_set(ctx)
    a = ease(t / 0.3); e4.top_box(ctx, a, 380)
    ctext(ctx, "Flight cancelled. Again.", 245, 62, hexc('#22223b', a), maxw=900)
    ctext(ctx, "So I reserved Tesla’s flying car.", 350, 54, hexc(RED, ease((t - 1.3) / 0.4)), maxw=900)
    ai_tag(ctx, y=1860)

def s1(ctx, t, d):
    e4.begin_set(ctx); gate(ctx, t, "CANCELLED"); mv.suitcase(ctx, 170, 1700, 0.55, t)
    hl = e4.hand_path(t, [(0, L_HOLD), (0.5, L_HOLD)])
    wren(ctx, CX, GY, S, t, "point", hand=hl, expr="shock" if t > 1.3 else "happy", flush=0.0)
    p = hwp(hl, t); phone_prop(ctx, p[0] + 14, p[1] - 36)
    e4.bubble(ctx, 330, 1010, "I’ll be 74. Snacks!", 46, ease((t - 2.5) / 0.3), (370, 1090))
    e4.end_set(ctx)
    big_phone(ctx, ease((t - 0.2) / 0.5), t)
    a = ease(t / 0.3); e4.top_box(ctx, a, 380)
    ctext(ctx, "THE FINE PRINT", 215, 44, hexc(RED, a), maxw=900)
    ctext(ctx, "Delivery: 2028.", 305, 66, hexc('#22223b', a), maxw=900)
    ctext(ctx, "(Maybe.)", 410, 56, hexc(RED, ease((t - 1.6) / 0.4)), maxw=900)
    share_pill(ctx, t); ai_tag(ctx, y=1860)

def car_state(t):
    P = [(90, 1600), (230, 1600), (300, 1540), (310, 1440)]
    def bez(u):
        a_, b_, c_, d_ = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
        return (a_ * P[0][0] + b_ * P[1][0] + c_ * P[2][0] + d_ * P[3][0], a_ * P[0][1] + b_ * P[1][1] + c_ * P[2][1] + d_ * P[3][1])
    def tang(u):
        dx = 3 * (1 - u) ** 2 * (P[1][0] - P[0][0]) + 6 * (1 - u) * u * (P[2][0] - P[1][0]) + 3 * u * u * (P[3][0] - P[2][0])
        dy = 3 * (1 - u) ** 2 * (P[1][1] - P[0][1]) + 6 * (1 - u) * u * (P[2][1] - P[1][1]) + 3 * u * u * (P[3][1] - P[2][1])
        return math.atan2(dy, dx)
    if t < 0.5: return (90, 1600, 0.0, 0.0)
    if t < 1.4:
        u = ((t - 0.5) / 0.9) ** 1.6; x, y = bez(u); return (x, y, tang(u), 0.0)
    if t < 2.7:
        u = (t - 1.4) / 1.3; x = 310 + 480 * u; y = 1440 + 160 * u - 4 * 480 * u * (1 - u)
        a0 = tang(1.0); ang = a0 + (2 * math.pi - a0) * ease(u); return (x, y, ang, 1.0 if 0.03 < u < 0.92 else 0.0)
    k = ease((t - 2.7) / 0.8); return (790 + 30 * k, 1600, 0.0, 0.0)

def s2(ctx, t, d):
    test_site(ctx, t)
    for x, col in ((430, '#2a9d8f'), (540, '#f4a261'), (650, '#9b5de5')): parked(ctx, x, 1600, col)
    x, y, ang, puff = car_state(t)
    car(ctx, x, y, 0.62, ang, puff, t)
    if 2.7 < t < 3.2:
        for k in range(4):
            ph = (t - 2.7) / 0.5; circle(ctx, x - 60 - k * 20 - ph * 40, 1590 - ph * 30 - k * 5, 16 + ph * 22, (1, 1, 1, 0.6 * (1 - ph)))
    if 0.55 < t < 3.2: wren(ctx, 985, 1790, 0.62, t, "cheer", expr="shock" if t < 2.8 else "happy")
    else: wren(ctx, 985, 1790, 0.62, t, "point", hand=L_REST, expr="happy")
    if t >= 3.2: pass
    e4.bubble(ctx, 700, 1330, "That’s a hop, darling.", 44, ease((t - 3.5) / 0.3), (900, 1440))
    a = ease(t / 0.3); e4.top_box(ctx, a, 380)
    ctext(ctx, "THE DEMO", 215, 44, hexc(RED, a), maxw=900)
    ctext(ctx, "It hopped over cars.", 305, 62, hexc('#22223b', a), maxw=900)
    ctext(ctx, "Nobody was driving.", 415, 54, hexc(RED, ease((t - 2.0) / 0.4)), maxw=900)
    share_pill(ctx, t); ai_tag(ctx, y=1860)

def s3(ctx, t, d):
    e4.begin_set(ctx); street(ctx, t)
    ctx.rectangle(872, 1250, 14, 340); ctx.set_source_rgba(*hexc('#6c757d')); ctx.fill()
    rrect(ctx, 820, 1180, 120, 86, 12); ctx.set_source_rgba(*hexc('#1f55a8')); ctx.fill()
    mv.font(ctx, 30); e = ctx.text_extents("PLAN B"); ctx.move_to(880 - e.x_advance / 2, 1232); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text("PLAN B")
    bx = -420 + (400 + 420) * ease(t / 1.6) if t < 3.0 else 400 + 1200 * ease((t - 3.0) / 1.3)
    on_board = t > 2.0
    mv.suitcase(ctx, 650, 1590, 0.45, t) if not on_board else None
    if not on_board:
        wren(ctx, 740, 1590, 0.8, t, "wave", expr="happy")
    bus(ctx, bx, 1620)
    if on_board: mini_head(ctx, bx + 20, 1432, 1.0)
    e4.end_set(ctx)
    a = ease(t / 0.3); e4.top_box(ctx, a, 380)
    ctext(ctx, "WREN’S RULE", 215, 44, hexc(RED, a), maxw=900)
    ctext(ctx, "Always have a Plan B.", 305, 62, hexc('#22223b', a), maxw=900)
    ctext(ctx, "Bus: 2 hours late. Still beat 2028.", 405, 46, hexc(RED, ease((t - 2.2) / 0.4)), maxw=900)
    share_pill(ctx, t); ai_tag(ctx, y=1860)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    hop = abs(math.sin(t * 3.2)) * 150
    car(ctx, (t * 170) % (W + 500) - 250, 1790 - hop, 0.5, -0.12 if math.cos(t * 3.2) > 0 else 0.12, 1.0 if hop > 30 else 0.0, t)
    pop = ease(t / 0.5)
    wren(ctx, 540, 1600, 1.1 * (0.9 + 0.1 * pop), t, "wave")
    a = ease((t - 0.2) / 0.4)
    ctext(ctx, "Send this to someone still waiting for a flying car", 210 - (1 - a) * 30, 56, hexc('#22223b', a), maxw=900, lh=1.2)
    a2 = ease((t - 1.0) / 0.4)
    mv.font(ctx, 54); s2_ = "@wrentrips"; e = ctx.text_extents(s2_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 500, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 568); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s2_)
    ctext(ctx, "Follow for the next disaster", 690, 44, hexc('#5c2a1e', ease((t - 1.6) / 0.4)), bold=False)
    ai_tag(ctx, y=1890, dark=True)

SCENES = [(s0, 3.5), (s1, 4.5), (s2, 5.0), (s3, 4.5), (s4, 4.0)]

def frame(fn, t, d):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    fn(ctx, t, d)
    a_in = 0 if fn is s0 else 1 - t / 0.25
    a_out = (t - (d - 0.6)) / 0.6 if fn is s4 else (t - (d - 0.2)) / 0.2
    a = max(a_in, a_out, 0)
    if a > 0:
        ctx.set_source_rgba(*hexc('#fff3e0', min(1, ease(a)))); ctx.paint()
    return surf

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        from PIL import Image
        picks = [(s0, 2.4), (s1, 0.9), (s1, 3.6), (s2, 0.9), (s2, 1.9), (s2, 2.3), (s2, 4.3), (s3, 1.0), (s3, 2.8), (s3, 4.0), (s4, 3.0)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((270, 480)))
        c = Image.new("RGB", (280 * 6, 490 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 6) * 280, (i // 6) * 490))
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

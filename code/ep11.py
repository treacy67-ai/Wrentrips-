import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ai_tag, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, pill, header
from ep9 import bubble_ml
ai_tag = lambda *a, **k: None   # no burned-in tag (profile-level AI label is used)

OUT = "/home/claude/wren/ep11"
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'
WX, LX, GY = 400, 660, 1520
WS, LS = 0.8, 1.0
ROAD_Y = 1760
def clamp01(x): return max(0.0, min(1.0, x))

# ---------------------------------------------------------------- environment
def street(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, 1380); g.add_color_stop_rgb(0, *hexc('#6f8197')[:3]); g.add_color_stop_rgb(1, *hexc('#b5c2ce')[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1400); ctx.fill()
    rng = random.Random(5)
    x = -20
    while x < W:                                                   # buildings
        bw = rng.randint(150, 230); bh = rng.randint(380, 700)
        ctx.rectangle(x, 1400 - bh, bw, bh); ctx.set_source_rgba(*hexc(rng.choice(['#56677d', '#4a5a70', '#617289']))); ctx.fill()
        for wy in range(1400 - bh + 40, 1360, 70):
            for wx in range(int(x) + 22, int(x + bw - 30), 54):
                lit = rng.random() < 0.35
                ctx.rectangle(wx, wy, 30, 40); ctx.set_source_rgba(*hexc('#ffd98a' if lit else '#3d4b60', 0.9 if lit else 0.8)); ctx.fill()
        x += bw + 6
    ctx.rectangle(0, 1380, W, 200); ctx.set_source_rgba(*hexc('#b9b2a8')); ctx.fill()                # pavement
    for xx in range(0, W, 140): ctx.move_to(xx, 1380); ctx.line_to(xx - 30, 1580); ctx.set_line_width(3); ctx.set_source_rgba(0, 0, 0, 0.08); ctx.stroke()
    ctx.rectangle(0, 1562, W, 34); ctx.set_source_rgba(*hexc('#8a847b')); ctx.fill()                  # kerb
    ctx.rectangle(0, 1596, W, H - 1596); ctx.set_source_rgba(*hexc('#3b3f4a')); ctx.fill()           # road
    ctx.set_source_rgba(1, 1, 1, 0.55)
    for xx in range(-60, W, 220): ctx.rectangle(xx, 1860, 120, 12)
    ctx.fill()
    e4.ell(ctx, 540, ROAD_Y + 8, 300, 26, hexc('#5a6b80', 0.95)); e4.ell(ctx, 520, ROAD_Y + 2, 210, 12, hexc('#8fa6bd', 0.6))   # puddle
    # street lamp
    ctx.rectangle(968, 760, 14, 800); ctx.set_source_rgba(*hexc('#2d3340')); ctx.fill()
    rrect(ctx, 930, 740, 92, 28, 12); ctx.set_source_rgba(*hexc('#2d3340')); ctx.fill()
    gl = cairo.RadialGradient(975, 780, 6, 975, 780, 230); gl.add_color_stop_rgba(0, 1, 0.9, 0.55, 0.55); gl.add_color_stop_rgba(1, 1, 0.9, 0.55, 0)
    ctx.set_source(gl); ctx.rectangle(740, 560, 340, 440); ctx.fill()

def rain(ctx, t, heavy=1.0):
    rng = random.Random(11)
    ctx.set_line_width(3); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(int(110 * heavy)):
        x = rng.uniform(-100, W + 100); y0 = rng.uniform(0, H); sp = rng.uniform(1500, 2200)
        y = (y0 + t * sp) % (H + 200) - 100
        ctx.set_source_rgba(1, 1, 1, rng.uniform(0.2, 0.45)); ctx.move_to(x + y * 0.12, y); ctx.line_to(x + y * 0.12 - 9, y + 46); ctx.stroke()

def car(ctx, x, col, t, glow=True):
    base = 1790
    ctx.save(); ctx.translate(x, 0)
    ctx.set_source_rgba(0, 0, 0, 0.25); e4.ell(ctx, 0, base + 4, 250, 14, (0, 0, 0, 0.25))
    rrect(ctx, -230, base - 128, 460, 84, 30); ctx.set_source_rgba(*hexc(col)); ctx.fill()                  # body
    ctx.move_to(-130, base - 128); ctx.line_to(-80, base - 200); ctx.line_to(80, base - 200); ctx.line_to(150, base - 128); ctx.close_path()
    ctx.set_source_rgba(*hexc(col)); ctx.fill()
    ctx.move_to(-110, base - 134); ctx.line_to(-70, base - 190); ctx.line_to(-6, base - 190); ctx.line_to(-6, base - 134); ctx.close_path(); ctx.set_source_rgba(*hexc('#cfe8f7')); ctx.fill()
    ctx.move_to(6, base - 134); ctx.line_to(6, base - 190); ctx.line_to(72, base - 190); ctx.line_to(126, base - 134); ctx.close_path(); ctx.fill()
    for wx in (-135, 135):
        circle(ctx, wx, base - 44, 46, hexc('#15171c')); circle(ctx, wx, base - 44, 26, hexc('#b8bec9'))
        ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#6c7380'))
        for k in range(4):
            a = k * math.pi / 2 + t * 30; ctx.move_to(wx, base - 44); ctx.line_to(wx + 24 * math.cos(a), base - 44 + 24 * math.sin(a)); ctx.stroke()
    rrect(ctx, 214, base - 112, 24, 20, 8); ctx.set_source_rgba(*hexc('#fff3b0')); ctx.fill()
    rrect(ctx, -238, base - 112, 18, 20, 8); ctx.set_source_rgba(*hexc('#ff3b30')); ctx.fill()
    if glow:
        gl = cairo.LinearGradient(236, 0, 520, 0); gl.add_color_stop_rgba(0, 1, 0.95, 0.6, 0.45); gl.add_color_stop_rgba(1, 1, 0.95, 0.6, 0)
        ctx.move_to(236, base - 106); ctx.line_to(520, base - 150); ctx.line_to(520, base - 40); ctx.line_to(236, base - 94); ctx.close_path(); ctx.set_source(gl); ctx.fill()
    ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.5)
    for k in range(4): ctx.move_to(-250 - k * 40, base - 150 + k * 26); ctx.line_to(-380 - k * 40, base - 150 + k * 26); ctx.stroke()
    ctx.restore()

def splash(ctx, cx, u, width, maxh, seed=0, tint=(0.58, 0.80, 0.96)):
    if u < 0 or u > 1.7: return
    rise = ease(clamp01(u / 0.28)); fall = ease(clamp01((u - 0.8) / 0.8))
    h = maxh * rise * (1 - 0.9 * fall); al = 0.93 * (1 - 0.85 * fall)
    N = 40
    for layer, (sc, a2) in enumerate(((1.0, al), (0.72, al * 0.35))):
        ctx.move_to(cx - width / 2, ROAD_Y + 20)
        for i in range(N + 1):
            x = cx - width / 2 + width * i / N
            prof = math.sin(math.pi * i / N) ** 0.55
            jag = 1 + 0.05 * math.sin(i * 1.3 + u * 14 + seed) + 0.025 * math.sin(i * 3.1 + u * 9)
            ctx.line_to(x, ROAD_Y + 20 - h * sc * prof * jag)
        ctx.line_to(cx + width / 2, ROAD_Y + 20); ctx.close_path()
        ctx.set_source_rgba(*(tint if layer == 0 else (1, 1, 1)), a2); ctx.fill()
    rng = random.Random(seed + 3)
    for k in range(46):
        x0 = cx + rng.uniform(-width / 2, width / 2); vx = rng.uniform(-260, 260); vy = -rng.uniform(500, 1500) * (maxh / 800.0 + 0.3)
        y = ROAD_Y + vy * u + 0.5 * 2400 * u * u
        if y < ROAD_Y + 10: circle(ctx, x0 + vx * u, y, rng.uniform(5, 12), (*tint, 0.85))

def drips(ctx, x, ytop, w, t, n=8):
    for k in range(n):
        ph = (t * 1.4 + k / n) % 1.0
        circle(ctx, x + (k - n / 2 + 0.5) * w / n, ytop + ph * 360, 5, hexc('#7fc4ee', 1 - ph))

def puddle_feet(ctx, x, k):
    e4.ell(ctx, x, GY + 12, 40 + 90 * k, 8 + 12 * k, hexc('#6f95b5', 0.55))

def umbrella_closed(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#3d2b1f'))
    ctx.move_to(0, -150); ctx.line_to(0, 70); ctx.arc(-16, 70, 16, 0, math.pi); ctx.stroke()
    ctx.move_to(0, -190); ctx.curve_to(26, -140, 24, -60, 0, -20); ctx.curve_to(-24, -60, -26, -140, 0, -190); ctx.close_path()
    ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    ctx.restore()

def umbrella_shield(ctx, cx, cy, r, t, wet=0.0, hit_u=None):
    if r <= 4: return
    ctx.save(); ctx.translate(cx, cy)
    circle(ctx, 0, 0, r + 8, hexc('#7b1620'))
    for k in range(8):
        a0 = k * math.pi / 4
        ctx.move_to(0, 0); ctx.arc(0, 0, r, a0, a0 + math.pi / 4); ctx.close_path()
        ctx.set_source_rgba(*hexc(RED if k % 2 == 0 else '#fff3e0')); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(0, 0, 0, 0.18)
    for k in range(8): ctx.move_to(0, 0); ctx.line_to(r * math.cos(k * math.pi / 4), r * math.sin(k * math.pi / 4)); ctx.stroke()
    circle(ctx, 0, 0, r * 0.07, hexc('#3d2b1f'))
    if wet > 0:
        rng = random.Random(21)
        for k in range(26):
            a = rng.uniform(-math.pi, 0.1); d = rng.uniform(0.2, 0.95) * r
            circle(ctx, d * math.cos(a), d * math.sin(a) + 4 + wet * 18 * rng.random(), rng.uniform(4, 9), (0.7, 0.88, 1, 0.9 * wet))
    ctx.restore()

def bulb(ctx, x, y, a, t):
    if a <= 0: return
    ctx.save(); ctx.translate(x, y)
    ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#ffd60a', a))
    for k in range(8):
        ang = k * math.pi / 4 + 0.4; ctx.move_to(math.cos(ang) * 52, math.sin(ang) * 52); ctx.line_to(math.cos(ang) * 74, math.sin(ang) * 74); ctx.stroke()
    circle(ctx, 0, 0, 36, hexc('#fff3a0', a)); rrect(ctx, -16, 30, 32, 24, 6); ctx.set_source_rgba(*hexc('#9aa0aa', a)); ctx.fill()
    ctx.restore()

def badge(ctx, text, x, y, t, t0, col='#1f9d6b'):
    k = ease((t - t0) / 0.3)
    if k <= 0: return
    pop = 1 + 0.18 * max(0.0, 1 - (t - t0) / 0.3)
    ctx.save(); ctx.translate(x, y); ctx.scale(pop, pop)
    mv.font(ctx, 72); e = ctx.text_extents(text); w = e.x_advance + 90
    rrect(ctx, -w / 2, -64, w, 128, 64); ctx.set_source_rgba(*hexc(col, k)); ctx.fill()
    ctx.move_to(-e.x_advance / 2, 26); ctx.set_source_rgba(1, 1, 1, k); ctx.show_text(text); ctx.restore()

def duo(ctx, t, wmode="point", wexpr="happy", lexpr="smile", whand=(110, -110), lhand=(0, -150), wflush=0.0, wet=0.0):
    if wet > 0: ctx.push_group()
    wren(ctx, WX, GY, WS, t, wmode, flush=wflush, expr=wexpr, hand=whand)
    kid(ctx, LX, GY, LS, t, lexpr, lhand)
    if wet > 0:
        ctx.set_operator(cairo.OPERATOR_ATOP); ctx.set_source_rgba(0.30, 0.50, 0.80, 0.32 * wet); ctx.paint(); ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.pop_group_to_source(); ctx.paint()

# ---------------------------------------------------------------- scenes
CAR1_TP = 1.0    # car 1 passes the puddle at this time in scene 0
def s0(ctx, t, d):
    street(ctx, t)
    u = t - CAR1_TP
    soaked = u > 0.5
    duo(ctx, t, wexpr="shock" if soaked else "happy", lexpr="flat" if soaked else "smile", wet=ease((u - 0.4) / 0.6) if u > 0.4 else 0.0)
    if not soaked: umbrella_closed(ctx, LX + 22, GY - 150, 0.9)
    else: umbrella_closed(ctx, LX + 22, GY - 150, 0.9)
    if soaked:
        k = clamp01((u - 0.5) / 1.0)
        puddle_feet(ctx, WX, k); puddle_feet(ctx, LX, k)
        drips(ctx, WX, 980, 170, t); drips(ctx, LX, 1130, 130, t, 6)
    splash(ctx, 540, u, 780, 820, seed=1)
    car(ctx, 540 + 1100 * (t - CAR1_TP), '#ffc300', t)
    rain(ctx, t)
    header(ctx, ease(t / 0.2 + 1), "RAINY DAY", "Speeding car. Big puddle.", "Guess who's standing there?", -0.3, t, main_size=54)
    wm(ctx); ai_tag(ctx, y=1860)

def s1(ctx, t, d):
    street(ctx, t)
    duo(ctx, t, wexpr="shock" if t < 0.9 else "happy", lexpr="flat" if t < 0.9 else "smug", wet=1.0)
    puddle_feet(ctx, WX, 1.0); puddle_feet(ctx, LX, 1.0)
    drips(ctx, WX, 980, 170, t); drips(ctx, LX, 1130, 130, t, 6)
    # umbrella opens into a shield
    k = ease((t - 1.2) / 0.7)
    if t < 1.2: umbrella_closed(ctx, LX + 22, GY - 150, 0.9)
    else:
        umbrella_shield(ctx, lerp(LX + 22, 530, k), lerp(GY - 220, 1470, k), 240 * ease((t - 1.2) / 0.5), t)
    bulb(ctx, LX, 1010, ease((t - 0.9) / 0.2) * (1 - ease((t - 1.9) / 0.3)), t)
    # distant headlights
    gl = cairo.RadialGradient(-20, 1700, 10, -20, 1700, 120 + 140 * ease(t / 2.0)); gl.add_color_stop_rgba(0, 1, 0.96, 0.7, 0.9); gl.add_color_stop_rgba(1, 1, 0.96, 0.7, 0)
    ctx.set_source(gl); ctx.rectangle(-60, 1500, 420, 400); ctx.fill()
    rain(ctx, t)
    header(ctx, ease(t / 0.2), "NEXT CAR IS COMING", "Leo has a plan.", "Watch the umbrella.", 1.4, t)
    pill(ctx, t, "Wait for the ending", 0.4); wm(ctx); ai_tag(ctx, y=1860)

CAR2_TP = 1.2
def s2(ctx, t, d):
    street(ctx, t)
    u = t - CAR2_TP
    duo(ctx, t, wmode="cheer" if t > 2.1 else "point", wexpr="shock" if 0.9 < t < 2.0 else "happy", lexpr="smug", whand=(110, -110), wet=1.0)
    puddle_feet(ctx, WX, 1.0); puddle_feet(ctx, LX, 1.0)
    splash(ctx, 530, u, 520, 520, seed=4)
    wet = clamp01(u / 0.5) * (1 - clamp01((u - 1.2) / 0.8))
    umbrella_shield(ctx, 530, 1470, 240, t, wet=wet)
    car(ctx, 540 + 1100 * (t - CAR2_TP), '#4361ee', t)
    rain(ctx, t)
    header(ctx, ease(t / 0.2), "THE PLAN", "Umbrella as a shield", "Not a drop.", 2.2, t)
    badge(ctx, "SAVED!", 540, 640, t, 2.2)
    wm(ctx); ai_tag(ctx, y=1860)

def s3(ctx, t, d):
    street(ctx, t)
    duo(ctx, t, wmode="cheer", wexpr="happy", lexpr="smug", wet=1.0)
    puddle_feet(ctx, WX, 1.0); puddle_feet(ctx, LX, 1.0)
    umbrella_shield(ctx, 530, 1470, 240, t, wet=max(0.0, 1 - t / 1.0))
    rain(ctx, t)
    header(ctx, ease(t / 0.2), "RESULT", "Umbrella 1 - Car 0", "Still wet. Still winning.", 1.0, t)
    bubble_ml(ctx, 400, 840, ["Leo, you're a genius!"], 40, ease((t - 0.3) / 0.25), (WX, 975))
    bubble_ml(ctx, 760, 990, ["Obviously."], 40, ease((t - 1.5) / 0.25), (LX, 1120))
    wm(ctx); ai_tag(ctx, y=1860)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    a = ease(t / 0.3)
    ctext(ctx, "Umbrellas aren't for rain.", 205 - (1 - a) * 20, 60, hexc('#22223b', a), maxw=940)
    ctext(ctx, "They're for cars.", 290, 62, hexc(RED, ease((t - 0.5) / 0.3)), maxw=900)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Send this to someone who always gets splashed", 625, 36, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=960)
    ai_tag(ctx, y=1890, dark=True)

def lerp(a, b, k): return a + (b - a) * k

SCENES = [(s0, 2.6), (s1, 3.0), (s2, 3.4), (s3, 3.0), (s4, 2.6)]

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
        picks = [(s0, 0.7), (s0, 1.3), (s0, 2.3), (s1, 1.0), (s1, 2.4), (s2, 0.9), (s2, 1.6), (s2, 2.6), (s3, 1.8), (s4, 2.0)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((300, 533)))
        c = Image.new("RGB", (310 * 5, 543 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 5) * 310, (i // 5) * 543))
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

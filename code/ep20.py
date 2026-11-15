"""ep20 - Baggage claim: every suitcase is black. Wren's is hand-knitted."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep20")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1700
BELT_Y = 1185
WX, LX = 392, 910

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

def txt(ctx, s, x, y, size, col, center=False):
    mv.font(ctx, size); e = ctx.text_extents(s); ctx.move_to(x - (e.x_advance / 2 if center else 0), y); ctx.set_source_rgba(*col); ctx.show_text(s)

KNIT = ['#ff4fa3', '#ffd60a', '#4cc9f0', '#7ae582', '#ff8c42', '#b388ff']
def pompom(ctx, x, y, r, col):
    circle(ctx, x, y, r, hexc(col))
    for k in range(8):
        a = k * math.pi / 4; circle(ctx, x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8, r * 0.42, hexc(col))
    circle(ctx, x - r * 0.25, y - r * 0.3, r * 0.3, (1, 1, 1, 0.35))

def suitcase(ctx, x, y, s=1.0, style='black', t=0.0, open_=0.0):
    """bottom-centre at (x, y)."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#6b7280'))
    ctx.move_to(-28, -185); ctx.line_to(-28, -222); ctx.line_to(28, -222); ctx.line_to(28, -185); ctx.stroke()
    for dx in (-40, 40): circle(ctx, dx, -8, 11, hexc('#15171c'))
    body = '#23262f' if style == 'black' else KNIT[0]
    rrect(ctx, -65, -185, 130, 170, 22); ctx.set_source_rgba(*hexc(body)); ctx.fill()
    if style == 'black':
        for dx in (-30, 0, 30): rrect(ctx, dx - 4, -170, 8, 140, 4); ctx.set_source_rgba(*hexc('#343844')); ctx.fill()
    else:
        ctx.save(); rrect(ctx, -65, -185, 130, 170, 22); ctx.clip()
        cols = KNIT if style == 'leo' else ['#ff4fa3', '#ffd60a', '#ff4fa3', '#4cc9f0']
        for i in range(9):
            ctx.rectangle(-65, -185 + i * 19, 130, 19); ctx.set_source_rgba(*hexc(cols[i % len(cols)])); ctx.fill()
        ctx.set_line_width(2.5); ctx.set_source_rgba(1, 1, 1, 0.45)                     # knit stitches
        for i in range(9):
            for j in range(9):
                cx_, cy_ = -65 + j * 16 + 4, -185 + i * 19 + 4
                ctx.move_to(cx_, cy_); ctx.line_to(cx_ + 5, cy_ + 10); ctx.line_to(cx_ + 10, cy_); ctx.stroke()
        if style == 'leo':
            rrect(ctx, -65, -128, 130, 56, 0); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        ctx.restore()
        if style == 'leo':
            txt(ctx, "LEO", 0, -84, 40, hexc(RED), True)
            pompom(ctx, 0, -232, 26, '#ffd60a'); pompom(ctx, -62, -185, 17, '#4cc9f0'); pompom(ctx, 62, -185, 17, '#ff4fa3')
        else:
            ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#8a5a2b')); ctx.move_to(50, -185); ctx.line_to(50, -262); ctx.stroke()
            wv = 6 * math.sin(t * 6)
            ctx.move_to(50, -262); ctx.line_to(118, -246 + wv); ctx.line_to(50, -224); ctx.close_path(); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
            pompom(ctx, 0, -232, 26, '#4cc9f0'); pompom(ctx, -62, -185, 18, '#ffd60a'); pompom(ctx, 62, -20, 18, '#7ae582'); pompom(ctx, -62, -20, 18, '#ff8c42')
            on = int(t * 5) % 2                                                          # fairy lights
            for i in range(6):
                lit = (i + on) % 2 == 0
                circle(ctx, -52 + i * 21, -100 + 8 * math.sin(i * 1.3), 7, hexc('#fff3b0' if lit else '#c9367f'))
                if lit: circle(ctx, -52 + i * 21, -100 + 8 * math.sin(i * 1.3), 13, hexc('#fff3b0', 0.35))
    if open_ > 0:
        rrect(ctx, -55, -175, 110, 150, 14); ctx.set_source_rgba(*hexc('#0c0d12', open_)); ctx.fill()
        ctx.move_to(-65, -180); ctx.line_to(-65 - 105 * open_, -200); ctx.line_to(-65 - 105 * open_, -28); ctx.line_to(-65, -20); ctx.close_path()
        ctx.set_source_rgba(*hexc('#2f333e')); ctx.fill()
    ctx.restore()

def duck(ctx, x, y, s=1.0, flip=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s * flip, s)
    e4.ell(ctx, 0, 0, 34, 25, hexc('#ffd60a')); circle(ctx, 22, -28, 19, hexc('#ffd60a'))
    ctx.move_to(-20, -6); ctx.line_to(-44, -22); ctx.line_to(-24, 8); ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd60a')); ctx.fill()
    ctx.move_to(38, -30); ctx.line_to(56, -24); ctx.line_to(38, -18); ctx.close_path(); ctx.set_source_rgba(*hexc('#ff8c42')); ctx.fill()
    circle(ctx, 26, -33, 4, hexc('#22223b'))
    ctx.restore()

# ------------------------------------------------------------ baggage hall
def hall_bg(ctx, t, belt_off=0.0):
    mv.vgrad(ctx, '#e6eef7', '#cddbea')
    rrect(ctx, 90, 640, 540, 130, 20); ctx.set_source_rgba(*hexc('#1a1c2e')); ctx.fill()               # sign
    txt(ctx, "BAGGAGE CLAIM", 120, 722, 44, hexc('#ffd166'))
    circle(ctx, 572, 705, 40, hexc('#ffd166')); txt(ctx, "4", 572, 722, 46, hexc('#1a1c2e'), True)
    rrect(ctx, 720, 640, 290, 190, 16); ctx.set_source_rgba(*hexc('#1a1c2e')); ctx.fill()               # arrivals screen
    for i in range(4):
        rrect(ctx, 740, 662 + i * 40, 150, 22, 6); ctx.set_source_rgba(*hexc('#4cc9f0' if i != 1 else '#ffd166', 0.9)); ctx.fill()
        rrect(ctx, 910, 662 + i * 40, 80, 22, 6); ctx.set_source_rgba(*hexc('#7ae582' if (i + int(t)) % 3 else '#ff8c42', 0.9)); ctx.fill()
    rrect(ctx, 930, 960, 200, 240, 24); ctx.set_source_rgba(*hexc('#8d99a8')); ctx.fill()               # hatch
    rrect(ctx, 950, 985, 160, 200, 12); ctx.set_source_rgba(*hexc('#15171c')); ctx.fill()
    for i in range(5):
        sw = 6 * math.sin(t * 5 + i)
        ctx.move_to(954 + i * 31, 985); ctx.line_to(982 + i * 31, 985); ctx.line_to(982 + i * 31 + sw, 1180); ctx.line_to(954 + i * 31 + sw, 1180); ctx.close_path()
        ctx.set_source_rgba(*hexc('#3a3f4b')); ctx.fill()
    rrect(ctx, -30, BELT_Y - 40, W + 60, 80, 16); ctx.set_source_rgba(*hexc('#3a3f4b')); ctx.fill()     # belt
    for k in range(14):
        x = (k * 100 - belt_off) % 1400 - 150
        ctx.move_to(x, BELT_Y - 38); ctx.line_to(x - 26, BELT_Y + 38); ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#2a2e37')); ctx.stroke()
    ctx.rectangle(-30, BELT_Y + 30, W + 60, 230); ctx.set_source_rgba(*hexc('#b9c3cf')); ctx.fill()
    ctx.rectangle(-30, BELT_Y + 30, W + 60, 14); ctx.set_source_rgba(*hexc('#e9eef3')); ctx.fill()
    for k in range(18):
        ctx.rectangle(k * 64 - 20, 1392, 32, 28); ctx.set_source_rgba(*hexc('#ffd60a')); ctx.fill()
        ctx.rectangle(k * 64 + 12, 1392, 32, 28); ctx.set_source_rgba(*hexc('#22223b')); ctx.fill()
    ctx.rectangle(0, 1420, W, H - 1420); ctx.set_source_rgba(*hexc('#d8d3cb')); ctx.fill()               # floor
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#c6c0b6'))
    for k in range(7): ctx.move_to(k * 180, 1420); ctx.line_to(k * 220 - 120, H); ctx.stroke()
    for yy in (1560, 1760): ctx.move_to(0, yy); ctx.line_to(W, yy); ctx.stroke()

def belt_bags(ctx, t, speed=140, skip=()):
    off = t * speed
    for k in range(7):
        if k in skip: continue
        x = (k * 200 - off) % 1400 - 150
        suitcase(ctx, x, BELT_Y, 1.0, 'black')
    return off

def s0(ctx, t, d):
    hall_bg(ctx, t, t * 140); belt_bags(ctx, t)
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy", hand=(150, -330))
    cx, cy = WX + 150 * 1.1 + 6, GY - 330 * 1.1                                    # teacup, of course
    rrect(ctx, cx - 30, cy - 50, 60, 50, 12); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill(); e4.ell(ctx, cx, cy + 4, 50, 9, (1, 1, 1, 1))
    look = 40 * math.sin(t * 3.2)
    kid(ctx, LX, GY, 0.95, t, "flat" if t > 1.6 else "smile", (-60 + look, -210))
    bubble_ml(ctx, 760, 900, ["Mine's the", "black one."], 44, ramp(t, 2.3, 2.5), (LX, GY - 400))
    header(ctx, ease(t / 0.2 + 1), "BAGGAGE CLAIM", "Every suitcase is black.", "Which one is Leo's?", -0.3, t, main_size=56)
    meter(ctx, "BLACK SUITCASES", "%d" % int(3 + 44 * clamp01(t / 3.0))); wm(ctx)

random.seed(7)
DUCKS = [(1.2 + 0.13 * i, random.uniform(-120, 110), random.uniform(-640, -470), random.choice((-1, 1))) for i in range(8)]
def s1(ctx, t, d):
    hall_bg(ctx, t, t * 140); belt_bags(ctx, t, skip=(2,))
    wren(ctx, WX, GY, 1.1, t, "point", expr="shock" if 1.2 < t < 2.6 else "happy", hand=(150, -330))
    cx, cy = WX + 150 * 1.1 + 6, GY - 330 * 1.1
    rrect(ctx, cx - 30, cy - 50, 60, 50, 12); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill(); e4.ell(ctx, cx, cy + 4, 50, 9, (1, 1, 1, 1))
    bx = lerp(790, 655, ramp(t, 0.15, 0.8)); by = lerp(BELT_Y, GY + 30, ramp(t, 0.15, 0.8))
    op = ramp(t, 1.0, 1.25)
    suitcase(ctx, bx, by, 1.35, 'black', t, open_=op)
    if 1.15 < t < 1.5: burst(ctx, bx, by - 130, 1 - (t - 1.15) / 0.35, 150)
    g = 900.0; y0 = by - 130;
    for i, (t0, vx, vy, fl) in enumerate(DUCKS):
        dt = t - t0
        if dt < 0: continue
        floor = GY + 60 + (i % 3) * 38
        tl = (-vy + math.sqrt(vy * vy + 2 * g * (floor - y0))) / g
        dd = min(dt, tl)
        x = bx + vx * dd * 1.6; y = y0 + vy * dd + 0.5 * g * dd * dd
        hop = 14 * abs(math.sin((t - t0 - tl) * 7)) * math.exp(-(dt - tl) * 2) if dt > tl else 0
        duck(ctx, x, y - hop, 0.95, fl)
    kid(ctx, LX, GY, 0.95, t, "flat" if t > 1.2 else "smile", (-90, -180))
    bubble_ml(ctx, 770, 900, ["I don't", "own ducks."], 44, ramp(t, 1.7, 1.9) * (1 - ramp(t, 3.0, 3.15)), (LX, GY - 400))
    bubble_ml(ctx, 500, 830, ["Wrong black", "one, dear."], 44, ramp(t, 3.15, 3.35), (WX + 60, GY - 700))
    header(ctx, ease(t / 0.2), "ATTEMPT ONE", "Leo grabs a black one.", "It is full of ducks.", 1.3, t, main_size=56)
    n = 0 if t < 1.1 else (1 if t < 3.2 else 3)
    meter(ctx, "WRONG BAGS OPENED", "%d" % n); wm(ctx)

def s2(ctx, t, d):
    k = ramp(t, 0.1, 1.5); P = 560 * (1 - k)
    hall_bg(ctx, t, -P)
    for fx in (40, 250, 480, 960, 1170): suitcase(ctx, fx + P, BELT_Y, 1.0, 'black')
    wbx = 725 + P
    if 1.45 < t < 2.0: burst(ctx, wbx, BELT_Y - 150, 1 - (t - 1.45) / 0.55, 260)
    suitcase(ctx, wbx, BELT_Y + 4, 1.5, 'wren', t)
    for i in range(6):                                                             # sparkles
        ph = (t * 0.9 + i / 6) % 1; a = i * 1.05 + 0.4
        if t > 1.4: circle(ctx, wbx + math.cos(a) * (150 + 60 * ph), BELT_Y - 160 + math.sin(a) * (170 + 60 * ph), 9 * (1 - ph), hexc('#ffd60a', 1 - ph))
    wren(ctx, WX, GY, 1.1, t, "cheer" if t > 1.5 else "point", expr="happy", hand=(150, -330))
    kid(ctx, LX, GY, 0.95, t, "flat" if t > 1.3 else "smile", (0, -150))
    bubble_ml(ctx, 830, 745, ["That is SO", "embarrassing."], 42, ramp(t, 1.8, 2.0) * (1 - ramp(t, 3.0, 3.15)), (LX, GY - 400))
    bubble_ml(ctx, 450, 800, ["That is so", "findable."], 44, ramp(t, 3.15, 3.35), (WX + 60, GY - 700))
    header(ctx, ease(t / 0.2), "THEN WREN'S BAG ARRIVES", "Hand-knitted. With lights.", "Visible from the plane.", 1.5, t, main_size=54)
    meter(ctx, "TIME TO FIND IT", "0.2 sec"); wm(ctx)

def s3(ctx, t, d):
    hall_bg(ctx, t, t * 140); belt_bags(ctx, t, skip=(1, 4))
    wren(ctx, WX, GY, 1.1, t, "cheer" if 1.0 < t < 2.4 else "point", expr="happy", hand=(150, -330))
    bx, by = 655, GY + 30
    drop = ramp(t, 0.5, 1.0)
    suitcase(ctx, bx, by, 1.45, 'leo' if t >= 1.0 else 'black', t)
    if t < 1.0:                                                                    # the cosy descends
        ctx.save(); ctx.rectangle(0, by - 360, W, 20 + 345 * drop); ctx.clip()
        suitcase(ctx, bx, by, 1.45, 'leo', t); ctx.restore()
    if 1.0 < t < 1.5: burst(ctx, bx, by - 150, 1 - (t - 1.0) / 0.5, 240)
    kid(ctx, LX, GY, 0.95, t, "smile" if t < 0.9 else "flat", (0, -150))
    if t > 1.2:                                                                    # sweat drop
        ph = ((t - 1.2) * 1.2) % 1; circle(ctx, LX + 66, GY - 330 + 40 * ph, 9, hexc('#4cc9f0', 1 - ph))
    bubble_ml(ctx, 500, 830, ["I knitted", "yours too!"], 44, ramp(t, 1.2, 1.4) * (1 - ramp(t, 2.5, 2.65)), (WX + 60, GY - 700))
    bubble_ml(ctx, 780, 900, ["Can I lose it?"], 44, ramp(t, 2.7, 2.9), (LX, GY - 400))
    header(ctx, ease(t / 0.2), "WREN'S FIX", "One for Leo too.", "With his name on it.", 1.2, t, main_size=56)
    meter(ctx, "LEO'S DIGNITY", "%d%%" % int(100 * (1 - ramp(t, 0.6, 1.8)))); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    suitcase(ctx, 850, 1660, 1.3, 'leo', t)
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “Now you can't lose it.”", 205 - (1 - a) * 20, 60, hexc('#22223b', a), maxw=980)
    ctext(ctx, "Leo: “Watch me.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "How do you spot your bag? Comment below", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 1.5), (s0, 3.2), (s1, 0.6), (s1, 1.5), (s1, 2.4), (s1, 3.9), (s2, 0.7), (s2, 1.7), (s2, 2.6), (s2, 3.9), (s3, 0.75), (s3, 1.8), (s3, 3.5), (s4, 2.6)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((300, 533)))
        c = Image.new("RGB", (310 * 8, 543 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 8) * 310, (i // 8) * 543))
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

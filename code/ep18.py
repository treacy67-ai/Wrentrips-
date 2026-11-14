import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = "/home/claude/wren/ep18"
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1700

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

def croissant(ctx, x, y, s=1.0, ang=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(34); ctx.set_source_rgba(*hexc('#c9822f')); ctx.arc(0, 26, 44, math.radians(200), math.radians(340)); ctx.stroke()
    ctx.set_line_width(24); ctx.set_source_rgba(*hexc('#eab35a')); ctx.arc(0, 26, 44, math.radians(204), math.radians(336)); ctx.stroke()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#b06f24'))
    for a in (235, 258, 282, 305):
        r = math.radians(a); ctx.move_to(math.cos(r) * 33, 26 + math.sin(r) * 33); ctx.line_to(math.cos(r) * 55, 26 + math.sin(r) * 55); ctx.stroke()
    ctx.restore()

def bag(ctx, x, y, s=1.0, bulge=0.0, open_=True):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    w = 120 + 40 * bulge
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#5a2d1a')); ctx.arc(0, -150, 70, math.pi, 0); ctx.stroke()
    ctx.move_to(-95, -150); ctx.curve_to(-w - 30, -90, -w - 20, 0, -w + 10, 0); ctx.line_to(w - 10, 0); ctx.curve_to(w + 20, 0, w + 30, -90, 95, -150); ctx.close_path()
    ctx.set_source_rgba(*hexc('#8a4b2a')); ctx.fill()
    if open_: e4.ell(ctx, 0, -150, 95, 20, hexc('#2e150b'))
    rrect(ctx, -22, -100, 44, 34, 8); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    ctx.restore()

def waiter(ctx, x, gy, t, tray=True):
    b = 4 * math.sin(t * 6)
    for dx in (-26, 26): rrect(ctx, x + dx - 18, gy - 260, 36, 250, 14); ctx.set_source_rgba(*hexc('#1d1d2c')); ctx.fill()
    for dx in (-30, 30): e4.ell(ctx, x + dx, gy - 6, 36, 16, hexc('#111111'))
    rrect(ctx, x - 78, gy - 520 + b, 156, 290, 40); ctx.set_source_rgba(*hexc('#1d1d2c')); ctx.fill()
    ctx.move_to(x - 34, gy - 520 + b); ctx.line_to(x + 34, gy - 520 + b); ctx.line_to(x, gy - 380 + b); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.move_to(x - 24, gy - 500 + b); ctx.line_to(x, gy - 488 + b); ctx.line_to(x - 24, gy - 476 + b); ctx.close_path(); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    ctx.move_to(x + 24, gy - 500 + b); ctx.line_to(x, gy - 488 + b); ctx.line_to(x + 24, gy - 476 + b); ctx.close_path(); ctx.fill()
    circle(ctx, x, gy - 600 + b, 76, hexc('#c98d5e'))
    ctx.arc(x, gy - 618 + b, 78, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc('#2a1a10')); ctx.fill()
    for dx in (-26, 26): circle(ctx, x + dx, gy - 600 + b, 8, hexc('#1d1d2c'))
    ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#1d1d2c')); ctx.arc(x, gy - 575 + b, 22, 0.2, math.pi - 0.2); ctx.stroke()
    ctx.set_line_width(40); ctx.set_source_rgba(*hexc('#1d1d2c'))
    if tray:
        ctx.move_to(x + 70, gy - 480 + b); ctx.line_to(x + 130, gy - 560 + b); ctx.stroke(); circle(ctx, x + 130, gy - 565 + b, 22, hexc('#c98d5e'))
        e4.ell(ctx, x + 130, gy - 592 + b, 90, 14, hexc('#cfd6de'))
        ctx.arc(x + 130, gy - 600 + b, 56, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc('#e6ebf0')); ctx.fill(); circle(ctx, x + 130, gy - 660 + b, 10, hexc('#cfd6de'))

# ------------------------------------------------------------ buffet room
def buffet_bg(ctx, t, table=True):
    mv.vgrad(ctx, '#ffe9c9', '#ffd9a8')
    for wx in (90, 600):                                                      # windows with morning light
        rrect(ctx, wx, 640, 390, 420, 24); ctx.set_source_rgba(*hexc('#bfe9ff')); ctx.fill()
        circle(ctx, wx + 290, 760, 46, hexc('#fff3b0'))
        ctx.set_line_width(12); ctx.set_source_rgba(1, 1, 1, 1); rrect(ctx, wx, 640, 390, 420, 24); ctx.stroke()
        ctx.move_to(wx + 195, 640); ctx.line_to(wx + 195, 1060); ctx.stroke()
    ctx.rectangle(0, 1420, W, H - 1420); ctx.set_source_rgba(*hexc('#c98f5c')); ctx.fill()
    for k in range(8): ctx.rectangle(k * 150 - 20, 1420, 6, H - 1420); ctx.set_source_rgba(*hexc('#b57a48')); ctx.fill()
    if table:
        rrect(ctx, -30, 1130, W + 60, 70, 16); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        ctx.rectangle(-30, 1180, W + 60, 260); ctx.set_source_rgba(*hexc('#fff8ee')); ctx.fill()
        for k in range(12):
            ctx.move_to(k * 100 - 20, 1440); ctx.curve_to(k * 100 + 10, 1480, k * 100 + 60, 1480, k * 100 + 80, 1440); ctx.set_source_rgba(*hexc('#fff8ee')); ctx.fill()
        for dx in (150, 420):                                                 # chafing dishes
            rrect(ctx, dx - 100, 1080, 200, 56, 14); ctx.set_source_rgba(*hexc('#b8c0c8')); ctx.fill()
            ctx.arc(dx, 1080, 96, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc('#dfe5ea')); ctx.fill(); circle(ctx, dx, 978, 12, hexc('#b8c0c8'))
            for k in range(3):
                ph = (t * 0.7 + k / 3) % 1; circle(ctx, dx - 30 + k * 30 + 8 * math.sin(t * 3 + k), 960 - ph * 70, 10 + 8 * ph, (1, 1, 1, 0.5 * (1 - ph)))
        e4.ell(ctx, 700, 1120, 120, 26, hexc('#8a5a2b'))                      # bread basket
        for k in range(4): croissant(ctx, 640 + k * 40, 1060 - (k % 2) * 16, 0.8, 0.3 * (k - 1.5))
        for k, c in enumerate(('#ff8c42', '#ffd60a', '#e63946')):             # juice
            rrect(ctx, 880 + k * 62, 1010, 50, 120, 10); ctx.set_source_rgba(*hexc(c, 0.9)); ctx.fill()
            rrect(ctx, 880 + k * 62, 990, 50, 26, 8); ctx.set_source_rgba(*hexc('#b8c0c8')); ctx.fill()

FOOD = ['#e9b96e', '#f4d58d', '#c9822f', '#fff6e0', '#a0522d', '#eab35a', '#ffd60a', '#e9b96e', '#d94f4f', '#f4d58d', '#c9822f', '#fff6e0', '#eab35a', '#7ac143']
def plate_stack(ctx, x, y, n, t, s=1.0):
    e4.ell(ctx, x, y, 110 * s, 20 * s, (1, 1, 1, 1)); e4.ell(ctx, x, y - 3, 84 * s, 13 * s, hexc('#e8edf2'))
    for i in range(n):
        wob = math.sin(t * 5 + i * 0.5) * (i * 1.6)
        yy = y - 22 * s - i * 30 * s
        rrect(ctx, x - 70 * s + wob, yy - 14 * s, 140 * s, 28 * s, 14 * s); ctx.set_source_rgba(*hexc(FOOD[i % len(FOOD)])); ctx.fill()
        if FOOD[i % len(FOOD)] == '#fff6e0': circle(ctx, x + wob, yy - 4 * s, 13 * s, hexc('#ffb703'))
    if n > 0:
        wob = math.sin(t * 5 + n * 0.5) * (n * 1.6); circle(ctx, x + wob, y - 22 * s - n * 30 * s - 6 * s, 15 * s, hexc(RED))

def s0(ctx, t, d):
    buffet_bg(ctx, t)
    n = int(clamp01((t - 0.4) / 2.5) * 14)
    hx, hy = 150, -330
    wren(ctx, 400, GY, 1.1, t, "point", expr="happy", hand=(hx, hy))
    plate_stack(ctx, 400 + hx * 1.1 + 30, GY + hy * 1.1 - 26, n, t)
    kid(ctx, 870, GY, 0.95, t, "flat" if n < 10 else "shock", (-60, -200))
    px, py = 870 - 60 * 0.95, GY - 200 * 0.95 - 26
    e4.ell(ctx, px, py, 70, 13, (1, 1, 1, 1)); rrect(ctx, px - 30, py - 22, 60, 18, 6); ctx.set_source_rgba(*hexc('#e9b96e')); ctx.fill()
    bubble_ml(ctx, 760, 1040, ["It's a buffet,", "not a dare."], 42, ramp(t, 2.7, 2.9), (870, GY - 400))
    header(ctx, ease(t / 0.2 + 1), "HOTEL BREAKFAST BUFFET", "Leo takes one toast.", "Wren takes the buffet.", -0.3, t, main_size=56)
    meter(ctx, "PLATE HEIGHT", "%d cm" % (n * 4)); wm(ctx)

def s1(ctx, t, d):
    buffet_bg(ctx, t)
    n = int(clamp01((t - 0.5) / 2.6) * 9)
    ph = (clamp01((t - 0.5) / 2.6) * 9) % 1
    throwing = 0.5 < t < 3.1
    hy = -330 - (60 * math.sin(math.pi * ph) if throwing else 0)
    wren(ctx, 300, GY, 1.1, t, "point", expr="happy", hand=(150, hy))
    bx, by = 640, GY - 10
    rrect(ctx, bx - 150, by - 150, 300, 30, 12); ctx.set_source_rgba(*hexc('#6b4423')); ctx.fill()      # stool
    for dx in (-120, 120): ctx.rectangle(bx + dx - 10, by - 120, 20, 130); ctx.fill()
    bag(ctx, bx, by - 150, 1.25, bulge=n / 9)
    if throwing:
        sx, sy = 300 + 150 * 1.1, GY - 330 * 1.1
        cx = lerp(sx, bx, ph); cy = lerp(sy, by - 340, ph) - 260 * math.sin(math.pi * ph)
        croissant(ctx, cx, cy, 1.1, ph * 6)
    kid(ctx, 930, GY, 0.9, t, "flat", (0, -150))
    bubble_ml(ctx, 800, 1010, ["Grandma, that's", "stealing."], 40, ramp(t, 1.0, 1.2) * (1 - ramp(t, 2.6, 2.8)), (930, GY - 380))
    bubble_ml(ctx, 330, 990, ["It's called", "lunch."], 44, ramp(t, 3.0, 3.2), (300, GY - 680))
    header(ctx, ease(t / 0.2), "PHASE TWO", "The handbag opens.", "“For later.”", 0.8, t, main_size=56)
    meter(ctx, "CROISSANTS IN BAG", "%d" % n); wm(ctx)

def s2(ctx, t, d):
    buffet_bg(ctx, t, table=False)
    kid(ctx, 130, GY - 80, 0.78, t, "shock" if 1.2 < t < 3.0 else "flat", (0, -150))
    froze = t > 0.8
    wren(ctx, 420, GY, 1.1, 0.3 if froze and t < 3.2 else t, "point", expr="shock" if 1.3 < t < 3.2 else "happy", hand=(165, -300))
    bgx, bgy = 420 + 165 * 1.1 + 10, GY - 300 * 1.1 + 200
    bag(ctx, bgx, bgy, 1.0, bulge=1.0)
    for k in range(3): croissant(ctx, bgx - 50 + k * 50, bgy - 175 - (k % 2) * 14, 0.7, 0.4 * (k - 1))
    wx = lerp(1250, 880, ramp(t, 0.3, 1.2))
    waiter(ctx, wx, GY, t if t < 1.2 else 0, tray=True)
    # whistling notes
    if 0.8 < t < 1.4:
        for k in range(2):
            ph = ((t - 0.8) * 1.6 + k * 0.5) % 1; nx, ny = 540 + 50 * k + 30 * ph, GY - 720 - 90 * ph; e4.ell(ctx, nx, ny, 16, 12, hexc('#22223b', 1 - ph)); ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#22223b', 1 - ph)); ctx.move_to(nx + 13, ny); ctx.line_to(nx + 13, ny - 56); ctx.line_to(nx + 36, ny - 44); ctx.stroke()
    # croissant falls out, waiter returns it
    fall = clamp01((t - 1.3) / 0.45); back = ramp(t, 2.9, 3.5)
    fx, fy = bgx + 150, GY - 30
    if t > 1.3:
        cx = lerp(lerp(bgx + 60, fx, fall), bgx, back); cy = lerp(lerp(bgy - 170, fy, fall * fall), bgy - 175, back) - 200 * math.sin(math.pi * back)
        croissant(ctx, cx, cy, 1.0, fall * 4 + back * 6)
        if 0 < t - 1.75 < 0.3: burst(ctx, fx, fy, 1 - (t - 1.75) / 0.3, 90)
    bubble_ml(ctx, 760, 900, ["Madam, you dropped", "your lunch."], 40, ramp(t, 2.1, 2.3), (wx, GY - 690))
    header(ctx, ease(t / 0.2), "A WAITER APPEARS", "Act natural.", "The bag does not act natural.", 1.5, t, main_size=56)
    meter(ctx, "SUSPICION", "%d%%" % int(100 * ramp(t, 0.5, 1.9))); wm(ctx)

def s3(ctx, t, d):
    g = cairo.LinearGradient(0, 0, 0, 1300); g.add_color_stop_rgb(0, *hexc('#6ec6ff')[:3]); g.add_color_stop_rgb(1, *hexc('#e3f6ff')[:3]); ctx.set_source(g); ctx.rectangle(0, 0, W, 1300); ctx.fill()
    for cx, cy, r in ((200, 1320, 360), (620, 1340, 420), (980, 1320, 340)): circle(ctx, cx, cy, r, hexc('#7cc47a'))
    # closed cafe
    rrect(ctx, 640, 860, 400, 470, 16); ctx.set_source_rgba(*hexc('#f2e2c4')); ctx.fill()
    ctx.move_to(610, 870); ctx.line_to(840, 740); ctx.line_to(1070, 870); ctx.close_path(); ctx.set_source_rgba(*hexc('#c1583a')); ctx.fill()
    rrect(ctx, 700, 960, 280, 260, 10); ctx.set_source_rgba(*hexc('#9aa5b1')); ctx.fill()
    for k in range(8): ctx.rectangle(700, 975 + k * 31, 280, 5); ctx.set_source_rgba(*hexc('#7d8894')); ctx.fill()
    ctx.save(); ctx.translate(840, 1080); ctx.rotate(-0.08 + 0.03 * math.sin(t * 2)); rrect(ctx, -120, -42, 240, 84, 12); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
    mv.font(ctx, 50); e = ctx.text_extents("CLOSED"); ctx.move_to(-e.x_advance / 2, 18); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text("CLOSED"); ctx.restore()
    ctx.rectangle(0, 1300, W, H - 1300); ctx.set_source_rgba(*hexc('#8fd18a')); ctx.fill()
    # picnic blanket
    a = ramp(t, 0.9, 1.5)
    rrect(ctx, 250, 1640, 620, 150, 20); ctx.set_source_rgba(*hexc('#e63946', a)); ctx.fill()
    if a > 0.5:
        for k in range(6): ctx.rectangle(250 + k * 104, 1640, 52, 150); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.fill()
        for k in range(5):
            pop = ramp(t, 1.2 + k * 0.15, 1.5 + k * 0.15)
            if pop > 0: croissant(ctx, 330 + k * 115, 1700 - 40 * math.sin(math.pi * pop) , 0.9 * pop, 0.3 * (k - 2))
        circle(ctx, 500, 1750, 20 * a, hexc('#ffd60a')); circle(ctx, 620, 1755, 20 * a, hexc(RED)); circle(ctx, 740, 1750, 20 * a, hexc('#ff8c42'))
    wren(ctx, 300, GY - 60, 1.05, t, "point" if t < 2.6 else "cheer", expr="happy", hand=(170, -260))
    bag(ctx, 300 + 170 * 1.05 + 10, GY - 60 - 260 * 1.05 + 190, 0.95, bulge=1 - 0.7 * a)
    kid(ctx, 790, GY - 60, 0.95, t, "shock" if t < 1.6 else "smug", (-70, -230))
    if t > 1.9: croissant(ctx, 790 - 70 * 0.95, GY - 60 - 230 * 0.95 - 30, 0.8, 0.2)
    bubble_ml(ctx, 600, 930, ["Okay. You're", "a genius."], 42, ramp(t, 2.0, 2.2) * (1 - ramp(t, 3.0, 3.15)), (790, GY - 450))
    bubble_ml(ctx, 330, 960, ["I'm a grandmother.", "Same thing."], 40, ramp(t, 3.1, 3.3), (300, GY - 720))
    header(ctx, ease(t / 0.2), "2 PM. EVERYTHING'S CLOSED.", "Leo is starving.", "Wren opens the bag.", 0.9, t, main_size=56)
    meter(ctx, "LUNCH BILL", "$0"); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    croissant(ctx, 760, 1560, 1.3, 0.2 * math.sin(t * 3))
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “It was included.”", 205 - (1 - a) * 20, 60, hexc('#22223b', a), maxw=940)
    ctext(ctx, "Leo: “The cutlery wasn't.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "What's your buffet move? Comment below", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.5), (s0, 1.8), (s0, 3.4), (s1, 1.3), (s1, 2.4), (s1, 3.8), (s2, 1.0), (s2, 1.7), (s2, 3.0), (s3, 0.6), (s3, 2.4), (s3, 3.6), (s4, 2.4)]
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

import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, caption, ai_tag, ease, wren

OUT = "/home/claude/wren/ep3"
os.makedirs(OUT, exist_ok=True)

ROAD_TOP, ROAD_BOT = 1180, 1620
LANES = [(1290, 1, 260), (1420, -1, 330), (1560, 1, 300)]  # ground y, direction, speed
BIKE_COLS = ['#e63946', '#2a9d8f', '#f4a261', '#457b9d', '#9b5de5', '#f15bb5', '#00bbf9']
HELM_COLS = ['#ffffff', '#ffd166', '#ef476f', '#118ab2', '#06d6a0']

def hat(ctx, cx, gy, s, t, bob=True):
    ctx.save(); ctx.translate(cx, gy); ctx.scale(s, s)
    if bob: ctx.translate(0, math.sin(t * 2 * math.pi * 1.1) * 5)
    ctx.move_to(-165, -585); ctx.line_to(0, -735); ctx.line_to(165, -585)
    ctx.curve_to(80, -570, -80, -570, -165, -585); ctx.close_path()
    ctx.set_source_rgba(*hexc('#e9c46a')); ctx.fill_preserve()
    ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#b08933')); ctx.stroke()
    for k in range(1, 4):
        f = k / 4; ctx.move_to(-165 * f, -735 + 150 * f); ctx.line_to(165 * f, -735 + 150 * f); ctx.stroke()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#e63946'))
    ctx.move_to(-80, -580); ctx.curve_to(-60, -470, 60, -470, 80, -580); ctx.stroke()
    ctx.restore()

def wren_hat(ctx, cx, gy, s, t, mode="wave", seed=0.0):
    wren(ctx, cx, gy, s, t, mode, blink_seed=seed); hat(ctx, cx, gy, s, t)

def bike(ctx, x, y, s, d, col, helm, cargo=0, t=0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s * d, s)
    ctx.save(); ctx.scale(1, 0.2); circle(ctx, 0, 0, 80, (0, 0, 0, 0.15)); ctx.restore()
    for wx in (-48, 48):
        circle(ctx, wx, -24, 24, hexc('#222222')); circle(ctx, wx, -24, 9, hexc('#999999'))
    ctx.move_to(-60, -40); ctx.line_to(30, -42); ctx.line_to(55, -70); ctx.line_to(62, -66); ctx.line_to(45, -25)
    ctx.line_to(-30, -22); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    rrect(ctx, -55, -55, 60, 16, 8); ctx.set_source_rgba(*hexc('#333333')); ctx.fill()
    if cargo == 1:
        for k, c in enumerate(('#d4a373', '#c08552', '#d4a373')):
            rrect(ctx, -95, -95 - k * 34, 50, 32, 4); ctx.set_source_rgba(*hexc(c)); ctx.fill()
    elif cargo == 2:
        for k, c in enumerate(('#ff4d6d', '#ffd166', '#06d6a0', '#4cc9f0')):
            ctx.set_line_width(2); ctx.set_source_rgba(0.3, 0.3, 0.3, 1)
            bx, by = -70 + k * 14, -170 - (k % 2) * 25
            ctx.move_to(-45, -60); ctx.line_to(bx, by); ctx.stroke(); circle(ctx, bx, by, 20, hexc(c))
    # rider
    rrect(ctx, -32, -112, 34, 62, 12); ctx.set_source_rgba(*hexc('#3d5a80')); ctx.fill()
    ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#3d5a80'))
    ctx.move_to(-10, -98); ctx.line_to(50, -66); ctx.stroke()
    circle(ctx, -14, -128, 19, hexc('#e0ac69'))
    ctx.arc(-14, -130, 21, math.pi, 2 * math.pi); ctx.close_path(); ctx.set_source_rgba(*hexc(helm)); ctx.fill()
    ctx.restore()

def speed_lines(ctx, x, y, d, a=0.5):
    ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, a)
    for k in range(3):
        ctx.move_to(x - d * (80 + k * 6), y - 40 - k * 25); ctx.line_to(x - d * (140 + k * 20), y - 40 - k * 25); ctx.stroke()

def street(ctx, t):
    mv.vgrad(ctx, '#ffcf99', '#ffe8cc')
    # tube houses
    random.seed(11)
    x = -20; cols = ['#f6bd60', '#84a59d', '#f28482', '#f5cac3', '#a3c4bc', '#ffd166']
    while x < W:
        w = random.randint(150, 220); h = random.randint(620, 820); c = cols[random.randrange(len(cols))]
        top = ROAD_TOP - h
        ctx.rectangle(x, top, w, h); ctx.set_source_rgba(*hexc(c)); ctx.fill()
        for wy in range(top + 50, ROAD_TOP - 200, 150):
            rrect(ctx, x + 30, wy, w - 60, 90, 10); ctx.set_source_rgba(*hexc('#5c4d7d', 0.55)); ctx.fill()
            ctx.rectangle(x + 20, wy + 90, w - 40, 10); ctx.set_source_rgba(*hexc('#3d3d3d')); ctx.fill()
            for px in range(x + 30, x + w - 30, 18):
                ctx.rectangle(px, wy + 62, 4, 28); ctx.fill()
            circle(ctx, x + w - 40, wy + 70, 14, hexc('#2a9d8f'))
        x += w
    # cafe sign
    rrect(ctx, 600, ROAD_TOP - 230, 300, 90, 14); ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    mv.font(ctx, 46); e = ctx.text_extents("CÀ PHÊ")
    ctx.move_to(750 - e.x_advance / 2, ROAD_TOP - 168); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text("CÀ PHÊ")
    # tangled power lines
    ctx.set_line_width(3); ctx.set_source_rgba(0.15, 0.12, 0.12, 0.8)
    for k in range(7):
        y0 = 470 + k * 12
        ctx.move_to(-20, y0); ctx.curve_to(300, y0 + 60 + k * 5, 700, y0 + 40 - k * 4, W + 20, y0 + 10); ctx.stroke()
    ctx.rectangle(ROAD_TOP * 0 + 120, 440, 16, ROAD_TOP - 440); ctx.set_source_rgba(*hexc('#4a4e69')); ctx.fill()
    # pavements + road
    ctx.rectangle(0, ROAD_TOP - 40, W, 40); ctx.set_source_rgba(*hexc('#c9ada7')); ctx.fill()
    ctx.rectangle(0, ROAD_TOP, W, ROAD_BOT - ROAD_TOP); ctx.set_source_rgba(*hexc('#6b705c')); ctx.fill()
    ctx.set_line_width(8); ctx.set_dash([50, 40]); ctx.set_source_rgba(1, 1, 1, 0.6)
    for y in (1355, 1490):
        ctx.move_to(0, y); ctx.line_to(W, y); ctx.stroke()
    ctx.set_dash([])
    ctx.rectangle(0, ROAD_BOT, W, H - ROAD_BOT); ctx.set_source_rgba(*hexc('#c9ada7')); ctx.fill()
    ctx.rectangle(0, ROAD_BOT, W, 16); ctx.set_source_rgba(*hexc('#9a8c98')); ctx.fill()

def traffic(t, speed=1.0, wren_pos=None, gap=None, gap_amt=0.0):
    """Return list of (ground_y, draw_fn) for every bike."""
    items = []
    for li, (ly, d, v) in enumerate(LANES):
        n = 5
        span = W + 400
        for k in range(n):
            base = (k * span / n + li * 97)
            x = (base + d * v * speed * t) % span - 200
            y = ly
            if gap is not None and gap_amt > 0 and abs(x - gap) < 190:
                tgt = gap + (190 if x >= gap else -190)
                x = x + (tgt - x) * gap_amt
            if wren_pos is not None:
                wx, wy = wren_pos
                if abs(wy - ly) < 110:
                    g = math.exp(-((x - wx) / 170) ** 2)
                    y = ly + (1 if (k % 2) else -1) * 115 * g * (1 - abs(wy - ly) / 110 * 0.3)
            col = BIKE_COLS[(k * 3 + li) % len(BIKE_COLS)]; helm = HELM_COLS[(k + li) % len(HELM_COLS)]
            cargo = 1 if (k + li) % 4 == 0 else (2 if (k + li) % 7 == 3 else 0)
            def fn(ctx, x=x, y=y, d=d, col=col, helm=helm, cargo=cargo):
                speed_lines(ctx, x, y, d, 0.45); bike(ctx, x, y, 0.95, d, col, helm, cargo)
            items.append((y, fn))
    return items

def draw_sorted(ctx, items):
    for _, fn in sorted(items, key=lambda it: it[0]):
        fn(ctx)

def kid(ctx, kx, gy, s, hand_world, t):
    ctx.save(); ctx.translate(kx, gy); ctx.scale(s, s)
    ctx.translate(0, math.sin(t * 2 * math.pi * 1.6) * 4)
    ctx.save(); ctx.scale(1, 0.2); circle(ctx, 0, 0, 70, (0, 0, 0, 0.15)); ctx.restore()
    rrect(ctx, -60, -235, 120, 120, 26); ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()  # school bag
    ctx.set_line_width(24); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#c68642'))
    for lx in (-20, 20):
        ctx.move_to(lx, -95); ctx.line_to(lx, -15); ctx.stroke()
        ctx.save(); ctx.translate(lx, -8); ctx.scale(1.5, 0.8); circle(ctx, 0, 0, 15, hexc('#ffffff')); ctx.restore()
    rrect(ctx, -42, -135, 84, 50, 12); ctx.set_source_rgba(*hexc('#1d3557')); ctx.fill()
    rrect(ctx, -45, -230, 90, 105, 22); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    ctx.set_line_width(20); ctx.set_source_rgba(*hexc('#ffd166'))
    ctx.move_to(-38, -215); ctx.line_to(-62, -140); ctx.stroke()
    circle(ctx, -62, -135, 12, hexc('#c68642'))
    # arm up to Wren's hand (convert world target into local units)
    hx = (hand_world[0] - kx) / s; hy = (hand_world[1] - gy) / s
    ctx.set_source_rgba(*hexc('#ffd166')); ctx.move_to(38, -215); ctx.line_to(38 + (hx - 38) * 0.45, -215 + (hy + 215) * 0.45); ctx.stroke()
    ctx.set_line_width(16); ctx.set_source_rgba(*hexc('#c68642'))
    ctx.move_to(38 + (hx - 38) * 0.45, -215 + (hy + 215) * 0.45); ctx.line_to(hx, hy); ctx.stroke()
    circle(ctx, 0, -290, 58, hexc('#c68642'))
    ctx.arc(0, -296, 62, math.radians(170), math.radians(370)); ctx.close_path(); ctx.set_source_rgba(*hexc('#1b1b1b')); ctx.fill()
    ctx.rectangle(-62, -300, 14, 50); ctx.rectangle(48, -300, 14, 50); ctx.fill()
    for ex in (-20, 20): circle(ctx, ex, -282, 7, hexc('#1b1b1b'))
    circle(ctx, -34, -262, 10, hexc('#f28b82', 0.5)); circle(ctx, 34, -262, 10, hexc('#f28b82', 0.5))
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#7a3e2b'))
    ctx.arc(0, -262, 16, math.radians(20), math.radians(160)); ctx.stroke()
    ctx.restore()

def star(ctx, x, y, r, a=1.0, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        ang = -math.pi / 2 + i * math.pi / 5
        (ctx.move_to if i == 0 else ctx.line_to)(rr * math.cos(ang), rr * math.sin(ang))
    ctx.close_path(); ctx.set_source_rgba(*hexc('#ffc300', a)); ctx.fill_preserve()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#e09f00', a)); ctx.stroke(); ctx.restore()

def wren_and_kid(ctx, wx, wy, s, t):
    ks = s * 1.3
    kx = wx - 185 * s
    hand = (wx - 140 * s, wy - 235 * s)
    kid(ctx, kx, wy, ks, hand, t)
    wren_hat(ctx, wx, wy, s, t, "wave", 0.5)

# ---------- scenes ----------
def s_hook(ctx, t, d):
    street(ctx, t)
    items = traffic(t, 1.6)
    items.append((1850, lambda c: wren_hat(c, 200, 1850, 0.42, t, "wave")))
    draw_sorted(ctx, items)
    rrect(ctx, 60, 140, W - 120, 330, 40); ctx.set_source_rgba(1, 1, 1, 0.9 * ease(t / 0.3)); ctx.fill()
    a = ease((t - 0.1) / 0.4)
    ctext(ctx, "Me vs. Hanoi traffic.", 270 - (1 - a) * 20, 84, hexc('#22223b', a))
    a2 = ease((t - 1.1) / 0.4)
    ctext(ctx, "I just wanted a coffee.", 400, 60, hexc('#e63946', a2))
    ai_tag(ctx, y=1895)

def s_problem(ctx, t, d):
    street(ctx, t)
    items = traffic(t + 5, 1.8)
    items.append((1850, lambda c: wren_hat(c, 540, 1850, 0.42, t, "wave", 1.1)))
    draw_sorted(ctx, items)
    rrect(ctx, 60, 140, W - 120, 300, 40); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.fill()
    mins = min(20, 1 + int(t / d * 26))
    ctext(ctx, f"Minute {mins} on the kerb.", 270, 76, hexc('#22223b', ease(t / 0.3)))
    ctext(ctx, "Still on the kerb.", 380, 56, hexc('#5c6b7a', ease((t - 1.2) / 0.4)), bold=False)
    caption(ctx, t, "THE PROBLEM", "The café was RIGHT THERE.", y=560, delay=1.8)
    ai_tag(ctx, y=1895)

def s_fix(ctx, t, d):
    street(ctx, t)
    p = ease((t - 1.0) / (d - 1.8))
    wy = 1850 - p * (1850 - ROAD_TOP + 10)
    wx = 600
    slow = 1 - math.exp(-t * 2.2)            # scooters brake to a stop
    items = traffic(9 + 0.45 * slow, 1.0, None, gap=wx - 80, gap_amt=ease(t / 1.0))
    items.append((wy, lambda c: wren_and_kid(c, wx, wy, 0.42, t)))
    draw_sorted(ctx, items)
    if t < 1.2:
        ctx.set_source_rgba(*hexc('#ff4d4d', 0.5 * (1 - t / 1.2)))
        for _, (ly, dd, v) in enumerate(LANES):
            pass
    rrect(ctx, 60, 140, W - 120, 330, 40); ctx.set_source_rgba(1, 1, 1, 0.92); ctx.fill()
    a = ease((t - 0.1) / 0.4)
    ctext(ctx, "THE FIX", 230, 52, hexc('#e63946', a))
    ctext(ctx, "Find a local. Hold hands. Walk steady.", 320, 62, hexc('#22223b', a), maxw=900, lh=1.15)
    caption(ctx, t, "GOLD STAR", "Little Minh walked me across and every scooter stopped for her. Best guide in Hanoi!", y=540, delay=1.6)
    sp = ease((t - (d - 1.3)) / 0.4)
    if sp > 0:
        kx = wx - 185 * 0.42
        star(ctx, kx, wy - 0.42 * 1.3 * 360 - 50 - sp * 30, 60 * sp, 1.0, math.sin(t * 6) * 0.2)
        mv.font(ctx, 30); e = ctx.text_extents("Minh")
        ctx.move_to(kx - e.x_advance / 2, wy + 40); ctx.set_source_rgba(*hexc('#22223b', sp)); ctx.show_text("Minh")
    ai_tag(ctx, y=1895)

def egg_coffee(ctx, x, y, s, t):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.save(); ctx.scale(1, 0.3); circle(ctx, 0, 40, 120, hexc('#ffffff', 0.9)); ctx.restore()
    ctx.move_to(-110, -20); ctx.curve_to(-100, 60, 100, 60, 110, -20); ctx.close_path()
    ctx.set_source_rgba(*hexc('#e0e0e0')); ctx.fill()
    ctx.move_to(-60, -150); ctx.line_to(60, -150); ctx.line_to(50, 10); ctx.line_to(-50, 10); ctx.close_path()
    ctx.set_source_rgba(*hexc('#4a2c1d')); ctx.fill()
    ctx.move_to(-60, -150); ctx.line_to(60, -150); ctx.line_to(56, -80); ctx.line_to(-56, -80); ctx.close_path()
    ctx.set_source_rgba(*hexc('#f7d488')); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.move_to(-60, -150); ctx.line_to(-50, 10); ctx.stroke()
    for k in range(3):
        ph = (t * 0.8 + k * 0.33) % 1
        ctx.set_line_width(6); ctx.set_source_rgba(1, 1, 1, 0.6 * (1 - ph))
        bx = -30 + k * 30; by = -170 - ph * 120
        ctx.move_to(bx, by); ctx.curve_to(bx + 15, by - 20, bx - 15, by - 40, bx, by - 60); ctx.stroke()
    ctx.restore()

def banh_mi(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(-0.15)
    ctx.save(); ctx.scale(1, 0.32); circle(ctx, 0, 0, 170, hexc('#d9a05b')); ctx.restore()
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#70e000')); ctx.move_to(-120, 8)
    for i in range(12): ctx.line_to(-120 + i * 22, 8 + (8 if i % 2 else -4))
    ctx.stroke()
    ctx.set_line_width(10); ctx.set_source_rgba(*hexc('#ff8fa3')); ctx.move_to(-110, 20); ctx.line_to(120, 18); ctx.stroke()
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#b5762d'))
    for i in range(-2, 3):
        ctx.move_to(i * 45 - 15, -40); ctx.line_to(i * 45 + 15, -30); ctx.stroke()
    ctx.restore()

def s_reward(ctx, t, d):
    mv.vgrad(ctx, '#ffd6a5', '#ffb4a2')
    for i in range(5):
        lx = 140 + i * 200; ly = 560 + 25 * math.sin(i)
        ctx.set_line_width(2); ctx.set_source_rgba(0.2, 0.2, 0.2, 1); ctx.move_to(lx, 470); ctx.line_to(lx, ly); ctx.stroke()
        mv.lantern(ctx, lx, ly + 40, 0.6, ['#ff4d4d', '#ffd166', '#ff9f1c'][i % 3])
    wren_hat(ctx, 540, 1330, 0.8, t, "cheer" if t > 1.2 else "wave")
    rrect(ctx, -20, 1290, W + 40, 50, 10); ctx.set_source_rgba(*hexc('#8d5524')); ctx.fill()
    ctx.rectangle(0, 1340, W, H); ctx.set_source_rgba(*hexc('#a0522d')); ctx.fill()
    pop = ease((t - 0.3) / 0.5)
    if pop > 0:
        egg_coffee(ctx, 330, 1280, 0.95 * pop, t); banh_mi(ctx, 770, 1260, 1.0 * pop)
    a = ease((t - 0.1) / 0.4)
    ctext(ctx, "Made it.", 250, 96, hexc('#22223b', a))
    ctext(ctx, "Egg coffee + bánh mì.", 370, 64, hexc('#e63946', ease((t - 0.7) / 0.4)))
    caption(ctx, t, "WREN'S REVIEW", "Egg coffee tastes like tiramisu you can drink. 10/10.", y=1460, delay=1.6)
    ai_tag(ctx)

def s_twist(ctx, t, d):
    street(ctx, t)
    items = traffic(t + 14, 1.8)
    items.append((1250, lambda c: wren_hat(c, 540, ROAD_TOP - 10, 0.42, t, "wave", 0.2)))
    draw_sorted(ctx, items)
    rrect(ctx, 60, 140, W - 120, 330, 40); ctx.set_source_rgba(1, 1, 1, 0.92); ctx.fill()
    ctext(ctx, "Then I remembered...", 270, 64, hexc('#22223b', ease(t / 0.4)))
    ctext(ctx, "My hotel is on the other side.", 380, 60, hexc('#e63946', ease((t - 1.3) / 0.4)), maxw=900)
    ai_tag(ctx, y=1895)

def s_outro(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    for i in range(4):
        bike(ctx, (i * 330 + t * 160) % (W + 300) - 150, 1810, 0.7, 1, BIKE_COLS[i], HELM_COLS[i], i % 3)
    pop = ease(t / 0.5)
    s = 1.0 * (0.9 + 0.1 * pop)
    wren_hat(ctx, 540, 1640, s, t, "wave")
    a = ease((t - 0.2) / 0.4)
    ctext(ctx, "Send this to the friend who'd still be standing on the kerb", 210 - (1 - a) * 30, 60, hexc('#22223b', a), maxw=900, lh=1.2)
    a2 = ease((t - 1.0) / 0.4)
    mv.font(ctx, 54); s2 = "@wrentrips"; e = ctx.text_extents(s2)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 480, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc('#e63946', a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 548); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s2)
    ctext(ctx, "Follow for the next disaster", 660, 44, hexc('#5c2a1e', ease((t - 1.6) / 0.4)), bold=False)
    ai_tag(ctx, y=1890, dark=True)

SCENES = [(s_hook, 3.5), (s_problem, 4.5), (s_fix, 7.0), (s_reward, 5.0), (s_twist, 3.5), (s_outro, 4.5)]

def frame(fn, t, d):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    fn(ctx, t, d)
    a_in = 0 if fn is s_hook else 1 - t / 0.25
    a_out = (t - (d - 0.6)) / 0.6 if fn is s_outro else (t - (d - 0.2)) / 0.2
    a = max(a_in, a_out, 0)
    if a > 0:
        ctx.set_source_rgba(*hexc('#fff3e0', min(1, ease(a)))); ctx.paint()
    return surf

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        from PIL import Image
        ims = []
        for i, (fn, d) in enumerate(SCENES):
            tt = d * 0.5 if fn is s_fix else d * 0.8
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, d).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((360, 640)))
        c = Image.new("RGB", (370 * 6, 640), "white")
        for i, im in enumerate(ims): c.paste(im, (i * 370, 0))
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

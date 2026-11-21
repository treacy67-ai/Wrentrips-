"""ep26 - Camping trip: the tent box says '10-minute setup'. Minute 187, Leo is tangled in 46 poles. He gets it up, the wind takes it. Wren throws a pop-up tent: two seconds."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep26"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; ORANGE = '#f77f00'; ORANGE_D = '#c75f00'; DOME = '#7b2cbf'; DOME_D = '#5a189a'; POLE = '#8d99ae'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1600                         # characters' ground line (kept above the @wrentrips watermark)

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

def ftext(ctx, s, cx, y, size, col, maxw, bold=True):
    mv.font(ctx, size, bold); e = ctx.text_extents(s)
    while e.x_advance > maxw and size > 12:
        size -= 1; mv.font(ctx, size, bold); e = ctx.text_extents(s)
    ctx.move_to(cx - e.x_advance / 2, y); ctx.set_source_rgba(*col); ctx.show_text(s)

# ------------------------------------------------------------ background: lakeside campsite
def pine(ctx, x, base, s, col):
    ctx.set_source_rgba(*hexc('#5e3b25')); ctx.rectangle(x - 10 * s, base - 40 * s, 20 * s, 40 * s); ctx.fill()
    for k in range(4):
        w = (90 - k * 18) * s; y0 = base - 30 * s - k * 52 * s
        ctx.move_to(x - w, y0); ctx.line_to(x, y0 - 110 * s); ctx.line_to(x + w, y0); ctx.close_path()
        ctx.set_source_rgba(*col); ctx.fill()

def camp(ctx, t, night=0.0):
    g = cairo.LinearGradient(0, 0, 0, 1300)
    top = mv.mixc(hexc('#7ec8e3'), hexc('#0b1d3a'), night); bot = mv.mixc(hexc('#ffe5b4'), hexc('#2b3f6b'), night)
    g.add_color_stop_rgb(0, *top[:3]); g.add_color_stop_rgb(1, *bot[:3]); ctx.set_source(g); ctx.rectangle(0, 0, W, 1300); ctx.fill()
    if night > 0.5:
        rnd = random.Random(26)
        for k in range(60):
            sx, sy = rnd.uniform(0, W), rnd.uniform(600, 1180); tw = 0.5 + 0.5 * math.sin(t * 3 + k)
            circle(ctx, sx, sy, rnd.uniform(1.5, 3.5), (1, 1, 1, (0.4 + 0.6 * tw) * (night - 0.5) * 2))
        circle(ctx, 860, 780, 60, hexc('#fff3c4')); circle(ctx, 885, 765, 54, mv.mixc(top, bot, 0.3))
    else:
        circle(ctx, 820, 900, 70, hexc('#ffd166'))
        for cx_, cy_ in ((180, 720), (620, 680)):
            x = (cx_ + t * 12) % 1300 - 110
            for dx, r in ((-40, 34), (0, 48), (46, 32)): circle(ctx, x + dx, cy_, r, (1, 1, 1, 0.9))
    # mountains
    for pts, col in (([(0, 1250), (180, 1010), (330, 1150), (520, 960), (760, 1180), (900, 1040), (1080, 1170), (1080, 1300), (0, 1300)], '#6d83a8'),
                     ([(0, 1280), (240, 1130), (430, 1230), (690, 1090), (980, 1250), (1080, 1210), (1080, 1300), (0, 1300)], '#526a8f')):
        ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        ctx.close_path(); ctx.set_source_rgba(*mv.mixc(hexc(col), hexc('#1b2a4a'), night)); ctx.fill()
    # lake
    ctx.rectangle(0, 1260, W, 90); ctx.set_source_rgba(*mv.mixc(hexc('#48cae4'), hexc('#1d3557'), night)); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.5 - 0.3 * night)
    for k in range(6):
        x = (k * 210 + t * 30) % 1200 - 60; ctx.move_to(x, 1290 + (k % 3) * 18); ctx.line_to(x + 70, 1290 + (k % 3) * 18); ctx.stroke()
    # pines along the far shore
    for x, s in ((-20, 1.0), (70, 1.25), (980, 1.2), (1070, 1.0), (900, 0.8)):
        pine(ctx, x, 1360, s, mv.mixc(hexc('#2d6a4f'), hexc('#10291f'), night))
    # grass
    ctx.rectangle(0, 1340, W, H - 1340); ctx.set_source_rgba(*mv.mixc(hexc('#80b918'), hexc('#2b4a1f'), night)); ctx.fill()
    ctx.rectangle(0, 1340, W, 12); ctx.set_source_rgba(*mv.mixc(hexc('#55a630'), hexc('#1f3a17'), night)); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(*mv.mixc(hexc('#55a630'), hexc('#1f3a17'), night))
    for i in range(34):
        x = (i * 37) % 1100; y = 1400 + (i * 53) % 480
        ctx.move_to(x, y); ctx.line_to(x + 6, y - 20); ctx.stroke(); ctx.move_to(x + 10, y); ctx.line_to(x + 14, y - 16); ctx.stroke()

# ------------------------------------------------------------ props
def tent_up(ctx, x, base, k, col=ORANGE, dark=ORANGE_D, w=340, h=280):
    """Leo's tent; k = how far it is up (0 flat, 1 standing)."""
    if k <= 0.02: return
    hh = h * k; ww = w * (1.25 - 0.25 * k)
    ctx.move_to(x - ww / 2, base); ctx.curve_to(x - ww / 2 + 20, base - hh * 0.6, x - 30, base - hh, x, base - hh)
    ctx.curve_to(x + 30, base - hh, x + ww / 2 - 20, base - hh * 0.6, x + ww / 2, base); ctx.close_path()
    ctx.set_source_rgba(*hexc(col)); ctx.fill()
    ctx.move_to(x - 60 * k, base); ctx.line_to(x, base - hh * 0.75); ctx.line_to(x + 60 * k, base); ctx.close_path(); ctx.set_source_rgba(*hexc(dark)); ctx.fill()
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#ffd166'))
    ctx.move_to(x - ww * 0.27, base); ctx.curve_to(x - ww * 0.22, base - hh * 0.7, x - 10, base - hh * 0.98, x, base - hh * 0.98); ctx.stroke()
    ctx.move_to(x + ww * 0.27, base); ctx.curve_to(x + ww * 0.22, base - hh * 0.7, x + 10, base - hh * 0.98, x, base - hh * 0.98); ctx.stroke()

def tent_flat(ctx, x, base, t):
    ctx.move_to(x - 170, base)
    for i in range(9):
        xx = x - 170 + i * 42.5; ctx.line_to(xx, base - 55 - 22 * math.sin(i * 1.7 + t * 2))
    ctx.line_to(x + 170, base); ctx.close_path(); ctx.set_source_rgba(*hexc(ORANGE)); ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(8); ctx.set_source_rgba(*hexc(POLE))
    for (a, b, c, d) in ((-120, -40, -190, -140), (30, -50, 90, -170), (100, -30, 210, -90), (-40, -60, -10, -190)):
        ctx.move_to(x + a, base + b); ctx.line_to(x + c, base + d); ctx.stroke()

def tent_box(ctx, x, y):
    rrect(ctx, x - 110, y - 120, 220, 120, 10); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#c99a2e')); rrect(ctx, x - 110, y - 120, 220, 120, 10); ctx.stroke()
    ctx.move_to(x - 80, y - 20); ctx.line_to(x - 40, y - 70); ctx.line_to(x, y - 20); ctx.close_path(); ctx.set_source_rgba(*hexc(ORANGE)); ctx.fill()
    ftext(ctx, "EASY", x + 50, y - 72, 30, hexc('#10132b'), 110)
    ftext(ctx, "10 MIN", x + 50, y - 36, 30, hexc(RED), 110)
    ftext(ctx, "SETUP!", x + 50, y - 8, 22, hexc('#10132b'), 110)

def poles_tangle(ctx, hx, hy, t):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(8); ctx.set_source_rgba(*hexc(POLE))
    for k, (ang, ln) in enumerate(((0.3, 210), (1.2, 180), (2.4, 220), (-0.6, 170), (3.4, 190), (-1.9, 140))):
        a = ang + 0.12 * math.sin(t * 4 + k)
        mx, my = hx + math.cos(a) * ln * 0.55, hy + math.sin(a) * ln * 0.55
        ctx.move_to(hx - math.cos(a) * 30, hy - math.sin(a) * 30); ctx.line_to(mx, my)
        ctx.line_to(mx + math.cos(a + 0.5) * ln * 0.45, my + math.sin(a + 0.5) * ln * 0.45); ctx.stroke()
    ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#ffd166'))       # guy rope wrapped round him
    ctx.move_to(hx - 70, hy - 40); ctx.curve_to(hx + 40, hy - 110, hx + 90, hy + 60, hx - 50, hy + 90); ctx.curve_to(hx - 120, hy + 60, hx - 20, hy - 10, hx + 60, hy + 20); ctx.stroke()

def mug(ctx, x, y, steam_t=None):
    rrect(ctx, x - 24, y - 44, 48, 48, 10); ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#e63946')); ctx.arc(x + 26, y - 22, 12, -1.6, 1.6); ctx.stroke()
    if steam_t is not None:
        for k in range(2):
            ph = (steam_t * 0.8 + k * 0.5) % 1; circle(ctx, x - 8 + k * 16 + 6 * math.sin(steam_t * 3 + k), y - 56 - ph * 60, 8 + 6 * ph, (1, 1, 1, 0.55 * (1 - ph)))

def disc(ctx, x, y, ang, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    e4.ell(ctx, 0, 0, 70, 70, hexc(DOME)); e4.ell(ctx, 0, 0, 50, 50, hexc(DOME_D))
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#ffd166')); ctx.arc(0, 0, 60, 0, 2 * math.pi); ctx.stroke()
    ctx.restore()

def dome(ctx, x, base, s, t=0.0, lights=0.0):
    if s <= 0.01: return
    ctx.save(); ctx.translate(x, base); ctx.scale(s, s)
    ctx.move_to(-190, 0); ctx.curve_to(-190, -190, -110, -270, 0, -270); ctx.curve_to(110, -270, 190, -190, 190, 0); ctx.close_path()
    ctx.set_source_rgba(*hexc(DOME)); ctx.fill()
    ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#ffd166'))
    for sx in (-1, 1):
        ctx.move_to(sx * 120, 0); ctx.curve_to(sx * 100, -170, sx * 40, -262, 0, -268); ctx.stroke()
    ctx.move_to(-80, 0); ctx.curve_to(-70, -120, 70, -120, 80, 0); ctx.close_path()
    glow = lights
    ctx.set_source_rgba(*mv.mixc(hexc(DOME_D), hexc('#ffd88a'), glow)); ctx.fill()
    ctx.restore()
    if lights > 0:                                                         # fairy lights along the dome
        for k in range(11):
            u = k / 10; ang = math.pi * (1 - u)
            lx = x + math.cos(ang) * 200 * s; ly = base - math.sin(ang) * 250 * s - 8
            col = ('#ffd166', '#ff6b6b', '#4cc9f0', '#80ffdb')[k % 4]
            circle(ctx, lx, ly, 10, hexc(col, lights * (0.6 + 0.4 * math.sin(t * 5 + k))))

def pop_scale(t, t0):
    if t < t0: return 0.0
    u = t - t0
    return max(0.0, 1 - math.exp(-u * 9) * math.cos(u * 16))

def fire(ctx, x, base, t):
    e4.ell(ctx, x, base, 150, 32, hexc('#ffb703', 0.18 + 0.05 * math.sin(t * 9)))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(26); ctx.set_source_rgba(*hexc('#6f4518'))
    ctx.move_to(x - 70, base); ctx.line_to(x + 70, base - 20); ctx.stroke(); ctx.move_to(x + 70, base); ctx.line_to(x - 70, base - 20); ctx.stroke()
    for k, (dx, hh, col) in enumerate(((-30, 120, '#f77f00'), (25, 140, '#f77f00'), (0, 170, '#fcbf49'), (-8, 100, '#ffea00'))):
        fl = hh * (0.85 + 0.15 * math.sin(t * 11 + k * 2))
        ctx.move_to(x + dx - 34, base - 14); ctx.curve_to(x + dx - 40, base - fl * 0.5, x + dx + 8 * math.sin(t * 7 + k), base - fl * 0.8, x + dx, base - fl)
        ctx.curve_to(x + dx + 10, base - fl * 0.7, x + dx + 40, base - fl * 0.4, x + dx + 34, base - 14); ctx.close_path()
        ctx.set_source_rgba(*hexc(col, 0.95)); ctx.fill()
    for k in range(4):
        ph = (t * 0.9 + k / 4) % 1; circle(ctx, x - 20 + k * 14 + 20 * math.sin(t * 2 + k), base - 180 - ph * 200, 4, hexc('#ffd166', 1 - ph))

def plate_pile(ctx, x, base, n, t):
    for i in range(n):
        wob = math.sin(t * 5 + i * 0.7) * i * 1.2; y = base - i * 22
        e4.ell(ctx, x + wob, y, 70, 14, (1, 1, 1, 1)); e4.ell(ctx, x + wob, y - 2, 46, 8, hexc('#c9b79c'))
    if n > 2:
        ctx.set_line_width(8); ctx.set_source_rgba(*hexc('#adb5bd')); ctx.move_to(x + 40, base - n * 22); ctx.line_to(x + 90, base - n * 22 - 70); ctx.stroke()

def wind(ctx, t, a):
    if a <= 0: return
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(7)
    for k in range(6):
        ph = (t * 1.8 + k / 6) % 1; x = -200 + ph * 1500; y = 1050 + k * 95
        ctx.set_source_rgba(1, 1, 1, 0.7 * a * math.sin(math.pi * ph))
        ctx.move_to(x, y); ctx.curve_to(x + 80, y - 20, x + 160, y + 20, x + 240, y); ctx.stroke()

# ------------------------------------------------------------ scenes
WX0, LX0 = 860, 540
def s0(ctx, t, d):
    camp(ctx, t)
    tent_flat(ctx, 230, GY, t)
    tent_box(ctx, 210, GY + 10)
    mins = int(lerp(10, 187, ramp(t, 0.2, 2.2)))
    lhx, lhy = (-20 + 14 * math.sin(t * 6), -210)
    kid(ctx, LX0, GY, 0.95, t, "flat", (lhx, lhy))
    poles_tangle(ctx, LX0 + lhx * 0.95, GY + lhy * 0.95, t)
    wren(ctx, WX0, GY, 1.05, t, "point", expr="happy", hand=(150, -330))
    mug(ctx, WX0 + 150 * 1.05 + 4, GY - 330 * 1.05 - 6, t)
    bubble_ml(ctx, 400, 860, ["Why are there", "46 poles?!"], 44, ramp(t, 2.3, 2.5), (LX0 - 10, GY - 360))
    header(ctx, ease(t / 0.2 + 1), "CAMPING TRIP", "Box: “10-minute setup.”", "Minute 187.", -0.3, t, main_size=56)
    meter(ctx, "MINUTES SPENT ON THE TENT", "%d" % mins); wm(ctx)

def s1(ctx, t, d):
    camp(ctx, t)
    wa = ramp(t, 1.9, 2.2) * (1 - ramp(t, 3.4, 3.8))
    wind(ctx, t, wa)
    up = ramp(t, 0.3, 1.3)
    gust = clamp01((t - 2.2) / 1.1)
    tx = lerp(250, 1450, gust ** 1.4); ty = GY - 1000 * math.sin(0.5 * math.pi * min(1, gust * 1.6))
    ctx.save(); ctx.translate(tx, ty); ctx.rotate(gust * 5.5); ctx.translate(-tx, -ty)
    if gust < 1: tent_up(ctx, tx, GY if gust == 0 else ty + 140 * gust, up)
    ctx.restore()
    cheering = 1.3 < t < 2.3
    kid(ctx, 600, GY, 0.95, t, "smug" if cheering else ("flat" if t >= 2.3 else "smile"), (0, -420) if cheering else (-30, -200))
    wren(ctx, WX0 + 20, GY, 1.05, t, "point", expr="shock" if 2.3 < t < 3.3 else "happy", hand=(150, -330))
    mug(ctx, WX0 + 20 + 150 * 1.05 + 4, GY - 330 * 1.05 - 6, t)
    bubble_ml(ctx, 380, 860, ["DONE! Three", "hours flat!"], 44, ramp(t, 1.4, 1.6) * (1 - ramp(t, 2.3, 2.45)), (580, GY - 400))
    bubble_ml(ctx, 560, 760, ["It's gone camping", "without you, love."], 42, ramp(t, 3.25, 3.45), (WX0 - 30, GY - 760))
    status = "Rising..." if t < 1.3 else ("UP!" if t < 2.2 else ("Flying" if t < 3.2 else "Gone"))
    header(ctx, ease(t / 0.2), "FINALLY", "The tent is up!", "Then the wind arrives.", 1.8, t, main_size=56)
    meter(ctx, "TENT STATUS", status); wm(ctx)

DX = 790
def s2(ctx, t, d):
    camp(ctx, t)
    throw = clamp01((t - 0.5) / 0.8)
    wx = 400
    hand = (150, -330) if t < 0.5 else ((60, -560) if t < 1.3 else (150, -330))
    wren(ctx, wx, GY, 1.05, t, "point", expr="happy", hand=hand)
    sx, sy = wx + 150 * 1.05, GY - 330 * 1.05
    if t < 0.5: disc(ctx, sx + 10, sy - 10, 0.0, 0.8)
    elif t < 1.3:
        cx = lerp(sx, DX, throw); cy = lerp(sy, GY - 60, throw) - 360 * math.sin(math.pi * throw)
        disc(ctx, cx, cy, throw * 10, lerp(0.8, 1.0, throw))
    ps = pop_scale(t, 1.3)
    dome(ctx, DX, GY, ps, t)
    if 1.3 < t < 1.7: burst(ctx, DX, GY - 150, 1 - (t - 1.3) / 0.4, 260)
    kid(ctx, 170, GY, 0.9, t, "flat" if t > 1.3 else "smile", (-10, -200))
    bubble_ml(ctx, 210, 1010, ["HOW?!"], 46, ramp(t, 1.7, 1.9) * (1 - ramp(t, 2.6, 2.75)), (190, GY - 345))
    bubble_ml(ctx, 620, 760, ["I never read", "the instructions."], 42, ramp(t, 2.8, 3.0), (470, GY - 740))
    secs = "-" if t < 0.5 else ("%.1f s" % min(2.0, (t - 0.5) * 2.0 / 0.8) if t < 1.3 else "2.0 s")
    header(ctx, ease(t / 0.2), "WREN'S TURN", "One flat disc. One throw.", "POP.", 1.3, t, main_size=56)
    meter(ctx, "WREN'S SETUP TIME", secs); wm(ctx)

def s3(ctx, t, d):
    camp(ctx, t, night=ramp(t, 0.0, 0.6) * 0.4 + 0.6)
    dome(ctx, 880, GY, 0.95, t, lights=ramp(t, 0.4, 0.9))
    fire(ctx, 470, GY + 10, t)
    wren(ctx, 230, GY, 1.0, t, "point", expr="happy", hand=(150, -330))
    mug(ctx, 230 + 150 + 4, GY - 330 - 6, t)
    kid(ctx, 760, GY, 0.9, t, "smile" if t < 2.8 else "flat", (0, -230))
    rrect(ctx, 760 - 60, GY - 230 * 0.9 - 40, 120, 70, 24); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()        # pillow
    n = int(clamp01((t - 2.9) / 0.6) * 7)
    if n: plate_pile(ctx, 615, GY + 40, n, t)
    bubble_ml(ctx, 720, 860, ["Room for", "one more?"], 44, ramp(t, 0.9, 1.1) * (1 - ramp(t, 2.6, 2.75)), (760, GY - 330))
    bubble_ml(ctx, 400, 760, ["Rent is the", "washing up."], 44, ramp(t, 2.8, 3.0), (270, GY - 720))
    header(ctx, ease(t / 0.2), "NIGHTFALL", "Leo's tent: still missing.", "Wren's has fairy lights.", 0.9, t, main_size=52)
    meter(ctx, "RENT", "Washing up" if t > 2.8 else "?"); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 450, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    dome(ctx, 860, 1640, 0.62 + 0.02 * math.sin(t * 3), t, lights=1.0)
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “Ten minutes? Two seconds.”", 205 - (1 - a) * 20, 52, hexc('#22223b', a), maxw=1000)
    ctext(ctx, "Leo: “Mine is still out camping.”", 290, 52, hexc(RED, ease((t - 0.5) / 0.3)), maxw=1000)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Tent or hotel? Comment below!", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 3.3), (s1, 1.9), (s1, 2.6), (s1, 2.8), (s1, 3.0), (s1, 4.0), (s2, 0.9), (s2, 1.5), (s2, 2.2), (s2, 3.9), (s3, 1.5), (s3, 3.7), (s4, 2.6)]
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

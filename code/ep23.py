"""ep23 - Supermarket self-checkout: Wren scans one banana. 'Unexpected item in bagging area.' She goes to a real cashier."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep23"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; BLUE = '#3a86ff'; AMBER = '#ff9f1c'; GREEN = '#2a9d8f'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1700
WX, LX = 420, 995
HAND = (180, -320)
HX, HY = WX + HAND[0] * 1.1, GY + HAND[1] * 1.1          # Wren's hand on screen
SCAN = (690, 1328); PLAT = (862, 1380)

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

def ftext(ctx, s, cx, y, size, col, maxw):
    mv.font(ctx, size); e = ctx.text_extents(s)
    while e.x_advance > maxw and size > 12:
        size -= 1; mv.font(ctx, size); e = ctx.text_extents(s)
    ctx.move_to(cx - e.x_advance / 2, y); ctx.set_source_rgba(*col); ctx.show_text(s)

# ------------------------------------------------------------ props
def banana(ctx, x, y, s=1.0, ang=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.move_to(-62, -18); ctx.curve_to(-40, 26, 40, 26, 62, -18); ctx.curve_to(40, 8, -40, 8, -62, -18); ctx.close_path()
    ctx.set_source_rgba(*hexc('#ffd60a')); ctx.fill()
    ctx.move_to(-62, -18); ctx.curve_to(-40, 26, 40, 26, 62, -18); ctx.curve_to(42, 14, -42, 14, -62, -18); ctx.close_path()
    ctx.set_source_rgba(*hexc('#f4b400')); ctx.fill()
    ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#6b4423'))
    ctx.move_to(60, -16); ctx.line_to(72, -28); ctx.stroke(); circle(ctx, -62, -17, 5, hexc('#3b2a1a'))
    ctx.restore()

def shelves(ctx, t):
    mv.vgrad(ctx, '#e8f6f1', '#d3ece4')
    random.seed(23)
    for row, sy in enumerate((700, 900, 1100, 1300)):
        ctx.rectangle(0, sy, W, 16); ctx.set_source_rgba(*hexc('#9aa5b1')); ctx.fill()
        x = 10
        while x < W - 20:
            w = random.choice((46, 56, 66, 40)); h = random.choice((70, 90, 110, 130))
            c = random.choice(('#ff6b6b', '#ffd166', '#06d6a0', '#118ab2', '#f78c6b', '#c77dff', '#ffffff', '#ef476f'))
            rrect(ctx, x, sy - h, w, h, 6); ctx.set_source_rgba(*hexc(c, 0.85)); ctx.fill()
            rrect(ctx, x + 8, sy - h + 16, w - 16, 14, 4); ctx.set_source_rgba(1, 1, 1, 0.6); ctx.fill()
            x += w + 8
    ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(*hexc('#e8f6f1', 0.35)); ctx.fill()     # soften: it's background
    # floor tiles
    ctx.rectangle(0, 1420, W, H - 1420); ctx.set_source_rgba(*hexc('#eef1f4')); ctx.fill()
    for i in range(10):
        for j in range(5):
            if (i + j) % 2: ctx.rectangle(i * 120 - 20, 1420 + j * 110, 120, 110); ctx.set_source_rgba(*hexc('#d9dfe6')); ctx.fill()

SCREENS = {
    'welcome': (BLUE, "WELCOME!", "Scan your first item"),
    'banana': (BLUE, "BANANA", "Now bag your item"),
    'unexp': (RED, "UNEXPECTED ITEM", "IN BAGGING AREA"),
    'place': (AMBER, "PLEASE PLACE ITEM", "IN BAGGING AREA"),
    'wait': (RED, "PLEASE WAIT", "FOR ASSISTANCE"),
}
def kiosk(ctx, t, msg, light=False, shake=0.0, scanflash=0.0):
    sx = math.sin(t * 70) * 6 * shake
    ctx.save(); ctx.translate(sx, 0)
    # pole + light
    ctx.set_line_width(12); ctx.set_source_rgba(*hexc('#5c677d')); ctx.move_to(840, 940); ctx.line_to(840, 860); ctx.stroke()
    on = light and int(t * 6) % 2 == 0
    if on: circle(ctx, 840, 835, 70, hexc(RED, 0.25))
    ctx.arc(840, 852, 34, math.pi, 0); ctx.close_path(); ctx.set_source_rgba(*hexc(RED if on else '#b5838d')); ctx.fill()
    # screen
    col, l1, l2 = SCREENS[msg]
    rrect(ctx, 556, 930, 312, 248, 20); ctx.set_source_rgba(*hexc('#2b2d42')); ctx.fill()
    rrect(ctx, 570, 944, 284, 220, 12); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    if msg in ('unexp', 'wait'):
        ctx.move_to(712, 962); ctx.line_to(746, 1020); ctx.line_to(678, 1020); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        ftext(ctx, "!", 712, 1014, 40, hexc(col), 40)
    elif msg == 'banana': banana(ctx, 712, 1000, 0.6)
    else:
        circle(ctx, 712, 992, 32, (1, 1, 1, 1)); circle(ctx, 700, 984, 5, hexc(col)); circle(ctx, 724, 984, 5, hexc(col))
        ctx.set_line_width(5); ctx.set_source_rgba(*hexc(col)); ctx.arc(712, 994, 14, 0.3, math.pi - 0.3); ctx.stroke()
    ftext(ctx, l1, 712, 1080, 34, (1, 1, 1, 1), 260)
    ftext(ctx, l2, 712, 1128, 26, (1, 1, 1, 1), 260)
    if msg == 'wait':
        for k in range(8):
            a = k * math.pi / 4 + t * 4; circle(ctx, 712 + 16 * math.cos(a) + 110, 1000 + 16 * math.sin(a), 4, (1, 1, 1, 0.3 + 0.7 * k / 8))
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#5c677d')); ctx.move_to(712, 1178); ctx.line_to(712, 1350); ctx.stroke()
    # cabinet + scanner
    rrect(ctx, 580, 1350, 220, 350, 18); ctx.set_source_rgba(*hexc('#8d99ae')); ctx.fill()
    rrect(ctx, 580, 1350, 220, 40, 12); ctx.set_source_rgba(*hexc('#5c677d')); ctx.fill()
    rrect(ctx, 620, 1360, 140, 20, 6); ctx.set_source_rgba(*hexc('#ff4d6d', 0.35 + 0.65 * scanflash)); ctx.fill()
    rrect(ctx, 610, 1470, 160, 30, 8); ctx.set_source_rgba(*hexc('#2b2d42')); ctx.fill()          # card slot
    rrect(ctx, 640, 1560, 100, 70, 10); ctx.set_source_rgba(*hexc('#edf2f4')); ctx.fill()
    # bagging platform
    ctx.rectangle(820, 1404, 16, 296); ctx.rectangle(890, 1404, 16, 296); ctx.set_source_rgba(*hexc('#5c677d')); ctx.fill()
    rrect(ctx, 800, 1390, 126, 22, 8); ctx.set_source_rgba(*hexc('#8d99ae')); ctx.fill()
    ctx.restore()
    return sx

def trolley(ctx, x, y, s, t, goods=0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    random.seed(int(goods) + 7)
    for k in range(5):
        c = random.choice(('#ff6b6b', '#ffd166', '#06d6a0', '#118ab2', '#c77dff', '#f78c6b'))
        rrect(ctx, -100 + k * 42, -250 - random.randint(0, 60), 40, 120, 6); ctx.set_source_rgba(*hexc(c)); ctx.fill()
    ctx.move_to(-120, -170); ctx.line_to(120, -170); ctx.line_to(96, -40); ctx.line_to(-96, -40); ctx.close_path()
    ctx.set_source_rgba(*hexc('#adb5bd', 0.55)); ctx.fill()
    ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#6c757d'))
    ctx.move_to(-120, -170); ctx.line_to(120, -170); ctx.line_to(96, -40); ctx.line_to(-96, -40); ctx.close_path(); ctx.stroke()
    for k in range(1, 6): ctx.move_to(-120 + k * 40, -170); ctx.line_to(-96 + k * 32, -40); ctx.stroke()
    ctx.move_to(120, -170); ctx.line_to(160, -200); ctx.stroke()
    ctx.move_to(-96, -40); ctx.line_to(-90, -16); ctx.line_to(90, -16); ctx.line_to(96, -40); ctx.stroke()
    for wx in (-80, 80): circle(ctx, wx, -6, 14, hexc('#343a40'))
    ctx.restore()

def cashier(ctx, x, gy, t, smile=True):
    b = 3 * math.sin(t * 5)
    rrect(ctx, x - 82, gy - 520 + b, 164, 300, 44); ctx.set_source_rgba(*hexc(GREEN)); ctx.fill()        # shirt
    rrect(ctx, x - 56, gy - 470 + b, 112, 250, 20); ctx.set_source_rgba(*hexc('#fefae0')); ctx.fill()     # apron
    rrect(ctx, x - 40, gy - 440 + b, 80, 30, 8); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()        # name tag
    circle(ctx, x, gy - 600 + b, 74, hexc('#a86b4c'))
    for sg in (-1, 1): circle(ctx, x + sg * 72, gy - 596 + b, 16, hexc('#a86b4c'))
    ctx.arc(x, gy - 612 + b, 78, math.pi * 1.05, -0.05); ctx.close_path(); ctx.set_source_rgba(*hexc('#3a2618')); ctx.fill()
    circle(ctx, x + 70, gy - 650 + b, 30, hexc('#3a2618'))
    for dx in (-26, 26): circle(ctx, x + dx, gy - 600 + b, 8, hexc('#1d1d2c'))
    circle(ctx, x - 44, gy - 572 + b, 12, hexc('#f28b82', 0.5)); circle(ctx, x + 44, gy - 572 + b, 12, hexc('#f28b82', 0.5))
    ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#1d1d2c')); ctx.arc(x, gy - 578 + b, 22, 0.2, math.pi - 0.2); ctx.stroke()
    ctx.set_line_width(36); ctx.set_source_rgba(*hexc(GREEN))
    ctx.move_to(x - 70, gy - 470 + b); ctx.line_to(x - 140, gy - 380); ctx.stroke(); circle(ctx, x - 140, gy - 380, 20, hexc('#a86b4c'))

def lane_bg(ctx, t):
    shelves(ctx, t)
    rrect(ctx, 760, 640, 260, 90, 14); ctx.set_source_rgba(*hexc(GREEN)); ctx.fill()                      # lane sign
    ftext(ctx, "LANE 1", 890, 702, 46, (1, 1, 1, 1), 230)
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#5c677d')); ctx.move_to(800, 600); ctx.line_to(800, 640); ctx.move_to(980, 600); ctx.line_to(980, 640); ctx.stroke()

def counter(ctx, t, belt_speed=1.0):
    rrect(ctx, 590, 1310, 520, 60, 10); ctx.set_source_rgba(*hexc('#2b2d42')); ctx.fill()                  # belt
    ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.2)
    for k in range(10):
        x = 590 + ((k * 60 + t * 90 * belt_speed) % 520); ctx.move_to(x, 1316); ctx.line_to(x - 10, 1364); ctx.stroke()
    ctx.rectangle(590, 1370, 520, 330); ctx.set_source_rgba(*hexc('#f4a261')); ctx.fill()
    ctx.rectangle(590, 1370, 520, 26); ctx.set_source_rgba(*hexc('#e76f51')); ctx.fill()
    for k in range(4): ctx.rectangle(620 + k * 120, 1430, 8, 270); ctx.set_source_rgba(*hexc('#e9915a')); ctx.fill()
    rrect(ctx, 920, 1200, 120, 110, 12); ctx.set_source_rgba(*hexc('#343a40')); ctx.fill()                 # till
    rrect(ctx, 934, 1214, 92, 50, 6); ctx.set_source_rgba(*hexc('#90e0ef')); ctx.fill()

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    shelves(ctx, t)
    scanned = t >= 0.95; landed = t >= 1.7
    msg = 'welcome' if not scanned else ('banana' if not landed else 'unexp')
    flash = clamp01(1 - abs(t - 0.95) / 0.15)
    kiosk(ctx, t, msg, shake=clamp01(1 - (t - 1.7) / 0.4) if landed else 0, scanflash=flash)
    wren(ctx, WX, GY, 1.1, t, "point", expr="shock" if 1.75 < t < 2.4 else "happy", hand=HAND)
    k1 = ramp(t, 0.4, 0.95); k2 = ramp(t, 1.2, 1.7)
    bx = lerp(lerp(HX, SCAN[0], k1), PLAT[0], k2); by = lerp(lerp(HY - 4, SCAN[1], k1), PLAT[1], k2) - 90 * math.sin(math.pi * k2)
    banana(ctx, bx, by, 1.0, 0.3 * math.sin(math.pi * k2))
    if 0.95 < t < 1.2: burst(ctx, SCAN[0], SCAN[1] - 20, 1 - (t - 0.95) / 0.25, 80)
    kid(ctx, LX, GY, 0.85, t, "flat" if landed else "smile", (-60, -200))
    bubble_ml(ctx, 400, 760, ["We were just", "introduced!"], 44, ramp(t, 2.3, 2.5), (WX, 930))
    header(ctx, ease(t / 0.2 + 1), "SELF-CHECKOUT", "Wren scans one banana.", "The machine panics.", -0.3, t, main_size=56)
    meter(ctx, "MACHINE ERRORS", "1" if landed else "0"); wm(ctx)

TOG = 0.42
def s1(ctx, t, d):
    shelves(ctx, t)
    n = int(clamp01((t - 0.3) / (TOG * 8)) * 8) if t > 0.3 else 0          # toggles done
    on_plat = n % 2 == 0
    ph = clamp01(((t - 0.3) % TOG) / 0.22) if 0.3 < t < 0.3 + TOG * 8 else 1.0
    msg = 'unexp' if on_plat else 'place'
    kiosk(ctx, t, msg, shake=0.6 if 0.3 < t < 0.3 + TOG * 8 else 0)
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy" if t < 2.0 else "shock", hand=HAND)
    a, b = ((HX, HY - 4), PLAT) if on_plat else (PLAT, (HX, HY - 4))
    k = ease(ph); bx = lerp(a[0], b[0], k); by = lerp(a[1], b[1], k) - 70 * math.sin(math.pi * k)
    banana(ctx, bx, by, 1.0, 0.25 * math.sin(math.pi * k))
    kid(ctx, LX, GY, 0.85, t, "flat", (-60, -200))
    errs = 1 + n
    bubble_ml(ctx, 420, 760, ["Make up", "your MIND!"], 48, ramp(t, 3.0, 3.2), (WX, 930))
    header(ctx, ease(t / 0.2), "ROUND TWO", "Take it off. Put it back.", "Repeat. Forever.", 1.2, t, main_size=56)
    meter(ctx, "MACHINE ERRORS", "%d" % errs); wm(ctx)

def s2(ctx, t, d):
    shelves(ctx, t)
    nq = int(clamp01((t - 0.2) / 2.6) * 8)
    for k in range(min(nq, 3)):                                              # queue rolls in behind
        x = lerp(-300, 120 + k * 60, ramp(t, 0.2 + k * 0.6, 0.7 + k * 0.6))
        trolley(ctx, x, 1470 - k * 24, 0.75 - 0.08 * k, t, k)
    kiosk(ctx, t, 'wait', light=True)
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy", hand=HAND)
    banana(ctx, PLAT[0], PLAT[1], 1.0)
    kid(ctx, LX, GY, 0.85, t, "flat", (0, -150))
    bubble_ml(ctx, 890, 1250, ["Everyone's", "staring!"], 40, ramp(t, 0.9, 1.1) * (1 - ramp(t, 2.6, 2.75)), (LX, 1372))
    bubble_ml(ctx, 400, 760, ["Good.", "Witnesses."], 48, ramp(t, 2.9, 3.1), (WX, 930))
    header(ctx, ease(t / 0.2), "THE LIGHT STARTS FLASHING", "Help is coming.", "Help is not coming.", 1.4, t, main_size=56)
    meter(ctx, "QUEUE BEHIND WREN", "%d trolleys" % nq); wm(ctx)

def s3(ctx, t, d):
    lane_bg(ctx, t)
    cashier(ctx, 800, GY, t)
    counter(ctx, t, 1.0 if t < 1.0 else 0.0)
    wx = lerp(-200, WX, ramp(t, 0.0, 0.6))
    wren(ctx, wx, GY, 1.1, t, "point", expr="happy", hand=HAND)
    hx = wx + HAND[0] * 1.1
    k = ramp(t, 0.6, 1.1); bx = lerp(hx, 700, k); by = lerp(HY - 4, 1300, k) - 50 * math.sin(math.pi * k)
    if t < 1.3: banana(ctx, bx, by, 1.0)
    else: banana(ctx, 662, 1296, 1.0, -0.2)                                  # cashier holds it up
    if 1.2 < t < 1.5: burst(ctx, 980, 1190, 1 - (t - 1.2) / 0.3, 110)
    if t > 1.2:                                                               # receipt
        L = 120 * ramp(t, 1.2, 1.8); rrect(ctx, 952, 1200 - L, 56, L, 4); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ftext(ctx, "PAID" if t > 1.2 else "$0.45", 980, 1250, 26, hexc('#1d3557'), 84)
    bubble_ml(ctx, 760, 790, ["Lovely banana!", "Have a nice day."], 40, ramp(t, 1.4, 1.6) * (1 - ramp(t, 2.6, 2.75)), (800, 1010))
    bubble_ml(ctx, 400, 780, ["See, Leo?", "SHE expected me."], 44, ramp(t, 2.85, 3.05), (WX, 930))
    header(ctx, ease(t / 0.2), "WREN'S FIX", "Lane 1. A real human.", "Done in two seconds.", 1.2, t, main_size=56)
    meter(ctx, "TIME AT LANE 1", "%d sec" % (2 if t > 1.2 else int(t * 2))); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 470, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    banana(ctx, 800, 1560, 1.6, 0.2 * math.sin(t * 3))
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “I'm an EXPECTED item.”", 205 - (1 - a) * 20, 56, hexc('#22223b', a), maxw=1000)
    ctext(ctx, "Leo: “The machine disagrees.”", 290, 58, hexc(RED, ease((t - 0.5) / 0.3)), maxw=960)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Team self-checkout or team cashier?", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 1.2), (s0, 3.3), (s1, 0.5), (s1, 1.6), (s1, 3.9), (s2, 1.5), (s2, 2.0), (s2, 3.9), (s3, 0.9), (s3, 2.0), (s3, 3.6), (s4, 2.6), (s4, 1.0)]
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

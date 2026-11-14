import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = "/home/claude/wren/ep15"
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1560           # jetty deck
WATER = 1560

def lake(ctx, t, sun=0.0):
    g = cairo.LinearGradient(0, 0, 0, 1200); g.add_color_stop_rgb(0, *hexc('#ffb88c')[:3]); g.add_color_stop_rgb(0.6, *hexc('#ffd9a8')[:3]); g.add_color_stop_rgb(1, *hexc('#fff0cf')[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1250); ctx.fill()
    circle(ctx, 780, 1010 - 40 * sun, 120, hexc('#fff3b0')); circle(ctx, 780, 1010 - 40 * sun, 170, hexc('#fff3b0', 0.25))
    for x0, h, c in ((-80, 360, '#7aa18f'), (260, 250, '#8bb09e'), (700, 420, '#6f9884'), (980, 280, '#7aa18f')):   # hills
        ctx.move_to(x0, 1250); ctx.curve_to(x0 + 120, 1250 - h, x0 + 300, 1250 - h, x0 + 480, 1250); ctx.set_source_rgba(*hexc(c)); ctx.fill()
    g2 = cairo.LinearGradient(0, 1250, 0, H); g2.add_color_stop_rgb(0, *hexc('#8fd0d8')[:3]); g2.add_color_stop_rgb(1, *hexc('#2f7f9a')[:3])
    ctx.set_source(g2); ctx.rectangle(0, 1250, W, H - 1250); ctx.fill()
    for k in range(10):                                                     # sun glitter
        w = (220 - k * 14) * (0.9 + 0.1 * math.sin(t * 3 + k)); ctx.rectangle(780 - w / 2, 1262 + k * 28, w, 7); ctx.set_source_rgba(1, 0.97, 0.7, 0.55 - k * 0.04); ctx.fill()
    for k in range(7):                                                      # ripples
        y = 1330 + k * 96; ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.25)
        for j in range(5):
            x = (j * 260 + k * 90 + t * 20 * (1 + k % 2)) % 1300 - 100; ctx.move_to(x, y); ctx.curve_to(x + 30, y - 8, x + 60, y + 8, x + 90, y); ctx.stroke()

def jetty(ctx):
    ctx.rectangle(-10, GY, 700, 40); ctx.set_source_rgba(*hexc('#a0622d')); ctx.fill()
    for k in range(8): ctx.rectangle(-10 + k * 90, GY, 4, 40); ctx.set_source_rgba(0, 0, 0, 0.18); ctx.fill()
    for px in (60, 330, 600):
        ctx.rectangle(px, GY + 40, 30, 330); ctx.set_source_rgba(*hexc('#6b4423')); ctx.fill()
        ctx.rectangle(px, GY + 40, 30, 330); ctx.set_source_rgba(*hexc('#2f7f9a', 0.35)); ctx.fill()
    ctx.rectangle(-10, GY + 2, 700, 8); ctx.set_source_rgba(*hexc('#c98a52')); ctx.fill()

def water_front(ctx, t):
    # translucent water overlay hiding lower piles
    g = cairo.LinearGradient(0, GY + 120, 0, H); g.add_color_stop_rgba(0, *hexc('#8fd0d8')[:3], 0.0); g.add_color_stop_rgba(0.25, *hexc('#4aa0b8')[:3], 0.85); g.add_color_stop_rgba(1, *hexc('#2f7f9a')[:3], 1)
    ctx.set_source(g); ctx.rectangle(0, GY + 120, W, H - GY - 120); ctx.fill()

def rod(ctx, hand, tip, float_pos, bend=0.0, taut=False, col='#3d2b1f'):
    hx, hy = hand; tx, ty = tip
    cx, cy = (hx + tx) / 2, (hy + ty) / 2 + 90 * bend
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(9); ctx.set_source_rgba(*hexc(col))
    ctx.move_to(hx - (tx - hx) * 0.12, hy - (ty - hy) * 0.12); ctx.quad_curve_to(cx, cy, tx, ty) if hasattr(ctx, 'quad_curve_to') else ctx.curve_to(cx, cy, cx, cy, tx, ty); ctx.stroke()
    fx, fy = float_pos
    ctx.set_line_width(2.5); ctx.set_source_rgba(1, 1, 1, 0.85)
    if taut: ctx.move_to(tx, ty); ctx.line_to(fx, fy)
    else: ctx.move_to(tx, ty); ctx.curve_to(tx + 60, ty + 50, fx - 30, fy - 120, fx, fy)
    ctx.stroke()

def bobber(ctx, x, y, dip=0.0):
    ctx.save(); ctx.translate(x, y + 26 * dip)
    ctx.save(); ctx.rectangle(-30, -60, 60, 60 + 0); ctx.clip()
    circle(ctx, 0, 0, 20, hexc('#ffffff')); ctx.restore()
    ctx.save(); ctx.rectangle(-30, -60, 60, 62); ctx.clip(); circle(ctx, 0, 0, 20, hexc(RED)); ctx.rectangle(-22, -14, 44, 14); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill(); ctx.restore()
    ctx.restore()
    for k in range(3):
        a = (math.sin(0) if dip < 0.05 else 1)
    e4.ell(ctx, x, y + 34 * dip + 2, 34 + 20 * dip, 8 + 5 * dip, (1, 1, 1, 0.45))

def fish(ctx, x, y, s, ang=0.0, col='#ff9f43', mood="smug"):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.move_to(-90, 0); ctx.line_to(-150, -46); ctx.line_to(-150, 46); ctx.close_path(); ctx.set_source_rgba(*hexc('#ff7f2a')); ctx.fill()
    e4.ell(ctx, 0, 0, 100, 56, hexc(col))
    e4.ell(ctx, 10, 22, 72, 22, hexc('#ffe0b0'))
    ctx.move_to(-10, -52); ctx.line_to(24, -92); ctx.line_to(50, -50); ctx.close_path(); ctx.set_source_rgba(*hexc('#ff7f2a')); ctx.fill()
    circle(ctx, 56, -10, 16, hexc('#ffffff')); circle(ctx, 60, -8, 8, hexc('#22223b'))
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#22223b'))
    if mood == "smug": ctx.move_to(40, -30); ctx.line_to(76, -26); ctx.stroke(); ctx.move_to(62, 22); ctx.curve_to(78, 28, 92, 20, 96, 10); ctx.stroke()
    ctx.restore()

def boot(ctx, x, y, s=1.0, ang=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.move_to(-40, -110); ctx.line_to(40, -110); ctx.line_to(46, 20); ctx.curve_to(110, 30, 130, 70, 100, 90); ctx.line_to(-50, 90); ctx.close_path(); ctx.set_source_rgba(*hexc('#6b4a2b')); ctx.fill()
    ctx.rectangle(-44, -120, 92, 24); ctx.set_source_rgba(*hexc('#4a321d')); ctx.fill()
    ctx.restore()
    for k in range(3): ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#5a7a3a')); ctx.move_to(x - 30 + k * 30, y + 90); ctx.line_to(x - 40 + k * 32, y + 150); ctx.stroke()

def tally(ctx, leo, wr, a=1.0):
    rrect(ctx, 90, 524, 900, 74, 37); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 572); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text("FISH CAUGHT")
    mv.font(ctx, 34); s1 = "LEO: %d" % leo; ctx.move_to(450, 573); ctx.set_source_rgba(*hexc('#9ad1ff', a)); ctx.show_text(s1)
    s2 = "WREN: %d" % wr; e = ctx.text_extents(s2); ctx.move_to(960 - e.x_advance, 573); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(s2)

LW, LL = (430, GY), (150, GY)    # Wren, Leo foot positions

def scene_base(ctx, t, sun=0.0):
    lake(ctx, t, sun); jetty(ctx)

# ------------------------------------------------------------------ scenes
def s0(ctx, t, d):
    scene_base(ctx, t, ramp(t, 0, d))
    cast = ramp(t, 1.0, 1.6)
    wren(ctx, LW[0], GY, 0.85, t, "point", expr="happy", hand=(150, -230))
    kid(ctx, LL[0], GY, 1.05, t, "smug", (130 + 30 * cast, -260 - 40 * cast))
    rrect(ctx, 520, GY - 70, 40, 70, 10); ctx.set_source_rgba(*hexc('#2a9d8f')); ctx.fill()
    whand = (LW[0] + 150 * 0.85, GY - 230 * 0.85)
    rod(ctx, (LL[0] + 130 * 1.05, GY - 260 * 1.05), (700, 1220), (800, 1520), 0); bobber(ctx, 800, 1520)
    rod(ctx, whand, (810, 1210), (960, 1520), 0, col='#8d5524'); bobber(ctx, 960, 1520)
    water_front(ctx, t)
    bubble_ml(ctx, 400, 880, ["Leo watched", "3 videos."], 44, ramp(t, 0.5, 0.7), (LL[0] + 40, GY - 340))
    header(ctx, ease(t / 0.2 + 1), "WREN GOES FISHING", "Leo has the gear.", "Wren has a flask.", -0.3, t, main_size=56)
    tally(ctx, 0, 0); wm(ctx)

def s1(ctx, t, d):
    scene_base(ctx, t)
    got = t > 1.8
    wren(ctx, LW[0], GY, 0.85, t, "point", expr="happy", hand=(150, -230))
    kid(ctx, LL[0], GY, 1.05, t, "flat" if got else "smug", (130, -260))
    whand = (LW[0] + 150 * 0.85, GY - 230 * 0.85)
    rod(ctx, whand, (810, 1210), (960, 1520), 0, col='#8d5524'); bobber(ctx, 960, 1520)
    fl = (800, 1520)
    rod(ctx, (LL[0] + 130 * 1.05, GY - 260 * 1.05), (700, 1220), fl if t < 1.0 else (760, 1520 - 40 * ramp(t, 1.0, 1.8)), 0.1 * ramp(t, 1.0, 1.8))
    if t < 1.0: bobber(ctx, *fl)
    # catch: boot rising
    if t >= 1.0:
        k = ramp(t, 1.0, 1.9)
        y = lerp(1560 + 120, 1150, k); x = lerp(800, 740, k)
        boot(ctx, x, y, 0.8, 0.5 * math.sin(t * 6) * 0.5)
    water_front(ctx, t)
    if t >= 1.0:
        e4.ell(ctx, 800, 1560, 120 * (1 - 0.3 * ramp(t, 1.0, 1.9)), 24, hexc('#ffffff', 0.5))
    bubble_ml(ctx, 760, 1010, ["A boot."], 46, ramp(t, 2.0, 2.2) * (1 - ramp(t, 3.0, 3.2)), (LL[0] + 100, GY - 390))
    bubble_ml(ctx, 400, 980, ["Nice size!"], 44, ramp(t, 3.0, 3.2), (LW[0], GY - 330))
    header(ctx, ease(t / 0.2), "FIRST CATCH", "Leo hooks something big.", "It's a boot.", 2.0, t, main_size=54)
    tally(ctx, 0, 0); wm(ctx)

def s2(ctx, t, d):
    scene_base(ctx, t)
    pull = ramp(t, 1.0, 3.0)
    wx = LW[0] + 90 * pull
    shake = math.sin(t * 30) * 4 * ramp(t, 1.0, 1.4)
    lx = LL[0] + 70 * pull
    wren(ctx, wx + shake, GY, 0.85, t, "point", expr="shock" if t > 1.0 else "happy", hand=(150, -230))
    kid(ctx, lx, GY, 1.05, t, "shock" if t > 1.0 else "flat", (70, -230))
    # Leo hanging on to Wren
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(26); ctx.set_source_rgba(*hexc('#ff6b6b'))
    ctx.move_to(lx + 60, GY - 190); ctx.line_to(wx - 30, GY - 170); ctx.stroke()
    hand = (wx + 150 * 0.85, GY - 230 * 0.85)
    dip = ramp(t, 0.5, 0.8)
    rod(ctx, hand, (830, 1230 + 60 * pull), (960 + 8 * math.sin(t * 20), 1520 + 20 * dip), bend=0.6 * dip, taut=t > 1.0, col='#8d5524')
    bobber(ctx, 960, 1515, dip=dip * (1 if t < 1.0 else 1.4))
    # shadow under the water
    if t > 0.9:
        sh = ramp(t, 0.9, 1.5); ctx.save(); ctx.translate(960 - 60 * pull, 1700); ctx.scale(1, 0.5)
        e4.ell(ctx, 0, 0, 260 * sh, 110 * sh, hexc('#0d3b52', 0.65)); ctx.restore()
    water_front(ctx, t)
    if t > 1.0:
        for k in range(5): e4.ell(ctx, 900 + 30 * k, 1560 + 8 * (k % 2), 50 + 40 * ((t * 2 + k * 0.2) % 1), 10, (1, 1, 1, 0.35 * (1 - (t * 2 + k * 0.2) % 1)))
    bubble_ml(ctx, 760, 900, ["It's HUGE!"], 50, ramp(t, 1.3, 1.5) * (1 - ramp(t, 2.6, 2.8)), (wx + 60, GY - 330))
    bubble_ml(ctx, 460, 780, ["Hold on, Grandma!"], 42, ramp(t, 2.0, 2.2), (lx + 40, GY - 320))
    header(ctx, ease(t / 0.2), "WREN'S FLOAT MOVES", "Something big bites.", "Leo holds on.", 1.3, t, main_size=54)
    tally(ctx, 0, 0); wm(ctx)

def s3(ctx, t, d):
    scene_base(ctx, t, 1.0)
    WXs, LXs = 190, 520
    k = ramp(t, 0.5, 1.4)
    wren(ctx, WXs, GY, 0.85, t, "cheer" if 2.2 < t < 3.0 else "point", expr="happy", hand=(150, -230))
    lexpr = "shock" if 1.4 < t < 2.3 else ("flat" if t < 3.0 else "smug")
    kid(ctx, LXs, GY, 1.05, t, lexpr, (0, -150))
    whand = (WXs + 150 * 0.85, GY - 230 * 0.85)
    tipp = (640, 1170)
    drop = ramp(t, 3.0, 3.6)
    if t < 3.6:
        fx = lerp(960, 720, k) + 6 * math.sin(t * 9) * ramp(t, 1.4, 1.8)
        fy = lerp(1560, 1330, k) + 14 * math.sin(t * 6) * ramp(t, 1.4, 1.8)
        if t >= 3.0: fy = lerp(1330, 1580, drop * drop); fx += 30 * drop
        wig = (0.45 * math.sin(t * 16)) if t < 3.0 else 1.5 * drop
        if t < 3.0: rod(ctx, whand, tipp, (fx - 10, fy - 80), bend=0.2, taut=True, col='#8d5524')
        else: rod(ctx, whand, tipp, (fx, 1250), bend=0.0, col='#8d5524')
        fish(ctx, fx, fy, 0.62, ang=-0.6 + wig, mood="smug")
    else:
        rod(ctx, whand, tipp, (800, 1520), 0, col='#8d5524'); bobber(ctx, 800, 1520)
    water_front(ctx, t)
    burst(ctx, 960, 1540, clamp01(1 - (t - 0.5) / 0.4), 120 * (0.5 + (t - 0.5)))
    if 3.4 < t < 4.1: burst(ctx, 760, 1560, 1 - (t - 3.4) / 0.7, 130 * (0.4 + (t - 3.4)))
    bubble_ml(ctx, 330, 900, ["Dinner!"], 48, ramp(t, 1.4, 1.6) * (1 - ramp(t, 2.4, 2.6)), (WXs + 70, GY - 330))
    bubble_ml(ctx, 600, 900, ["...Is that it?"], 46, ramp(t, 2.0, 2.2) * (1 - ramp(t, 3.0, 3.2)), (LXs + 20, GY - 380))
    if t > 3.0:
        bubble_ml(ctx, 420, 880, ["Aww. He looks like Andy.", "Back you go."], 40, ramp(t, 3.0, 3.2), (WXs + 70, GY - 330))
    header(ctx, ease(t / 0.2), "THE BIG CATCH", "The monster is tiny.", "It has attitude.", 1.0, t, main_size=54)
    tally(ctx, 0, 1 if t > 1.2 else 0); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    a = ease(t / 0.3)
    ctext(ctx, "Leo: 1 boot.", 205 - (1 - a) * 20, 62, hexc('#22223b', a), maxw=940)
    ctext(ctx, "Wren: 1 fish. Released.", 290, 62, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Send this to your fishing buddy", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

SCENES = [(s0, 3.4), (s1, 4.0), (s2, 4.2), (s3, 4.4), (s4, 3.2)]

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
        picks = [(s0, 1.0), (s0, 2.4), (s1, 1.0), (s1, 2.5), (s2, 0.7), (s2, 2.4), (s3, 0.9), (s3, 2.3), (s3, 3.8), (s4, 2.0)]
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

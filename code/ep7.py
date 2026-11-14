import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ai_tag, ease, wren
import ep4 as e4
import ep2 as e2
from ep5 import CX, GY, S, gate, kid

OUT = "/home/claude/wren/ep7"
os.makedirs(OUT, exist_ok=True)
DARK, RED = hexc('#22223b'), '#e63946'
FLOOR = 1665

# ---------- props ----------
def big_suitcase(ctx, x, y, lid_open=0.0, packed=True):
    """Hard suitcase, base on the floor at y. lid_open in radians."""
    rrect(ctx, x - 190, y - 150, 380, 150, 24); ctx.set_source_rgba(*hexc('#457b9d')); ctx.fill()
    ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#2b4d66'))
    for k in (-1, 0, 1): ctx.move_to(x + k * 100, y - 140); ctx.line_to(x + k * 100, y - 10); ctx.stroke()
    if lid_open > 0.05:
        for cx_, cy_, r_, col in ((-120, -168, 54, '#e63946'), (-40, -190, 58, '#ffd166'), (50, -176, 56, '#80b918'), (130, -166, 52, '#f8f9fa')):
            circle(ctx, x + cx_, y + cy_, r_, hexc(col))
    ctx.save(); ctx.translate(x - 190, y - 150); ctx.rotate(-lid_open)
    rrect(ctx, 0, -92, 380, 92, 24); ctx.set_source_rgba(*hexc('#3a6a8a')); ctx.fill()
    ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#2b4d66'))
    for k in (1, 3): ctx.move_to(k * 95, -84); ctx.line_to(k * 95, -8); ctx.stroke()
    if packed and lid_open < 0.05:   # bulging seam, sleeve poking out
        ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#1d3a4d')); ctx.move_to(0, 0); ctx.curve_to(120, -14, 260, -14, 380, 0); ctx.stroke()
        rrect(ctx, 250, -22, 70, 26, 12); ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    ctx.restore()
    ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#2b2d42'))
    ctx.move_to(x - 50, y - 240 if lid_open < 0.05 else y - 150); ctx.line_to(x + 50, y - 240 if lid_open < 0.05 else y - 150); ctx.stroke()
    for wx in (-150, 150): circle(ctx, x + wx, y - 6, 14, hexc('#22223b'))
    for sx, sy, c in ((-110, -100, '#ffd166'), (90, -70, '#e63946')):
        ctx.save(); ctx.translate(x + sx, y + sy); ctx.rotate(0.2); rrect(ctx, -26, -18, 52, 36, 8); ctx.set_source_rgba(*hexc(c)); ctx.fill(); ctx.restore()

def layers(ctx, cx, gy, s, t, k):
    """Extra clothes worn on top of Wren; k in 0..1 reveals them one by one."""
    ctx.save(); ctx.translate(cx, gy); ctx.scale(s, s); ctx.translate(0, math.sin(t * 2 * math.pi * 1.1) * 5)
    if k > 0.12:
        ctx.save(); ctx.rectangle(-420, -452, 840, 300); ctx.clip()
        rrect(ctx, -140, -470, 280, 320, 64); ctx.set_source_rgba(*hexc('#f4a261')); ctx.fill()
        ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#d98a45'))
        for yy in (-400, -330, -260, -190): ctx.move_to(-134, yy); ctx.line_to(134, yy); ctx.stroke()
        ctx.set_source_rgba(*hexc('#b86a28')); ctx.move_to(0, -465); ctx.line_to(0, -155); ctx.stroke()
        for sg in (-1, 1):
            rrect(ctx, 120 * sg - (0 if sg > 0 else 180), -432, 180, 94, 47); ctx.set_source_rgba(*hexc('#f4a261')); ctx.fill()
            circle(ctx, sg * 296, -385, 38, hexc('#f1f3f5'))
        ctx.restore()
    for i, (th, col, yy) in enumerate(((0.3, '#ffd166', -432), (0.42, '#4cc9f0', -418), (0.54, '#80b918', -404))):
        if k > th: e4.ell(ctx, 0, yy, 100 - i * 4, 31, hexc(col))
    for i, (th, col, cyy, r) in enumerate(((0.66, '#4cc9f0', -625, 78), (0.8, '#e63946', -690, 56), (0.92, '#ffd166', -738, 42))):
        if k > th:
            ctx.arc(0, cyy, r, math.pi, 2 * math.pi); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
            rrect(ctx, -r - 6, cyy - 6, 2 * r + 12, 20, 9); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill()
    if k > 0.92: circle(ctx, 0, -738 - 46, 16, hexc('#f8f9fa'))
    ctx.restore()

def burst(ctx, t0, t, ox, oy, seed):
    tau = t - t0
    if tau < 0: return
    r = random.Random(seed)
    for i in range(14):
        vx, vy, g = r.uniform(-460, 460), r.uniform(-1150, -650), 2400
        x0, y0 = ox + r.uniform(-60, 60), oy
        tl = (-vy + math.sqrt(vy * vy - 2 * g * (y0 - FLOOR))) / g; tt = min(tau, tl)
        x, y = x0 + vx * tt, y0 + vy * tt + 0.5 * g * tt * tt
        rot = r.uniform(0, 6) + tt * r.uniform(-8, 8)
        ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(0.55, 0.55)
        if i % 3 == 0: e2.sock(ctx, 0, 0, 1.0)
        elif i % 3 == 1: e2.item_shirt(ctx)
        else: rrect(ctx, -40, -30, 80, 60, 14); ctx.set_source_rgba(*hexc(r.choice(['#e63946', '#ffd166', '#80b918', '#4cc9f0', '#f8f9fa']))); ctx.fill()
        ctx.restore()

def wm(ctx):
    rrect(ctx, 60, 1648, 262, 54, 27); ctx.set_source_rgba(1, 1, 1, 0.88); ctx.fill()
    mv.font(ctx, 28); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    ctx.move_to(60 + (262 - e.x_advance) / 2, 1685); ctx.set_source_rgba(*hexc(RED)); ctx.show_text(s_)

def pill(ctx, t, text, t0=0.3):
    a = ease((t - t0) / 0.3)
    if a <= 0: return
    rrect(ctx, 120, 1738, 840, 60, 30); ctx.set_source_rgba(1, 1, 1, 0.9 * a); ctx.fill()
    mv.font(ctx, 30); e = ctx.text_extents(text); ctx.move_to(540 - e.x_advance / 2, 1778); ctx.set_source_rgba(*hexc('#22223b', a)); ctx.show_text(text)

def header(ctx, a, chip, main, red=None, red_t=0.0, t=0.0, main_size=62):
    e4.top_box(ctx, a, 360)
    if chip: ctext(ctx, chip, 215, 44, hexc(RED, a), maxw=900)
    ctext(ctx, main, 305 if chip else 245, main_size, hexc('#22223b', a), maxw=900)
    if red: ctext(ctx, red, 410 if chip else 350, 54, hexc(RED, ease((t - red_t) / 0.3)), maxw=900)

def hotel(ctx, t, clock="10:59"):
    mv.vgrad(ctx, '#f6e8d6', '#ead7bf')
    ctx.set_line_width(2); ctx.set_source_rgba(1, 1, 1, 0.35)
    for x in range(-100, W + 200, 70): ctx.move_to(x, 700); ctx.line_to(x, 1640); ctx.stroke()
    # window with curtains and a little skyline
    ctx.save(); rrect(ctx, 610, 880, 290, 320, 14); ctx.clip()
    g = cairo.LinearGradient(0, 880, 0, 1200); g.add_color_stop_rgb(0, *hexc('#8ecae6')[:3]); g.add_color_stop_rgb(1, *hexc('#e1f4ff')[:3]); ctx.set_source(g); ctx.paint()
    for bx, bw, bh in ((620, 60, 140), (690, 50, 200), (748, 70, 120), (826, 60, 170)):
        ctx.rectangle(bx, 1200 - bh, bw, bh); ctx.set_source_rgba(*hexc('#6c8ea4')); ctx.fill()
    mv.cloud(ctx, 640 + t * 6, 930, 0.35); ctx.restore()
    ctx.set_line_width(12); ctx.set_source_rgba(*hexc('#8d5524')); rrect(ctx, 610, 880, 290, 320, 14); ctx.stroke()
    ctx.move_to(755, 880); ctx.line_to(755, 1200); ctx.stroke()
    rrect(ctx, 560, 850, 390, 18, 9); ctx.set_source_rgba(*hexc('#6b4423')); ctx.fill()
    for cx0, cw in ((566, 70), (880, 70)):
        rrect(ctx, cx0, 866, cw, 360, 20); ctx.set_source_rgba(*hexc('#2a9d8f')); ctx.fill()
    # picture frame
    rrect(ctx, 180, 900, 170, 130, 10); ctx.set_source_rgba(*hexc('#8d5524')); ctx.fill()
    rrect(ctx, 192, 912, 146, 106, 6); ctx.set_source_rgba(*hexc('#bde0fe')); ctx.fill()
    ctx.move_to(192, 1018); ctx.line_to(240, 950); ctx.line_to(280, 1000); ctx.line_to(305, 970); ctx.line_to(338, 1018); ctx.close_path(); ctx.set_source_rgba(*hexc('#5c8a6b')); ctx.fill()
    # check-out sign
    rrect(ctx, 250, 735, 580, 110, 18); ctx.set_source_rgba(*hexc('#1d2433')); ctx.fill()
    mv.font(ctx, 36); ctx.move_to(282, 800); ctx.set_source_rgba(*hexc('#ffb703')); ctx.show_text("CHECK-OUT 11:00")
    blink = 1.0 if math.sin(t * 6) > 0 else 0.45
    mv.font(ctx, 44); ctx.move_to(660, 802); ctx.set_source_rgba(1, 0.3, 0.3, blink); ctx.show_text(clock)
    # bed
    rrect(ctx, 560, 1330, 430, 230, 20); ctx.set_source_rgba(*hexc('#8d5524')); ctx.fill()
    rrect(ctx, 560, 1440, 430, 170, 22); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill()
    rrect(ctx, 560, 1510, 430, 100, 18); ctx.set_source_rgba(*hexc('#e76f51')); ctx.fill()
    e4.ell(ctx, 650, 1452, 62, 24, hexc('#ffffff')); e4.ell(ctx, 800, 1452, 62, 24, hexc('#f1f3f5'))
    # nightstand and lamp
    rrect(ctx, 110, 1500, 110, 120, 10); ctx.set_source_rgba(*hexc('#8d5524')); ctx.fill()
    ctx.move_to(130, 1500); ctx.line_to(200, 1500); ctx.line_to(184, 1430); ctx.line_to(146, 1430); ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    ctx.rectangle(160, 1500, 10, 16); ctx.set_source_rgba(*hexc('#6b4423')); ctx.fill()
    # floor
    ctx.rectangle(-200, 1640, W + 400, 700); ctx.set_source_rgba(*hexc('#c9a27a')); ctx.fill()
    ctx.set_line_width(3); ctx.set_source_rgba(0.35, 0.22, 0.1, 0.25)
    for x in range(-200, W + 300, 150): ctx.move_to(x, 1640); ctx.line_to(x - 40, 1800); ctx.stroke()
    e4.ell(ctx, 700, 1700, 330, 46, hexc('#e76f51', 0.55))

# ---------- scenes ----------
def s0(ctx, t, d):
    e4.begin_set(ctx); hotel(ctx, t, "10:59")
    wren(ctx, CX, GY, S, t, "wave", flush=0.45, expr="happy"); layers(ctx, CX, GY, S, t, 1.0)
    big_suitcase(ctx, 740, 1700)
    kid(ctx, 895, GY, 0.95, t, "smile", (40, -300))
    e4.end_set(ctx)
    header(ctx, 1.0, None, "Suitcase won’t close.", "So I wore it.", 0.9, t, 64)
    wm(ctx); ai_tag(ctx, y=1860)

def s1(ctx, t, d):
    e4.begin_set(ctx); hotel(ctx, t, "10:52")
    u = max(0.0, min(1.0, (t - 1.0) / 1.0))
    yoff = -300 * 4 * u * (1 - u) if 1.0 <= t <= 2.0 else 0.0
    bounce = 10 * abs(math.sin(t * 7)) if t < 1.0 else 0.0
    wren(ctx, 620, 1640 + yoff - bounce, S, t, "cheer" if 1.0 <= t <= 2.0 else "wave", expr="shock" if t > 1.0 else "happy")
    lid = 0.0 if t < 1.0 else min(1.05, (t - 1.0) / 0.15 * 1.05)
    big_suitcase(ctx, 620, 1700, lid)
    burst(ctx, 1.0, t, 620, 1500, 7)
    e4.end_set(ctx)
    header(ctx, ease(t / 0.15), "ATTEMPT 1", "Sit on it.", "The suitcase won.", 1.3, t)
    pill(ctx, t, "Send this to someone who overpacks"); wm(ctx); ai_tag(ctx, y=1860)

def s2(ctx, t, d):
    e4.begin_set(ctx); hotel(ctx, t, "10:56")
    pop = t >= 1.3
    wren(ctx, 280, GY, S, t, "cheer" if not pop else "wave", expr="shock" if pop else "happy")
    lid = 0.0 if not pop else min(1.05, (t - 1.3) / 0.15 * 1.05)
    big_suitcase(ctx, 640, 1700, lid)
    if not pop:
        hop = 46 * abs(math.sin(t * 10))
        kid(ctx, 640, 1460 - hop, 0.9, t, "smile", (0, -300))
    else:
        u = max(0.0, min(1.0, (t - 1.3) / 1.2))
        kx = 640 + 260 * u; ky = 1460 + 205 * u - 520 * 4 * u * (1 - u)
        kid(ctx, kx, ky, 0.9, t, "smile", (0, -330))
    burst(ctx, 1.3, t, 640, 1480, 11)
    e4.end_set(ctx)
    header(ctx, ease(t / 0.15), "ATTEMPT 2", "Ask a 9-year-old.", "Leo went flying.", 1.6, t)
    pill(ctx, t, "Follow: Leo’s back tomorrow", 0.2); wm(ctx); ai_tag(ctx, y=1860)

def s3(ctx, t, d):
    e4.begin_set(ctx); hotel(ctx, t, "10:59")
    k = ease((t - 0.3) / 1.9)
    wren(ctx, CX, GY, S, t, "wave", flush=min(0.45, k * 0.5), expr="happy"); layers(ctx, CX, GY, S, t, k)
    big_suitcase(ctx, 740, 1700)
    if 2.3 < t < 3.1: e2.sparkle(ctx, 740, 1480, 36 + 14 * math.sin(t * 9), 0.95); e2.sparkle(ctx, 860, 1540, 24, 0.9)
    if t > 2.5: kid(ctx, 895, GY, 0.95, t, "smile", (40, -300))
    e4.end_set(ctx)
    header(ctx, ease(t / 0.15), "ATTEMPT 3", "Wear it.", "Zipped. I can’t bend.", 2.3, t)
    pill(ctx, t, "Send this to someone who overpacks", 0.1); wm(ctx); ai_tag(ctx, y=1860)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave", flush=0.45); layers(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, 1.0)
    a = ease(t / 0.3)
    ctext(ctx, "Airlines weigh the bag.", 205 - (1 - a) * 20, 62, hexc('#22223b', a), maxw=900)
    ctext(ctx, "Not the grandma.", 290, 62, hexc(RED, ease((t - 0.7) / 0.3)), maxw=900)
    a2 = ease((t - 1.3) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow: Leo’s back tomorrow", 560, 44, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False)
    ctext(ctx, "Send this to someone who overpacks", 625, 40, hexc('#5c2a1e', ease((t - 2.2) / 0.3)), bold=False)
    ai_tag(ctx, y=1890, dark=True)

SCENES = [(s0, 2.5), (s1, 3.0), (s2, 3.0), (s3, 3.5), (s4, 3.5)]

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
        picks = [(s0, 0.0), (s0, 1.8), (s1, 0.7), (s1, 1.5), (s2, 0.9), (s2, 1.9), (s3, 0.9), (s3, 1.8), (s3, 3.0), (s4, 2.8)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((270, 480)))
        c = Image.new("RGB", (280 * 5, 490 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 5) * 280, (i // 5) * 490))
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

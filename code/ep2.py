import cairo, math, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, caption, ai_tag, ease, wren

OUT = "/home/claude/wren/ep2"
os.makedirs(OUT, exist_ok=True)

def airport_bg(ctx, t):
    mv.vgrad(ctx, '#dbe7f0', '#b8cad8')
    # big window with plane taking off
    rrect(ctx, 80, 560, 920, 420, 30); ctx.set_source_rgba(*hexc('#9fd3f5')); ctx.fill()
    mv.cloud(ctx, 150 + t * 20, 680, 0.6)
    mv.plane(ctx, 300 + t * 120, 860 - t * 40, 0.55, -0.2, t)
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#7d8fa0'))
    rrect(ctx, 80, 560, 920, 420, 30); ctx.stroke()
    ctx.move_to(540, 560); ctx.line_to(540, 980); ctx.stroke()
    # sign
    rrect(ctx, 290, 1010, 500, 90, 16); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    mv.font(ctx, 40); s = "BAGGAGE CLAIM  ·  LIS"; e = ctx.text_extents(s)
    ctx.move_to((W - e.x_advance) / 2, 1070); ctx.set_source_rgba(*hexc('#22223b')); ctx.show_text(s)
    ctx.rectangle(0, 1420, W, H); ctx.set_source_rgba(*hexc('#8aa0b2')); ctx.fill()

def belt(ctx, t, y=1450, item=None):
    rrect(ctx, -40, y, W + 80, 130, 30); ctx.set_source_rgba(*hexc('#3d4451')); ctx.fill()
    ctx.set_source_rgba(*hexc('#565f6e'))
    off = (t * 140) % 120
    for x in range(-120, W + 120, 120):
        rrect(ctx, x + off, y + 18, 108, 70, 12); ctx.fill()
    rrect(ctx, -40, y + 100, W + 80, 30, 10); ctx.set_source_rgba(*hexc('#2b3038')); ctx.fill()

def sock(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-20, -70); ctx.line_to(20, -70); ctx.line_to(20, -10); ctx.line_to(60, 5)
    ctx.curve_to(80, 15, 70, 40, 50, 40); ctx.line_to(-20, 25); ctx.close_path()
    ctx.set_source_rgba(*hexc('#f4d35e')); ctx.fill()
    ctx.rectangle(-20, -60, 40, 12); ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    ctx.restore()

def poncho(ctx, cx, gy, s, t):
    """Airline blanket worn as a poncho, drawn in Wren's coordinate space."""
    ctx.save(); ctx.translate(cx, gy); ctx.scale(s, s)
    ctx.translate(0, math.sin(t * 2 * math.pi * 1.1) * 5)
    ctx.move_to(-70, -445); ctx.line_to(70, -445); ctx.line_to(165, -215)
    ctx.curve_to(60, -195, -60, -195, -165, -215); ctx.close_path()
    ctx.save(); ctx.clip_preserve()
    ctx.set_source_rgba(*hexc('#3a5a9b')); ctx.fill()
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#e63946', 0.8))
    for x in range(-180, 200, 70):
        ctx.move_to(x, -460); ctx.line_to(x, -180); ctx.stroke()
    ctx.set_source_rgba(*hexc('#f4d35e', 0.6))
    for y in range(-420, -180, 70):
        ctx.move_to(-200, y); ctx.line_to(200, y); ctx.stroke()
    ctx.restore()
    # fringe
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#3a5a9b'))
    for i in range(-150, 160, 22):
        yb = -212 + 18 * (abs(i) / 165) ** 2 * -1
        ctx.move_to(i, yb); ctx.line_to(i + 4 * math.sin(t * 4 + i), yb + 26); ctx.stroke()
    ctx.restore()

def sparkle(ctx, x, y, r, a):
    ctx.save(); ctx.translate(x, y)
    ctx.move_to(0, -r); ctx.line_to(r * .25, -r * .25); ctx.line_to(r, 0); ctx.line_to(r * .25, r * .25)
    ctx.line_to(0, r); ctx.line_to(-r * .25, r * .25); ctx.line_to(-r, 0); ctx.line_to(-r * .25, -r * .25); ctx.close_path()
    ctx.set_source_rgba(1, 0.9, 0.4, a); ctx.fill(); ctx.restore()

# ---------- scenes ----------
def s_hook(ctx, t, d):
    airport_bg(ctx, t); belt(ctx, t)
    wren(ctx, 165, 1440, 0.75, t, "wave")
    # question marks
    for i, (qx, qy) in enumerate(((100, 840), (300, 790))):
        a = ease((t - 0.4 - i * 0.3) / 0.3)
        mv.font(ctx, 90); ctx.move_to(qx, qy - 10 * math.sin(t * 4 + i)); ctx.set_source_rgba(*hexc('#e63946', a)); ctx.show_text("?")
    a = ease((t - 0.1) / 0.4)
    ctext(ctx, "My suitcase went to Rome.", 230 - (1 - a) * 30, 84, hexc('#22223b', a), maxw=940, lh=1.15)
    a2 = ease((t - 1.2) / 0.4)
    ctext(ctx, "I went to Lisbon.", 450, 84, hexc('#e63946', a2))
    ai_tag(ctx)

def s_problem(ctx, t, d):
    airport_bg(ctx, t); belt(ctx, t)
    x = -100 + (t / d) * (W + 200)
    sock(ctx, x, 1490, 0.9)
    wren(ctx, 820, 1440, 0.62, t, "wave", blink_seed=1.3)
    a = ease((t - 0.2) / 0.4)
    ctext(ctx, "One sock came out.", 240, 72, hexc('#22223b', a))
    ctext(ctx, "Not even mine.", 340, 60, hexc('#5c6b7a', ease((t - 1.0) / 0.4)), bold=False)
    caption(ctx, t, "THE PROBLEM", "No clothes. No toothbrush. No plan... yet.", y=1580, delay=1.6)
    ai_tag(ctx, y=1890)

def s_fix(ctx, t, d):
    mv.vgrad(ctx, '#ffd6a5', '#ffadad')
    for i in range(12):
        ang = i / 12 * 2 * math.pi + t * 0.3
        ctx.move_to(540, 1000); ctx.arc(540, 1000, 1600, ang, ang + 0.13); ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.18); ctx.fill()
    ctx.rectangle(0, 1420, W, H); ctx.set_source_rgba(*hexc('#f4a261')); ctx.fill()
    pop = ease(t / 0.5)
    s = 1.0 * (0.9 + 0.1 * pop)
    wren(ctx, 540, 1430, s, t, "wave")
    poncho(ctx, 540, 1430, s, t)
    for i, (sx, sy) in enumerate(((240, 760), (840, 820), (300, 1180), (860, 1160))):
        sparkle(ctx, sx, sy, 30 + 10 * math.sin(t * 5 + i), 0.9)
    a = ease((t - 0.2) / 0.4)
    ctext(ctx, "THE FIX", 220, 56, hexc('#e63946', a))
    ctext(ctx, "Airline blanket = designer poncho.", 320, 74, hexc('#22223b', a), maxw=900, lh=1.15)
    caption(ctx, t, "WREN'S REVIEW", "Warm. Chic. Smells faintly of seat 34B.", y=1560, delay=1.6)
    ai_tag(ctx)

def item_shirt(ctx):
    ctx.move_to(-50, -45); ctx.line_to(-20, -55); ctx.curve_to(-10, -40, 10, -40, 20, -55); ctx.line_to(50, -45)
    ctx.line_to(65, -15); ctx.line_to(40, -5); ctx.line_to(40, 55); ctx.line_to(-40, 55); ctx.line_to(-40, -5)
    ctx.line_to(-65, -15); ctx.close_path(); ctx.set_source_rgba(*hexc('#2a9d8f')); ctx.fill()

def item_brush(ctx):
    ctx.save(); ctx.rotate(-0.6)
    rrect(ctx, -70, -10, 120, 20, 10); ctx.set_source_rgba(*hexc('#4cc9f0')); ctx.fill()
    rrect(ctx, 40, -24, 38, 22, 5); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill(); ctx.restore()

def item_charger(ctx):
    rrect(ctx, -35, -50, 70, 60, 12); ctx.set_source_rgba(*hexc('#3d4451')); ctx.fill()
    ctx.set_line_width(8); ctx.set_source_rgba(*hexc('#3d4451'))
    ctx.move_to(0, 10); ctx.curve_to(0, 60, 60, 40, 40, 70); ctx.stroke()
    ctx.set_line_width(6); ctx.set_source_rgba(0.3, 0.3, 0.3, 1)
    ctx.move_to(-12, -50); ctx.line_to(-12, -68); ctx.move_to(12, -50); ctx.line_to(12, -68); ctx.stroke()

def item_cookie(ctx):
    circle(ctx, 0, 0, 50, hexc('#d4a373'))
    for cx, cy in ((-18, -15), (15, -20), (0, 12), (22, 18), (-20, 22)):
        circle(ctx, cx, cy, 8, hexc('#5c3d1e'))

def s_rule(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffe0b3')
    a = ease((t - 0.1) / 0.4)
    ctext(ctx, "WREN'S RULE", 220, 56, hexc('#e63946', a))
    ctext(ctx, "Pack one day in your handbag. Always.", 320, 72, hexc('#22223b', a), maxw=900, lh=1.15)
    # handbag
    bx, by = 540, 1330
    ctx.new_path(); ctx.set_line_width(22); ctx.set_source_rgba(*hexc('#7b2d4f'))
    ctx.arc(bx, by - 170, 120, math.pi, 2 * math.pi); ctx.stroke()
    rrect(ctx, bx - 230, by - 170, 460, 330, 50); ctx.set_source_rgba(*hexc('#c9406a')); ctx.fill()
    rrect(ctx, bx - 30, by - 120, 60, 40, 8); ctx.set_source_rgba(*hexc('#f4d35e')); ctx.fill()
    items = [(item_shirt, "Spare top", -330, -520), (item_brush, "Toothbrush", -110, -620),
             (item_charger, "Charger", 110, -620), (item_cookie, "Snacks (essential)", 330, -520)]
    for i, (fn, label, dx, dy) in enumerate(items):
        p = ease((t - 0.8 - i * 0.55) / 0.45)
        if p <= 0: continue
        x = bx + dx * p; y = by - 150 + (dy + 150) * p - math.sin(p * math.pi) * 60
        circle(ctx, x, y, 95, (1, 1, 1, 0.85))
        ctx.save(); ctx.translate(x, y); ctx.scale(1.1, 1.1); fn(ctx); ctx.restore()
        if p > 0.9:
            mv.font(ctx, 32); e = ctx.text_extents(label)
            ctx.move_to(x - e.x_advance / 2, y + 140); ctx.set_source_rgba(*hexc('#22223b')); ctx.show_text(label)
    wren(ctx, 170, 1720, 0.38, t, "wave")
    ai_tag(ctx)

def s_twist(ctx, t, d):
    airport_bg(ctx, t); belt(ctx, t)
    p = ease(t / 1.8)
    sx = -200 + p * 740
    mv.suitcase(ctx, sx, 1480, 0.75, t)
    # sunglasses + ROMA sticker on the suitcase
    ctx.save(); ctx.translate(sx, 1480); ctx.scale(0.75, 0.75)
    for gx in (-45, 45):
        ctx.save(); ctx.translate(gx, -190); ctx.scale(1.2, 0.8); circle(ctx, 0, 0, 34, hexc('#111111')); ctx.restore()
    ctx.set_line_width(8); ctx.set_source_rgba(0.07, 0.07, 0.07, 1); ctx.move_to(-10, -195); ctx.line_to(10, -195); ctx.stroke()
    ctx.save(); ctx.translate(30, -70); ctx.rotate(-0.2)
    rrect(ctx, -70, -30, 140, 60, 12); ctx.set_source_rgba(*hexc('#009246')); ctx.fill()
    mv.font(ctx, 36); e = ctx.text_extents("ROMA"); ctx.move_to(-e.x_advance / 2, 13); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text("ROMA")
    ctx.restore(); ctx.restore()
    wren(ctx, 860, 1440, 0.62, t, "cheer" if t > 1.6 else "wave")
    a = ease((t - 0.2) / 0.4)
    ctext(ctx, "Day 3: it came back.", 240, 76, hexc('#22223b', a))
    ctext(ctx, "With a tan.", 350, 76, hexc('#e63946', ease((t - 1.6) / 0.4)))
    ai_tag(ctx)

def s_outro(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    ctx.set_line_width(8); ctx.set_dash([24, 18]); ctx.set_source_rgba(*hexc('#e63946', 0.5))
    ctx.move_to(100, 1650); ctx.curve_to(300, 1100, 800, 1500, 980, 900); ctx.stroke(); ctx.set_dash([])
    pop = ease(t / 0.5)
    s = 1.1 * (0.9 + 0.1 * pop)
    wren(ctx, 540, 1660, s, t, "wave"); poncho(ctx, 540, 1660, s, t)
    a = ease((t - 0.2) / 0.4)
    ctext(ctx, "Send this to someone who always loses their luggage", 210 - (1 - a) * 30, 64, hexc('#22223b', a), maxw=900, lh=1.2)
    a2 = ease((t - 1.0) / 0.4)
    mv.font(ctx, 54); s2 = "@wrentrips"; e = ctx.text_extents(s2)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 500, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc('#e63946', a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 568); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s2)
    ctext(ctx, "Follow for the next disaster", 690, 44, hexc('#5c2a1e', ease((t - 1.6) / 0.4)), bold=False)
    ai_tag(ctx, dark=True)

SCENES = [(s_hook, 3.5), (s_problem, 4.5), (s_fix, 5.0), (s_rule, 5.0), (s_twist, 4.0), (s_outro, 4.5)]

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
            p = f"{OUT}/prev_{i}.png"; frame(fn, d * 0.8, d).write_to_png(p)
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

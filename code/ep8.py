import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ai_tag, ease, wren
import ep4 as e4
from ep5 import kid
from ep6 import phone_prop
from ep7 import wm

OUT = "/home/claude/wren/ep8"
os.makedirs(OUT, exist_ok=True)
DARK, RED = hexc('#22223b'), '#e63946'
LEO = (270, 900, 1.5)
WRN = (790, 1790, 0.85)

def sparkle4(ctx, x, y, r, col):
    ctx.save(); ctx.translate(x, y)
    ctx.move_to(0, -r); ctx.line_to(r * .25, -r * .25); ctx.line_to(r, 0); ctx.line_to(r * .25, r * .25)
    ctx.line_to(0, r); ctx.line_to(-r * .25, r * .25); ctx.line_to(-r, 0); ctx.line_to(-r * .25, -r * .25); ctx.close_path()
    ctx.set_source_rgba(*col); ctx.fill(); ctx.restore()

def bg(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, 960); g.add_color_stop_rgb(0, *hexc('#3a0ca3')[:3]); g.add_color_stop_rgb(1, *hexc('#b5179e')[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 960); ctx.fill()
    rng = random.Random(2)
    for i in range(18):
        x = (rng.uniform(0, W) + t * rng.uniform(-18, 18)) % W; y = rng.uniform(260, 930); r = rng.uniform(10, 26)
        sparkle4(ctx, x, y, r * (0.8 + 0.3 * math.sin(t * 3 + i)), hexc(rng.choice(['#4cc9f0', '#ffd60a', '#f72585', '#ffffff']), 0.65))
    g2 = cairo.LinearGradient(0, 960, 0, H); g2.add_color_stop_rgb(0, *hexc('#ffe8cc')[:3]); g2.add_color_stop_rgb(1, *hexc('#ffd6a5')[:3])
    ctx.set_source(g2); ctx.rectangle(0, 960, W, H - 960); ctx.fill()
    for ix, gx in enumerate(range(60, W + 100, 170)):
        for iy, gy in enumerate(range(1080, 1900, 170)):
            ox = 85 if iy % 2 else 0
            for k in range(5):
                a = k * 2 * math.pi / 5; circle(ctx, gx + ox + 15 * math.cos(a), gy + 15 * math.sin(a), 10, hexc('#f4a261', 0.35))
            circle(ctx, gx + ox, gy, 7, hexc('#e76f51', 0.4))
    ctx.rectangle(0, 948, W, 24); ctx.set_source_rgba(*hexc('#ffd60a')); ctx.fill()

def hats(ctx, cx, gy, s, t, n):
    ctx.save(); ctx.translate(cx, gy); ctx.scale(s, s); ctx.translate(0, math.sin(t * 2 * math.pi * 1.1) * 5)
    for i, (col, cyy, r) in enumerate((('#4cc9f0', -625, 78), ('#e63946', -690, 56), ('#ffd166', -738, 42))):
        if n > i:
            ctx.arc(0, cyy, r, math.pi, 2 * math.pi); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
            rrect(ctx, -r - 6, cyy - 6, 2 * r + 12, 20, 9); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill()
    if n > 2: circle(ctx, 0, -784, 16, hexc('#f8f9fa'))
    ctx.restore()

def bubble2(ctx, cx, cy, text, size, a, tail_to):
    if a <= 0: return
    mv.font(ctx, size); e = ctx.text_extents(text); w = e.x_advance + 70; h = size * 1.15 + 40
    ctx.save(); ctx.translate(0, (1 - a) * 22)
    left, right, top, bot = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    rrect(ctx, left, top, w, h, h / 2); ctx.set_source_rgba(1, 1, 1, 0.97 * a); ctx.fill()
    tx, ty = tail_to
    if tx < left: ctx.move_to(left + 6, cy - 14); ctx.line_to(tx, ty); ctx.line_to(left + 6, cy + 14)
    elif tx > right: ctx.move_to(right - 6, cy - 14); ctx.line_to(tx, ty); ctx.line_to(right - 6, cy + 14)
    else:
        bx = max(left + 50, min(right - 50, tx)); by = bot - 4 if ty > cy else top + 4
        ctx.move_to(bx - 20, by); ctx.line_to(tx, ty); ctx.line_to(bx + 20, by)
    ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.97 * a); ctx.fill()
    ctx.move_to(cx - e.x_advance / 2, cy + size * 0.35); ctx.set_source_rgba(*hexc('#22223b', a)); ctx.show_text(text)
    ctx.restore()

def banner(ctx):
    rrect(ctx, 60, 100, 960, 134, 32); ctx.set_source_rgba(1, 1, 1, 0.94); ctx.fill()
    mv.font(ctx, 54); s_ = "GEN Z vs. GRANDMA"; e = ctx.text_extents(s_); ctx.move_to(540 - e.x_advance / 2, 170); ctx.set_source_rgba(*DARK); ctx.show_text(s_)
    mv.font(ctx, 32); s_ = "travel edition"; e = ctx.text_extents(s_); ctx.move_to(540 - e.x_advance / 2, 214); ctx.set_source_rgba(*hexc(RED)); ctx.show_text(s_)

def scoreboard(ctx, t, before, after, award_t):
    z, g = (after if t >= award_t else before)
    pop = 1 + 0.25 * max(0.0, 1 - (t - award_t) / 0.35) if t >= award_t else 1.0
    ctx.save(); ctx.translate(540, 285); ctx.scale(pop, pop)
    rrect(ctx, -250, -34, 500, 68, 34); ctx.set_source_rgba(*hexc('#1d2433')); ctx.fill()
    mv.font(ctx, 30); s_ = "GEN Z  %d — %d  GRANDMA" % (z, g); e = ctx.text_extents(s_)
    ctx.move_to(-e.x_advance / 2, 11); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text(s_); ctx.restore()

def question(ctx, text, a):
    if a <= 0: return
    mv.font(ctx, 36); e = ctx.text_extents(text); w = e.x_advance + 80
    rrect(ctx, 540 - w / 2, 925, w, 70, 35); ctx.set_source_rgba(*hexc('#1d2433', a)); ctx.fill()
    ctx.move_to(540 - e.x_advance / 2, 971); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(text)

def characters(ctx, t, leo_expr="smile", wren_expr="happy", hat_n=0, wren_mode="wave", flush=0.0):
    kid(ctx, LEO[0], LEO[1], LEO[2], t, leo_expr, (0, -190))
    ctx.save(); ctx.translate(LEO[0] + 6, LEO[1] - 190 * LEO[2] - 8); ctx.scale(1.6, 1.6); phone_prop(ctx, 0, 0, -0.1); ctx.restore()
    wren(ctx, WRN[0], WRN[1], WRN[2], t, wren_mode, expr=wren_expr, flush=flush)
    if hat_n: hats(ctx, WRN[0], WRN[1], WRN[2], t, hat_n)

def round_scene(ctx, t, d, q, leo_txt, wren_txt, before, after, award_t, leo_expr="smile", wren_expr="happy", hats_at=None):
    bg(ctx, t)
    hat_n = 3 if (hats_at is not None and t > hats_at) else 0
    le = leo_expr if t < 2.0 else ("smug" if after[0] > before[0] else ("flat" if hats_at is not None else leo_expr))
    characters(ctx, t, le, "shock" if (hats_at is not None and t > hats_at) else wren_expr, hat_n)
    question(ctx, q, ease(t / 0.2))
    bubble2(ctx, 690, 560, leo_txt, 50, ease((t - 0.35) / 0.25), (360, 470))
    bubble2(ctx, 380, 1340, wren_txt, 50, ease((t - 1.3) / 0.25), (715, 1330))
    banner(ctx); scoreboard(ctx, t, before, after, award_t); wm(ctx); ai_tag(ctx, y=1860)

def s0(ctx, t, d):
    bg(ctx, t); characters(ctx, t, "smug", "happy")
    k = ease(t / 0.35); r = 92 * (0.7 + 0.3 * k)
    circle(ctx, 540, 960, r, hexc(RED)); mv.font(ctx, 76); e = ctx.text_extents("VS"); ctx.move_to(540 - e.x_advance / 2, 960 + 26); ctx.set_source_rgba(1, 1, 1, 1); ctx.show_text("VS")
    bubble2(ctx, 700, 560, "Phones > everything", 50, ease((t - 0.7) / 0.25), (360, 470))
    bubble2(ctx, 380, 1340, "Not in my day, dear", 50, ease((t - 1.3) / 0.25), (715, 1330))
    banner(ctx); scoreboard(ctx, t, (0, 0), (0, 0), 99); wm(ctx); ai_tag(ctx, y=1860)

def s1(ctx, t, d): round_scene(ctx, t, d, "ROUND 1 — Getting around", "Phone maps. Easy.", "Ask a policeman.", (0, 0), (1, 0), 2.2)
def s2(ctx, t, d): round_scene(ctx, t, d, "ROUND 2 — Picking food", "Five-star reviews.", "Where the locals queue.", (1, 0), (1, 1), 2.3)
def s3(ctx, t, d): round_scene(ctx, t, d, "ROUND 3 — Packing", "One carry-on. No cap.", "I brought three hats.", (1, 1), (1, 1), 99, hats_at=1.5)

def s4(ctx, t, d):
    bg(ctx, t); characters(ctx, t, "smug" if t > 1.0 else "smile", "happy")
    a = ease(t / 0.25)
    rrect(ctx, 80, 640, 920, 560, 44); ctx.set_source_rgba(1, 1, 1, a); ctx.fill()
    ctext(ctx, "Final score: 1 — 1", 740, 62, hexc('#22223b', a), maxw=860)
    ctext(ctx, "Team Leo or Team Wren?", 835, 56, hexc(RED, ease((t - 0.4) / 0.3)), maxw=860)
    ctext(ctx, "Vote in the comments", 905, 40, hexc('#5c2a1e', ease((t - 0.8) / 0.3)), bold=False, maxw=860)
    a2 = ease((t - 1.2) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 960, e.x_advance + 80, 96, 48); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 1026); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 1130, 36, hexc('#5c2a1e', ease((t - 1.6) / 0.3)), bold=False, maxw=860)
    banner(ctx); ai_tag(ctx, y=1860)

SCENES = [(s0, 2.4), (s1, 3.0), (s2, 3.0), (s3, 3.4), (s4, 3.4)]

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
        picks = [(s0, 1.8), (s1, 0.8), (s1, 2.6), (s2, 2.7), (s3, 0.9), (s3, 2.8), (s4, 2.6)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((300, 533)))
        c = Image.new("RGB", (310 * 4, 543 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 4) * 310, (i // 4) * 543))
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

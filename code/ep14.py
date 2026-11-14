import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = "/home/claude/wren/ep14"
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
WX, LX, GY = 260, 800, 1700

# ------------------------------------------------------------ living room
def room(ctx, t):
    ctx.rectangle(0, 0, W, 1560); ctx.set_source_rgba(*hexc('#cfe8d5')); ctx.fill()
    for yy in range(40, 1560, 110):
        for xx in range(0, W + 60, 110):
            ox = 55 if (yy // 110) % 2 else 0
            circle(ctx, xx + ox, yy, 11, hexc('#a9d3b6', 0.85)); circle(ctx, xx + ox, yy, 5, hexc('#f7c6d0', 0.9))
    ctx.rectangle(0, 1380, W, 180); ctx.set_source_rgba(*hexc('#b9dcc4')); ctx.fill()                       # dado
    ctx.rectangle(0, 1372, W, 12); ctx.set_source_rgba(*hexc('#8c5a34')); ctx.fill()
    # shelf with plant and teapot
    ctx.rectangle(80, 1180, 330, 16); ctx.set_source_rgba(*hexc('#8c5a34')); ctx.fill()
    rrect(ctx, 100, 1112, 62, 70, 10); ctx.set_source_rgba(*hexc('#e76f51')); ctx.fill()
    for k in range(5):
        a = -1.2 + k * 0.6; ctx.move_to(131, 1116); ctx.curve_to(131 + 30 * math.sin(a), 1060, 131 + 50 * math.sin(a), 1040, 131 + 46 * math.sin(a), 1030 + 10 * k % 20)
        ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#2f8f4e')); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    e4.ell(ctx, 300, 1146, 46, 34, hexc('#8ecae6')); rrect(ctx, 286, 1104, 28, 14, 7); ctx.set_source_rgba(*hexc('#8ecae6')); ctx.fill()
    ctx.set_line_width(8); ctx.set_source_rgba(*hexc('#8ecae6')); ctx.move_to(340, 1140); ctx.line_to(366, 1120); ctx.stroke()
    # floor lamp glow
    gl = cairo.RadialGradient(960, 1100, 10, 960, 1100, 340); gl.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.45); gl.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
    ctx.set_source(gl); ctx.rectangle(560, 760, 520, 700); ctx.fill()
    ctx.rectangle(954, 1050, 12, 520); ctx.set_source_rgba(*hexc('#6b4423')); ctx.fill()
    ctx.move_to(912, 1060); ctx.line_to(1008, 1060); ctx.line_to(984, 985); ctx.line_to(936, 985); ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    # floor + desk
    ctx.rectangle(0, 1560, W, H - 1560); ctx.set_source_rgba(*hexc('#c98a52')); ctx.fill()

def desk(ctx, t):
    rrect(ctx, -20, 1560, W + 40, 40, 10); ctx.set_source_rgba(*hexc('#8c5a34')); ctx.fill()
    ctx.rectangle(-20, 1600, W + 40, H - 1600); ctx.set_source_rgba(*hexc('#6f4526')); ctx.fill()
    rrect(ctx, 60, 1608, 400, 200, 12); ctx.set_source_rgba(*hexc('#5c391e')); ctx.fill()
    # tea cup on desk (Wren side)
    rrect(ctx, 400, 1500, 70, 62, 14); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill()
    ctx.set_line_width(7); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.arc(474, 1530, 16, -math.pi / 2, math.pi / 2); ctx.stroke()
    for k in range(2):
        ph = (t * 0.7 + k * 0.5) % 1; ctx.move_to(420 + k * 24, 1490); ctx.curve_to(410 + k * 24, 1470 - ph * 10, 434 + k * 24, 1450, 424 + k * 24, 1430)
        ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.6 * (1 - ph)); ctx.stroke()

# ------------------------------------------------------------ chat window
UX0, UX1, AY0, AY1 = 110, 990, 668, 1000
def bubble(ctx, who, text, y, a, t0, t):
    mv.font(ctx, 36, True); e = ctx.text_extents(text); w = e.x_advance + 56; h = 66
    x = UX1 - w if who == "u" else UX0
    ctx.save(); ctx.translate((1 - a) * (40 if who == "u" else -40), 0)
    rrect(ctx, x, y, w, h, 30); ctx.set_source_rgba(*hexc('#4361ee' if who == "u" else '#e9ecf2', a)); ctx.fill()
    ctx.move_to(x + 28, y + 45); ctx.set_source_rgba(*hexc('#ffffff' if who == "u" else '#22223b', a)); ctx.show_text(text); ctx.restore()
    return h

def dots(ctx, y, t):
    rrect(ctx, UX0, y, 130, 66, 30); ctx.set_source_rgba(*hexc('#e9ecf2')); ctx.fill()
    for k in range(3): circle(ctx, UX0 + 35 + k * 30, y + 33 - 8 * max(0, math.sin(t * 9 - k * 0.8)), 8, hexc('#8d96a5'))

def eiffel_hat(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#6b4a2b'))
    ctx.move_to(-50, 80); ctx.line_to(-8, -60); ctx.line_to(8, -60); ctx.line_to(50, 80); ctx.close_path(); ctx.set_source_rgba(*hexc('#7a5230')); ctx.fill()
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#3a2614'))
    for yy, hw in ((20, 26), (-20, 16), (55, 36)): ctx.move_to(-hw, yy); ctx.line_to(hw, yy); ctx.stroke()
    ctx.move_to(-26, 20); ctx.line_to(16, -20); ctx.move_to(26, 20); ctx.line_to(-16, -20); ctx.stroke()
    e4.ell(ctx, 0, -66, 46, 10, hexc('#c1121f'))                                        # brim
    ctx.move_to(-22, -68); ctx.curve_to(-24, -104, 24, -104, 22, -68); ctx.close_path(); ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    ctx.restore()

def chat(ctx, t, msgs, typing=None, card=None):
    rrect(ctx, 60, 590, 960, 430, 38); ctx.set_source_rgba(*hexc('#1d2233')); ctx.fill()
    rrect(ctx, 84, 628, 912, 368, 22); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.save(); rrect(ctx, 84, 628, 912, 368, 22); ctx.clip()
    ctx.rectangle(84, 628, 912, 38); ctx.set_source_rgba(*hexc('#f1f3f8')); ctx.fill()
    for k, c in enumerate(('#ff5f57', '#febc2e', '#28c840')): circle(ctx, 112 + k * 28, 647, 8, hexc(c))
    mv.font(ctx, 22, False); ctx.move_to(420, 654); ctx.set_source_rgba(*hexc('#6c7380')); ctx.show_text("AI Assistant")
    y = AY0 + 4
    for who, text, t0 in msgs:
        a = ramp(t, t0, t0 + 0.2)
        if a > 0: bubble(ctx, who, text, y, a, t0, t)
        y += 76
    if typing and typing[0] <= t < typing[1]: dots(ctx, y, t)
    if card and t >= card:
        a = ramp(t, card, card + 0.25)
        rrect(ctx, UX0, y, 560, 150, 26); ctx.set_source_rgba(*hexc('#e9f5ee', a)); ctx.fill()
        ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#2a9d8f', a)); rrect(ctx, UX0, y, 560, 150, 26); ctx.stroke()
        mv.font(ctx, 26, False); ctx.move_to(UX0 + 24, y + 38); ctx.set_source_rgba(*hexc('#2a9d8f', a)); ctx.show_text("Trip booked")
        mv.font(ctx, 52); ctx.move_to(UX0 + 24, y + 104); ctx.set_source_rgba(*hexc('#22223b', a)); ctx.show_text("Paris, Texas")
        ctx.save()
        eiffel_hat(ctx, UX0 + 660 + 0, y + 70, 0.9 * (0.5 + 0.5 * a)); ctx.restore()
    ctx.restore()
    circle(ctx, 540, 604, 6, hexc('#3b4560'))

def patience(ctx, pct, a=1.0, t=0.0):
    sh = math.sin(t * 40) * 3 if pct < 25 else 0
    ctx.save(); ctx.translate(sh, 0)
    rrect(ctx, 90, 524, 900, 56, 28); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 24); ctx.move_to(122, 561); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text("AI PATIENCE")
    bx, bw = 380, 440
    rrect(ctx, bx, 540, bw, 24, 12); ctx.set_source_rgba(1, 1, 1, 0.16 * a); ctx.fill()
    col = '#4ade80' if pct > 60 else ('#ffd60a' if pct > 30 else '#ff4d5a')
    rrect(ctx, bx, 540, max(24, bw * pct / 100.0), 24, 12); ctx.set_source_rgba(*hexc(col, a)); ctx.fill()
    mv.font(ctx, 30); s_ = "%d%%" % pct; e = ctx.text_extents(s_); ctx.move_to(960 - e.x_advance, 563); ctx.set_source_rgba(*hexc(col, a)); ctx.show_text(s_)
    ctx.restore()

def pair(ctx, t, wmode="point", wexpr="happy", lexpr="flat", wflush=0.0, lhand=(0, -150), wh=(110, -110)):
    wren(ctx, WX, GY, 0.78, t, wmode, flush=wflush, expr=wexpr, hand=wh)
    kid(ctx, LX, GY, 0.95, t, lexpr, lhand)

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    room(ctx, t); pair(ctx, t, lexpr="flat"); desk(ctx, t)
    chat(ctx, t, [("u", "Hello dear! Are you there?", 0.15), ("a", "Yes! How can I help?", 0.8), ("u", "Paris please. No planes. No walking.", 1.4), ("u", "No French. Thank you x", 2.0)],
         typing=(0.4, 0.8))
    header(ctx, ease(t / 0.2 + 1), "WREN USES AI", "Plan my trip to Paris", "No planes. No walking.", -0.3, t, main_size=56)
    patience(ctx, int(lerp(98, 90, ramp(t, 0.8, 2.0))), 1.0, t); wm(ctx)

def s1(ctx, t, d):
    room(ctx, t); pair(ctx, t, wexpr="shock" if t > 2.4 else "happy", lexpr="flat"); desk(ctx, t)
    chat(ctx, t, [("a", "That's quite a challenge.", 0.9), ("a", "Have you considered staying home?", 1.7), ("u", "NO. Please.", 2.4)], typing=(0.3, 0.9) if t < 1.0 else (1.2, 1.7))
    header(ctx, ease(t / 0.2), "THE AI RESPONDS", "It is not impressed.", "Wren says please anyway.", 1.2, t)
    p = 90 - 20 * ramp(t, 0.9, 1.2) - 20 * ramp(t, 1.7, 2.0) - 8 * ramp(t, 2.4, 2.6)
    patience(ctx, int(p), 1.0, t); wm(ctx)

def s2(ctx, t, d):
    room(ctx, t); pair(ctx, t, wmode="cheer" if t > 2.0 else "point", wexpr="happy", lexpr="flat"); desk(ctx, t)
    chat(ctx, t, [("a", "Booking Paris now... done!", 0.6)], typing=(0.2, 0.6) if t < 0.9 else (0.9, 1.4), card=1.4)
    bubble_ml(ctx, 760, 1230, ["Which Paris?"], 40, ramp(t, 0.8, 1.0) * (1 - ramp(t, 2.0, 2.2)), (LX, 1340))
    bubble_ml(ctx, 330, 1120, ["Wonderful!"], 44, ramp(t, 2.1, 2.3), (WX, 1230))
    header(ctx, ease(t / 0.2), "TRIP BOOKED", "Leo asks the real question", "Which Paris?", 1.4, t, main_size=52)
    p = 50 - 25 * ramp(t, 1.4, 1.7)
    patience(ctx, int(p), 1.0, t); wm(ctx)

def s3(ctx, t, d):
    room(ctx, t)
    pair(ctx, t, wmode="cheer" if 1.3 < t < 2.9 else "point", wexpr="happy", lexpr="flat" if t < 2.2 else "shock", wflush=0.2)
    desk(ctx, t)
    chat(ctx, t, [("u", "Is there an Eiffel Tower?", 0.2), ("a", "Yes. It wears a cowboy hat.", 1.0)], typing=(0.6, 1.0))
    bubble_ml(ctx, 330, 1120, ["Even better!"], 44, ramp(t, 1.3, 1.5) * (1 - ramp(t, 2.1, 2.3)), (WX, 1230))
    bubble_ml(ctx, 700, 1190, ["Grandma... we're", "AI too."], 40, ramp(t, 2.2, 2.4) * (1 - ramp(t, 3.1, 3.3)), (LX, 1330))
    bubble_ml(ctx, 330, 1100, ["Shh. Don't tell", "the algorithm."], 40, ramp(t, 3.2, 3.4), (WX, 1230))
    header(ctx, ease(t / 0.2), "THE RESULT", "Paris has an Eiffel Tower.", "In a cowboy hat.", 0.8, t, main_size=54)
    p = 25 - 20 * ramp(t, 1.0, 1.3)
    patience(ctx, int(p), 1.0, t); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “AI is wonderful.”", 205 - (1 - a) * 20, 60, hexc('#22223b', a), maxw=940)
    ctext(ctx, "AI: “Please send help.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Send this to someone who says please to AI", 625, 36, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

SLOW = 1.4
SCENES = [(s0, 2.8 * SLOW), (s1, 3.0 * SLOW), (s2, 3.2 * SLOW), (s3, 4.0 * SLOW), (s4, 3.2)]
def _w(fn, k):
    def g(ctx, t, d): fn(ctx, t / k, d / k)
    g.__name__ = fn.__name__
    return g
_o = {s0: s0, s1: s1, s2: s2, s3: s3}
_s0, _s1, _s2, _s3 = s0, s1, s2, s3
s0, s1, s2, s3 = _w(_s0, SLOW), _w(_s1, SLOW), _w(_s2, SLOW), _w(_s3, SLOW)
SCENES = [(s0, 2.8 * SLOW), (s1, 3.0 * SLOW), (s2, 3.2 * SLOW), (s3, 4.0 * SLOW), (s4, 3.2)]

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
        picks = [(s0, 0.5), (s0, 2.5), (s1, 1.2), (s1, 2.8), (s2, 1.1), (s2, 2.6), (s3, 1.8), (s3, 2.8), (s3, 3.7), (s4, 2.0)]
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

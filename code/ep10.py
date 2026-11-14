import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ai_tag, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, pill, header
from ep9 import bubble_ml

OUT = "/home/claude/wren/ep10"
os.makedirs(OUT, exist_ok=True)
RED, GREEN, DARK = '#e63946', '#1f9d6b', hexc('#22223b')
WX, LX, GY = 290, 800, 1700
WS, LS = 0.8, 1.1
CY = 525

def ltext(ctx, text, x, y, size, col, bold=True):
    mv.font(ctx, size, bold); ctx.move_to(x, y); ctx.set_source_rgba(*col); ctx.show_text(text)

# ------------------------------------------------------------ shop
def shelf_item(ctx, x, y, kind, col):
    if kind == 0:      # snow globe
        circle(ctx, x, y - 52, 32, hexc('#d9f0ff')); circle(ctx, x - 10, y - 62, 7, (1, 1, 1, 0.8))
        rrect(ctx, x - 30, y - 26, 60, 26, 8); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    elif kind == 1:    # jar
        rrect(ctx, x - 24, y - 70, 48, 70, 10); ctx.set_source_rgba(*hexc(col)); ctx.fill()
        rrect(ctx, x - 28, y - 82, 56, 16, 6); ctx.set_source_rgba(*hexc('#6b4423')); ctx.fill()
    elif kind == 2:    # teapot
        e4.ell(ctx, x, y - 32, 38, 30, hexc(col)); rrect(ctx, x - 14, y - 74, 28, 14, 7); ctx.set_source_rgba(*hexc(col)); ctx.fill()
        ctx.set_line_width(7); ctx.set_source_rgba(*hexc(col)); ctx.move_to(x + 34, y - 44); ctx.line_to(x + 58, y - 62); ctx.stroke()
        ctx.arc(x - 44, y - 36, 15, math.pi * 0.5, math.pi * 1.5); ctx.stroke()
    else:              # postcard stack
        for k in range(3):
            ctx.save(); ctx.translate(x, y - 12 - k * 12); ctx.rotate((k - 1) * 0.12)
            rrect(ctx, -34, -22, 68, 44, 4); ctx.set_source_rgba(*hexc(['#ffadad', '#ffd6a5', '#caffbf'][k])); ctx.fill(); ctx.restore()

def shop(ctx, t):
    mv.vgrad(ctx, '#ffe8c7', '#ffd09b')
    for k, x in enumerate(range(-20, W + 80, 90)):             # bunting
        ctx.move_to(x, 8 + 18 * math.sin(x * 0.02)); ctx.line_to(x + 80, 8 + 18 * math.sin((x + 80) * 0.02)); ctx.line_to(x + 40, 92)
        ctx.close_path(); ctx.set_source_rgba(*hexc(['#e63946', '#ffd166', '#2a9d8f', '#4361ee'][k % 4])); ctx.fill()
    cols = ['#4361ee', '#e76f51', '#2a9d8f', '#9d4edd', '#f4a261']
    for sy in (1170, 1420):
        for k, x in enumerate(range(70, W, 125)):
            shelf_item(ctx, x, sy, (k + (sy // 250)) % 4, cols[(k * 2 + sy // 100) % 5])
        rrect(ctx, 0, sy, W, 26, 6); ctx.set_source_rgba(*hexc('#a0622d')); ctx.fill()
        ctx.rectangle(0, sy + 20, W, 8); ctx.set_source_rgba(0, 0, 0, 0.12); ctx.fill()
    for yy in range(1700, H, 110):                              # floor tiles
        for xx in range(-110, W + 110, 110):
            ctx.rectangle(xx + (55 if (yy // 110) % 2 else 0), yy, 110, 110)
            ctx.set_source_rgba(*hexc('#f1d3a8' if ((xx // 110) + (yy // 110)) % 2 else '#e6c08c')); ctx.fill()
    ctx.rectangle(0, 1690, W, 14); ctx.set_source_rgba(*hexc('#a0622d')); ctx.fill()

# ------------------------------------------------------------ icons + card
def icon(ctx, kind, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    if kind == "globe":
        circle(ctx, 0, -20, 74, hexc('#d9f0ff')); circle(ctx, -24, -44, 14, (1, 1, 1, 0.85))
        for px, py in ((10, -30), (30, -4), (-30, -2), (0, 10)): circle(ctx, px, py, 4, (1, 1, 1, 0.9))
        ctx.move_to(-40, 20); ctx.line_to(-8, -30); ctx.line_to(14, 0); ctx.line_to(30, -18); ctx.line_to(46, 20); ctx.close_path(); ctx.set_source_rgba(*hexc('#8fbf8f')); ctx.fill()
        rrect(ctx, -62, 38, 124, 40, 12); ctx.set_source_rgba(*hexc('#9d4edd')); ctx.fill()
    elif kind == "teapot":
        e4.ell(ctx, 0, 0, 70, 56, hexc('#e76f51')); rrect(ctx, -22, -72, 44, 20, 10); ctx.set_source_rgba(*hexc('#c1583a')); ctx.fill()
        circle(ctx, 0, -78, 10, hexc('#c1583a'))
        ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#e76f51'))
        ctx.move_to(60, -10); ctx.line_to(104, -50); ctx.stroke(); ctx.arc(-70, 0, 28, math.pi * 0.5, math.pi * 1.5); ctx.stroke()
        ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.6); ctx.arc(0, 0, 40, math.pi * 1.1, math.pi * 1.5); ctx.stroke()
    elif kind == "rug":
        ctx.rotate(-0.1); rrect(ctx, -90, -62, 180, 124, 8); ctx.set_source_rgba(*hexc('#4361ee')); ctx.fill()
        for k, c in enumerate(('#ffd166', '#e63946', '#ffffff')):
            rrect(ctx, -76 + k * 12, -48 + k * 12, 152 - k * 24, 96 - k * 24, 4); ctx.set_source_rgba(*hexc(c)); ctx.set_line_width(7); ctx.stroke()
        ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#f8f9fa'))
        for k in range(-8, 9): ctx.move_to(k * 10, 62); ctx.line_to(k * 10, 78); ctx.move_to(k * 10, -62); ctx.line_to(k * 10, -78)
        ctx.stroke()
    elif kind == "phone":
        rrect(ctx, -58, -98, 116, 196, 18); ctx.set_source_rgba(*hexc('#1d2433')); ctx.fill()
        rrect(ctx, -48, -84, 96, 168, 10); ctx.set_source_rgba(*hexc('#f1f3f5')); ctx.fill()
        rrect(ctx, -38, -70, 76, 28, 6); ctx.set_source_rgba(*hexc('#4361ee')); ctx.fill()
        for k in range(3): rrect(ctx, -38, -30 + k * 28, 76, 18, 5); ctx.set_source_rgba(*hexc('#ced4da')); ctx.fill()
    ctx.restore()

def card(ctx, t, kind, l1, l2, res, res_col, t_l2, t_res, a=1.0, ik=1.0):
    ctx.save(); ctx.translate(0, (1 - a) * -30)
    rrect(ctx, 66, CY + 8, 948, 440, 44); ctx.set_source_rgba(0, 0, 0, 0.12 * a); ctx.fill()
    rrect(ctx, 60, CY, 948, 440, 44); ctx.set_source_rgba(1, 1, 1, 0.97 * a); ctx.fill()
    icon(ctx, kind, 195, CY + 175, 1.15 * ik)
    ltext(ctx, l1, 340, CY + 105, 46, hexc('#22223b', a))
    a2 = ease((t - t_l2) / 0.3)
    if a2 > 0: ltext(ctx, l2, 340, CY + 185, 36, hexc(RED, a * a2))
    k = ease((t - t_res) / 0.3)
    if k > 0:
        pop = 1 + 0.2 * max(0.0, 1 - (t - t_res) / 0.3)
        ctx.save(); ctx.translate(664, CY + 345); ctx.scale(pop, pop)
        mv.font(ctx, 104 if len(res) <= 6 else 72); e = ctx.text_extents(res); ctx.move_to(-e.x_advance / 2, 36); ctx.set_source_rgba(*hexc(res_col, k)); ctx.show_text(res); ctx.restore()
    ctx.restore()

def chars(ctx, t, wmode="wave", wflush=0.0, wexpr="happy", lexpr="flat", lhands=(0, -200)):
    wren(ctx, WX, GY, WS, t, wmode, flush=wflush, expr=wexpr)
    kid(ctx, LX, GY, LS, t, lexpr, lhands)

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    shop(ctx, t); chars(ctx, t, "cheer", lexpr="flat")
    card(ctx, t, "globe", "Snow globe: $200", "Wren paid:", "$0", GREEN, 0.0, 0.15)
    header(ctx, ease(t / 0.15 + 1), "GRANDMA MATH", "Travel edition", "How does she do it?", -0.3, t)
    wm(ctx); ai_tag(ctx, y=1860)

def s1(ctx, t, d):
    shop(ctx, t); chars(ctx, t, "cheer" if t > 1.8 else "wave", lexpr="flat")
    card(ctx, t, "globe", "Snow globe  $200", "Holiday money isn't real: -$200", "= $0", GREEN, 0.7, 1.7)
    header(ctx, ease(t / 0.2), "RULE 1", "Holiday money isn't real", "Free. Obviously.", 1.7, t, main_size=56)
    pill(ctx, t, "Wait for the ending", 0.5); wm(ctx); ai_tag(ctx, y=1860)

def s2(ctx, t, d):
    shop(ctx, t); chars(ctx, t, "cheer" if t > 1.9 else "wave", lexpr="flat")
    card(ctx, t, "teapot", "Teapot  $90", "Walked 3 km to get here: -$90", "= $0", GREEN, 0.7, 1.8)
    header(ctx, ease(t / 0.2), "RULE 2", "Walking pays for it", "Free. Again.", 1.8, t, main_size=58)
    wm(ctx); ai_tag(ctx, y=1860)

def s3(ctx, t, d):
    shop(ctx, t); chars(ctx, t, "cheer" if t > 2.3 else "wave", lexpr="flat")
    card(ctx, t, "rug", "Rug  $300", "70% off sale: saved $210", "+$210 PROFIT", GREEN, 0.8, 2.2)
    header(ctx, ease(t / 0.2), "RULE 3", "A sale is basically profit", "Free AND she earns.", 2.2, t, main_size=54)
    wm(ctx); ai_tag(ctx, y=1860)

def s4(ctx, t, d):
    shop(ctx, t)
    chars(ctx, t, "cheer" if t > 2.6 else "wave", wexpr="happy", lexpr="flat" if t < 1.5 else "flat")
    card(ctx, t, "phone", "LEO'S BANK APP", "3 purchases today: -$590", "$3.20", RED, 0.5, 1.1)
    header(ctx, ease(t / 0.2), "PLOT TWIST", "Who paid?", "Not Wren.", 1.2, t)
    bubble_ml(ctx, 760, 1075, ["Grandma.", "That was MY card."], 40, ease((t - 1.7) / 0.25) * (1 - ease((t - 2.6) / 0.2)), (LX - 10, 1330))
    bubble_ml(ctx, 330, 1075, ["Then it's free", "for me."], 40, ease((t - 2.7) / 0.25), (WX, 1230))
    wm(ctx); ai_tag(ctx, y=1860)

def s5(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    a = ease(t / 0.3)
    ctext(ctx, "Wren spent: $0.", 205 - (1 - a) * 20, 62, hexc('#22223b', a), maxw=900)
    ctext(ctx, "Leo's bank: $3.20.", 290, 62, hexc(RED, ease((t - 0.5) / 0.3)), maxw=900)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Send this to a friend who says it's free", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False)
    ai_tag(ctx, y=1890, dark=True)

SCENES = [(s0, 2.4), (s1, 3.0), (s2, 3.0), (s3, 3.4), (s4, 3.4), (s5, 2.6)]

def frame(fn, t, d):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    fn(ctx, t, d)
    a_in = 0 if fn is s0 else 1 - t / 0.1
    a_out = (t - (d - 0.5)) / 0.5 if fn is s5 else (t - (d - 0.1)) / 0.1
    a = max(a_in, a_out, 0)
    if a > 0:
        ctx.set_source_rgba(*hexc('#fff3e0', min(1, ease(a)))); ctx.paint()
    return surf

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        from PIL import Image
        picks = [(s0, 0.6), (s1, 1.0), (s1, 2.4), (s2, 2.5), (s3, 1.2), (s3, 3.0), (s4, 1.5), (s4, 2.2), (s4, 3.2), (s5, 2.0)]
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

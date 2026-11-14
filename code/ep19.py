import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = "/home/claude/wren/ep19"
RED = '#e63946'; GREEN = '#2a9d8f'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1700

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

def txt(ctx, s, x, y, size, col, center=False):
    mv.font(ctx, size); e = ctx.text_extents(s); ctx.move_to(x - (e.x_advance / 2 if center else 0), y); ctx.set_source_rgba(*col); ctx.show_text(s)

DROP = [0, .04, .02, .1, .08, .2, .3, .28, .45, .6, .58, .8, 1.0]
def fall_line(ctx, x, y, w, h, k, lw=10):
    ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_source_rgba(*hexc(RED))
    n = max(2, int(k * len(DROP)))
    for i in range(n):
        px, py = x + w * i / (len(DROP) - 1), y + h * DROP[i]
        ctx.line_to(px, py) if i else ctx.move_to(px, py)
    ctx.stroke(); circle(ctx, px, py, lw, hexc(RED))

def cafe_bg(ctx, t, tv=True, k=1.0):
    mv.vgrad(ctx, '#d8efe8', '#bfe3d8')
    for sx in (70,):                                                         # shelf with cups
        rrect(ctx, sx, 900, 380, 18, 6); ctx.set_source_rgba(*hexc('#8a5a2b')); ctx.fill()
        for j, c in enumerate(('#e63946', '#ffd166', '#4361ee', '#ffffff')):
            rrect(ctx, sx + 30 + j * 88, 846, 56, 54, 10); ctx.set_source_rgba(*hexc(c)); ctx.fill()
        rrect(ctx, sx, 720, 380, 18, 6); ctx.set_source_rgba(*hexc('#8a5a2b')); ctx.fill()
        for j in range(3):
            circle(ctx, sx + 70 + j * 120, 690, 34, hexc('#3a8f5c')); rrect(ctx, sx + 46 + j * 120, 690, 48, 30, 6); ctx.set_source_rgba(*hexc('#c1583a')); ctx.fill()
    if tv:
        rrect(ctx, 540, 640, 470, 330, 22); ctx.set_source_rgba(*hexc('#1a1c2e')); ctx.fill()
        rrect(ctx, 556, 656, 438, 298, 12); ctx.set_source_rgba(*hexc('#10132b')); ctx.fill()
        txt(ctx, "NVIDIA", 580, 712, 40, (1, 1, 1, 1))
        ctx.move_to(850, 684); ctx.line_to(890, 684); ctx.line_to(870, 714); ctx.close_path(); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
        txt(ctx, "18%", 900, 714, 40, hexc(RED))
        fall_line(ctx, 590, 750, 370, 150, k, 8)
        if int(t * 2) % 2 == 0: rrect(ctx, 580, 916, 150, 28, 8); ctx.set_source_rgba(*hexc(RED)); ctx.fill(); txt(ctx, "THIS MONTH", 592, 938, 20, (1, 1, 1, 1))
    ctx.rectangle(0, 1420, W, H - 1420); ctx.set_source_rgba(*hexc('#d9b48a')); ctx.fill()
    for kx in range(8): ctx.rectangle(kx * 150 - 20, 1420, 6, H - 1420); ctx.set_source_rgba(*hexc('#c79f72')); ctx.fill()

def phone(ctx, x, y):
    rrect(ctx, x - 26, y - 46, 52, 92, 10); ctx.set_source_rgba(*hexc('#1a1c2e')); ctx.fill()
    rrect(ctx, x - 20, y - 38, 40, 70, 6); ctx.set_source_rgba(*hexc('#ffb3b8')); ctx.fill()

def s0(ctx, t, d):
    cafe_bg(ctx, t, k=ramp(t, 0.2, 1.8))
    wren(ctx, 330, GY, 1.1, t, "point", expr="happy", hand=(150, -330))
    cx, cy = 330 + 150 * 1.1 + 6, GY - 330 * 1.1                               # teacup
    rrect(ctx, cx - 30, cy - 50, 60, 50, 12); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill(); e4.ell(ctx, cx, cy + 4, 50, 9, (1, 1, 1, 1))
    kid(ctx, 840, GY, 0.95, t, "shock", (-40, -240)); phone(ctx, 840 - 40 * 0.95, GY - 240 * 0.95 - 30)
    bubble_ml(ctx, 760, 1060, ["Who's Nvidia?"], 46, ramp(t, 2.5, 2.7), (450, GY - 600))
    header(ctx, ease(t / 0.2 + 1), "WREN SEES THE NVIDIA NEWS", "Down 18% this month.", "Leo is not okay.", -0.3, t, main_size=56)
    meter(ctx, "LEO'S MOOD", "%d%%" % int(100 - 95 * ramp(t, 0.2, 1.8))); wm(ctx)

def s1(ctx, t, d):
    cafe_bg(ctx, t)
    wren(ctx, 330, GY, 1.1, t, "wave" if t > 2.6 else "point", expr="happy", hand=(110, -200))
    kid(ctx, 840, GY, 0.95, t, "flat", (-40, -240)); phone(ctx, 840 - 40 * 0.95, GY - 240 * 0.95 - 30)
    bubble_ml(ctx, 760, 1060, ["They make chips,", "Grandma."], 40, ramp(t, 0.4, 0.6) * (1 - ramp(t, 2.7, 2.9)), (840, GY - 400))
    a = ramp(t, 1.3, 1.7)                                                    # thought bubble: potato chips
    if a > 0:
        for j, (dx, dy, r) in enumerate(((60, -730, 14), (30, -790, 22))): circle(ctx, 330 + dx, GY + dy, r * a, (1, 1, 1, a))
        for dx, dy, r in ((-90, 0, 80), (0, -30, 100), (90, 0, 80), (0, 30, 90)): circle(ctx, 280 + dx, 760 + dy, r * a, (1, 1, 1, a))
        ctx.save(); ctx.translate(280, 760); ctx.rotate(0.12 * math.sin(t * 3)); ctx.scale(a, a)
        rrect(ctx, -60, -80, 120, 160, 14); ctx.set_source_rgba(*hexc(RED)); ctx.fill()
        e4.ell(ctx, 0, 0, 48, 34, hexc('#ffd60a')); txt(ctx, "CHIPS", 0, 10, 24, hexc(RED), True); ctx.restore()
    bubble_ml(ctx, 750, 1060, ["All this fuss", "over crisps?"], 44, ramp(t, 2.9, 3.1), (450, GY - 600))
    header(ctx, ease(t / 0.2), "LEO EXPLAINS", "“They make chips.”", "Wren pictures the wrong chips.", 1.4, t, main_size=56)
    meter(ctx, "WREN'S UNDERSTANDING", "4%"); wm(ctx)

def s2(ctx, t, d):
    cafe_bg(ctx, t, tv=False)
    # comparison board
    rrect(ctx, 90, 630, 900, 400, 26); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    k = ramp(t, 0.3, 1.8)
    txt(ctx, "NVIDIA", 130, 700, 34, hexc(RED)); fall_line(ctx, 130, 730, 380, 250, k)
    txt(ctx, "WREN'S BISCUIT TIN", 560, 700, 34, hexc(GREEN))
    ctx.set_line_width(10); ctx.set_source_rgba(*hexc(GREEN)); ctx.move_to(560, 850); ctx.line_to(560 + 380 * k, 850); ctx.stroke(); circle(ctx, 560 + 380 * k, 850, 10, hexc(GREEN))
    txt(ctx, "0.0%", 750, 950, 46, hexc(GREEN), True)
    wren(ctx, 330, GY, 1.1, t, "point", expr="happy", hand=(160, -330))
    tx, ty = 330 + 160 * 1.1 + 10, GY - 330 * 1.1
    rrect(ctx, tx - 70, ty - 60, 140, 110, 16); ctx.set_source_rgba(*hexc('#4361ee')); ctx.fill()
    rrect(ctx, tx - 76, ty - 76, 152, 30, 12); ctx.set_source_rgba(*hexc('#2f47b8')); ctx.fill(); circle(ctx, tx, ty - 4, 26, hexc('#e9b96e'))
    kid(ctx, 840, GY, 0.95, t, "shock" if t < 2.4 else "flat", (-40, -240)); phone(ctx, 840 - 40 * 0.95, GY - 240 * 0.95 - 30)
    bubble_ml(ctx, 740, 1150, ["It lost $500 billion", "in two days!"], 38, ramp(t, 0.6, 0.8) * (1 - ramp(t, 2.6, 2.8)), (840, GY - 400))
    bubble_ml(ctx, 750, 1150, ["My biscuit tin", "lost nothing."], 42, ramp(t, 2.8, 3.0), (450, GY - 600))
    header(ctx, ease(t / 0.2), "WREN'S PORTFOLIO", "Leo reads the numbers.", "Wren checks her tin.", 1.6, t, main_size=56)
    wm(ctx)

def s3(ctx, t, d):
    cafe_bg(ctx, t, tv=False)
    rrect(ctx, 520, 1180, 600, 60, 14); ctx.set_source_rgba(*hexc('#8a5a2b')); ctx.fill()            # counter
    ctx.rectangle(540, 1240, 560, 200); ctx.set_source_rgba(*hexc('#a9714a')); ctx.fill()
    rrect(ctx, 600, 700, 380, 250, 20); ctx.set_source_rgba(*hexc('#1a1c2e')); ctx.fill()             # menu board
    txt(ctx, "TODAY", 790, 770, 40, hexc('#ffd166'), True); txt(ctx, "Chips & dip", 790, 840, 40, (1, 1, 1, 1), True); txt(ctx, "$6", 790, 905, 40, (1, 1, 1, 1), True)
    wx = lerp(700, 360, ramp(t, 0.2, 1.4))
    wren(ctx, wx, GY, 1.1, t, "point", expr="happy", hand=(160, -330))
    bx, by = wx + 160 * 1.1 + 10, GY - 330 * 1.1 - 10
    e4.ell(ctx, bx, by + 30, 120, 22, (1, 1, 1, 1))
    ctx.arc(bx, by, 60, 0, math.pi); ctx.close_path(); ctx.set_source_rgba(*hexc('#e9edf2')); ctx.fill(); e4.ell(ctx, bx, by, 60, 14, hexc('#7ac143'))
    for j in range(5):
        a = -0.6 + j * 0.3; ctx.save(); ctx.translate(bx - 90 + j * 45, by + 12 - 6 * abs(j - 2)); ctx.rotate(a)
        ctx.move_to(0, -34); ctx.line_to(24, 12); ctx.line_to(-24, 12); ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill(); ctx.restore()
    if 1.4 < t < 1.8: burst(ctx, bx, by - 40, 1 - (t - 1.4) / 0.4, 120)
    kid(ctx, 860, GY, 0.95, t, "flat", (0, -150))
    bubble_ml(ctx, 780, 1060, ["You said", "buy the dip."], 44, ramp(t, 1.5, 1.7) * (1 - ramp(t, 2.5, 2.65)), (wx + 120, GY - 600))
    bubble_ml(ctx, 800, 1090, ["Not THAT dip."], 42, ramp(t, 2.7, 2.9), (860, GY - 400))
    header(ctx, ease(t / 0.2), "WREN TAKES ACTION", "“People are buying the dip.”", "So Wren buys the dip.", 1.3, t, main_size=52)
    meter(ctx, "DIP PURCHASED", "Guacamole"); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “I bought the dip.”", 205 - (1 - a) * 20, 60, hexc('#22223b', a), maxw=940)
    ctext(ctx, "Leo: “That's guacamole.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Not financial advice. Just snacks.", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.6), (s0, 3.2), (s1, 1.0), (s1, 2.2), (s1, 3.8), (s2, 1.4), (s2, 3.6), (s3, 0.6), (s3, 2.0), (s3, 3.4), (s4, 2.6)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((300, 533)))
        c = Image.new("RGB", (310 * 6, 543 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 6) * 310, (i // 6) * 543))
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

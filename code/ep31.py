"""ep31 - Plane cabin: Leo paid $39 extra for the window seat. Seat 23A has no window, just wall. He stretches for row 22's window: the shade slams shut. He draws his own window. Wren opens her powder compact, angles it at row 24's window, and serves him a sunset."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep31"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; GOLD = '#ffb703'; NAVY = '#24345e'; SEAT = '#3b5ba5'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))

LX, LGY, LS = 540, 1560, 1.2          # Leo (seat 23A, in front of the blank wall)
WX, WGY, WS = 875, 1730, 1.0          # Wren (seat 23B)
WIN_L, WIN_R, WIN_Y = 160, 960, 740   # row 22 window (left) and row 24 window (right); top y
WIN_W, WIN_H = 170, 250
SEAT_TOP = 1420                       # top of the row-22 seat backs in the foreground

def meter(ctx, label, val, a=1.0, col='#ffd166'):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc(col, a)); ctx.show_text(val)

def txt(ctx, s, x, y, size, col, center=True, bold=True):
    mv.font(ctx, size, bold); e = ctx.text_extents(s); ctx.move_to(x - (e.x_advance / 2 if center else 0), y); ctx.set_source_rgba(*col); ctx.show_text(s)

def cloud(ctx, x, y, s, a=1.0):
    for dx, dy, r in ((-40, 6, 26), (0, -8, 34), (40, 6, 26), (0, 14, 26)): circle(ctx, x + dx * s, y + dy * s, r * s, (1, 1, 1, a))

def sky(ctx, x, y, w, h, t, sunset=False):
    g = cairo.LinearGradient(0, y, 0, y + h)
    if sunset:
        for k, c in ((0, '#3d348b'), (0.45, '#f35b04'), (0.75, '#f7b801'), (1, '#ff8c42')): g.add_color_stop_rgb(k, *hexc(c)[:3])
    else:
        g.add_color_stop_rgb(0, *hexc('#4ea8de')[:3]); g.add_color_stop_rgb(1, *hexc('#bde0fe')[:3])
    ctx.set_source(g); ctx.rectangle(x, y, w, h); ctx.fill()
    if sunset:
        circle(ctx, x + w * 0.5, y + h * 0.62, h * 0.16, hexc('#fff3b0'))
        ctx.rectangle(x, y + h * 0.7, w, h * 0.3); ctx.set_source_rgba(*hexc('#c44536', 0.85)); ctx.fill()
        for k in range(4): ctx.rectangle(x + w * (0.3 + 0.03 * k), y + h * (0.74 + 0.05 * k), w * (0.4 - 0.06 * k), 5); ctx.set_source_rgba(*hexc('#fff3b0', 0.7)); ctx.fill()
    for k, (fx, fy, s) in enumerate(((0.2, 0.3, 0.9), (0.8, 0.55, 0.7), (0.5, 0.85, 1.0))):
        cx = x + ((fx * w - t * 40 * (k + 1)) % (w + 160)) - 80
        cloud(ctx, cx, y + fy * h * (0.4 if sunset else 1.0), s * w / 170 * (0.5 if sunset else 1.0), 0.95 if not sunset else 0.7)

def window(ctx, cx, t, shade=0.0, hand=0.0):
    x, y = cx - WIN_W / 2, WIN_Y
    rrect(ctx, x - 22, y - 22, WIN_W + 44, WIN_H + 44, 70); ctx.set_source_rgba(*hexc('#c9d0da')); ctx.fill()
    ctx.save(); rrect(ctx, x, y, WIN_W, WIN_H, 60); ctx.clip()
    sky(ctx, x, y, WIN_W, WIN_H, t)
    if shade > 0:
        sh = WIN_H * shade
        ctx.rectangle(x, y, WIN_W, sh); ctx.set_source_rgba(*hexc('#ecebe4')); ctx.fill()
        rrect(ctx, cx - 30, y + sh - 22, 60, 14, 7); ctx.set_source_rgba(*hexc('#b8b6ac')); ctx.fill()
    ctx.restore()
    if hand > 0:                                      # row 22 passenger's hand pulling the shade
        hy = y + WIN_H * shade - 10
        ctx.set_line_width(40); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#6d597a', hand))
        ctx.move_to(cx - 160, hy + 70); ctx.line_to(cx - 30, hy); ctx.stroke(); circle(ctx, cx - 20, hy, 24, hexc('#e0ac69', hand))

def cabin(ctx, t, shadeL=0.0, handL=0.0, shadeR=0.0):
    mv.vgrad(ctx, '#eef1f5', '#d9dee6')
    for px in (360, 720):                                                    # wall panel seams
        ctx.rectangle(px, 700, 4, 800); ctx.set_source_rgba(*hexc('#c7cdd6')); ctx.fill()
    ctx.rectangle(0, 596, W, 110); ctx.set_source_rgba(*hexc('#f7f8fa')); ctx.fill()     # overhead bins
    ctx.rectangle(0, 700, W, 10); ctx.set_source_rgba(*hexc('#c7cdd6')); ctx.fill()
    for px in (360, 720): ctx.rectangle(px, 596, 4, 104); ctx.set_source_rgba(*hexc('#d5dae2')); ctx.fill()
    for n, px in (("22", WIN_L), ("23", LX), ("24", WIN_R)):
        rrect(ctx, px - 40, 616, 80, 40, 10); ctx.set_source_rgba(*hexc('#ffffff')); ctx.fill()
        txt(ctx, n, px, 648, 28, hexc('#5c677d'))
    window(ctx, WIN_L, t, shadeL, handL)
    window(ctx, WIN_R, t, shadeR)

def seat_back(ctx, x, w):                                                  # the seats Leo and Wren sit in
    rrect(ctx, x - w / 2, 1040, w, 460, 60); ctx.set_source_rgba(*hexc(SEAT)); ctx.fill()
    rrect(ctx, x - w / 2 + 26, 1060, w - 52, 110, 30); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill()

def front_row(ctx):                                                        # row 22 seat backs in front of us
    for x0 in (90, 560):
        rrect(ctx, x0 - 120, SEAT_TOP, 560, 600, 70); ctx.set_source_rgba(*hexc(SEAT)); ctx.fill()
        rrect(ctx, x0 - 50, SEAT_TOP + 90, 420, 230, 20); ctx.set_source_rgba(*hexc('#2e4a8a')); ctx.fill()
        ctx.rectangle(x0 + 100, SEAT_TOP + 108, 120, 12); ctx.set_source_rgba(*hexc('#8da2cf')); ctx.fill()

def boarding_pass(ctx, x, y, a=1.0):
    rrect(ctx, x - 120, y - 62, 240, 124, 14); ctx.set_source_rgba(*hexc('#ffffff', a)); ctx.fill()
    rrect(ctx, x - 120, y - 62, 240, 34, 14); ctx.set_source_rgba(*hexc('#4361ee', a)); ctx.fill()
    txt(ctx, "BOARDING PASS", x, y - 37, 18, (1, 1, 1, a))
    txt(ctx, "23A WINDOW", x, y + 6, 32, hexc('#22223b', a)); txt(ctx, "+$39", x, y + 46, 30, hexc(RED, a))

def leo(ctx, t, expr, hands=(0, -200), lean=0.0, stretch=0.0):
    ctx.save(); ctx.translate(LX, LGY); ctx.rotate(-lean); ctx.scale(1, 1 + stretch); ctx.translate(-LX, -LGY)
    kid(ctx, LX, LGY, LS, t, expr, hands); ctx.restore()

def leo_hand(hands): return (LX + hands[0] * LS, LGY + hands[1] * LS)

def napkin(ctx, k, t):                                                     # Leo's hand-drawn window
    cx, cy = LX, 840
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(-0.04)
    rrect(ctx, -130, -115, 260, 230, 8); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    for sx in (-110, 90): ctx.rectangle(sx, -125, 26, 20); ctx.set_source_rgba(*hexc('#f2e8cf', 0.9)); ctx.fill()
    ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#22223b'))
    k1 = clamp01(k / 0.4)
    if k1 > 0:
        ctx.new_path(); ctx.save(); ctx.scale(1, 1.3); ctx.arc(0, 0, 70, -math.pi / 2, -math.pi / 2 + 2 * math.pi * k1); ctx.restore(); ctx.stroke()
    k2 = clamp01((k - 0.4) / 0.3)
    if k2 > 0:
        ctx.set_source_rgba(*hexc('#f4a261')); ctx.new_path(); ctx.arc(-18, -20, 22, 0, 2 * math.pi * k2); ctx.stroke()
        for j in range(int(6 * k2)):
            a = j * math.pi / 3; ctx.move_to(-18 + math.cos(a) * 30, -20 + math.sin(a) * 30); ctx.line_to(-18 + math.cos(a) * 42, -20 + math.sin(a) * 42); ctx.stroke()
    k3 = clamp01((k - 0.7) / 0.3)
    if k3 > 0:
        ctx.set_source_rgba(*hexc('#4ea8de')); ctx.new_path(); ctx.arc(20, 40, 18, math.pi, math.pi + math.pi * k3); ctx.stroke()
        if k3 > 0.5: ctx.new_path(); ctx.arc(46, 40, 16, math.pi, math.pi + math.pi * (k3 - 0.5) * 2); ctx.stroke()
    ctx.restore()

def compact(ctx, x, y, s=1.0, open_=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    e4.ell(ctx, 0, 12, 46, 46, hexc('#d4a373'))                                  # base
    e4.ell(ctx, 0, 12, 38, 38, hexc('#f1c0a0'))                                  # powder
    if open_ > 0:
        ctx.save(); ctx.translate(0, -30); ctx.scale(1, open_)
        e4.ell(ctx, 0, -40, 46, 46, hexc('#d4a373')); e4.ell(ctx, 0, -40, 38, 38, hexc('#e9f5ff'))
        ctx.move_to(-20, -60); ctx.line_to(8, -18); ctx.set_line_width(6); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.stroke()
        ctx.restore()
    ctx.restore()

def wren_r(ctx, t, mode="point", expr="happy", hand=(150, -330)):
    wren(ctx, WX, WGY, WS, t, mode, expr=expr, hand=hand)

def wren_l(ctx, t, expr="happy", hand=(150, -330)):                        # mirrored: her pointing hand reaches toward Leo
    ctx.save(); ctx.translate(WX, 0); ctx.scale(-1, 1)
    wren(ctx, 0, WGY, WS, t, "point", expr=expr, hand=hand); ctx.restore()
    return WX - hand[0] * WS, WGY + (hand[1] + math.sin(t * 2 * math.pi * 1.1) * 5) * WS

def teacup(ctx, x, y):
    rrect(ctx, x - 26, y - 44, 52, 44, 10); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill(); e4.ell(ctx, x, y + 2, 42, 8, (1, 1, 1, 1))
    ctx.set_line_width(6); ctx.set_source_rgba(1, 1, 1, 1); ctx.arc(x + 30, y - 24, 12, -1.4, 1.4); ctx.stroke()

def cast(ctx, t, leo_expr, wren_expr="happy", hands=(0, -200), lean=0.0, stretch=0.0, pass_a=0.0, wren_fn=None):
    seat_back(ctx, LX, 300); seat_back(ctx, WX, 330)
    if wren_fn: wren_fn()
    else:
        wren_r(ctx, t, expr=wren_expr, hand=(150, -330))
        teacup(ctx, WX + 150 * WS + 4, WGY - 330 * WS - 6 + math.sin(t * 2 * math.pi * 1.1) * 5)
    leo(ctx, t, leo_expr, hands, lean, stretch)
    if pass_a > 0:
        hx, hy = leo_hand(hands); boarding_pass(ctx, hx, hy + 6, pass_a)
    front_row(ctx)

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    cabin(ctx, t)
    looked = t > 1.2
    cast(ctx, t, "shock" if looked else "smile", hands=(0, -195), pass_a=1.0)
    if 1.2 < t < 1.6: burst(ctx, LX, 860, 1 - (t - 1.2) / 0.4, 110)
    a = ramp(t, 1.25, 1.5)
    if a > 0:                                                               # arrow + label on the blank wall
        ctx.save(); ctx.translate(LX, 830 + 8 * math.sin(t * 6))
        rrect(ctx, -150, -54, 300, 70, 35); ctx.set_source_rgba(*hexc(RED, a)); ctx.fill()
        txt(ctx, "YOUR VIEW", 0, -6, 34, (1, 1, 1, a))
        ctx.move_to(-22, 22); ctx.line_to(22, 22); ctx.line_to(0, 62); ctx.close_path(); ctx.set_source_rgba(*hexc(RED, a)); ctx.fill(); ctx.restore()
    bubble_ml(ctx, LX, 960, ["Where's my window?"], 42, ramp(t, 2.2, 2.4), (LX, 1095))
    header(ctx, ease(t / 0.2 + 1), "WINDOW SEAT: +$39", "Leo paid extra for the view.", "Seat 23A has no window.", -0.3, t, main_size=54)
    meter(ctx, "WINDOWS AT SEAT 23A", "0", col='#ff8fa3'); wm(ctx)

def s1(ctx, t, d):
    shade = ramp(t, 2.1, 2.45)
    handA = ramp(t, 1.8, 2.05) * (1 - ramp(t, 3.0, 3.3))
    cabin(ctx, t, shadeL=shade, handL=handA)
    k = ramp(t, 0.2, 1.6) * (1 - ramp(t, 2.5, 3.1))
    expr = "smile" if t < 2.1 else ("shock" if t < 2.9 else "flat")
    cast(ctx, t, expr, hands=(-40, -230), lean=0.32 * k, stretch=0.22 * k, wren_expr="happy")
    if 2.4 < t < 2.8: burst(ctx, WIN_L, WIN_Y + WIN_H - 10, 1 - (t - 2.4) / 0.4, 110)
    if 2.4 < t < 2.9: txt(ctx, "CLACK!", WIN_L + 40, WIN_Y + WIN_H + 90, 46, hexc(RED, 1 - ramp(t, 2.7, 2.9)))
    bubble_ml(ctx, 640, 900, ["Sooo close..."], 42, ramp(t, 0.9, 1.1) * (1 - ramp(t, 1.9, 2.05)), (470, 1060))
    bubble_ml(ctx, 620, 920, ["Seriously?!"], 44, ramp(t, 3.1, 3.3), (LX, 1095))
    header(ctx, ease(t / 0.2), "PLAN A: LEAN", "Row 22 has a window.", "Row 22 closes the shade.", 1.9, t, main_size=56)
    meter(ctx, "NECK STRETCH", "%d cm" % int(round(22 * k))); wm(ctx)

def s2(ctx, t, d):
    cabin(ctx, t, shadeL=1.0)
    k = ramp(t, 0.3, 2.4)
    drawing = t < 2.5
    # Leo's arm reaches up to the napkin while drawing
    hands = (60 + 25 * math.sin(t * 9) * (1 if drawing else 0), -330) if drawing else (0, -200)
    cast(ctx, t, "smile" if t < 2.7 else "flat", hands=hands)
    napkin(ctx, k, t)
    if drawing:
        hx, hy = leo_hand(hands); ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#22223b'))
        ctx.move_to(hx + 20, hy); ctx.line_to(hx + 40, hy - 50); ctx.stroke()
    bubble_ml(ctx, 820, 1000, ["Lovely, dear.", "Bit cloudy."], 40, ramp(t, 2.8, 3.0), (WX - 10, 1060))
    header(ctx, ease(t / 0.2), "PLAN B: DRAW ONE", "Leo makes his own window.", "Marker sunset. Very sad.", 1.6, t, main_size=54)
    meter(ctx, "VIEW QUALITY", "%d/10" % (1 + int(k)), col='#ff8fa3'); wm(ctx)

def s3(ctx, t, d):
    cabin(ctx, t, shadeL=1.0)
    op = ramp(t, 0.3, 0.8)
    hand = (lerp(80, 175, op), lerp(-330, -640, op))
    pos = {}
    def wfn():
        pos['h'] = wren_l(ctx, t, "happy", hand)
    lit = ramp(t, 1.0, 1.3)
    cast(ctx, t, "shock" if t < 1.3 else ("smile" if t < 2.6 else "smug"), hands=(0, -200), wren_fn=wfn)
    mx, my = pos['h']
    if lit > 0:                                                             # beam: row 24 window -> mirror -> towards Leo
        lx_, ly_ = mx - 10, my - 80
        ctx.move_to(WIN_R - 60, WIN_Y + 150); ctx.line_to(WIN_R - 20, WIN_Y + 235); ctx.line_to(lx_, ly_ + 22); ctx.line_to(lx_, ly_ - 22); ctx.close_path()
        ctx.set_source_rgba(*hexc('#ffd166', 0.45 * lit)); ctx.fill()
        g = cairo.LinearGradient(lx_, 0, LX + 90, 0); g.add_color_stop_rgba(0, *hexc('#ffd166', 0.6 * lit)); g.add_color_stop_rgba(1, *hexc('#ffd166', 0.0))
        ctx.move_to(lx_, ly_ - 22); ctx.line_to(LX + 90, 1130); ctx.line_to(LX + 90, 1190); ctx.line_to(lx_, ly_ + 22); ctx.close_path(); ctx.set_source(g); ctx.fill()
    compact(ctx, mx - 10, my - 10, 1.0, op)
    if lit > 0:
        for j in range(6):                                                  # sparkles
            ph = (t * 1.3 + j / 6) % 1; ang = j * 1.05 + t
            circle(ctx, mx - 10 + math.cos(ang) * (50 + 60 * ph), my - 80 + math.sin(ang) * (50 + 60 * ph), 7 * (1 - ph), hexc('#fff3b0', lit))
    z = ramp(t, 1.3, 1.7)                                                   # zoomed mirror view
    if z > 0:
        cx, cy, r = 300, 845, 150 * z
        circle(ctx, cx, cy, r + 16, hexc('#d4a373'))
        ctx.save(); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.clip(); sky(ctx, cx - r, cy - r, 2 * r, 2 * r, t, sunset=True); ctx.restore()
        ctx.move_to(cx - r * 0.5, cy - r * 0.7); ctx.line_to(cx - r * 0.1, cy - r * 0.2); ctx.set_line_width(8); ctx.set_source_rgba(1, 1, 1, 0.6 * z); ctx.stroke()
        txt(ctx, "SUNSET, LIVE", cx, cy + r + 56, 30, hexc('#22223b', z))
    bubble_ml(ctx, 790, 900, ["Grandma.", "That's a SUNSET."], 40, ramp(t, 1.8, 2.0) * (1 - ramp(t, 2.6, 2.75)), (LX + 30, 1095))
    bubble_ml(ctx, 790, 900, ["Always pack", "a view."], 44, ramp(t, 2.8, 3.0), (WX + 40, 1015))
    header(ctx, ease(t / 0.2), "PLAN C: GRANDMA", "Wren opens her powder compact.", "Mirror. Angle. Sunset.", 0.9, t, main_size=50)
    meter(ctx, "VIEW FROM 23A", "%d%%" % int(100 * ramp(t, 1.0, 1.8)), col='#2ecc71'); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    compact(ctx, 790, 1540, 1.4, 1.0)
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “I always pack a view.”", 205 - (1 - a) * 20, 60, hexc('#22223b', a), maxw=940)
    ctext(ctx, "Leo: “I paid $39 for a wall.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Window or aisle? Tell us below", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 1.4), (s0, 3.2), (s1, 1.4), (s1, 2.6), (s1, 3.8), (s2, 1.2), (s2, 3.6), (s3, 0.6), (s3, 2.2), (s3, 3.5), (s4, 2.6)]
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

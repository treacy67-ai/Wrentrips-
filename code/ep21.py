"""ep21 - Tulip fields: Leo asks for ONE photo. Wren photographs her thumb, herself, her shoes. Then paints him."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep21")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
def mix(c1, c2, k):
    a, b = hexc(c1), hexc(c2); return tuple(lerp(a[i], b[i], k) for i in range(3)) + (1,)
GY = 1700
WX, LX = 450, 900
HAND = (150, -330)
PHX, PHY = WX + HAND[0] * 1.1 + 8, GY + HAND[1] * 1.1 - 30          # phone position in Wren's hand
CARD = (290, 772)                                                    # photo card centre (above Wren, left)

def meter(ctx, label, val, a=1.0):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(val)

def txt(ctx, s, x, y, size, col, center=False):
    mv.font(ctx, size); e = ctx.text_extents(s); ctx.move_to(x - (e.x_advance / 2 if center else 0), y); ctx.set_source_rgba(*col); ctx.show_text(s)

# ------------------------------------------------------------ tulip fields
TULIP = ['#e63946', '#ffd60a', '#ff4fa3', '#b388ff', '#ff8c42', '#ffffff']
def windmill(ctx, x, base, s, t):
    ctx.save(); ctx.translate(x, base); ctx.scale(s, s)
    ctx.move_to(-70, 0); ctx.line_to(-42, -330); ctx.line_to(42, -330); ctx.line_to(70, 0); ctx.close_path(); ctx.set_source_rgba(*hexc('#f5efe2')); ctx.fill()
    ctx.move_to(-48, -330); ctx.line_to(0, -400); ctx.line_to(48, -330); ctx.close_path(); ctx.set_source_rgba(*hexc('#a44a3f')); ctx.fill()
    rrect(ctx, -20, -70, 40, 70, 18); ctx.set_source_rgba(*hexc('#7a4a2b')); ctx.fill()
    rrect(ctx, -16, -230, 32, 44, 10); ctx.set_source_rgba(*hexc('#8ecae6')); ctx.fill()
    ctx.translate(0, -345); ctx.rotate(t * 0.7)
    for k in range(4):
        ctx.save(); ctx.rotate(k * math.pi / 2)
        ctx.rectangle(-5, -200, 10, 200); ctx.set_source_rgba(*hexc('#5c4033')); ctx.fill()
        ctx.rectangle(5, -200, 46, 140); ctx.set_source_rgba(*hexc('#fff8ee', 0.95)); ctx.fill()
        ctx.set_line_width(3); ctx.set_source_rgba(*hexc('#5c4033'))
        for j in range(5): ctx.move_to(5, -200 + j * 35); ctx.line_to(51, -200 + j * 35); ctx.stroke()
        ctx.rectangle(5, -200, 46, 140); ctx.stroke()
        ctx.restore()
    circle(ctx, 0, 0, 14, hexc('#5c4033'))
    ctx.restore()

def tulip(ctx, x, y, s, col, sway=0.0):
    ctx.set_line_width(7 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#2f9e44'))
    ctx.move_to(x, y); ctx.line_to(x + sway, y - 80 * s); ctx.stroke()
    e4.ell(ctx, x + 16 * s, y - 28 * s, 20 * s, 8 * s, hexc('#2f9e44'), -0.6)
    hx, hy = x + sway, y - 80 * s
    ctx.move_to(hx - 24 * s, hy); ctx.curve_to(hx - 26 * s, hy - 50 * s, hx - 6 * s, hy - 44 * s, hx - 12 * s, hy - 56 * s)
    ctx.line_to(hx, hy - 36 * s); ctx.line_to(hx + 12 * s, hy - 56 * s)
    ctx.curve_to(hx + 6 * s, hy - 44 * s, hx + 26 * s, hy - 50 * s, hx + 24 * s, hy); ctx.curve_to(hx + 14 * s, hy + 16 * s, hx - 14 * s, hy + 16 * s, hx - 24 * s, hy)
    ctx.set_source_rgba(*hexc(col)); ctx.fill()

def field_bg(ctx, t, dusk=0.0, mill=True):
    g = cairo.LinearGradient(0, 0, 0, 1160)
    g.add_color_stop_rgb(0, *mix('#6ec6ff', '#ff9e6d', dusk)[:3]); g.add_color_stop_rgb(1, *mix('#e3f6ff', '#ffe0a3', dusk)[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1160); ctx.fill()
    sx, sy = lerp(180, 620, dusk), lerp(690, 1090, dusk)
    circle(ctx, sx, sy, 80, hexc('#fff3b0', 0.45)); circle(ctx, sx, sy, 54, mix('#fff3b0', '#ff7b39', dusk))
    for cx, cy, s in ((700, 700, 1.0), (240, 1010, 0.8)):
        x = (cx + t * 9) % 1300 - 110
        for dx, dy, r in ((-60, 10, 36), (0, -8, 50), (60, 10, 38)): circle(ctx, x + dx * s, cy + dy * s, r * s, (1, 1, 1, 0.9 - 0.3 * dusk))
    if mill: windmill(ctx, 850, 1170, 0.95, t)
    for i, c in enumerate(('#ffd60a', '#e63946', '#ff4fa3', '#b388ff', '#ff8c42')):            # far stripes
        y0 = 1150 + i * 54
        ctx.rectangle(0, y0, W, 54); ctx.set_source_rgba(*hexc(c)); ctx.fill()
        ctx.rectangle(0, y0 + 42, W, 12); ctx.set_source_rgba(*hexc('#2f9e44')); ctx.fill()
        for k in range(30):
            circle(ctx, k * 38 + (i % 2) * 19, y0 + 14 + 8 * math.sin(k * 1.7 + i), 7 + i, (1, 1, 1, 0.22))
    ctx.rectangle(0, 1420, W, H - 1420); ctx.set_source_rgba(*hexc('#e9cfa6')); ctx.fill()     # path
    ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#dcbf92'))
    for k in range(6): ctx.move_to(120 + k * 190, 1470 + (k % 3) * 90); ctx.line_to(200 + k * 190, 1470 + (k % 3) * 90); ctx.stroke()
    if dusk > 0: ctx.rectangle(0, 1150, W, H - 1150); ctx.set_source_rgba(*hexc('#ff7b39', 0.16 * dusk)); ctx.fill()

def front_tulips(ctx, t):
    for k in range(13):
        tulip(ctx, 30 + k * 86, 1940, 1.25, TULIP[(k * 5) % 6], 8 * math.sin(t * 2 + k))

def phone(ctx, x, y, flash=0.0):
    if flash > 0: burst(ctx, x + 48, y - 26, flash, 130)
    rrect(ctx, x - 62, y - 36, 124, 72, 14); ctx.set_source_rgba(*hexc('#1a1c2e')); ctx.fill()
    circle(ctx, x + 40, y - 14, 11, hexc('#3a3f5c')); circle(ctx, x + 40, y - 14, 5, hexc('#8ecae6'))
    circle(ctx, x - 62 + 14, y + 22, 24, mv.SKIN)                                              # thumb gripping

# ------------------------------------------------------------ photo cards
def card(ctx, kind, pop, t, cx=None, cy=None, rot=-0.05, w=440, h=300):
    if pop <= 0: return
    cx = CARD[0] if cx is None else cx; cy = CARD[1] if cy is None else cy
    ctx.save(); ctx.translate(lerp(PHX, cx, pop), lerp(PHY, cy, pop)); ctx.rotate(rot * pop); s = 0.15 + 0.85 * pop + 0.08 * math.sin(math.pi * pop); ctx.scale(s, s)
    rrect(ctx, -w / 2 + 6, -h / 2 + 10, w, h, 18); ctx.set_source_rgba(0, 0, 0, 0.18); ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, 18); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    iw, ih = w - 36, h - 36
    ctx.rectangle(-iw / 2, -ih / 2, iw, ih); ctx.clip()
    if kind == 'thumb':
        ctx.rectangle(-iw / 2, -ih / 2, iw, ih); ctx.set_source_rgba(*hexc('#8fd3ff')); ctx.fill()
        for i, c in enumerate(('#ffd60a', '#e63946', '#ff4fa3')):
            ctx.rectangle(-iw / 2, 40 + i * 30, iw, 30); ctx.set_source_rgba(*hexc(c)); ctx.fill()
        ctx.rectangle(-iw / 2, 100, iw, 60); ctx.set_source_rgba(*hexc('#e9cfa6')); ctx.fill()
        kid(ctx, 172, 132, 0.52, 0.5, "smile", (0, -390))
        e4.ell(ctx, -70, 30, 250, 205, hexc('#f2c9a5'), 0.15)
        e4.ell(ctx, -70, 30, 250, 205, hexc('#e9b58c', 0.0), 0.15)
        ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#dba67d'))
        for r in (40, 75, 110, 145): ctx.arc(-80, 20, r, math.radians(200), math.radians(340)); ctx.stroke(); ctx.arc(-80, 20, r - 16, math.radians(20), math.radians(160)); ctx.stroke()
    elif kind == 'selfie':
        ctx.rectangle(-iw / 2, -ih / 2, iw, ih); ctx.set_source_rgba(*hexc('#8fd3ff')); ctx.fill()
        wren(ctx, 30, 30 + 545 * 2.3, 2.3, 0.6, "point", expr="shock", hand=(150, -100))
    elif kind == 'video':
        ctx.rectangle(-iw / 2, -ih / 2, iw, ih); ctx.set_source_rgba(*hexc('#e9cfa6')); ctx.fill()
        ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#dcbf92'))
        for k in range(5): ctx.move_to(-190 + k * 90, -80 + (k % 2) * 40); ctx.line_to(-130 + k * 90, -80 + (k % 2) * 40); ctx.stroke()
        wob = 6 * math.sin(t * 5)
        for sg in (-1, 1):
            rrect(ctx, sg * 62 - 36 + wob, 20, 72, 160, 30); ctx.set_source_rgba(*hexc('#3b3b58')); ctx.fill()
            e4.ell(ctx, sg * 66 + wob, 20, 50, 74, hexc('#7a3e2b'))
            e4.ell(ctx, sg * 66 + wob, -4, 30, 40, hexc('#8f4d38'))
        rrect(ctx, -iw / 2 + 14, -ih / 2 + 14, 196, 50, 25); ctx.set_source_rgba(*hexc('#10132b', 0.85)); ctx.fill()
        if int(t * 3) % 2 == 0: circle(ctx, -iw / 2 + 40, -ih / 2 + 39, 11, hexc(RED))
        secs = 14 * 60 + 7 + int(t)
        txt(ctx, "REC %d:%02d" % (secs // 60, secs % 60), -iw / 2 + 60, -ih / 2 + 50, 28, (1, 1, 1, 1))
    elif kind == 'painting':
        ctx.rectangle(-iw / 2, -ih / 2, iw, ih); ctx.set_source_rgba(*hexc('#ffd9a8')); ctx.fill()
        circle(ctx, -iw / 2 + 50, -ih / 2 + 60, 30, hexc('#ff8c42'))
        for i, c in enumerate(('#ffd60a', '#e63946', '#ff4fa3')):
            ctx.rectangle(-iw / 2, ih / 2 - 90 + i * 30, iw, 30); ctx.set_source_rgba(*hexc(c)); ctx.fill()
        windmill(ctx, iw / 2 - 46, ih / 2 - 80, 0.28, 0.4)
        kid(ctx, -8, ih / 2 + 60, 0.62, 0.5, "smile", (0, -390))
    ctx.restore()

def easel(ctx, x, top, k, t):
    """canvas top-centre at (x, top); k = how much is painted."""
    ctx.set_line_width(16); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#8a5a2b'))
    for dx in (-110, 0, 110): ctx.move_to(x + dx * 0.25, top - 30); ctx.line_to(x + dx, GY + 10); ctx.stroke()
    rrect(ctx, x - 150, top + 330, 300, 22, 8); ctx.set_source_rgba(*hexc('#6b4423')); ctx.fill()
    rrect(ctx, x - 130, top, 260, 330, 10); ctx.set_source_rgba(*hexc('#fffdf7')); ctx.fill()
    if k > 0:
        ctx.save(); ctx.rectangle(x - 130, top, 260, 330 * k); ctx.clip()
        ctx.translate(x, top + 165); ctx.scale(1.0, 1.0)
        ctx.save(); card(ctx, 'painting', 1.0, t, 0, 0, 0.0, 296, 366); ctx.restore()
        ctx.restore()
    ctx.set_line_width(8); ctx.set_source_rgba(*hexc('#c79f72')); rrect(ctx, x - 130, top, 260, 330, 10); ctx.stroke()

def pose_hands(k=1.0): return (0, lerp(-150, -462, k))

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    field_bg(ctx, t)
    n = int(47 * clamp01((t - 0.5) / 2.7) ** 1.4)
    fl = 0.0
    if 0.5 < t < 3.3:
        ph = ((t - 0.5) * (2.5 + 2.2 * t)) % 1; fl = max(0.0, 1 - ph * 2.2)
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy", hand=HAND); phone(ctx, PHX, PHY, fl)
    tired = ramp(t, 1.4, 2.6)
    kid(ctx, LX, GY, 0.95, t, "smile" if t < 1.6 else "flat", pose_hands(1 - 0.75 * tired))
    bubble_ml(ctx, 780, 1010, ["Just ONE,", "Grandma."], 44, ramp(t, 2.3, 2.5), (LX, GY - 450))
    header(ctx, ease(t / 0.2 + 1), "TULIP FIELDS", "Leo asks for ONE photo.", "Wren is holding the phone.", -0.3, t, main_size=56)
    meter(ctx, "PHOTOS TAKEN", "%d" % n); front_tulips(ctx, t); wm(ctx)

def s1(ctx, t, d):
    field_bg(ctx, t)
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy", hand=HAND); phone(ctx, PHX, PHY)
    card(ctx, 'thumb', ramp(t, 0.35, 0.85), t)
    if 0.8 < t < 1.2: burst(ctx, CARD[0] + 200, CARD[1] - 140, 1 - (t - 0.8) / 0.4, 110)
    kid(ctx, LX, GY, 0.95, t, "flat", (0, -150))
    bubble_ml(ctx, 790, 1010, ["That's your", "thumb."], 44, ramp(t, 1.5, 1.7) * (1 - ramp(t, 2.8, 2.95)), (LX, GY - 395))
    bubble_ml(ctx, 800, 990, ["It's a lovely", "thumb."], 44, ramp(t, 3.0, 3.2), (WX + 118, GY - 610))
    header(ctx, ease(t / 0.2), "PHOTO ONE", "Wren nails the framing.", "Of her own thumb.", 1.0, t, main_size=56)
    meter(ctx, "THUMB IN FRAME", "%d%%" % int(94 * ramp(t, 0.4, 1.3))); front_tulips(ctx, t); wm(ctx)

def s2(ctx, t, d):
    field_bg(ctx, t)
    wren(ctx, WX, GY, 1.1, t, "point", expr="shock" if 0.7 < t < 2.2 else "happy", hand=HAND); phone(ctx, PHX, PHY)
    a1 = ramp(t, 0.3, 0.8) * (1 - ramp(t, 2.25, 2.4))
    card(ctx, 'selfie', a1, t)
    card(ctx, 'video', ramp(t, 2.4, 2.85), t, rot=0.04)
    if 2.8 < t < 3.2: burst(ctx, CARD[0] + 200, CARD[1] - 140, 1 - (t - 2.8) / 0.4, 110)
    kid(ctx, LX, GY, 0.95, t, "flat", (0, -150))
    bubble_ml(ctx, 800, 990, ["Why am I", "in it?"], 44, ramp(t, 0.9, 1.1) * (1 - ramp(t, 2.15, 2.3)), (WX + 118, GY - 610))
    bubble_ml(ctx, 780, 1010, ["Those are", "your shoes."], 44, ramp(t, 3.1, 3.3), (LX, GY - 395))
    header(ctx, ease(t / 0.2), "PHOTO TWO", "Selfie mode. By accident.", "Then a 14-minute video.", 2.3, t, main_size=56)
    meter(ctx, "PHOTOS OF LEO", "0"); front_tulips(ctx, t); wm(ctx)

def s3(ctx, t, d):
    k = ramp(t, 0.4, 1.9)
    field_bg(ctx, t * (1 + 6 * (1 - k)), dusk=k)
    EX, ET = 735, 1050
    easel(ctx, EX, ET, k, t)
    if 1.9 < t < 2.4: burst(ctx, EX, ET + 160, 1 - (t - 1.9) / 0.5, 230); easel(ctx, EX, ET, 1.0, t)
    painting = t < 1.9
    hx = 150 + (16 * math.sin(t * 14) if painting else 0); hy = -330 + (40 * math.sin(t * 9) if painting else 0) + 150 * (k if painting else 1)
    wren(ctx, WX, GY, 1.1, t, "point", expr="happy", hand=(hx, hy))
    bx, by = WX + hx * 1.1, GY + hy * 1.1                                           # brush
    ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#8a5a2b')); ctx.move_to(bx - 14, by + 22); ctx.line_to(bx + 46, by - 38); ctx.stroke()
    ctx.set_line_width(18); ctx.set_source_rgba(*hexc(RED)); ctx.move_to(bx + 46, by - 38); ctx.line_to(bx + 58, by - 50); ctx.stroke()
    shake = 5 * math.sin(t * 40) * k
    kid(ctx, LX + 75 + shake, GY, 0.95, t, "smile" if t < 0.7 else "flat", pose_hands(1.0))
    if t > 1.0:
        ph = ((t - 1.0) * 1.3) % 1; circle(ctx, LX + 139, GY - 330 + 40 * ph, 9, hexc('#4cc9f0', 1 - ph))
    bubble_ml(ctx, 800, 910, ["It's been", "three hours."], 44, ramp(t, 1.5, 1.7) * (1 - ramp(t, 2.7, 2.85)), (LX + 75, GY - 500))
    bubble_ml(ctx, 420, 850, ["Nearly got", "your nose."], 44, ramp(t, 2.9, 3.1), (WX + 40, GY - 700))
    header(ctx, ease(t / 0.2), "WREN'S FIX", "No phone. An easel.", "“Hold that pose, dear.”", 1.0, t, main_size=56)
    meter(ctx, "TIME PER PHOTO", "%.1f hrs" % (3.0 * k)); front_tulips(ctx, t); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 500, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    ctx.save(); ctx.translate(860, 1420); ctx.rotate(0.06); rrect(ctx, -124, -159, 248, 318, 12); ctx.set_source_rgba(*hexc('#8a5a2b')); ctx.fill()
    card(ctx, 'painting', 1.0, t, 0, 0, 0.0, 228, 298); ctx.restore()
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “One photo, as requested.”", 205 - (1 - a) * 20, 58, hexc('#22223b', a), maxw=1000)
    ctext(ctx, "Leo: “I can't feel my arms.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Who's your family's worst photographer?", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 1.2), (s0, 3.2), (s1, 0.6), (s1, 2.2), (s1, 3.9), (s2, 0.55), (s2, 1.6), (s2, 2.6), (s2, 3.9), (s3, 0.9), (s3, 2.1), (s3, 2.5), (s3, 3.6), (s4, 2.6)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((300, 533)))
        c = Image.new("RGB", (310 * 8, 543 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 8) * 310, (i // 8) * 543))
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

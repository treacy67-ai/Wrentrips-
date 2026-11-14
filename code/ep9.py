import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ai_tag, ease
import ep4 as e4
from ep7 import wm, pill, header

OUT = "/home/claude/wren/ep9"
os.makedirs(OUT, exist_ok=True)
DARK, RED = hexc('#22223b'), '#e63946'
CXW, CXL = 235, 845           # bed centres (Wren left, Leo right)
HY = 1100                     # head centre y
BED_TOP, BED_BOT = 1010, 1640
SKIN_W, SKIN_L = hexc('#f2c9a5'), hexc('#c68642')

def lerp(a, b, k): return a + (b - a) * k
def clamp01(x): return max(0.0, min(1.0, x))
def ramp(t, t0, t1): return ease(clamp01((t - t0) / (t1 - t0)))

# ---------------------------------------------------------------- cabin
def window(ctx, t, shake):
    dx = math.sin(t * 58) * 4 * shake; dy = math.cos(t * 47) * 3 * shake
    x0, y0, w, h = 330 + dx, 600 + dy, 420, 330
    ctx.save(); rrect(ctx, x0, y0, w, h, 20); ctx.clip()
    g = cairo.LinearGradient(0, y0, 0, y0 + h); g.add_color_stop_rgb(0, *hexc('#0b1034')[:3]); g.add_color_stop_rgb(1, *hexc('#3a4a8c')[:3])
    ctx.set_source(g); ctx.paint()
    rng = random.Random(7)
    for i in range(26):
        sx = x0 + rng.uniform(0, w); sy = y0 + rng.uniform(0, h * 0.6)
        circle(ctx, sx, sy, rng.uniform(1.2, 2.6) * (0.6 + 0.4 * math.sin(t * 3 + i) ** 2), (1, 1, 0.9, 0.9))
    circle(ctx, x0 + 300, y0 + 90, 46, hexc('#fff3c4')); circle(ctx, x0 + 316, y0 + 80, 40, hexc('#10153a', 0.0))
    for k, (sp, col, amp, base) in enumerate(((25, '#27336b', 50, 250), (80, '#161f4a', 70, 290))):
        ctx.move_to(x0 - 10, y0 + h + 5)
        for px in range(-10, int(w) + 30, 20):
            wx = px + t * sp
            ctx.line_to(x0 + px, y0 + base + amp * 0.5 * math.sin(wx * 0.021 + k * 2) + amp * 0.3 * math.sin(wx * 0.047 + k))
        ctx.line_to(x0 + w + 10, y0 + h + 5); ctx.close_path(); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    for i in range(3):          # village lights
        px = (x0 + w - ((t * 80 + i * 170) % (w + 60)))
        circle(ctx, px, y0 + 292 + (i % 2) * 14, 4, hexc('#ffd166'))
    ps = (t * 700) % 520         # telegraph poles
    for off in (0, 520):
        px = x0 + w - ps + off - 520 + 520
        px = x0 + ((w + 140) - ((t * 600 + off) % (w + 140)))
        ctx.set_source_rgba(*hexc('#05081c')); ctx.rectangle(px - 5, y0 + 120, 10, h); ctx.fill()
        ctx.rectangle(px - 30, y0 + 140, 60, 8); ctx.fill()
    ctx.restore()
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#8d5524')); rrect(ctx, x0, y0, w, h, 20); ctx.stroke()
    ctx.set_line_width(10); ctx.move_to(x0 + w / 2, y0); ctx.line_to(x0 + w / 2, y0 + h); ctx.stroke()
    rrect(ctx, x0 - 40, y0 - 34, w + 80, 22, 11); ctx.set_source_rgba(*hexc('#6b4423')); ctx.fill()
    for cx0, cw in ((x0 - 44, 74), (x0 + w - 30, 74)):
        rrect(ctx, cx0, y0 - 22, cw, h + 60, 24); ctx.set_source_rgba(*hexc('#9d2b3f')); ctx.fill()
        ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#7b1d2e'))
        for k in range(1, 4): ctx.move_to(cx0 + k * cw / 4, y0 - 12); ctx.line_to(cx0 + k * cw / 4, y0 + h + 30); ctx.stroke()

def cabin(ctx, t, shake=0.0, glasses=True, lamp_pop=0.0):
    g = cairo.LinearGradient(0, 0, 0, 1660); g.add_color_stop_rgb(0, *hexc('#241c4a')[:3]); g.add_color_stop_rgb(1, *hexc('#3f3170')[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1660); ctx.fill()
    ctx.set_line_width(3); ctx.set_source_rgba(1, 1, 1, 0.05)
    for x in range(0, W + 1, 90): ctx.move_to(x, 0); ctx.line_to(x, 1660); ctx.stroke()
    ctx.rectangle(0, 1560, W, 100); ctx.set_source_rgba(*hexc('#5a3a22')); ctx.fill()            # wood skirting
    # lamp glow
    lx, ly = 540, 1290
    gl = cairo.RadialGradient(lx, ly, 10, lx, ly, 420); gl.add_color_stop_rgba(0, 1, 0.85, 0.45, 0.45); gl.add_color_stop_rgba(1, 1, 0.85, 0.45, 0)
    ctx.set_source(gl); ctx.rectangle(0, 800, W, 860); ctx.fill()
    window(ctx, t, shake)
    # carpet floor
    ctx.rectangle(0, 1640, W, H - 1640); ctx.set_source_rgba(*hexc('#2b1f3d')); ctx.fill()
    ctx.set_source_rgba(*hexc('#4a3a66')); ctx.rectangle(0, 1640, W, 8); ctx.fill()
    for xx in range(30, W, 90):
        for yy in (1700, 1790):
            circle(ctx, xx + (45 if yy > 1700 else 0), yy, 9, hexc('#4a3a66', 0.7))
    # table
    jx = math.sin(t * 61) * 3 * shake; jy = abs(math.sin(t * 50)) * -4 * shake
    rrect(ctx, 452, 1420, 176, 22, 8); ctx.set_source_rgba(*hexc('#8d5524')); ctx.fill()
    ctx.rectangle(470, 1440, 16, 200); ctx.rectangle(594, 1440, 16, 200); ctx.fill()
    ctx.save(); ctx.translate(jx, jy)
    ctx.move_to(522, 1420); ctx.line_to(558, 1420); ctx.line_to(550, 1330); ctx.line_to(530, 1330); ctx.close_path(); ctx.set_source_rgba(*hexc('#6b4423')); ctx.fill()
    ctx.move_to(490, 1330); ctx.line_to(590, 1330); ctx.line_to(566, 1236); ctx.line_to(514, 1236); ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    ctx.restore()
    # cup of tea with ripples
    rrect(ctx, 582 + jx, 1384 + jy, 36, 36, 8); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill()
    e4.ell(ctx, 600 + jx, 1386 + jy, 18, 6, hexc('#a8683a'))
    if shake > 0.05:
        ctx.set_line_width(2); ctx.set_source_rgba(1, 1, 1, 0.6); ctx.arc(600 + jx, 1386 + jy, 7 + 5 * (t * 6 % 1), 0, 2 * math.pi); ctx.stroke()
    if glasses:                  # Wren's glasses on the table
        ctx.set_line_width(4); ctx.set_source_rgba(*hexc('#5c4033'))
        for gx in (474, 506): ctx.arc(gx, 1409, 12, 0, 2 * math.pi); ctx.stroke()
        ctx.move_to(486, 1407); ctx.line_to(494, 1407); ctx.stroke()

# ---------------------------------------------------------------- beds
def bed_back(ctx, cx):
    rrect(ctx, cx - 205, BED_TOP - 60, 410, 130, 26); ctx.set_source_rgba(*hexc('#8d5524')); ctx.fill()           # headboard
    rrect(ctx, cx - 195, BED_TOP + 20, 390, BED_BOT - BED_TOP - 10, 30); ctx.set_source_rgba(*hexc('#f1f3f5')); ctx.fill()
    rrect(ctx, cx - 205, BED_BOT - 22, 410, 40, 16); ctx.set_source_rgba(*hexc('#8d5524')); ctx.fill()           # footboard

def pillow(ctx, cx, y, rot=0.0, col='#ffffff'):
    ctx.save(); ctx.translate(cx, y + 65); ctx.rotate(rot)
    rrect(ctx, -150, -65, 300, 130, 56); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(0.75, 0.78, 0.85, 1); rrect(ctx, -150, -65, 300, 130, 56); ctx.stroke()
    ctx.restore()

def blanket(ctx, cx, kind, t, breathe=0.0, shake=0.0):
    top = 1196 + math.sin(t * 2.6) * 3 * breathe + math.sin(t * 40) * 3 * shake
    col, col2 = (('#f4a261', '#e07b39') if kind == 'w' else ('#4361ee', '#2f46b9'))
    rrect(ctx, cx - 190, top, 380, BED_BOT - top - 6, 36); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    ctx.save(); rrect(ctx, cx - 190, top, 380, BED_BOT - top - 6, 36); ctx.clip()
    ctx.set_source_rgba(*hexc(col2))
    if kind == 'w':
        for r in range(4):
            for c in range(4):
                if (r + c) % 2 == 0: ctx.rectangle(cx - 190 + c * 95, top + 70 + r * 95, 95, 95)
        ctx.fill()
    else:
        for k in range(8): ctx.rectangle(cx - 190, top + 70 + k * 58, 380, 24)
        ctx.fill()
    ctx.restore()
    rrect(ctx, cx - 190, top, 380, 62, 30); ctx.set_source_rgba(*hexc('#ffffff', 0.92)); ctx.fill()               # folded sheet edge
    ctx.set_line_width(3); ctx.set_source_rgba(0.8, 0.82, 0.9, 1); rrect(ctx, cx - 190, top, 380, 62, 30); ctx.stroke()
    for fx in (cx - 70, cx + 70):                                                                              # feet bumps
        e4.ell(ctx, fx, BED_BOT - 52, 46, 26, hexc('#000000', 0.12))
    return top

def zzz(ctx, x, y, t, level, col, sgn=1):
    for k in range(3):
        ph = ((t * 0.6 + k / 3.0) % 1.0)
        size = (30 + 34 * level) * (0.5 + ph)
        a = (1 - ph) * min(1, ph * 6)
        mv.font(ctx, size)
        ctx.save(); ctx.translate(x + sgn * (ph * 120 + 8 * math.sin(ph * 9)), y - ph * 260); ctx.rotate(sgn * 0.2)
        ctx.set_source_rgba(*hexc(col, a)); ctx.show_text("Z"); ctx.restore()

def waves(ctx, x, y, t, level, direction, col, reach=520):
    if level <= 0.02: return
    for k in range(4):
        ph = ((t * 1.25 + k / 4.0) % 1.0)
        r = 50 + ph * reach
        a = (1 - ph) ** 0.8 * min(1, level * 1.5)
        ctx.set_line_width(5 + 9 * level); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgba(*hexc(col, 0.85 * a))
        base = 0 if direction > 0 else math.pi
        ctx.arc(x, y, r, base - 0.55, base + 0.55); ctx.stroke()

# ---------------------------------------------------------------- faces
def eyes(ctx, cx, cy, spread, style, rs, ink='#2b2d42', skin=None):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for sg in (-1, 1):
        ex = cx + sg * spread
        if style == "closed":
            ctx.set_line_width(5); ctx.set_source_rgba(*hexc(ink)); ctx.arc(ex, cy - 3, rs * 1.7, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
        elif style == "open":
            circle(ctx, ex, cy, rs, hexc(ink))
        elif style == "wide":
            circle(ctx, ex, cy, rs * 2.3, (1, 1, 1, 1)); circle(ctx, ex, cy, rs * 0.95, hexc(ink))
        elif style == "flat":
            circle(ctx, ex, cy, rs, hexc(ink))
            ctx.rectangle(ex - rs - 1, cy - rs - 2, 2 * rs + 2, rs + 1); ctx.set_source_rgba(*skin); ctx.fill()
            ctx.set_line_width(5); ctx.set_source_rgba(*hexc(ink)); ctx.move_to(ex - rs - 2, cy - 1); ctx.line_to(ex + rs + 2, cy - 1); ctx.stroke()
        elif style == "angry":
            circle(ctx, ex, cy, rs, hexc(ink))
            ctx.set_line_width(6); ctx.set_source_rgba(*hexc(ink))
            ctx.move_to(ex - sg * (-12) , cy - rs - 12 + 8) if False else None
            ctx.move_to(ex - sg * 14, cy - rs - 4); ctx.line_to(ex + sg * 14, cy - rs - 15); ctx.stroke()

def vein(ctx, x, y, a, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*hexc('#e63946', a))
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ctx.arc(sx * 14, sy * 14, 11, 0, 2 * math.pi) if False else None
        st = {(-1, -1): math.pi, (1, -1): 1.5 * math.pi, (-1, 1): 0.5 * math.pi, (1, 1): 0.0}[(sx, sy)]
        ctx.new_path(); ctx.arc(sx * 15, sy * 15, 12, st, st + 0.5 * math.pi); ctx.stroke()
    ctx.restore()

def wren_head(ctx, cx, cy, t, eye="closed", mouth="snore", amt=0.0, glasses=False, shake=0.0):
    cx += math.sin(t * 45) * 3 * shake
    # nightgown shoulders
    e4.ell(ctx, cx, cy + 100, 118, 52, hexc('#9d8df1'))
    circle(ctx, cx - 76, cy + 4, 18, SKIN_W); circle(ctx, cx + 76, cy + 4, 18, SKIN_W)
    circle(ctx, cx, cy, 74, SKIN_W)
    for sg in (-1, 1):                                                  # side hair puffs
        circle(ctx, cx + sg * 64, cy - 28, 26, hexc('#dfe3ea')); circle(ctx, cx + sg * 70, cy - 4, 20, hexc('#dfe3ea'))
    # nightcap
    ctx.save()
    ctx.move_to(cx - 78, cy - 22); ctx.curve_to(cx - 70, cy - 120, cx + 10, cy - 150, cx + 92, cy - 96)
    ctx.curve_to(cx + 100, cy - 84, cx + 84, cy - 52, cx + 78, cy - 22); ctx.close_path()
    ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    rrect(ctx, cx - 84, cy - 40, 168, 28, 14); ctx.set_source_rgba(*hexc('#ffffff')); ctx.fill()
    circle(ctx, cx + 100, cy - 84 + 20 * math.sin(t * 2.6), 17, hexc('#ffffff'))
    ctx.restore()
    circle(ctx, cx - 44, cy + 28, 14, hexc('#f28b82', 0.55)); circle(ctx, cx + 44, cy + 28, 14, hexc('#f28b82', 0.55))
    eyes(ctx, cx, cy + 2, 29, eye, 7, skin=SKIN_W)
    if glasses:
        ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#5c4033'))
        for sg in (-1, 1): ctx.arc(cx + sg * 29, cy + 2, 23, 0, 2 * math.pi); ctx.stroke()
        ctx.move_to(cx - 6, cy); ctx.line_to(cx + 6, cy); ctx.stroke()
    my = cy + 38
    if mouth == "snore":
        a = amt * (0.5 + 0.5 * math.sin(t * 2 * math.pi / 1.15))
        ctx.save(); ctx.translate(cx, my + 4 * a); ctx.scale(11 + 12 * a, 5 + 17 * a); circle(ctx, 0, 0, 1, hexc('#7a1f2b')); ctx.restore()
        if a > 0.4: e4.ell(ctx, cx, my + 4 + 12 * a, 8 + 4 * a, 5, hexc('#ff8fa3'))
    elif mouth == "smile":
        ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#7a3e2b')); ctx.arc(cx, my - 12, 20, math.radians(25), math.radians(155)); ctx.stroke()
    elif mouth == "flat":
        ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#7a3e2b')); ctx.move_to(cx - 14, my + 4); ctx.line_to(cx + 14, my + 4); ctx.stroke()
    elif mouth == "shout":
        ry = 18 + 4 * math.sin(t * 16)
        ctx.save(); ctx.translate(cx, my + 8); ctx.scale(24, ry); circle(ctx, 0, 0, 1, hexc('#7a1f2b')); ctx.restore()
        e4.ell(ctx, cx, my + 8 + ry * 0.6, 12, 6, hexc('#ff8fa3'))

def leo_head(ctx, cx, cy, t, eye="closed", mouth="smile", amt=0.0, shake=0.0):
    cx += math.sin(t * 45) * 3 * shake
    e4.ell(ctx, cx, cy + 96, 112, 50, hexc('#ff6b6b'))
    circle(ctx, cx - 66, cy + 6, 14, SKIN_L); circle(ctx, cx + 66, cy + 6, 14, SKIN_L)
    circle(ctx, cx, cy, 64, SKIN_L)
    ctx.arc(cx, cy - 8, 68, math.pi, 2 * math.pi); ctx.close_path(); ctx.set_source_rgba(*hexc('#2a9d8f')); ctx.fill()          # beanie
    rrect(ctx, cx - 70, cy - 18, 140, 20, 10); ctx.set_source_rgba(*hexc('#1f7a70')); ctx.fill()
    circle(ctx, cx, cy - 78, 11, hexc('#ffffff'))
    circle(ctx, cx - 38, cy + 24, 11, hexc('#f28b82', 0.45)); circle(ctx, cx + 38, cy + 24, 11, hexc('#f28b82', 0.45))
    eyes(ctx, cx, cy + 6, 22, eye, 6, skin=SKIN_L)
    my = cy + 36
    if mouth == "smile":
        ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#7a3e2b')); ctx.arc(cx, my - 10, 16, math.radians(20), math.radians(160)); ctx.stroke()
    elif mouth == "flat":
        ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#7a3e2b')); ctx.move_to(cx - 12, my); ctx.line_to(cx + 12, my); ctx.stroke()
    elif mouth == "snore":
        a = amt * (0.5 + 0.5 * math.sin(t * 2 * math.pi / 0.95))
        ctx.save(); ctx.translate(cx, my + 3 * a); ctx.scale(9 + 11 * a, 5 + 15 * a); circle(ctx, 0, 0, 1, hexc('#7a1f2b')); ctx.restore()

def arm(ctx, sx, sy, hx, hy, col, skin, w=34):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(w); ctx.set_source_rgba(*hexc(col))
    ctx.move_to(sx, sy); ctx.line_to(hx, hy); ctx.stroke(); circle(ctx, hx, hy, w * 0.55, skin)

def sock(ctx, x, y, rot, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    rrect(ctx, -38, -17, 76, 34, 17); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill()
    ctx.save(); rrect(ctx, -38, -17, 76, 34, 17); ctx.clip()
    for k in (-24, -4, 16): ctx.rectangle(k, -20, 10, 40)
    ctx.set_source_rgba(*hexc('#e63946')); ctx.fill(); ctx.restore()
    ctx.restore()

def burst(ctx, x, y, a, r):
    if a <= 0: return
    ctx.save(); ctx.translate(x, y)
    for k in range(10):
        ang = k * math.pi / 5
        ctx.move_to(math.cos(ang) * r * 0.45, math.sin(ang) * r * 0.45); ctx.line_to(math.cos(ang + 0.15) * r, math.sin(ang + 0.15) * r)
        ctx.line_to(math.cos(ang - 0.15) * r, math.sin(ang - 0.15) * r); ctx.close_path()
    ctx.set_source_rgba(*hexc('#ffd60a', a)); ctx.fill(); ctx.restore()

def bubble_ml(ctx, cx, cy, lines, size, a, tail_to):
    if a <= 0: return
    mv.font(ctx, size)
    w = max(ctx.text_extents(s_).x_advance for s_ in lines) + 70; lh = size * 1.25; h = lh * len(lines) + 34
    ctx.save(); ctx.translate(0, (1 - a) * 20)
    left, top = cx - w / 2, cy - h / 2
    rrect(ctx, left, top, w, h, 36); ctx.set_source_rgba(1, 1, 1, 0.97 * a); ctx.fill()
    tx, ty = tail_to; bx = max(left + 60, min(left + w - 60, tx))
    ctx.move_to(bx - 24, top + h - 4); ctx.line_to(tx, ty); ctx.line_to(bx + 24, top + h - 4); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.97 * a); ctx.fill()
    for i, s_ in enumerate(lines):
        e = ctx.text_extents(s_); ctx.move_to(cx - e.x_advance / 2, top + 17 + lh * (i + 0.8)); ctx.set_source_rgba(*hexc('#22223b', a)); ctx.show_text(s_)
    ctx.restore()

def meter(ctx, who, db, a=1.0, t=0.0):
    if a <= 0: return
    shake = max(0.0, (db - 100) / 30.0) * 3
    ctx.save(); ctx.translate(math.sin(t * 50) * shake, 0)
    rrect(ctx, 90, 524, 900, 74, 37); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 27); ctx.move_to(122, 572); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text("%s SNORE-O-METER" % who)
    bx, bw = 470, 330
    rrect(ctx, bx, 546, bw, 28, 14); ctx.set_source_rgba(1, 1, 1, 0.16 * a); ctx.fill()
    f = clamp01((db - 30) / 100.0)
    col = '#4ade80' if f < 0.4 else ('#ffd60a' if f < 0.7 else '#ff4d5a')
    rrect(ctx, bx, 546, max(28, bw * f), 28, 14); ctx.set_source_rgba(*hexc(col, a)); ctx.fill()
    mv.font(ctx, 32); s_ = "%d dB" % db; e = ctx.text_extents(s_); ctx.move_to(960 - e.x_advance, 573); ctx.set_source_rgba(*hexc(col, a)); ctx.show_text(s_)
    ctx.restore()

# ---------------------------------------------------------------- composed scene
def scene(ctx, t, *, w_eye="closed", w_mouth="snore", w_amt=0.0, w_glasses=False, w_arm=None,
          l_eye="closed", l_mouth="smile", l_amt=0.0, l_pillow=None, l_arm=None, l_buds=False,
          shake=0.0, w_waves=0.0, w_reach=520, l_waves=0.0, w_z=0.0, l_z=0.0, sock_pos=None, extras=None):
    cabin(ctx, t, shake, glasses=not w_glasses)
    bed_back(ctx, CXW); bed_back(ctx, CXL)
    pillow(ctx, CXW, 1040);
    if l_pillow is None: pillow(ctx, CXL, 1040)
    elif l_pillow.get('mode') == 'under': pillow(ctx, CXL, 1040)
    wren_head(ctx, CXW, HY, t, w_eye, w_mouth, w_amt, w_glasses, shake * 0.4)
    leo_head(ctx, CXL, HY, t, l_eye, l_mouth, l_amt, shake * 0.5)
    if l_buds:
        for sg in (-1, 1): circle(ctx, CXL + sg * 66, HY + 12, 9, (1, 1, 1, 1))
    blanket(ctx, CXW, 'w', t, 1.0, shake * 0.6); blanket(ctx, CXL, 'l', t, 1.0, shake * 0.6)
    if w_arm: arm(ctx, CXW + 105, 1200, w_arm[0], w_arm[1], '#9d8df1', SKIN_W)
    if l_arm: arm(ctx, CXL - 105, 1200, l_arm[0], l_arm[1], '#ff6b6b', SKIN_L)
    mw = (CXW + 6, HY + 44); ml = (CXL - 6, HY + 40)
    if w_waves > 0:
        ctx.save(); ctx.rectangle(0, 700, W, 1000); ctx.clip(); waves(ctx, mw[0], mw[1], t, w_waves, 1, '#ffe08a'); ctx.restore()
    if l_waves > 0:
        ctx.save(); ctx.rectangle(0, 700, W, 1000); ctx.clip(); waves(ctx, ml[0], ml[1], t, l_waves, -1, '#9ad1ff'); ctx.restore()
    if w_z > 0: zzz(ctx, CXW + 40, HY - 70, t, w_z, '#ffffff', 1)
    if l_z > 0: zzz(ctx, CXL - 40, HY - 70, t + 0.3, l_z, '#9ad1ff', -1)
    if sock_pos: sock(ctx, *sock_pos)
    if l_pillow and l_pillow.get('mode') == 'over':
        pillow(ctx, l_pillow['x'], l_pillow['y'], l_pillow.get('rot', 0.0))
    if extras: extras(ctx)
    wm(ctx)

# ---------------------------------------------------------------- scenes
def s0(ctx, t, d):
    lvl = lerp(0.3, 0.7, t / d); awake = t > 1.5
    scene(ctx, t, w_amt=lvl, w_waves=lvl * 0.7, w_z=lvl, shake=0.15 * lvl,
          l_eye="flat" if awake else "closed", l_mouth="flat" if awake else "smile", l_z=0.0 if awake else 0.3)
    a = ease(t / 0.25); header(ctx, a, "NIGHT TRAIN, TWO BEDS", "Wren is snoring.", "Leo is NOT sleeping.", -0.3, t)
    meter(ctx, "WREN", int(lerp(42, 70, t / d)), a, t)
    ai_tag(ctx, y=1860)

def s1(ctx, t, d):
    lvl = lerp(0.65, 1.0, t / d)
    k = ramp(t, 0.0, 0.55); blown = t > 1.9
    py = lerp(1040, HY - 62, k); pr = 0.0
    pos = {'mode': 'over', 'x': CXL, 'y': py, 'rot': 0.0}
    if t < 0.55:
        pos['mode'] = 'over'
    if blown:
        u = (t - 1.9) / 0.6
        pos = {'mode': 'over', 'x': CXL + 900 * u * u + 60 * u, 'y': py - 260 * u, 'rot': 3.5 * u}
    else:
        pos['x'] = CXL + math.sin(t * 52) * 3 * lvl; pos['y'] = py + math.cos(t * 44) * 3 * lvl * (1 if t > 0.5 else 0)
    arm_t = None
    def ex(c):
        if not blown and t > 0.3:
            for sg in (-1, 1): circle(c, pos['x'] + sg * 152, pos['y'] + 60, 22, SKIN_L)
        if blown: vein(c, CXL + 90, HY - 100, ease((t - 2.1) / 0.2), 1.1)
    scene(ctx, t, w_amt=lvl, w_waves=lvl, w_z=lvl, shake=0.5 + 0.5 * lvl,
          l_eye="angry" if blown else ("closed" if t < 0.6 else "flat"), l_mouth="flat", l_pillow=pos, l_arm=arm_t, extras=ex)
    a = ease(t / 0.25); header(ctx, a, "ATTEMPT 1", "Pillow over the head", "Nope.", 2.0, t)
    meter(ctx, "WREN", int(lerp(76, 98, t / d)), a, t)
    pill(ctx, t, "Wait for the ending", 0.6); ai_tag(ctx, y=1860)

def s2(ctx, t, d):
    # sock flight
    hand0 = (CXL - 215, 1118)
    fl = clamp01((t - 0.6) / 0.55)
    hit = t >= 1.15
    wind = ramp(t, 0.0, 0.5)
    arm_t = (lerp(CXL - 110, CXL - 190, wind) if t < 0.6 else CXL - 235, lerp(1180, 1075, wind) if t < 0.6 else 1118)
    sp = None
    tx, ty = CXW + 40, HY - 50
    if t < 0.6: sp = (arm_t[0] - 6, arm_t[1] - 24, -0.5 + wind * 0.6, 1.0)
    elif not hit:
        sx = lerp(hand0[0] - 20, tx, fl); sy = lerp(1100, ty, fl) - 230 * math.sin(math.pi * fl)
        sp = (sx, sy, fl * 9.0, 1.0)
    else:
        u = t - 1.15; fy = min(ty + 330, ty + 300 * u * u * 3.0)
        sp = (tx + 20 * u, fy, 9.0 + u * 3, 1.0)
    paused = 1.15 <= t < 2.1
    lvl = 0.0 if paused else (1.0 if t >= 2.1 else lerp(0.9, 1.0, t / 1.15))
    wake = 1.2 <= t < 2.1
    def ex(c):
        burst(c, tx, ty, clamp01(1 - (t - 1.15) / 0.3) if hit else 0, 90 * (0.6 + (t - 1.15) * 2.2) if hit else 0)
        if hit: bubble_ml(c, 330, 820, ["5 more minutes..."], 38, ramp(t, 1.3, 1.5) * (1 - ramp(t, 2.0, 2.15)), (CXW, HY - 90))
        if t > 2.2: vein(c, CXL + 90, HY - 100, ease((t - 2.2) / 0.2), 1.1)
    scene(ctx, t, w_amt=lvl, w_waves=lvl, w_z=lvl if not paused else 0.0, shake=0.4 + 0.9 * lvl,
          w_eye="closed", w_mouth="smile" if paused else "snore",
          l_eye="angry" if t > 0.5 else "flat", l_mouth="flat", l_arm=arm_t if t < 1.15 else (CXL - 150, 1190), sock_pos=sp if (hit and sp[1] > 0) else sp, extras=ex)
    a = ease(t / 0.25); header(ctx, a, "ATTEMPT 2", "Throw a sock", "It got worse.", 2.1, t)
    meter(ctx, "WREN", 122 if t >= 2.1 else (35 if paused else int(lerp(98, 108, t / 1.15))), a, t)
    ai_tag(ctx, y=1860)

def s3(ctx, t, d):
    buds = t > 0.35
    l_closed = t > 0.9
    l_snore = ramp(t, 1.6, 3.0)
    w_lvl = 1.0 - ramp(t, 1.9, 2.5)
    w_open = t > 2.9
    reach = 520 if t < 0.35 else 250
    def ex(c):
        if buds:
            for k in range(3):
                ph = ((t * 0.9 + k / 3) % 1); al = (1 - ph) * min(1, (t - 0.35) * 4)
                nx, ny = CXL - 150 + 20 * math.sin(ph * 7), 1040 - ph * 170
                e4.ell(c, nx, ny, 13, 9, hexc('#ffd166', al)); c.set_line_width(5); c.set_source_rgba(*hexc('#ffd166', al))
                c.move_to(nx + 11, ny); c.line_to(nx + 11, ny - 38); c.line_to(nx + 28, ny - 28); c.stroke()
        if w_open: vein(c, CXW - 90, HY - 100, ease((t - 2.9) / 0.2), 1.1)
    scene(ctx, t, w_amt=w_lvl, w_waves=w_lvl * 0.9, w_reach=reach, w_z=w_lvl * (0.5 if buds else 1.0), shake=0.5 * w_lvl + 0.8 * l_snore,
          w_eye="flat" if w_open else "closed", w_mouth="flat" if w_open else "snore",
          l_eye="closed" if l_closed else "flat", l_mouth="snore" if t > 1.6 else ("smile" if l_closed else "flat"),
          l_amt=l_snore, l_waves=l_snore * 0.9 if t > 1.6 else 0, l_z=0.0 if t < 1.2 else max(0.25, l_snore), l_buds=buds, extras=ex)
    a = ease(t / 0.25); header(ctx, a, "ATTEMPT 3", "Earbuds", "Finally. Sleep.", 1.2, t)
    if t < 2.0: meter(ctx, "WREN", int(lerp(122, 120, t / 2.0)) if t < 1.9 else int(lerp(120, 50, ramp(t, 1.9, 2.5))), a, t)
    else: meter(ctx, "LEO", int(lerp(50, 112, ramp(t, 2.0, 3.0))), 1.0, t)
    ai_tag(ctx, y=1860)

def s4(ctx, t, d):
    shake_arm = math.sin(t * 22) * 8 * ramp(t, 0.5, 0.8)
    ar = (CXW + 250 + 60 * ramp(t, 0.4, 0.8), 1090 + shake_arm)
    def ex(c):
        bubble_ml(c, 395, 830, ["LEO! Some of us are", "trying to sleep!"], 40, ramp(t, 0.55, 0.75), (CXW + 20, HY - 92))
        vein(c, CXW - 90, HY - 100, 1.0, 1.1)
    scene(ctx, t, w_eye="wide" if t < 0.6 else "angry", w_mouth="shout" if t > 0.55 else "flat", w_glasses=True, w_arm=ar if t > 0.4 else None,
          shake=0.7, l_eye="closed", l_mouth="snore", l_amt=0.95, l_waves=0.95, l_z=0.95, extras=ex)
    a = ease(t / 0.25); header(ctx, a, "PLOT TWIST", "Leo snores too.", None, 0, t, main_size=62)
    meter(ctx, "LEO", 118, a, t); ai_tag(ctx, y=1860)

def s5(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    mv.wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    a = ease(t / 0.3)
    ctext(ctx, "Wren: \u201cI don\u2019t snore.\u201d", 205 - (1 - a) * 20, 62, hexc('#22223b', a), maxw=900)
    ctext(ctx, "The whole train: \u201cOkay.\u201d", 290, 62, hexc(RED, ease((t - 0.5) / 0.3)), maxw=900)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Send this to your family snorer", 625, 40, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False)
    ai_tag(ctx, y=1890, dark=True)

SCENES = [(s0, 2.4), (s1, 3.0), (s2, 3.0), (s3, 3.4), (s4, 3.4), (s5, 2.6)]

def frame(fn, t, d):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    fn(ctx, t, d)
    a_in = 0 if fn is s0 else 1 - t / 0.1
    a_out = (t - (d - 0.5)) / 0.5 if fn is s5 else (t - (d - 0.1)) / 0.1
    a = max(a_in, a_out, 0)
    if a > 0:
        ctx.set_source_rgba(*hexc('#1b1840', min(1, ease(a)))); ctx.paint()
    return surf

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        from PIL import Image
        picks = [(s0, 0.9), (s0, 2.0), (s1, 1.2), (s1, 2.4), (s2, 0.85), (s2, 1.4), (s2, 2.5), (s3, 0.8), (s3, 2.6), (s3, 3.2), (s4, 0.3), (s5, 2.2)]
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

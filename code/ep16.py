import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = "/home/claude/wren/ep16"
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))
GY = 1720
GLASS_Y0, GLASS_Y1 = 640, 1780

# ------------------------------------------------------------ platform (seen from the track side)
def platform(ctx, t, glow=0.0):
    g = cairo.LinearGradient(0, 0, 0, 1300); g.add_color_stop_rgb(0, *hexc('#e9eef3')[:3]); g.add_color_stop_rgb(1, *hexc('#cfd8e1')[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1300); ctx.fill()
    for k in range(5):                                                      # ceiling lights
        rrect(ctx, 40 + k * 220, 30, 150, 20, 10); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
        gl = cairo.RadialGradient(115 + k * 220, 50, 4, 115 + k * 220, 50, 150); gl.add_color_stop_rgba(0, 1, 1, 0.9, 0.5); gl.add_color_stop_rgba(1, 1, 1, 0.9, 0)
        ctx.set_source(gl); ctx.rectangle(k * 220 - 40, 0, 300, 220); ctx.fill()
    # back wall with tile lines and ad panels
    for xx in range(0, W, 120): ctx.rectangle(xx, 560, 3, 760); ctx.set_source_rgba(0, 0, 0, 0.05); ctx.fill()
    ctx.rectangle(0, 1300, W, 40); ctx.set_source_rgba(*hexc('#9aa5b1')); ctx.fill()
    # floor
    ctx.rectangle(0, 1340, W, H - 1340); ctx.set_source_rgba(*hexc('#b9c2cc')); ctx.fill()
    for k in range(-6, 8):
        ctx.move_to(540 + k * 70, 1340); ctx.line_to(540 + k * 300, H); ctx.set_line_width(3); ctx.set_source_rgba(1, 1, 1, 0.3); ctx.stroke()
    for yy in (1400, 1480, 1580, 1700, 1850): ctx.rectangle(0, yy, W, 3); ctx.set_source_rgba(1, 1, 1, 0.3); ctx.fill()
    ctx.rectangle(0, 1752, W, 30); ctx.set_source_rgba(*hexc('#ffd60a')); ctx.fill()                          # tactile line
    for xx in range(10, W, 36): circle(ctx, xx, 1767, 4, hexc('#c9a800'))
    # other passengers (tiny, background)
    for px, col in ((120, '#e76f51'), (930, '#4361ee')):
        circle(ctx, px, 1235, 22, hexc('#d9a27a')); rrect(ctx, px - 28, 1257, 56, 78, 22); ctx.set_source_rgba(*hexc(col)); ctx.fill()
    if glow > 0:
        gl = cairo.LinearGradient(0, 0, W, 0); gl.add_color_stop_rgba(0, 1, 1, 0.8, 0.55 * glow * (0.6 + 0.4 * math.sin(t * 30))); gl.add_color_stop_rgba(1, 1, 1, 0.8, 0)
        ctx.set_source(gl); ctx.rectangle(0, 0, W, H); ctx.fill()

# ------------------------------------------------------------ glass doors (foreground)
def doors(ctx, t, open_k=0.0, ripple=None, smudge=0.0):
    pw = 520
    for side in (-1, 1):
        x0 = 20 + (0 if side == -1 else pw + 20) + (-side) * 0 + side * open_k * 440
        ctx.save()
        rrect(ctx, x0, GLASS_Y0, pw, GLASS_Y1 - GLASS_Y0, 8); ctx.set_source_rgba(0.75, 0.9, 1.0, 0.16); ctx.fill()
        ctx.save(); rrect(ctx, x0, GLASS_Y0, pw, GLASS_Y1 - GLASS_Y0, 8); ctx.clip()
        for k in range(4):
            xs = x0 + 80 + k * 150 + 60 * math.sin(t * 0.6 + k); ctx.move_to(xs, GLASS_Y0); ctx.line_to(xs + 70, GLASS_Y0); ctx.line_to(xs - 120, GLASS_Y1); ctx.line_to(xs - 190, GLASS_Y1)
            ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.10); ctx.fill()
        ctx.restore()
        ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#aeb8c4')); rrect(ctx, x0, GLASS_Y0, pw, GLASS_Y1 - GLASS_Y0, 8); ctx.stroke()
        ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#6f7c8c')); rrect(ctx, x0 + 7, GLASS_Y0 + 7, pw - 14, GLASS_Y1 - GLASS_Y0 - 14, 4); ctx.stroke()
        ctx.rectangle(x0 + 6, 1140, pw - 12, 40); ctx.set_source_rgba(1, 0.84, 0.04, 0.9); ctx.fill()           # safety band
        ctx.restore()
    # lintel + sign
    rrect(ctx, 0, 520, W, 120, 0); ctx.set_source_rgba(*hexc('#2b3a55')); ctx.fill()
    rrect(ctx, 30, 540, 320, 80, 12); ctx.set_source_rgba(*hexc('#10162b')); ctx.fill()
    mv.font(ctx, 38); ctx.move_to(54, 590); ctx.set_source_rgba(*hexc('#ffd166')); ctx.show_text("METRO  PLATFORM 1")
    # stand-behind sticker
    rrect(ctx, 130, 1000, 130, 130, 20); ctx.set_source_rgba(*hexc('#ffd60a', 0.0)); ctx.fill()
    if ripple:
        rx, ry, k = ripple
        for j in range(3):
            kk = clamp01(k - j * 0.18)
            if 0 < kk < 1:
                ctx.set_line_width(8 * (1 - kk)); ctx.set_source_rgba(1, 1, 1, 0.9 * (1 - kk)); ctx.arc(rx, ry, 30 + kk * 260, 0, 6.3); ctx.stroke()
        for j in range(8):
            ang = j * math.pi / 4 + 0.3; kk = clamp01(k * 1.3)
            ctx.set_line_width(7); ctx.set_source_rgba(1, 1, 1, 0.9 * (1 - kk)); ctx.move_to(rx + math.cos(ang) * 40, ry + math.sin(ang) * 40); ctx.line_to(rx + math.cos(ang) * (60 + 140 * kk), ry + math.sin(ang) * (60 + 140 * kk)); ctx.stroke()
    if smudge > 0:
        ctx.save(); ctx.translate(smudge * 0 + 330, 1115); e4.ell(ctx, 0, 0, 56, 38, (1, 1, 1, 0.22 * smudge)); ctx.restore()

# ------------------------------------------------------------ actors
def stars(ctx, x, y, t, a=1.0):
    for k in range(4):
        ang = t * 7 + k * math.pi / 2
        sx, sy = x + math.cos(ang) * 85, y + math.sin(ang) * 26
        ctx.save(); ctx.translate(sx, sy); ctx.rotate(t * 4 + k)
        for j in range(5):
            aa = j * 2 * math.pi / 5 - math.pi / 2; ctx.line_to(math.cos(aa) * 20, math.sin(aa) * 20); a2 = aa + math.pi / 5; ctx.line_to(math.cos(a2) * 8, math.sin(a2) * 8)
        ctx.close_path(); ctx.set_source_rgba(*hexc('#ffd60a', a)); ctx.fill(); ctx.restore()

def bump(ctx, x, s, k, plaster=False):
    if k <= 0: return
    bx, by = x + 40 * s, GY - 655 * s
    circle(ctx, bx, by, 26 * s * k, hexc('#f4a09a')); circle(ctx, bx - 5 * s, by - 6 * s, 9 * s * k, (1, 1, 1, 0.35))
    if plaster:
        ctx.save(); ctx.translate(bx, by); ctx.rotate(-0.5); rrect(ctx, -44 * s, -14 * s, 88 * s, 28 * s, 10 * s); ctx.set_source_rgba(*hexc('#f2d1b0')); ctx.fill()
        ctx.set_line_width(2); ctx.set_source_rgba(0.7, 0.5, 0.4, 0.6); ctx.rectangle(-14 * s, -9 * s, 28 * s, 18 * s); ctx.stroke(); ctx.restore()

def actor_w(ctx, x, s, t, mode="wave", expr="happy", tilt=0.0, sx=1.0, sy=1.0, hand=(110, -110), flush=0.0):
    ctx.save(); ctx.translate(x, GY); ctx.rotate(tilt); ctx.scale(sx, sy); ctx.translate(-x, -GY)
    wren(ctx, x, GY, s, t, mode, flush=flush, expr=expr, hand=hand)
    ctx.restore()

def tally(ctx, doors_n, wren_n, a=1.0):
    rrect(ctx, 400, 664, 600, 56, 28); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 22); ctx.move_to(422, 702); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text("HEAD VS DOOR")
    mv.font(ctx, 26); s1 = "DOORS: %d" % doors_n; ctx.move_to(660, 702); ctx.set_source_rgba(*hexc('#9ad1ff', a)); ctx.show_text(s1)
    s2 = "WREN: %d" % wren_n; e = ctx.text_extents(s2); ctx.move_to(980 - e.x_advance, 702); ctx.set_source_rgba(*hexc('#ffd166', a)); ctx.show_text(s2)

def bonk_text(ctx, t, t0, x, y):
    k = ease((t - t0) / 0.1)
    if k <= 0 or t - t0 > 0.9: return
    sc = 1 + 0.6 * max(0.0, 1 - (t - t0) / 0.15)
    ctx.save(); ctx.translate(x, y); ctx.rotate(-0.15); ctx.scale(sc, sc); mv.font(ctx, 130)
    e = ctx.text_extents("BONK!"); ctx.move_to(-e.x_advance / 2 + 6, 6); ctx.set_source_rgba(0.1, 0.1, 0.2, 1 - (t - t0) / 0.9); ctx.show_text("BONK!")
    ctx.move_to(-e.x_advance / 2, 0); ctx.set_source_rgba(*hexc('#ffd60a', 1 - (t - t0) / 0.9)); ctx.show_text("BONK!"); ctx.restore()

LEO = (820, 0.95)
# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    platform(ctx, t)
    walk = ramp(t, 0.0, 1.8)
    ws = lerp(0.62, 1.0, walk); wx = lerp(330, 340, walk)
    hit = t - 1.85
    tilt = 0.0; sx = sy = 1.0
    if 0 <= hit < 0.5:
        k = math.sin(min(1, hit / 0.5) * math.pi); tilt = -0.2 * k; sx = 1 + 0.06 * k; sy = 1 - 0.05 * k
    elif hit >= 0.5: tilt = -0.04
    actor_w(ctx, wx, ws, t, "wave", "ouch" if hit >= 0 else "happy", tilt, sx, sy, hand=(110, -140))
    kid(ctx, LEO[0], GY, LEO[1], t, "flat", (0, -150))
    if hit >= 0:
        bump(ctx, wx, ws, ramp(t, 1.9, 2.4)); stars(ctx, wx + 10, GY - 760 * ws, t, clamp01((hit) / 0.2) * (1 - ramp(t, 3.0, 3.4)))
    doors(ctx, t, 0.0, ripple=(wx + 30, GY - 650 * ws, hit / 0.7) if 0 <= hit < 0.7 else None)
    bonk_text(ctx, t, 1.85, 540, 900)
    header(ctx, ease(t / 0.2 + 1), "WREN TAKES THE METRO", "She walks into the door.", "Glass. Closed. Hard.", -0.3, t, main_size=54)
    tally(ctx, 1 if hit > 0 else 0, 0); wm(ctx)

def s1(ctx, t, d):
    platform(ctx, t)
    wx, ws = 340, 1.0
    actor_w(ctx, wx, ws, t, "wave" if t > 2.8 else "wave", "ouch" if t < 2.6 else "shock", -0.03 + 0.03 * math.sin(t * 2), hand=(110, -140))
    kid(ctx, LEO[0], GY, LEO[1], t, "flat" if t < 1.6 else "smug", (0, -150))
    bump(ctx, wx, ws, 1.0 + 0.15 * math.sin(t * 6)); stars(ctx, wx + 10, GY - 760 * ws, t, 1 - ramp(t, 0.4, 1.0))
    doors(ctx, t)
    bubble_ml(ctx, 700, 930, ["Grandma. They're doors."], 42, ramp(t, 0.7, 0.9) * (1 - ramp(t, 2.0, 2.2)), (LEO[0] - 20, GY - 340))
    bubble_ml(ctx, 700, 930, ["They open when", "the train arrives."], 42, ramp(t, 2.2, 2.4), (LEO[0] - 20, GY - 340))
    bubble_ml(ctx, 330, 1020, ["Rude."], 50, ramp(t, 1.2, 1.4) * (1 - ramp(t, 2.1, 2.3)), (wx, GY - 760))
    header(ctx, ease(t / 0.2), "LEO EXPLAINS", "Doors open for trains.", "Not for heads.", 1.6, t, main_size=54)
    tally(ctx, 1, 0); wm(ctx)

def s2(ctx, t, d):
    platform(ctx, t)
    walk = ramp(t, 0.5, 1.9); wx = 340; ws = lerp(0.82, 1.0, walk)
    hit = t - 2.0
    tilt = 0.0; sx = sy = 1.0
    if 0 <= hit < 0.5:
        k = math.sin(min(1, hit / 0.5) * math.pi); tilt = 0.2 * k; sx = 1 + 0.06 * k; sy = 1 - 0.05 * k
    elif hit >= 0.5: tilt = 0.04
    actor_w(ctx, wx, ws, t, "point" if t < 1.9 else "wave", "ouch" if hit >= 0 else "happy", tilt, sx, sy, hand=(120, -190) if t < 1.9 else (110, -140))
    kid(ctx, LEO[0], GY, LEO[1], t, "flat" if hit < 0 else "shock", (0, -150))
    bump(ctx, wx - 30, ws, 1.0, plaster=True)
    if hit >= 0 and hit < 1.6: bump(ctx, wx + 30, ws, ramp(t, 2.1, 2.5))
    if hit >= 0: stars(ctx, wx + 10, GY - 760 * ws, t, clamp01(hit / 0.2) * (1 - ramp(t, 3.2, 3.8)))
    doors(ctx, t, 0.0, ripple=(wx + 10, GY - 650 * ws, hit / 0.7) if 0 <= hit < 0.7 else None)
    bonk_text(ctx, t, 2.0, 540, 900)
    bubble_ml(ctx, 360, 1000, ["Just checking."], 46, ramp(t, 0.5, 0.7) * (1 - ramp(t, 1.8, 2.0)), (wx, GY - 760))
    bubble_ml(ctx, 700, 930, ["That's the other", "door, Grandma."], 42, ramp(t, 3.0, 3.2), (LEO[0] - 20, GY - 340))
    header(ctx, ease(t / 0.2), "ROUND TWO", "She tests it. Politely.", "It's still a door.", 1.3, t, main_size=54)
    tally(ctx, 2 if hit > 0 else 1, 0); wm(ctx)

# ------------------------------------------------------------ platform-side view with a train
def station_front(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, 1300); g.add_color_stop_rgb(0, *hexc('#e9eef3')[:3]); g.add_color_stop_rgb(1, *hexc('#cfd8e1')[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 700); ctx.fill()
    for k in range(5):
        rrect(ctx, 40 + k * 220, 30, 150, 20, 10); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    ctx.rectangle(0, 700, W, 1000); ctx.set_source_rgba(*hexc('#14192b')); ctx.fill()          # tunnel behind the glass
    ctx.rectangle(0, 1700, W, H - 1700); ctx.set_source_rgba(*hexc('#b9c2cc')); ctx.fill()
    for yy in (1790, 1860): ctx.rectangle(0, yy, W, 3); ctx.set_source_rgba(1, 1, 1, 0.3); ctx.fill()
    ctx.rectangle(0, 1700, W, 24); ctx.set_source_rgba(*hexc('#ffd60a')); ctx.fill()

def train(ctx, xf, door_open, lights=1.0):
    top, bot = 760, 1660
    body_w = 5200
    rrect(ctx, xf, top, body_w, bot - top, 40); ctx.set_source_rgba(*hexc('#e8edf2')); ctx.fill()
    ctx.rectangle(xf + 30, 1380, body_w - 60, 70); ctx.set_source_rgba(*hexc('#2a6fdb')); ctx.fill()
    ctx.rectangle(xf + 30, 1452, body_w - 60, 14); ctx.set_source_rgba(*hexc('#ffd166')); ctx.fill()
    # nose / cab at the left
    ctx.save(); ctx.translate(xf, 0)
    rrect(ctx, -70, top + 40, 170, bot - top - 40, 60); ctx.set_source_rgba(*hexc('#d5dde6')); ctx.fill()
    rrect(ctx, -30, top + 130, 100, 140, 20); ctx.set_source_rgba(*hexc('#243b5a')); ctx.fill()
    circle(ctx, -24, 1500, 26, hexc('#fff7c2')); circle(ctx, -24, 1500, 60, hexc('#fff7c2', 0.25 * lights))
    ctx.restore()
    # windows and doors
    for k in range(0, 5):
        dc = xf + 400 + 1100 * k
        for wx in (dc - 520, dc + 280):                                   # windows between doors
            rrect(ctx, wx, 880, 240, 190, 20); ctx.set_source_rgba(*hexc('#2b3a55')); ctx.fill()
            rrect(ctx, wx + 8, 888, 224, 174, 14); ctx.set_source_rgba(*hexc('#ffd98a', 0.55)); ctx.fill()
        # door opening
        ow = 400
        rrect(ctx, dc - ow / 2, 800, ow, 800, 8); ctx.set_source_rgba(*hexc('#fff0c2')); ctx.fill()            # lit interior
        ctx.save(); rrect(ctx, dc - ow / 2, 800, ow, 800, 8); ctx.clip()
        ctx.rectangle(dc - ow / 2, 1100, ow, 500); ctx.set_source_rgba(*hexc('#f6d98f')); ctx.fill()
        ctx.rectangle(dc - ow / 2, 1450, ow, 150); ctx.set_source_rgba(*hexc('#8b94a3')); ctx.fill()
        ctx.rectangle(dc - 6, 800, 12, 800); ctx.set_source_rgba(*hexc('#c8ced8')); ctx.fill()                  # pole
        for sx in (dc - 150, dc + 150): circle(ctx, sx, 900, 26, hexc('#2a6fdb')); ctx.rectangle(sx - 3, 820, 6, 80); ctx.set_source_rgba(*hexc('#c8ced8')); ctx.fill()
        ctx.restore()
        for sd in (-1, 1):                                                  # sliding leaves
            lw = ow / 2; x0 = dc + (-lw if sd < 0 else 0) + sd * door_open * (lw - 10)
            ctx.save(); rrect(ctx, dc - ow / 2, 800, ow, 800, 8); ctx.clip()
            ctx.rectangle(x0, 800, lw, 800); ctx.set_source_rgba(*hexc('#dfe6ee')); ctx.fill()
            rrect(ctx, x0 + 24, 850, lw - 48, 330, 10); ctx.set_source_rgba(*hexc('#243b5a', 0.9)); ctx.fill()
            ctx.rectangle(x0, 800, lw, 800); ctx.set_line_width(5); ctx.set_source_rgba(*hexc('#9aa5b1')); ctx.stroke(); ctx.restore()

def screen_doors_front(ctx, t, open_k):
    ow = 400
    for sd in (-1, 1):                                                       # sliding leaves at the centre
        lw = ow / 2; x0 = 540 + (-lw if sd < 0 else 0) + sd * open_k * (lw - 10)
        ctx.save(); rrect(ctx, x0, 690, lw, 1030, 6); ctx.set_source_rgba(0.75, 0.9, 1.0, 0.16); ctx.fill()
        ctx.set_line_width(12); ctx.set_source_rgba(*hexc('#aeb8c4')); rrect(ctx, x0, 690, lw, 1030, 6); ctx.stroke(); ctx.restore()
    for x0, x1 in ((-30, 340), (740, 1110)):                                 # fixed panels
        rrect(ctx, x0, 690, x1 - x0, 1030, 6); ctx.set_source_rgba(0.75, 0.9, 1.0, 0.14); ctx.fill()
        ctx.set_line_width(12); ctx.set_source_rgba(*hexc('#aeb8c4')); rrect(ctx, x0, 690, x1 - x0, 1030, 6); ctx.stroke()
        ctx.save(); rrect(ctx, x0, 690, x1 - x0, 1030, 6); ctx.clip()
        for k in range(3):
            xs = x0 + 60 + k * 130; ctx.move_to(xs, 690); ctx.line_to(xs + 60, 690); ctx.line_to(xs - 100, 1720); ctx.line_to(xs - 160, 1720); ctx.close_path(); ctx.set_source_rgba(1, 1, 1, 0.09); ctx.fill()
        ctx.restore()
    for xx in (340, 740, 140 if False else 340): pass
    ctx.rectangle(0, 1160, W, 36); ctx.set_source_rgba(1, 0.84, 0.04, 0.85); ctx.fill()
    ctx.rectangle(0, 520, W, 170); ctx.set_source_rgba(*hexc('#2b3a55')); ctx.fill()
    rrect(ctx, 30, 548, 340, 86, 12); ctx.set_source_rgba(*hexc('#10162b')); ctx.fill()
    mv.font(ctx, 38); ctx.move_to(54, 604); ctx.set_source_rgba(*hexc('#ffd166')); ctx.show_text("METRO  PLATFORM 1")
    rrect(ctx, 640, 548, 340, 86, 12); ctx.set_source_rgba(*hexc('#10162b')); ctx.fill()
    mv.font(ctx, 34); ctx.move_to(664, 604); ctx.set_source_rgba(*hexc('#4ade80' if t % 1.2 < 0.6 else '#2f8f4e')); ctx.show_text("TRAIN ARRIVING")

STOP_XF = 140
def s3(ctx, t, d):
    k = ramp(t, 0.0, 2.4)
    xf = lerp(STOP_XF + 2700, STOP_XF, k)
    trem = math.sin(t * 55) * 3 * (1 - k)
    ctx.save(); ctx.translate(0, trem)
    station_front(ctx, t)
    train(ctx, xf, ramp(t, 2.7, 3.4))
    ctx.restore()
    actor_w(ctx, 330, 0.95, t, "cheer" if t > 2.9 else "wave", "happy", hand=(110, -140))
    kid(ctx, 790, GY, 0.9, t, "smug" if t > 2.9 else "flat", (0, -150))
    bump(ctx, 300, 0.95, 1.0, plaster=True)
    screen_doors_front(ctx, t, ramp(t, 3.0, 3.7))
    bubble_ml(ctx, 540, 1010, ["Ding dong!"], 54, ramp(t, 2.6, 2.75) * (1 - ramp(t, 3.7, 3.9)), (540, 1260))
    header(ctx, ease(t / 0.2), "THE TRAIN ARRIVES", "It stops. Doors line up.", "Both doors open. Magic.", 2.4, t, main_size=54)
    tally(ctx, 2, 0); wm(ctx)

def s4(ctx, t, d):
    station_front(ctx, t)
    train(ctx, STOP_XF, 1.0 - ramp(t, 3.8, 4.3))
    walk = ramp(t, 0.4, 2.6)
    # Wren, then Leo, walk to the open door and step aboard (they shrink and climb as they go away)
    wxp = lerp(330, 500, walk); ws = lerp(0.95, 0.62, walk); wgy = lerp(GY, 1560, walk)
    lxp = lerp(790, 590, walk); ls = lerp(0.9, 0.58, walk); lgy = lerp(GY, 1560, walk)
    ctx.save()
    actor_w_pos(ctx, wxp, wgy, ws, t, "wave", "happy" if walk < 1 else "happy")
    kid(ctx, lxp, lgy, ls, t, "smug", (0, -150))
    ctx.restore()
    screen_doors_front(ctx, t, 1.0 - ramp(t, 3.9, 4.4))
    bubble_ml(ctx, 540, 1040, ["I knew that."], 50, ramp(t, 2.8, 3.0) * (1 - ramp(t, 4.0, 4.2)), (wxp, wgy - 560 * ws))
    header(ctx, ease(t / 0.2), "ALL ABOARD", "They walk right in.", "No bonks this time.", 1.0, t, main_size=54)
    tally(ctx, 2, 0); wm(ctx)

def actor_w_pos(ctx, x, gy, s, t, mode, expr):
    wren(ctx, x, gy, s, t, mode, expr=expr, hand=(110, -140))

def s5(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    bump(ctx, 540, 1.0, 1.0, plaster=True) if False else None
    a = ease(t / 0.3)
    ctext(ctx, "Doors: 2. Wren: 0.", 205 - (1 - a) * 20, 62, hexc('#22223b', a), maxw=940)
    ctext(ctx, "Wren: “They started it.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Send this to someone who walks into glass", 625, 36, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

SCENES = [(s0, 3.6), (s1, 3.8), (s2, 4.4), (s3, 4.4), (s4, 4.6), (s5, 3.2)]

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
        picks = [(s0, 0.6), (s0, 1.95), (s0, 2.8), (s1, 1.0), (s1, 2.8), (s2, 1.2), (s2, 2.2), (s2, 3.6), (s3, 1.0), (s3, 2.0), (s3, 3.6), (s4, 1.2), (s4, 2.6), (s4, 4.0), (s5, 2.0)]
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

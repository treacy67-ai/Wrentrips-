"""ep32 - Hotel bathroom: one shower dial, zero instructions. Leo gets 4°C, then cranks it to 71°C, then pulls the other knob and the hose goes rogue. Wren sets the dial to the middle, sips her tea and waits 30 seconds: 38°C, perfect."""
import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ease, wren
import ep4 as e4
from ep5 import kid
from ep7 import wm, header
from ep9 import bubble_ml, burst

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "ep32"))
os.makedirs(OUT, exist_ok=True)
RED = '#e63946'; BLUE = '#4cc9f0'; GREEN = '#2ecc71'
def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, k): return a + (b - a) * k
def ramp(t, a, b): return ease(clamp01((t - a) / (b - a)))

GY = 1700
LX, LS = 400, 1.1                     # Leo, inside the shower
WX, WS = 880, 0.95                    # Wren, outside the glass
DX, DY = 650, 1300                    # temperature dial
KX, KY = 650, 1420                    # the "other knob"
HX, HY = 400, 742                     # shower head
SH_L, SH_R = 140, 740                 # shower cubicle

def meter(ctx, label, val, a=1.0, col='#ffd166'):
    rrect(ctx, 90, 524, 900, 60, 30); ctx.set_source_rgba(*hexc('#10132b', 0.92 * a)); ctx.fill()
    mv.font(ctx, 26); ctx.move_to(122, 564); ctx.set_source_rgba(1, 1, 1, a); ctx.show_text(label)
    mv.font(ctx, 34); e = ctx.text_extents(val); ctx.move_to(960 - e.x_advance, 566); ctx.set_source_rgba(*hexc(col, a)); ctx.show_text(val)

def txt(ctx, s, x, y, size, col, center=True, bold=True):
    mv.font(ctx, size, bold); e = ctx.text_extents(s); ctx.move_to(x - (e.x_advance / 2 if center else 0), y); ctx.set_source_rgba(*col); ctx.show_text(s)

def temp_col(c):
    return BLUE if c < 20 else ('#ff6b35' if c > 45 else GREEN)

# ------------------------------------------------------------ props
def duck(ctx, x, y, s=1.0, ang=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    e4.ell(ctx, 0, 0, 52, 34, hexc('#ffd60a'))
    circle(ctx, 30, -40, 28, hexc('#ffd60a'))
    e4.ell(ctx, 60, -36, 18, 9, hexc('#ff8c42'))
    circle(ctx, 36, -48, 5, hexc('#22223b'))
    e4.ell(ctx, -10, -4, 24, 14, hexc('#f4c20d'), -0.3)
    ctx.restore()

def teacup(ctx, x, y):
    rrect(ctx, x - 26, y - 44, 52, 44, 10); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill(); e4.ell(ctx, x, y + 2, 42, 8, (1, 1, 1, 1))
    ctx.set_line_width(6); ctx.set_source_rgba(1, 1, 1, 1); ctx.arc(x + 30, y - 24, 12, -1.4, 1.4); ctx.stroke()

def dial(ctx, ang, glow=0.0):
    """ang: -1 = full cold, 0 = middle, +1 = full hot"""
    circle(ctx, DX, DY, 62, hexc('#b8c0c8'))
    ctx.set_line_width(14)
    ctx.set_source_rgba(*hexc(BLUE)); ctx.arc(DX, DY, 46, math.radians(150), math.radians(250)); ctx.stroke()
    ctx.set_source_rgba(*hexc(RED)); ctx.arc(DX, DY, 46, math.radians(290), math.radians(390)); ctx.stroke()
    if glow > 0:
        ctx.set_source_rgba(*hexc(GREEN, glow)); ctx.arc(DX, DY, 46, math.radians(255), math.radians(285)); ctx.stroke()
    circle(ctx, DX, DY, 34, hexc('#e9ecef'))
    a = math.radians(-90 + 115 * ang)
    ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#22223b'))
    ctx.move_to(DX, DY); ctx.line_to(DX + math.cos(a) * 40, DY + math.sin(a) * 40); ctx.stroke()

def knob(ctx, pulled=0.0):
    circle(ctx, KX, KY, 30, hexc('#b8c0c8'))
    rrect(ctx, KX - 12, KY - 12 - 0, 24, 24 + 40 * pulled, 10); ctx.set_source_rgba(*hexc('#6c757d')); ctx.fill()
    circle(ctx, KX, KY + 40 * pulled, 16, hexc('#495057'))

def spray(ctx, x0, y0, ang, spread, length, t, col, a=1.0, n=26, seed=3):
    """droplet streaks fanning from (x0, y0) along direction ang (radians)"""
    if a <= 0: return
    r = random.Random(seed)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        da = (r.random() - 0.5) * spread; sp = 0.6 + 0.8 * r.random(); ph = (t * 2.2 * sp + r.random()) % 1
        d0 = ph * length; d1 = d0 + 40
        ca, sa = math.cos(ang + da), math.sin(ang + da)
        ctx.set_line_width(6 + 3 * r.random()); ctx.set_source_rgba(*hexc(col, a * (0.9 - 0.4 * ph)))
        ctx.move_to(x0 + ca * d0, y0 + sa * d0); ctx.line_to(x0 + ca * d1, y0 + sa * d1); ctx.stroke()

def steam(ctx, t, a, x0=SH_L + 20, x1=SH_R - 20, top=640, bot=1600, n=16, seed=7):
    if a <= 0: return
    r = random.Random(seed)
    for i in range(n):
        x = lerp(x0, x1, r.random()); sp = 0.25 + 0.3 * r.random(); ph = (t * sp + r.random()) % 1
        y = lerp(bot, top, ph); rad = 60 + 70 * r.random()
        circle(ctx, x + 30 * math.sin(t * 1.5 + i), y, rad, (1, 1, 1, a * 0.45 * math.sin(math.pi * ph)))

# ------------------------------------------------------------ room
def bathroom(ctx, t, dial_ang=-1.0, knob_p=0.0, dial_glow=0.0, head_on=True):
    mv.vgrad(ctx, '#e6f3f1', '#cfe8e4')
    # wall tiles outside shower
    ctx.set_line_width(3); ctx.set_source_rgba(1, 1, 1, 0.7)
    for y in range(600, 1600, 90): ctx.move_to(0, y); ctx.line_to(W, y); ctx.stroke()
    for x in range(0, W, 90): ctx.move_to(x, 600); ctx.line_to(x, 1580); ctx.stroke()
    # towel rail + towel on the right
    rrect(ctx, 800, 690, 220, 14, 7); ctx.set_source_rgba(*hexc('#adb5bd')); ctx.fill()
    rrect(ctx, 830, 700, 160, 250, 18); ctx.set_source_rgba(*hexc('#ffffff')); ctx.fill()
    for k in range(3): ctx.rectangle(830, 880 + k * 18, 160, 8); ctx.set_source_rgba(*hexc('#90e0ef')); ctx.fill()
    # shower cubicle: darker teal tiles
    ctx.rectangle(SH_L, 600, SH_R - SH_L, 1000); ctx.set_source_rgba(*hexc('#8fd3ca')); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.55)
    for y in range(600, 1600, 75): ctx.move_to(SH_L, y); ctx.line_to(SH_R, y); ctx.stroke()
    for x in range(SH_L, SH_R, 75): ctx.move_to(x, 600); ctx.line_to(x, 1600); ctx.stroke()
    # little shelf with duck + bottles
    rrect(ctx, 170, 1110, 150, 14, 6); ctx.set_source_rgba(*hexc('#f8f9fa')); ctx.fill()
    duck(ctx, 220, 1080, 0.6)
    for k, c in enumerate(('#e85d75', '#7b2cbf')): rrect(ctx, 270 + k * 26, 1040, 20, 70, 6); ctx.set_source_rgba(*hexc(c)); ctx.fill()
    # floor
    ctx.rectangle(0, 1580, W, H - 1580); ctx.set_source_rgba(*hexc('#e9ecef')); ctx.fill()
    for x in range(-40, W, 120): ctx.rectangle(x, 1580, 4, H - 1580); ctx.set_source_rgba(*hexc('#ced4da')); ctx.fill()
    ctx.rectangle(SH_L, 1580, SH_R - SH_L, 26); ctx.set_source_rgba(*hexc('#ced4da')); ctx.fill()     # shower tray lip
    # pipework + head
    ctx.set_line_width(18); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#adb5bd'))
    ctx.move_to(DX, DY - 60); ctx.line_to(DX, 700); ctx.line_to(HX, 700); ctx.line_to(HX, HY - 20); ctx.stroke()
    ctx.move_to(HX - 60, HY); ctx.line_to(HX + 60, HY); ctx.line_to(HX + 28, HY - 34); ctx.line_to(HX - 28, HY - 34); ctx.close_path()
    ctx.set_source_rgba(*hexc('#ced4da')); ctx.fill()
    dial(ctx, dial_ang, dial_glow); knob(ctx, knob_p)

def glass(ctx):
    ctx.set_line_width(10); ctx.set_source_rgba(*hexc('#adb5bd'))
    ctx.move_to(SH_R, 600); ctx.line_to(SH_R, 1600); ctx.stroke()
    for k in range(2):                                             # glass shine
        ctx.set_line_width(8); ctx.set_source_rgba(1, 1, 1, 0.5)
        ctx.move_to(SH_R - 40 - k * 30, 1500); ctx.line_to(SH_R - 10 - k * 30, 1440); ctx.stroke()

def leo(ctx, t, expr, hands=(0, -200), tint=None, tint_a=0.0, shiver=0.0, icicles=0.0, wet=0.0, dx=0.0):
    x = LX + dx + shiver * 5 * math.sin(t * 70)
    kid(ctx, x, GY, LS, t, expr, hands)
    hy = GY - 312 * LS + math.sin(t * 2 * math.pi * 1.6) * 3 * LS
    if tint and tint_a > 0:
        circle(ctx, x, hy, 56 * LS, hexc(tint, 0.42 * tint_a))
    if icicles > 0:
        ctx.set_source_rgba(*hexc('#caf0f8', icicles))
        for k, ix in enumerate((-50, -28, -6, 16, 40)):
            yb = hy - 14 * LS; ln = (22 + 10 * (k % 2)) * icicles
            ctx.move_to(x + ix - 8, yb); ctx.line_to(x + ix + 8, yb); ctx.line_to(x + ix, yb + ln); ctx.close_path(); ctx.fill()
    if wet > 0:
        e4.ell(ctx, x, GY - 4, 120 * wet, 18 * wet, hexc('#90e0ef', 0.8))
        r = random.Random(11)
        for k in range(10):
            ox = (r.random() - 0.5) * 120; ph = (t * 1.6 + r.random()) % 1
            e4.ell(ctx, x + ox, GY - 420 + ph * 380, 6, 10, hexc('#4cc9f0', wet * (1 - ph)))
    return x, hy

def dial_hands(): return ((DX - LX) / LS, (DY - GY) / LS)

def wren_tea(ctx, t, expr="happy"):
    wren(ctx, WX, GY, WS, t, "point", expr=expr, hand=(150, -330))
    teacup(ctx, WX + 150 * WS + 4, GY - 330 * WS - 6 + math.sin(t * 2 * math.pi * 1.1) * 5)

def wren_reach(ctx, t, hand, expr="happy"):                      # mirrored: hand reaches left toward the dial
    ctx.save(); ctx.translate(WX, 0); ctx.scale(-1, 1)
    wren(ctx, 0, GY, WS, t, "point", expr=expr, hand=hand); ctx.restore()

def sfx(ctx, s, x, y, a, col=RED, size=50, rot=-0.1):
    if a <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); txt(ctx, s, 0, 0, size, hexc(col, a)); ctx.restore()

# ------------------------------------------------------------ scenes
def s0(ctx, t, d):
    on = ramp(t, 0.9, 1.1)
    ang = lerp(-0.2, -1.0, ramp(t, 0.4, 0.9))
    bathroom(ctx, t, dial_ang=ang)
    spray(ctx, HX, HY + 8, math.pi / 2, 0.7, 560, t, '#4cc9f0', on)
    wren_tea(ctx, t)
    glass(ctx)
    cold = ramp(t, 1.2, 1.6)
    hands = dial_hands() if t < 1.0 else (0, -200)
    leo(ctx, t, "smile" if t < 1.2 else "shock", hands, tint=BLUE, tint_a=cold, shiver=cold, icicles=ramp(t, 1.7, 2.2))
    if 1.2 < t < 1.6: burst(ctx, LX, GY - 520, 1 - (t - 1.2) / 0.4, 110)
    sfx(ctx, "BRRRR!", 200, 1520, ramp(t, 1.3, 1.5), BLUE, 46, -0.15)
    bubble_ml(ctx, 690, 800, ["COLD! COLD!", "COLD!"], 42, ramp(t, 2.2, 2.4), (LX + 40, 1290))
    header(ctx, ease(t / 0.2 + 1), "HOTEL SHOWER", "One dial. Zero instructions.", "Leo vs the shower.", -0.3, t, main_size=54)
    c = int(round(lerp(18, 4, ramp(t, 1.0, 1.6))))
    meter(ctx, "WATER TEMP", "%d°C" % c, col=temp_col(c)); wm(ctx)

def s1(ctx, t, d):
    hot = ramp(t, 0.3, 0.8); back = ramp(t, 2.9, 3.2)
    ang = lerp(lerp(-1.0, 1.0, hot), -1.0, back)
    bathroom(ctx, t, dial_ang=ang)
    heat = ramp(t, 0.9, 1.5) * (1 - ramp(t, 3.2, 3.6))
    steam(ctx, t, heat)
    col = '#ff9f80' if 0.9 < t < 3.3 else '#4cc9f0'
    spray(ctx, HX, HY + 8, math.pi / 2, 0.7, 560, t, col, 1.0)
    wren_tea(ctx, t)
    glass(ctx)
    grabbing = (0.2 < t < 0.9) or (2.8 < t < 3.3)
    hands = dial_hands() if grabbing else (0, -200)
    expr = "smile" if t < 1.0 else ("shock" if t < 3.6 else "flat")
    leo(ctx, t, expr, hands, tint=RED if t < 3.3 else BLUE, tint_a=heat if t < 3.3 else ramp(t, 3.3, 3.6),
        shiver=ramp(t, 3.3, 3.6), dx=18 * math.sin(t * 18) * heat)
    sfx(ctx, "HOT HOT HOT!", 330, 1520, ramp(t, 1.2, 1.4) * (1 - ramp(t, 2.6, 2.8)), RED, 46, -0.12)
    bubble_ml(ctx, 690, 800, ["Lobster mode!"], 42, ramp(t, 1.5, 1.7) * (1 - ramp(t, 2.6, 2.75)), (LX + 40, 1290))
    bubble_ml(ctx, 690, 800, ["Where's the", "MIDDLE?!"], 42, ramp(t, 3.5, 3.7), (LX + 40, 1290))
    header(ctx, ease(t / 0.2), "PLAN B: FULL HOT", "Leo cranks it all the way.", "Then all the way back.", 1.2, t, main_size=54)
    c = int(round(lerp(lerp(4, 71, ramp(t, 0.9, 1.6)), 6, ramp(t, 3.2, 3.6))))
    meter(ctx, "WATER TEMP", "%d°C" % c, col=temp_col(c)); wm(ctx)

def s2(ctx, t, d):
    pull = ramp(t, 0.5, 0.8)
    bathroom(ctx, t, dial_ang=-1.0, knob_p=pull)
    head = 1 - ramp(t, 0.8, 1.0)
    spray(ctx, HX, HY + 8, math.pi / 2, 0.7, 560, t, '#4cc9f0', head)
    wren_tea(ctx, t, expr="shock" if 1.4 < t < 2.6 else "happy")
    glass(ctx)
    wild = ramp(t, 0.9, 1.1)
    # hose: from the wall outlet under the knob to a flailing wand
    ox, oy = KX - 40, KY + 70
    if wild > 0:
        ph = t * 7
        ex = lerp(ox, 420 + 220 * math.sin(ph), wild); ey = lerp(oy, 1000 + 160 * math.cos(ph * 1.3), wild)
        ctx.set_line_width(16); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#adb5bd'))
        ctx.move_to(ox, oy); ctx.curve_to(ox - 120, oy + 120, ex + 160 * math.cos(ph), ey + 200, ex, ey); ctx.stroke()
        ang = ph * 1.7
        rrect(ctx, ex - 16, ey - 16, 32, 32, 12); ctx.set_source_rgba(*hexc('#ced4da')); ctx.fill()
        spray(ctx, ex, ey, ang, 0.6, 340, t, '#4cc9f0', wild, n=20, seed=5)
    else:
        ctx.set_line_width(16); ctx.set_source_rgba(*hexc('#adb5bd')); ctx.move_to(ox, oy); ctx.line_to(ox, oy + 40); ctx.stroke()
    hands = ((KX - LX) / LS, (KY - GY) / LS) if t < 0.85 else (0, -200)
    wet = ramp(t, 1.1, 2.6)
    leo(ctx, t, "smile" if t < 1.0 else ("shock" if t < 3.0 else "flat"), hands, wet=wet, dx=-30 * math.sin(t * 9) * wild * (1 - ramp(t, 2.8, 3.1)))
    for k, (sx, sy) in enumerate(((240, 1330), (560, 1050), (300, 880))):
        tk = 1.3 + k * 0.45
        if tk < t < tk + 0.35: burst(ctx, sx, sy, 1 - (t - tk) / 0.35, 70)
    sfx(ctx, "SPLOOSH!", 300, 1530, ramp(t, 1.2, 1.4) * (1 - ramp(t, 2.6, 2.8)), '#0077b6', 48, -0.12)
    bubble_ml(ctx, 860, 880, ["Bit damp,", "dear?"], 42, ramp(t, 3.0, 3.2), (WX - 20, 1020))
    header(ctx, ease(t / 0.2), "PLAN C: THE OTHER KNOB", "It controls the hose.", "The hose is now free.", 1.0, t, main_size=56)
    meter(ctx, "LEO, DRY", "%d%%" % int(round(100 * (1 - wet))), col='#ff8fa3'); wm(ctx)

def s3(ctx, t, d):
    turn = ramp(t, 0.35, 0.75)
    ang = lerp(-1.0, 0.0, turn)
    warm = ramp(t, 2.3, 2.7)
    bathroom(ctx, t, dial_ang=ang, dial_glow=warm)
    steam(ctx, t, 0.5 * warm, n=8)
    col = '#4cc9f0' if t < 2.3 else '#ffd6a5'
    spray(ctx, HX, HY + 8, math.pi / 2, 0.7, 560, t, col, 1.0)
    reach = ramp(t, 0.0, 0.35) * (1 - ramp(t, 0.9, 1.2))
    if reach > 0:
        wren_reach(ctx, t, (lerp(150, (WX - DX) / WS, reach), lerp(-330, (DY - GY) / WS, reach)))
    else:
        wren_tea(ctx, t, expr="happy")
    glass(ctx)
    # Leo steps aside in a towel while they wait, then back under
    side = ramp(t, 0.2, 0.6) * (1 - ramp(t, 2.6, 3.0))
    lx_off = 0.0
    _, hy = leo(ctx, t, "flat" if t < 2.6 else "smile", (0, -200), tint=BLUE, tint_a=side * 0.7, shiver=side, wet=1 - ramp(t, 2.6, 3.4), dx=lx_off)
    if side > 0.05:                                                # towel round his shoulders
        x = LX + lx_off + side * 5 * math.sin(t * 70)
        rrect(ctx, x - 70, GY - 245 * LS, 140, 110, 30); ctx.set_source_rgba(1, 1, 1, side); ctx.fill()
        for k in range(2): ctx.rectangle(x - 70, GY - 245 * LS + 74 + k * 16, 140, 6); ctx.set_source_rgba(*hexc('#90e0ef', side)); ctx.fill()
    # 30-second countdown chip
    cd = ramp(t, 0.8, 2.3, )
    ca = ramp(t, 0.7, 0.9) * (1 - ramp(t, 2.5, 2.7))
    if ca > 0:
        cx, cy = 440, 880
        rrect(ctx, cx - 150, cy - 70, 300, 120, 60); ctx.set_source_rgba(*hexc('#10132b', 0.9 * ca)); ctx.fill()
        circle(ctx, cx - 90, cy - 10, 34, hexc('#ffffff', ca)); ctx.set_line_width(6); ctx.set_source_rgba(*hexc('#10132b', ca))
        ctx.move_to(cx - 90, cy - 10); ctx.line_to(cx - 90, cy - 34); ctx.stroke()
        a2 = -math.pi / 2 + 2 * math.pi * cd; ctx.move_to(cx - 90, cy - 10); ctx.line_to(cx - 90 + math.cos(a2) * 26, cy - 10 + math.sin(a2) * 26); ctx.stroke()
        txt(ctx, "0:%02d" % int(round(30 * (1 - cd))), cx + 40, cy + 8, 54, hexc('#ffd166', ca))
    if 2.3 < t < 2.7: burst(ctx, DX, DY, 1 - (t - 2.3) / 0.4, 110)
    bubble_ml(ctx, 860, 880, ["Middle. Then", "wait, dear."], 42, ramp(t, 0.9, 1.1) * (1 - ramp(t, 2.2, 2.35)), (WX - 20, 1020))
    bubble_ml(ctx, 690, 800, ["Oh. That's", "perfect."], 42, ramp(t, 3.0, 3.2), (LX + 40, 1290))
    header(ctx, ease(t / 0.2), "PLAN GRANDMA", "Set it to the middle.", "Wait 30 seconds.", 0.9, t, main_size=56)
    c = int(round(lerp(6, 38, ramp(t, 0.8, 2.5))))
    meter(ctx, "WATER TEMP", ("%d°C  PERFECT" % c) if t > 2.5 else "%d°C" % c, col=temp_col(c) if t > 2.5 else '#ffd166'); wm(ctx)

def s4(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    pop = ease(t / 0.4)
    wren(ctx, 540, 1640, 1.0 * (0.92 + 0.08 * pop), t, "wave")
    duck(ctx, 790, 1580, 1.4, 0.15 * math.sin(t * 3))
    a = ease(t / 0.3)
    ctext(ctx, "Wren: “Patience, dear.”", 205 - (1 - a) * 20, 60, hexc('#22223b', a), maxw=940)
    ctext(ctx, "Leo: “I'm still dripping.”", 290, 60, hexc(RED, ease((t - 0.5) / 0.3)), maxw=940)
    a2 = ease((t - 1.0) / 0.3)
    mv.font(ctx, 54); s_ = "@wrentrips"; e = ctx.text_extents(s_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 400, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 468); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s_)
    ctext(ctx, "Follow for more Leo & Wren", 560, 44, hexc('#5c2a1e', ease((t - 1.4) / 0.3)), bold=False)
    ctext(ctx, "Do you wait for the hot water? Tell us", 625, 38, hexc('#5c2a1e', ease((t - 1.8) / 0.3)), bold=False, maxw=980)

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
        picks = [(s0, 0.0), (s0, 1.4), (s0, 3.2), (s1, 0.5), (s1, 2.0), (s1, 3.9), (s2, 0.6), (s2, 1.8), (s2, 3.6), (s3, 0.5), (s3, 1.6), (s3, 3.5), (s4, 2.6)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((300, 533)))
        c = Image.new("RGB", (310 * 7, 543 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 7) * 310, (i // 7) * 543))
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

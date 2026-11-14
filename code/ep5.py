import cairo, math, random, subprocess, os, sys
import make_video as mv
from make_video import W, H, hexc, circle, rrect, ctext, ai_tag, ease, wren
import ep4 as e4
from ep3 import star

OUT = "/home/claude/wren/ep5"
os.makedirs(OUT, exist_ok=True)
CX, GY, S = 380, 1700, 0.95
DARK, RED = hexc('#22223b'), '#e63946'
L_REST, L_HOLD, L_UP, L_PASS = (150, -300), (185, -400), (185, -540), (265, -350)

def bob(t): return math.sin(t * 2 * math.pi * 1.1) * 5
def hwp(hl, t, cx=CX): return (cx + S * hl[0], GY + S * (hl[1] + bob(t)))

# ---------- the puzzle cube (generic 3x3, original drawing) ----------
C = dict(W='#f4f4f4', Y='#ffd60a', R='#e63946', O='#ff8c1a', B='#1d6fd1', G='#2fb344')
FACE_COL = {'U': 'W', 'D': 'Y', 'F': 'G', 'B': 'B', 'L': 'O', 'R': 'R'}
FACES = {'F': ((0, 0, 1), (1, 0, 0), (0, 1, 0)), 'B': ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
         'R': ((1, 0, 0), (0, 0, -1), (0, 1, 0)), 'L': ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
         'U': ((0, 1, 0), (1, 0, 0), (0, 0, -1)), 'D': ((0, -1, 0), (1, 0, 0), (0, 0, 1))}
BLACK = '#16161d'

def solved_state(): return {f: [[C[FACE_COL[f]]] * 3 for _ in range(3)] for f in 'UDFBLR'}
def scrambled_state(seed, white_front=False):
    r = random.Random(seed); keys = list(C.keys()); st = {}
    for f in 'UDFBLR':
        g = [[C[r.choice(keys)] for _ in range(3)] for _ in range(3)]
        g[1][1] = C[FACE_COL[f]]
        if len({c for row in g for c in row}) == 1: g[0][0] = C['R'] if g[0][0] != C['R'] else C['B']
        st[f] = g
    if white_front: st['F'] = [[C['W']] * 3 for _ in range(3)]
    return st
_tr = random.Random(11)
THR = {f: [[_tr.random() for _ in range(3)] for _ in range(3)] for f in 'UDFBLR'}
SOL, SCR, SCR1 = solved_state(), scrambled_state(3), scrambled_state(5, True)

def blend(a, b, p):
    return {f: [[b[f][r][c] if p > THR[f][r][c] else a[f][r][c] for c in range(3)] for r in range(3)] for f in 'UDFBLR'}

def rot3(p, yaw, tilt):
    x, y, z = p
    x1 = x * math.cos(yaw) + z * math.sin(yaw); z1 = -x * math.sin(yaw) + z * math.cos(yaw)
    return (x1, y * math.cos(tilt) - z1 * math.sin(tilt), y * math.sin(tilt) + z1 * math.cos(tilt))

def cube(ctx, cx, cy, h, yaw, tilt, state):
    shadow = (0, 0, 0, 0.12)
    for name, (n, u, v) in FACES.items():
        nz = rot3(n, yaw, tilt)[2]
        if nz <= 0.02: continue
        def P(a, b):
            p = (n[0] + a * u[0] + b * v[0], n[1] + a * u[1] + b * v[1], n[2] + a * u[2] + b * v[2])
            x, y, _ = rot3(p, yaw, tilt); return (cx + h * x, cy - h * y)
        def poly(pts, col):
            ctx.move_to(*pts[0]); [ctx.line_to(*q) for q in pts[1:]]; ctx.close_path(); ctx.set_source_rgba(*col); ctx.fill()
        poly([P(-1, 1), P(1, 1), P(1, -1), P(-1, -1)], hexc(BLACK))
        for r in range(3):
            for c in range(3):
                a0, a1 = -1 + 2 * c / 3, -1 + 2 * (c + 1) / 3; b0, b1 = 1 - 2 * r / 3, 1 - 2 * (r + 1) / 3
                ac, bc, hw = (a0 + a1) / 2, (b0 + b1) / 2, 0.28
                poly([P(ac - hw, bc + hw), P(ac + hw, bc + hw), P(ac + hw, bc - hw), P(ac - hw, bc - hw)], hexc(state[name][r][c]))
        poly([P(-1, 1), P(1, 1), P(1, -1), P(-1, -1)], (0, 0, 0, 0.30 * (1 - nz)))

def sticker(ctx, x, y, size, rot, col):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); rrect(ctx, -size / 2, -size / 2, size, size, size * 0.18)
    ctx.set_source_rgba(*hexc(col)); ctx.fill(); ctx.restore()

# ---------- set pieces ----------
def plane_simple(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-120, -10); ctx.line_to(-175, -105); ctx.line_to(-120, -105); ctx.line_to(-50, -20); ctx.close_path(); ctx.set_source_rgba(*hexc('#e63946')); ctx.fill()
    e4.ell(ctx, 0, 0, 200, 52, (1, 1, 1, 1))
    ctx.move_to(-30, 14); ctx.line_to(-110, 125); ctx.line_to(-55, 125); ctx.line_to(65, 14); ctx.close_path(); ctx.set_source_rgba(*hexc('#8d99ae')); ctx.fill()
    for wx in range(-100, 150, 36): circle(ctx, wx, -10, 9, hexc('#457b9d'))
    ctx.restore()

def gate(ctx, t, status="DELAYED +6h"):
    mv.vgrad(ctx, '#e4ebf2', '#cdd8e3')
    ctx.save(); rrect(ctx, 70, 870, 940, 380, 26); ctx.clip()
    g = cairo.LinearGradient(0, 870, 0, 1250); g.add_color_stop_rgb(0, *hexc('#8ecae6')[:3]); g.add_color_stop_rgb(1, *hexc('#d7f0ff')[:3])
    ctx.set_source(g); ctx.paint()
    mv.cloud(ctx, 120 + t * 14, 940, 0.7); mv.cloud(ctx, 640 - t * 10, 1010, 0.55, 0.85)
    ctx.rectangle(60, 1175, 960, 90); ctx.set_source_rgba(*hexc('#7a8a99')); ctx.fill()
    plane_simple(ctx, 330 + t * 28, 1150, 0.42)
    ctx.restore()
    ctx.set_line_width(14); ctx.set_source_rgba(*hexc('#8795a3')); rrect(ctx, 70, 870, 940, 380, 26); ctx.stroke()
    for mx in (385, 700): ctx.move_to(mx, 870); ctx.line_to(mx, 1250); ctx.stroke()
    rrect(ctx, 250, 735, 580, 110, 18); ctx.set_source_rgba(*hexc('#1d2433')); ctx.fill()
    mv.font(ctx, 40); ctx.move_to(282, 800); ctx.set_source_rgba(*hexc('#ffb703')); ctx.show_text("GATE 34B")
    blink = 1.0 if math.sin(t * 6) > 0 else 0.35
    mv.font(ctx, 40); ctx.move_to(545, 800); ctx.set_source_rgba(1, 0.3, 0.3, blink); ctx.show_text(status)
    ctx.rectangle(-200, 1640, W + 400, 700); ctx.set_source_rgba(*hexc('#b8c2cc')); ctx.fill()
    ctx.set_line_width(3); ctx.set_source_rgba(1, 1, 1, 0.3)
    for x in range(-200, W + 200, 140): ctx.move_to(x, 1640); ctx.line_to(x - 60, 1760); ctx.stroke()
    for k in range(3):
        x = 600 + k * 150
        rrect(ctx, x, 1390, 124, 130, 18); ctx.set_source_rgba(*hexc('#2a6fdb')); ctx.fill()
        rrect(ctx, x, 1510, 124, 56, 14); ctx.set_source_rgba(*hexc('#1f55a8')); ctx.fill()
        ctx.set_line_width(10); ctx.set_source_rgba(*hexc('#6c7a89'))
        for lx in (x + 14, x + 110): ctx.move_to(lx, 1566); ctx.line_to(lx, 1650); ctx.stroke()

def kid(ctx, x, gy, s, t, expr="smile", hands=(0, -200)):
    ctx.save(); ctx.translate(x, gy); ctx.scale(s, s); ctx.translate(0, math.sin(t * 2 * math.pi * 1.6) * 3)
    skin = hexc('#c68642')
    ctx.save(); ctx.scale(1, 0.2); circle(ctx, 0, 0, 80, (0, 0, 0, 0.15)); ctx.restore()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(34); ctx.set_source_rgba(*hexc('#3d405b'))
    for lx in (-24, 24):
        ctx.move_to(lx, -120); ctx.line_to(lx, -24); ctx.stroke(); e4.ell(ctx, lx + (6 if lx > 0 else -6), -12, 30, 15, hexc('#f8f9fa'))
    rrect(ctx, -54, -250, 108, 150, 30); ctx.set_source_rgba(*hexc('#ff6b6b')); ctx.fill()
    rrect(ctx, -34, -170, 68, 42, 12); ctx.set_source_rgba(*hexc('#e85d5d')); ctx.fill()
    hx, hy = hands
    ctx.set_line_width(30); ctx.set_source_rgba(*hexc('#ff6b6b'))
    for sg in (-1, 1): ctx.move_to(sg * 46, -228); ctx.line_to(hx + sg * 18, hy); ctx.stroke()
    for sg in (-1, 1): circle(ctx, hx + sg * 18, hy, 17, skin)
    circle(ctx, 0, -312, 56, skin)
    ctx.arc(0, -326, 60, math.radians(180), math.radians(360)); ctx.close_path(); ctx.set_source_rgba(*hexc('#2a9d8f')); ctx.fill()
    rrect(ctx, -2, -338, 78, 16, 8); ctx.set_source_rgba(*hexc('#1f7a70')); ctx.fill()
    circle(ctx, -34, -290, 10, hexc('#f28b82', 0.45)); circle(ctx, 34, -290, 10, hexc('#f28b82', 0.45))
    ph = (t + 1.3) % 3.0; sy = 0.12 if ph < 0.12 else 1.0
    for ex in (-20, 20):
        ctx.save(); ctx.translate(ex, -306); ctx.scale(1, sy); circle(ctx, 0, 0, 6, hexc('#2b2d42')); ctx.restore()
    ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*hexc('#7a3e2b'))
    if expr == "smug":
        ctx.move_to(-16, -282); ctx.curve_to(-4, -274, 10, -276, 20, -288); ctx.stroke()
        ctx.set_source_rgba(*hexc('#2b2d42')); ctx.move_to(8, -326); ctx.line_to(30, -332); ctx.stroke()
    elif expr == "flat":
        ctx.move_to(-14, -278); ctx.line_to(14, -278); ctx.stroke()
        ctx.set_source_rgba(*hexc('#2b2d42')); ctx.move_to(-30, -326); ctx.line_to(-10, -322); ctx.stroke(); ctx.move_to(10, -322); ctx.line_to(30, -326); ctx.stroke()
    else:
        ctx.arc(0, -288, 20, math.radians(20), math.radians(160)); ctx.stroke()
    ctx.restore()

def stickers_on_wren(ctx, t, cx, show_cheek, show_coat):
    ctx.save(); ctx.translate(cx, GY); ctx.scale(S, S); ctx.translate(0, bob(t))
    if show_cheek: sticker(ctx, -52, -508, 30, -0.3, C['R'])
    if show_coat: sticker(ctx, -26, -330, 34, 0.25, C['O'])
    ctx.restore()

# ---------- scenes ----------
def s0(ctx, t, d):
    e4.begin_set(ctx); gate(ctx, t); mv.suitcase(ctx, 170, 1700, 0.55, t)
    hl = e4.hand_path(t, [(0, L_HOLD), (0.5, L_HOLD), (1.1, L_UP)])
    wren(ctx, CX, GY, S, t, "point", hand=hl)
    p = hwp(hl, t); cube(ctx, p[0] + 8, p[1] - 68, 62, -0.45 + t * 0.9, 0.35, SCR)
    e4.end_set(ctx)
    a = ease(t / 0.3); e4.top_box(ctx, a, 380)
    ctext(ctx, "Flight delayed 6 hours.", 245, 62, hexc('#22223b', a), maxw=900)
    ctext(ctx, "How hard can a cube be?", 350, 58, hexc(RED, ease((t - 1.8) / 0.4)), maxw=900)
    ai_tag(ctx, y=1860)

def s1(ctx, t, d):
    e4.begin_set(ctx); gate(ctx, t); mv.suitcase(ctx, 170, 1700, 0.55, t)
    hl = e4.hand_path(t, [(0, L_HOLD), (0.6, L_UP)])
    fl = max(0.0, min(0.55, (t - 2.8) / 0.8 * 0.55)); ex = "shock" if t > 2.6 else "happy"
    wren(ctx, CX, GY, S, t, "point", hand=hl, flush=fl, expr=ex)
    yaw = -0.2 + 0.05 * math.sin(t * 2) if t < 2.0 else -0.2 + (3.0 - (-0.2)) * ease((t - 2.0) / 0.9) + (0.12 * math.sin(t * 3) if t > 2.9 else 0)
    p = hwp(hl, t); cube(ctx, p[0] + 8, p[1] - 68, 62, yaw, 0.22, SCR1)
    e4.end_set(ctx)
    a = ease(t / 0.3); e4.top_box(ctx, a, 380)
    ctext(ctx, "ATTEMPT 1", 215, 44, hexc(RED, a), maxw=900)
    ctext(ctx, "I solved one side!", 305, 62, hexc('#22223b', a), maxw=900)
    ctext(ctx, "The other five disagree.", 415, 50, hexc(RED, ease((t - 2.5) / 0.4)), maxw=900)
    ai_tag(ctx, y=1860)

def s2(ctx, t, d):
    e4.begin_set(ctx); gate(ctx, t); mv.suitcase(ctx, 170, 1700, 0.55, t)
    hl = e4.hand_path(t, [(0, L_HOLD), (0.5, L_UP)])
    wren(ctx, CX, GY, S, t, "point", hand=hl, flush=0.0, expr="happy" if t < 3.0 else "happy")
    p = hwp(hl, t); ccx, ccy = p[0] + 8, p[1] - 68
    # state: scrambled -> bare black (peeled) -> neatly "solved"
    st = {}
    for f in 'UDFBLR':
        g = []
        for r in range(3):
            row = []
            for c in range(3):
                th = THR[f][r][c]
                if t < 1.2 + th * 0.4: row.append(SCR[f][r][c])
                elif t < 2.2 + th * 0.7: row.append(BLACK)
                else: row.append(SOL[f][r][c])
            g.append(row)
        st[f] = g
    if t > 3.0: st['F'][0][0] = C['W']
    cube(ctx, ccx, ccy, 62, -0.55 + t * 0.35, 0.3, st)
    rr = random.Random(21)
    for i in range(12):
        t0 = 1.2 + rr.random() * 0.4; tau = t - t0
        if tau < 0: continue
        x0, y0 = ccx + rr.uniform(-50, 50), ccy + rr.uniform(-40, 40)
        vx, vy, g_ = rr.uniform(-380, 380), rr.uniform(-900, -450), 2400; yf = 1650 + rr.uniform(0, 30)
        tl = (-vy + math.sqrt(vy * vy - 2 * g_ * (y0 - yf))) / g_
        tt = min(tau, tl); x = x0 + vx * tt; y = y0 + vy * tt + 0.5 * g_ * tt * tt
        sticker(ctx, x, y, 30, rr.uniform(0, 3) + tt * 6, list(C.values())[i % 6])
    stickers_on_wren(ctx, t, CX, t > 2.6, t > 2.9)
    e4.end_set(ctx)
    a = ease(t / 0.3); e4.top_box(ctx, a, 380)
    ctext(ctx, "ATTEMPT 2", 215, 44, hexc(RED, a), maxw=900)
    ctext(ctx, "I peeled the stickers off.", 305, 56, hexc('#22223b', a), maxw=920)
    ctext(ctx, "Technically solved.", 415, 54, hexc(RED, ease((t - 3.0) / 0.4)), maxw=900)
    ai_tag(ctx, y=1860)

def s3(ctx, t, d):
    sk = 1.05; kx = 1230 + (790 - 1230) * ease(t / 0.8)
    e4.begin_set(ctx); gate(ctx, t); mv.suitcase(ctx, 170, 1700, 0.55, t)
    keys = [(0, L_HOLD), (0.8, L_HOLD), (1.4, L_PASS), (2.2, L_REST)]
    hl = e4.hand_path(t, keys)
    solved_p = max(0.0, min(1.0, (t - 2.0) / 2.0))
    ex = "shock" if t > 2.4 else "happy"
    wren(ctx, CX, GY, S, t, "point", hand=hl, expr=ex)
    raise_k = ease((t - 4.0) / 0.4)
    kh = (0, -200 - 200 * raise_k)
    kid(ctx, kx, GY, sk, t, "smug" if t > 1.8 else "smile", kh)
    p = hwp(hl, t); wc = (p[0] + 8, p[1] - 68)
    kc = (kx + kh[0] * sk, GY + kh[1] * sk - 52)
    if t < 0.8: c = wc
    elif t < 1.7:
        k = ease((t - 0.8) / 0.9); c = (wc[0] + (kc[0] - wc[0]) * k, wc[1] + (kc[1] - wc[1]) * k - 70 * math.sin(math.pi * k))
    else: c = kc
    yaw = 0.4 + t * 0.9 if t < 2.0 else (0.4 + 2.0 * 0.9 + 2 * math.pi * 2.2 * (t - 2.0) / 2.0 if t < 4.0 else 0.5)
    state = blend(SCR, SOL, solved_p) if t >= 2.0 else SCR
    cube(ctx, c[0], c[1], 60, yaw, 0.35, state)
    if 2.0 <= t < 4.4:
        val = min(8.4, (t - 2.0) / 2.0 * 8.4)
        rrect(ctx, kx - 100, 1060, 200, 74, 16); ctx.set_source_rgba(*hexc('#1d2433')); ctx.fill()
        mv.font(ctx, 44); s_ = "0:%04.1f" % val; e = ctx.text_extents(s_)
        ctx.move_to(kx - e.x_advance / 2, 1112); ctx.set_source_rgba(*hexc('#ffd60a')); ctx.show_text(s_)
    if t > 4.4:
        sp = ease((t - 4.4) / 0.35); star(ctx, kx, 1095, 62 * sp, 1.0, math.sin(t * 6) * 0.15)
        mv.font(ctx, 34); e = ctx.text_extents("Leo"); ctx.move_to(kx - e.x_advance / 2, GY + 44); ctx.set_source_rgba(*DARK); ctx.show_text("Leo")
    e4.bubble(ctx, 300, 1010, "Gold star!", 50, ease((t - 4.8) / 0.3), (370, 1090))
    e4.end_set(ctx)
    a = ease(t / 0.3); e4.top_box(ctx, a, 380)
    ctext(ctx, "ATTEMPT 3", 215, 44, hexc(RED, a), maxw=900)
    ctext(ctx, "I asked a 9-year-old.", 305, 62, hexc('#22223b', a), maxw=900)
    ctext(ctx, "Solved in 8 seconds.", 415, 54, hexc(RED, ease((t - 4.0) / 0.4)), maxw=900)
    ai_tag(ctx, y=1860)

def s4(ctx, t, d):
    sk = 1.05; kx = 790
    e4.begin_set(ctx); gate(ctx, t); mv.suitcase(ctx, 170, 1700, 0.55, t)
    shake = 1.0 if 0.4 < t < 1.5 else 0.0
    base = e4.hand_path(t, [(0, L_UP), (1.5, L_UP), (2.2, L_PASS), (2.8, L_REST)])
    hl = (base[0] + shake * math.sin(t * 34) * 14, base[1] + shake * math.cos(t * 41) * 12)
    wren(ctx, CX, GY, S, t, "point", hand=hl, flush=0.0, expr="happy")
    flat = t > 2.4
    kid(ctx, kx, GY, sk, t, "flat" if flat else "smile", (0, -200))
    p = hwp(hl, t); wc = (p[0] + 8, p[1] - 68); kc = (kx, GY - 200 * sk - 52)
    if t < 1.5: c = wc
    elif t < 2.3:
        k = ease((t - 1.5) / 0.8); c = (wc[0] + (kc[0] - wc[0]) * k, wc[1] + (kc[1] - wc[1]) * k - 60 * math.sin(math.pi * k))
    else: c = kc
    scr_p = ease((t - 0.4) / 1.0)
    state = blend(SOL, SCR, scr_p)
    yaw = 0.5 + (t * 6.0 if 0.4 < t < 1.6 else (1.6 * 6.0 + 0.4 if t >= 1.6 else 0))
    cube(ctx, c[0], c[1], 60, yaw if t > 0.4 else 0.5, 0.35, state)
    e4.bubble(ctx, 330, 1010, "Again!", 52, ease((t - 2.6) / 0.3), (370, 1090))
    e4.end_set(ctx)
    a = ease(t / 0.3); e4.top_box(ctx, a, 380)
    ctext(ctx, "WREN’S RULE", 215, 44, hexc(RED, a), maxw=900)
    ctext(ctx, "Can’t solve it? Find a 9-year-old.", 300, 56, hexc('#22223b', a), maxw=900, lh=1.2)
    ctext(ctx, "Then scramble it again.", 445, 48, hexc(RED, ease((t - 2.4) / 0.4)), maxw=900)
    ai_tag(ctx, y=1860)

def s5(ctx, t, d):
    mv.vgrad(ctx, '#fff3e0', '#ffd6a5')
    for i in range(5):
        x = (i * 260 + t * 110) % (W + 260) - 130
        cube(ctx, x, 1755 - abs(math.sin(t * 4 + i)) * 36, 46, t * 2 + i, 0.4, SCR if i % 2 == 0 else SCR1)
    pop = ease(t / 0.5)
    wren(ctx, 540, 1640, 1.1 * (0.9 + 0.1 * pop), t, "wave", flush=0.35)
    a = ease((t - 0.2) / 0.4)
    ctext(ctx, "Send this to someone who only ever solves one side", 210 - (1 - a) * 30, 56, hexc('#22223b', a), maxw=900, lh=1.2)
    a2 = ease((t - 1.1) / 0.4)
    mv.font(ctx, 54); s2_ = "@wrentrips"; e = ctx.text_extents(s2_)
    rrect(ctx, (W - e.x_advance) / 2 - 40, 500, e.x_advance + 80, 100, 50); ctx.set_source_rgba(*hexc(RED, a2)); ctx.fill()
    ctx.move_to((W - e.x_advance) / 2, 568); ctx.set_source_rgba(1, 1, 1, a2); ctx.show_text(s2_)
    ctext(ctx, "Follow for the next disaster", 690, 44, hexc('#5c2a1e', ease((t - 1.7) / 0.4)), bold=False)
    ai_tag(ctx, y=1890, dark=True)

SCENES = [(s0, 4.0), (s1, 4.5), (s2, 5.0), (s3, 6.0), (s4, 4.0), (s5, 4.5)]

def frame(fn, t, d):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    fn(ctx, t, d)
    a_in = 0 if fn is s0 else 1 - t / 0.25
    a_out = (t - (d - 0.6)) / 0.6 if fn is s5 else (t - (d - 0.2)) / 0.2
    a = max(a_in, a_out, 0)
    if a > 0:
        ctx.set_source_rgba(*hexc('#fff3e0', min(1, ease(a)))); ctx.paint()
    return surf

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        from PIL import Image
        picks = [(s0, 2.2), (s1, 1.4), (s1, 3.6), (s2, 0.8), (s2, 1.9), (s2, 4.2), (s3, 1.2), (s3, 3.0), (s3, 5.2), (s4, 1.0), (s4, 3.2), (s5, 3.0)]
        dmap = {fn: d for fn, d in SCENES}; ims = []
        for i, (fn, tt) in enumerate(picks):
            p = f"{OUT}/prev_{i}.png"; frame(fn, tt, dmap[fn]).write_to_png(p)
            ims.append(Image.open(p).convert("RGB").resize((270, 480)))
        c = Image.new("RGB", (280 * 6, 490 * 2), "white")
        for i, im in enumerate(ims): c.paste(im, ((i % 6) * 280, (i // 6) * 490))
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

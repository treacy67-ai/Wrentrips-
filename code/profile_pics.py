import cairo, math
from PIL import Image, ImageDraw
import make_video as mv

S = 1080
OUT = "/home/claude/wren"

def grad(ctx, top, bottom):
    g = cairo.LinearGradient(0, 0, 0, S)
    g.add_color_stop_rgb(0, *mv.hexc(top)[:3]); g.add_color_stop_rgb(1, *mv.hexc(bottom)[:3])
    ctx.set_source(g); ctx.paint()

def bg_sunrise(ctx):
    grad(ctx, '#ffb385', '#ffe5c4')
    mv.circle(ctx, 840, 300, 170, mv.hexc('#fff1c1', 0.9))
    mv.cloud(ctx, 60, 230, 0.9, 0.85)

def bg_sky(ctx):
    grad(ctx, '#6cb4e4', '#e3f4ff')
    mv.cloud(ctx, 40, 200, 0.9); mv.cloud(ctx, 800, 330, 0.7)
    mv.plane(ctx, 800, 170, 0.6, -0.15, 0)

def bg_sunset(ctx):
    grad(ctx, '#ff8c69', '#6d597a')
    mv.circle(ctx, 540, 520, 300, mv.hexc('#ffd56b', 0.9))
    ctx.move_to(0, S)
    for x in range(0, S + 20, 20):
        ctx.line_to(x, 820 - 120 * abs(math.sin(x * 0.004 + 1)))
    ctx.line_to(S, S); ctx.close_path(); ctx.set_source_rgba(*mv.hexc('#355070')); ctx.fill()

def bg_lanterns(ctx):
    grad(ctx, '#1d1b3a', '#4a2f63')
    cols = ['#ff4d4d', '#ff9f1c', '#ffd166', '#ff7b39', '#ef476f']
    ctx.set_line_width(3); ctx.set_source_rgba(0.1, 0.08, 0.1, 1)
    ctx.move_to(-20, 120); ctx.curve_to(S / 3, 210, 2 * S / 3, 210, S + 20, 120); ctx.stroke()
    for k in range(6):
        u = (k + 0.5) / 6; x = u * S; y = 120 + 90 * 0.75 * 4 * u * (1 - u)
        mv.lantern(ctx, x, y + 70, 0.75, cols[k % 5])

OPTIONS = [
    ("sunrise", bg_sunrise, "wave", 0.6),
    ("sky", bg_sky, "wave", 1.4),
    ("sunset", bg_sunset, "cheer", 0.3),
    ("lanterns", bg_lanterns, "wave", 2.0),
]

def make(name, bg, mode, t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S); ctx = cairo.Context(surf)
    bg(ctx)
    s = 1.75 if mode != "cheer" else 1.6
    head_y = 470 if mode != "cheer" else 520
    mv.wren(ctx, S / 2, head_y + 545 * s, s, t, mode, blink_seed=1.0)
    path = f"{OUT}/wren_profile_{name}.png"
    surf.write_to_png(path)
    return path

paths = [make(*o) for o in OPTIONS]

# preview: how each looks in Instagram's circle crop
tile = 420
sheet = Image.new("RGB", (tile * 4 + 50 * 5, tile + 100), "white")
for i, p in enumerate(paths):
    im = Image.open(p).convert("RGB").resize((tile, tile), Image.LANCZOS)
    mask = Image.new("L", (tile, tile), 0); ImageDraw.Draw(mask).ellipse((0, 0, tile, tile), fill=255)
    sheet.paste(im, (50 + i * (tile + 50), 50), mask)
sheet.save(f"{OUT}/profile_preview.png")
print(paths)

"""Batch 8: Christmas characters and light streaks.
Reindeer flying across a night sky, gingerbread cookies falling, nutcracker soldiers marching,
a spiral of lights wrapping a Christmas tree, and red-green-gold light streaks (overlay on black).
Usage: python3 pack8.py <name> ...   (run from an empty output folder)"""
import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter
from pack import W, H, N, TAU, gradient, tone, encode
from pack2 import encode_raw
from xmas import splat, glowify

SS = 4  # supersampling for sprites

def shrink(im, f=SS):
    return im.resize((im.width // f, im.height // f), Image.LANCZOS)

def stars_bg(top, bot, seed, n=260):
    """night gradient with twinkling stars, as a list-free function of t"""
    base = gradient(top, bot, .55)
    rng = np.random.default_rng(seed)
    sx = rng.uniform(0, W, n); sy = rng.uniform(0, H * .8, n) ** 1.0
    sa = rng.uniform(.15, .9, n) ** 2; sk = rng.integers(1, 4, n); sp = rng.uniform(0, TAU, n)
    def at(t):
        buf = np.zeros((H, W, 3), np.float32)
        amp = sa * (.55 + .45 * np.sin(TAU * sk * t + sp))
        splat(buf, sx, sy, np.ones((n, 3), np.float32) * np.array([1, .97, .9], np.float32), amp * 2.2)
        return base + gaussian_filter(buf, (1.1, 1.1, 0)) * 3
    return at

# ---------------------------------------------------------------- 1. reindeer
def deer_sprite(pose, col=(255, 214, 120, 255), h=230):
    """reindeer silhouette facing right; pose 0..3 = gallop phases"""
    s = SS; Wd, Hd = int(h * 1.9) * s, int(h * 1.5) * s
    im = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    u = h * s / 100.0
    P = lambda x, y: (x * u, y * u)
    cx, cy = 85, 82   # body center
    # legs: (hip x, hip y, angle front/back in degrees) per pose
    swings = [(-38, 34, 30, -36), (-12, 14, 8, -14), (30, -30, -36, 36), (12, -10, -12, 14)][pose % 4]
    hips = [(cx + 30, cy + 6), (cx + 22, cy + 8), (cx - 32, cy + 6), (cx - 24, cy + 8)]
    for (hx, hy), a in zip(hips, swings):
        ang = math.radians(90 + a)
        kx, ky = hx + 22 * math.cos(ang), hy + 22 * math.sin(ang)
        ang2 = ang + math.radians(-25 if a > 0 else 25) * (1 if (hx > cx) else -1)
        fx, fy = kx + 22 * math.cos(ang2), ky + 22 * math.sin(ang2)
        d.line([P(hx, hy), P(kx, ky), P(fx, fy)], fill=col, width=int(7 * u), joint='curve')
        d.ellipse([P(fx - 3.5, fy - 3.5), P(fx + 3.5, fy + 3.5)], fill=col)
    d.ellipse([P(cx - 48, cy - 18), P(cx + 46, cy + 20)], fill=col)                      # body
    d.polygon([P(cx + 26, cy - 12), P(cx + 54, cy - 46), P(cx + 66, cy - 38), P(cx + 44, cy + 6)], fill=col)  # neck
    d.ellipse([P(cx + 50, cy - 56), P(cx + 76, cy - 34)], fill=col)                      # head
    d.polygon([P(cx + 70, cy - 52), P(cx + 92, cy - 44), P(cx + 90, cy - 36), P(cx + 68, cy - 36)], fill=col)  # snout
    d.ellipse([P(cx + 86, cy - 46), P(cx + 95, cy - 37)], fill=col)
    d.polygon([P(cx + 56, cy - 54), P(cx + 50, cy - 66), P(cx + 62, cy - 56)], fill=col)  # ear
    # antlers
    lw = int(4 * u)
    for off in (0, -9):
        bx, by = cx + 62 + off * .4, cy - 54
        tip = (bx - 16 + off, by - 40)
        d.line([P(bx, by), P(bx - 6 + off * .5, by - 20), P(*tip)], fill=col, width=lw, joint='curve')
        d.line([P(bx - 5 + off * .5, by - 16), P(bx + 8 + off * .3, by - 30)], fill=col, width=lw)
        d.line([P(bx - 10 + off * .7, by - 28), P(bx - 2 + off * .5, by - 44)], fill=col, width=lw)
        d.line([P(bx - 12 + off * .8, by - 34), P(bx - 28 + off, by - 40)], fill=col, width=lw)
    d.polygon([P(cx - 46, cy - 8), P(cx - 60, cy - 18), P(cx - 50, cy + 2)], fill=col)  # tail
    return shrink(im)

def reindeer():
    sky = stars_bg([.015, .03, .09], [.05, .10, .24], 81)
    moon_r = 120; mx, my = W * .76, H * .26
    m = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot(xx - mx, yy - my)
    disc = np.clip((moon_r - dist) / 2.5, 0, 1)
    craters = gaussian_filter(np.random.default_rng(3).random((H, W)).astype(np.float32), 18) - .5
    m += disc[..., None] * (np.array([1, .95, .82], np.float32) * (.86 + 4.5 * craters[..., None]) - .06 * ((yy - my + xx - mx) / moon_r)[..., None])
    m += np.exp(-(dist / 330) ** 2)[..., None] * np.array([.25, .27, .3], np.float32)
    poses = [deer_sprite(p) for p in range(4)]
    glow = [Image.fromarray((gaussian_filter(np.asarray(p.getchannel('A'), np.float32), 9) * .9).clip(0, 255).astype(np.uint8)) for p in poses]
    team = [(0, 0), (-330, 34), (-660, 68)]     # follow the leader, a little lower each
    L = 660 + W + 700; rng = np.random.default_rng(5)
    # sparkle trail: particles emitted along the path, period-safe (emission time wraps)
    ne = 900; et = rng.uniform(0, 1, ne); eo = rng.normal(0, 10, (ne, 2)); life = rng.uniform(.08, .22, ne)
    def path(tt):  # lead position for a phase tt in [0,1)
        x = -350 + L * tt; y = H * .50 - 170 * math.sin(TAU * tt * .9 + .4) - (x / W) * 140
        return x, y
    for f in range(N):
        t = f / N
        img = sky(t) + m
        buf = np.zeros((H, W, 3), np.float32)
        age = (t - et) % 1.0; on = age < life
        xs = np.array([path(e)[0] for e in et[on]]) - 140 + eo[on, 0] - age[on] * 260
        ys = np.array([path(e)[1] for e in et[on]]) + 40 + eo[on, 1] + age[on] * 260
        a = (1 - age[on] / life[on]) ** 1.6
        splat(buf, xs, ys, np.tile(np.array([1, .85, .5], np.float32), (on.sum(), 1)), a * 1.3)
        img = img + glowify(buf, .9, 3, 10) * .35
        c = Image.fromarray((np.clip(tone(img, 1.6), 0, 1) ** (1 / 1.1) * 255).astype(np.uint8)).convert('RGBA')
        lx, ly = path(t)
        for i, (dx, dy) in enumerate(team):
            p = (f // 3 + i) % 4                                 # 10 gallop cycles per loop
            x, y = lx + dx, ly + dy + 6 * math.sin(TAU * 20 * t + i)
            sp, g = poses[p], glow[p]
            halo = Image.new('RGBA', sp.size, (255, 190, 90, 0)); halo.putalpha(g)
            c.alpha_composite(halo, (int(x - sp.width / 2), int(y - sp.height / 2)))
            c.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
        yield np.asarray(c.convert('RGB'))

# ---------------------------------------------------------------- 2. gingerbread
BROWN = (176, 102, 48, 255); BROWN_D = (138, 74, 30, 255); ICING = (255, 252, 244, 255)
CANDY = [(220, 40, 50, 255), (40, 160, 80, 255), (250, 200, 50, 255)]

def ginger_man(size=200):
    s = SS; S = size * s; im = Image.new('RGBA', (S, int(S * 1.2)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    u = S / 100; P = lambda x, y: (x * u, y * u)
    def limb(a, b, w):
        d.line([P(*a), P(*b)], fill=BROWN_D, width=int((w + 3) * u));
    shapes = [((50, 52), (14, 44), 22), ((50, 52), (86, 44), 22), ((42, 70), (24, 106), 24), ((58, 70), (76, 106), 24)]
    for a, b, w in shapes:  # outline pass
        d.line([P(*a), P(*b)], fill=BROWN_D, width=int((w + 4) * u))
        for q in (b,): d.ellipse([P(q[0] - (w + 4) / 2, q[1] - (w + 4) / 2), P(q[0] + (w + 4) / 2, q[1] + (w + 4) / 2)], fill=BROWN_D)
    d.ellipse([P(28, 2), P(72, 46)], fill=BROWN_D); d.rounded_rectangle([P(30, 38), P(70, 84)], radius=16 * u, fill=BROWN_D)
    for a, b, w in shapes:
        d.line([P(*a), P(*b)], fill=BROWN, width=int(w * u))
        d.ellipse([P(b[0] - w / 2, b[1] - w / 2), P(b[0] + w / 2, b[1] + w / 2)], fill=BROWN)
    d.ellipse([P(30, 4), P(70, 44)], fill=BROWN); d.rounded_rectangle([P(32, 40), P(68, 82)], radius=14 * u, fill=BROWN)
    # face
    d.ellipse([P(40, 18), P(45, 23)], fill=ICING); d.ellipse([P(55, 18), P(60, 23)], fill=ICING)
    d.arc([P(40, 22), P(60, 36)], 20, 160, fill=ICING, width=int(2.4 * u))
    d.ellipse([P(36, 27), P(41, 31)], fill=(232, 120, 110, 255)); d.ellipse([P(59, 27), P(64, 31)], fill=(232, 120, 110, 255))
    # buttons and icing zigzags
    for i, y in enumerate((50, 60, 70)): d.ellipse([P(46.5, y - 3.5), P(53.5, y + 3.5)], fill=CANDY[i])
    def zig(x0, y0, x1, y1, n=4, amp=3.2):
        pts = []
        for k in range(n + 1):
            tt = k / n; x = x0 + (x1 - x0) * tt; y = y0 + (y1 - y0) * tt
            nx, ny = -(y1 - y0), (x1 - x0); L = math.hypot(nx, ny); nx, ny = nx / L, ny / L
            sg = amp * (1 if k % 2 else -1); pts.append(P(x + nx * sg, y + ny * sg))
        d.line(pts, fill=ICING, width=int(2.2 * u), joint='curve')
    zig(16, 40, 22, 50); zig(84, 40, 78, 50); zig(20, 98, 30, 102, 3); zig(70, 102, 80, 98, 3)
    return shrink(im)

def ginger_star(size=150):
    s = SS; S = size * s; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = S / 2
    def star(r1, r2):
        return [(c + (r1 if k % 2 == 0 else r2) * math.sin(TAU * k / 10), c - (r1 if k % 2 == 0 else r2) * math.cos(TAU * k / 10)) for k in range(10)]
    d.polygon(star(S * .49, S * .23), fill=BROWN_D); d.polygon(star(S * .45, S * .21), fill=BROWN)
    d.line(star(S * .37, S * .17) + [star(S * .37, S * .17)[0]], fill=ICING, width=int(S * .025), joint='curve')
    for k in range(5):
        a = TAU * k / 5; d.ellipse([c + S * .1 * math.sin(a) - S * .025, c - S * .1 * math.cos(a) - S * .025, c + S * .1 * math.sin(a) + S * .025, c - S * .1 * math.cos(a) + S * .025], fill=ICING)
    return shrink(im)

def ginger_heart(size=140):
    s = SS; S = size * s; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def heart(k):
        return [(S / 2 + k * 16 * math.sin(a) ** 3 * S / 36, S * .46 - k * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) * S / 36) for a in np.linspace(0, TAU, 160)]
    d.polygon(heart(1.0), fill=BROWN_D); d.polygon(heart(.93), fill=BROWN)
    d.line(heart(.72) + [heart(.72)[0]], fill=ICING, width=int(S * .028), joint='curve')
    d.ellipse([S * .44, S * .38, S * .56, S * .5], fill=CANDY[0])
    return shrink(im)

def candy_cane(size=170):
    s = SS; S = size * s; im = Image.new('RGBA', (int(S * .6), S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = S * .13; x = S * .42
    path = [(x, S * .96), (x, S * .3)] + [(x - S * .14 + S * .14 * math.cos(a), S * .3 - S * .14 * math.sin(a)) for a in np.linspace(0, math.pi, 30)][1:] + [(S * .14, S * .4)]
    d.line(path, fill=(250, 250, 250, 255), width=int(w), joint='curve')
    m = Image.new('L', im.size, 0); dm = ImageDraw.Draw(m); dm.line(path, fill=255, width=int(w), joint='curve')
    stripes = Image.new('RGBA', im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(stripes)
    for k in range(-20, 40):
        y0 = k * S * .09; ds.polygon([(0, y0), (im.width, y0 - im.width * .6), (im.width, y0 - im.width * .6 + S * .04), (0, y0 + S * .04)], fill=(215, 30, 45, 255))
    stripes.putalpha(Image.fromarray(np.minimum(np.asarray(stripes.getchannel('A')), np.asarray(m))))
    im.alpha_composite(stripes)
    return shrink(im)

def gingerbread():
    from pack4 import fall
    yy, xx = np.mgrid[0:H, 0:W]
    base = gradient([.55, .06, .08], [.28, .02, .04], .6)
    rng = np.random.default_rng(8)
    for _ in range(26):  # soft warm bokeh
        cx, cy, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 140)
        base += (np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)) * rng.uniform(.04, .12))[..., None] * np.array([1, .7, .4], np.float32)
    bg = Image.fromarray((np.clip(tone(base, 1.4), 0, 1) ** (1 / 1.1) * 255).astype(np.uint8))
    sprites = [ginger_man(), ginger_man(), ginger_man(), ginger_star(), ginger_heart(), ginger_star(), candy_cane()]
    # little drop shadow on every sprite
    def shadowed(sp):
        pad = 30; out = Image.new('RGBA', (sp.width + pad * 2, sp.height + pad * 2), (0, 0, 0, 0))
        sh = Image.new('RGBA', sp.size, (40, 0, 0, 0)); sh.putalpha(sp.getchannel('A').point(lambda v: int(v * .45)))
        out.alpha_composite(sh, (pad + 6, pad + 10)); out = out.filter(ImageFilter.GaussianBlur(6)); out.alpha_composite(sp, (pad, pad))
        return out
    sprites = [shadowed(s) for s in sprites]
    yield from fall(bg, sprites, 30, 12, cyc=(1, 1), sway=(20, 70), flip=False, wobble=22, sizes=(140, 250))

# ---------------------------------------------------------------- 3. nutcracker
def nutcracker(step, h=470):
    s = SS; S = h * s; Wd = int(S * .5)
    im = Image.new('RGBA', (Wd, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    u = S / 200; P = lambda x, y: (x * u, y * u)
    RED = (200, 28, 40, 255); RED_D = (150, 16, 28, 255); GOLD = (240, 190, 70, 255); BLACK = (28, 24, 30, 255)
    SKIN = (246, 206, 170, 255); WHITE = (250, 248, 242, 255); BLUE = (40, 70, 160, 255)
    cx = 50
    # legs (alternate lift) and boots
    lift = [(0, -10), (-10, 0), (0, -10), (-10, 0)][step % 4] if step % 2 else (0, 0)
    for i, (lx, dy) in enumerate(((cx - 12, lift[0]), (cx + 12, lift[1]))):
        d.rounded_rectangle([P(lx - 9, 128 + dy), P(lx + 9, 176 + dy)], radius=3 * u, fill=BLUE)
        d.rounded_rectangle([P(lx - 10, 168 + dy), P(lx + 13, 192 + dy)], radius=5 * u, fill=BLACK)
        d.rectangle([P(lx - 10, 166 + dy), P(lx + 10, 170 + dy)], fill=GOLD)
    # jacket
    d.rounded_rectangle([P(cx - 26, 78), P(cx + 26, 136)], radius=8 * u, fill=RED)
    d.rectangle([P(cx - 26, 120), P(cx + 26, 128)], fill=BLACK); d.rectangle([P(cx - 5, 119), P(cx + 5, 129)], fill=GOLD)
    for y in (88, 100, 112): d.ellipse([P(cx - 3, y - 3), P(cx + 3, y + 3)], fill=GOLD)
    d.line([P(cx - 18, 82), P(cx - 18, 118)], fill=GOLD, width=int(1.5 * u)); d.line([P(cx + 18, 82), P(cx + 18, 118)], fill=GOLD, width=int(1.5 * u))
    # arms swing opposite the legs
    sw = (6 if step % 4 < 2 else -6) if step % 2 else 0
    for side in (-1, 1):
        ax = cx + side * 30
        d.rounded_rectangle([P(ax - 7, 82 + sw * side), P(ax + 7, 122 + sw * side)], radius=7 * u, fill=RED_D)
        d.rectangle([P(ax - 7, 80 + sw * side), P(ax + 7, 86 + sw * side)], fill=GOLD)       # epaulette
        d.ellipse([P(ax - 7, 118 + sw * side), P(ax + 7, 132 + sw * side)], fill=WHITE)    # glove
    # head: face, jaw, beard, moustache, cheeks, eyes
    d.rounded_rectangle([P(cx - 20, 40), P(cx + 20, 80)], radius=10 * u, fill=SKIN)
    d.rounded_rectangle([P(cx - 20, 60), P(cx + 20, 84)], radius=8 * u, fill=WHITE)    # beard
    d.rectangle([P(cx - 9, 66), P(cx + 9, 78)], fill=(70, 50, 40, 255))                 # big jaw mouth
    d.rectangle([P(cx - 8, 66), P(cx + 8, 70)], fill=WHITE)                               # teeth
    d.ellipse([P(cx - 16, 56), P(cx, 64)], fill=WHITE); d.ellipse([P(cx, 56), P(cx + 16, 64)], fill=WHITE)  # moustache
    d.ellipse([P(cx - 8, 52), P(cx + 8, 60)], fill=(232, 150, 130, 255))                # nose
    d.ellipse([P(cx - 12, 46), P(cx - 6, 52)], fill=BLACK); d.ellipse([P(cx + 6, 46), P(cx + 12, 52)], fill=BLACK)
    d.ellipse([P(cx - 18, 54), P(cx - 11, 60)], fill=(240, 140, 140, 255)); d.ellipse([P(cx + 11, 54), P(cx + 18, 60)], fill=(240, 140, 140, 255))
    # tall hat with gold band and plume
    d.rounded_rectangle([P(cx - 19, 6), P(cx + 19, 44)], radius=4 * u, fill=BLACK)
    d.rectangle([P(cx - 19, 34), P(cx + 19, 40)], fill=GOLD); d.ellipse([P(cx - 6, 14), P(cx + 6, 26)], fill=GOLD)
    d.ellipse([P(cx - 5, -2), P(cx + 5, 12)], fill=RED)
    return shrink(im)

def nutcrackers():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # red curtain backdrop with soft folds, wooden floor, warm spotlight
    folds = .78 + .22 * np.cos(TAU * xx / 150) ** 2
    curtain = np.stack([.55 * folds, .05 * folds, .08 * folds], -1) * (1 - .35 * (yy / H))[..., None]
    floor_y = int(H * .80)
    wood = np.stack([.42 + .04 * np.sin(yy * .9), .24 + .02 * np.sin(yy * .9), .12 + 0 * yy], -1)
    img = np.where((yy >= floor_y)[..., None], wood * (1 - .3 * (yy - floor_y) / (H - floor_y))[..., None], curtain)
    spot = np.exp(-(((xx - W / 2) / (W * .45)) ** 2 + ((yy - H * .62) / (H * .55)) ** 2))
    img = img * (.55 + .75 * spot[..., None]) + spot[..., None] * np.array([.10, .07, .03], np.float32)
    # garland of lights along the top
    buf = np.zeros((H, W, 3), np.float32); gx = np.arange(30, W, 60, dtype=np.float32); gy = 70 + 70 * np.abs(np.sin(np.pi * gx / 480))
    cols = np.array([[1, .3, .25], [1, .8, .35], [.35, 1, .5], [.4, .6, 1]], np.float32)
    base = Image.fromarray((np.clip(tone(img, 1.3), 0, 1) ** (1 / 1.1) * 255).astype(np.uint8)).convert('RGBA')
    poses = [nutcracker(p) for p in range(4)]
    shadow = Image.new('RGBA', (170, 36), (0, 0, 0, 0)); ImageDraw.Draw(shadow).ellipse([0, 0, 169, 35], fill=(0, 0, 0, 110)); shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    sp_w = 400; n = int(math.ceil((W + sp_w * 2) / sp_w)) + 1; P = n * sp_w
    for f in range(N):
        t = f / N
        b = np.zeros_like(buf)
        tw = .6 + .4 * np.sin(TAU * 2 * t + gx * .05)
        splat(b, gx, gy, cols[(np.arange(len(gx)) + (f // 20)) % 4], tw * 4)
        g = glowify(b, 1.6, 6, 20) * .5
        frame = Image.fromarray(np.clip(np.asarray(base, np.float32)[..., :3] / 255 + g, 0, 1).__mul__(255).astype(np.uint8)).convert('RGBA')
        step = int(t * 16)                                    # 16 steps per loop
        for i in range(n):
            x = (i * sp_w + sp_w * t) % P - sp_w             # moves exactly one spacing per loop -> seamless
            sp = poses[step % 4]; bob = 4 if step % 2 else 0
            y = floor_y + 8 - sp.height - bob
            frame.alpha_composite(shadow, (int(x - shadow.width / 2), floor_y - 4))
            frame.alpha_composite(sp, (int(x - sp.width / 2), int(y)))
        yield np.asarray(frame.convert('RGB'))

# ---------------------------------------------------------------- 4. spiral of lights around a tree (on black)
def tree_spiral():
    cx, top, bot = W / 2, H * .16, H * .9; R = H * .36; turns = 7
    n = 6000; sgrid = np.linspace(0, 1, n, dtype=np.float32)
    cols = np.array([[1, .25, .2], [1, .78, .3], [.3, 1, .45]], np.float32)
    seg = (sgrid * turns * 3).astype(int) % 3
    bulbs = np.linspace(0, 1, 140, dtype=np.float32)
    for f in range(N):
        t = f / N
        th = TAU * turns * sgrid + TAU * t                     # one full turn per loop
        r = R * (1 - sgrid) ** 1.05
        x = cx + r * np.sin(th); y = bot - (bot - top) * sgrid + r * .12 * np.cos(th)
        depth = .35 + .65 * (np.cos(th) * .5 + .5)
        buf = np.zeros((H, W, 3), np.float32)
        splat(buf, x, y, cols[seg] * .6 + .4 * np.array([1, .9, .7], np.float32), depth * .16)
        # two streaks climbing the spiral, 2 trips per loop each
        for k, off in ((2, 0.0), (2, .5)):
            head = (k * t + off) % 1
            d = (head - sgrid) % 1; trail = np.exp(-d / .05) * (d < .3)
            splat(buf, x, y, np.tile(np.array([1, .92, .75], np.float32), (n, 1)), trail * depth * .9)
        # bulbs on the spiral that twinkle
        tb = TAU * turns * bulbs + TAU * t; rb = R * (1 - bulbs) ** 1.05
        bx = cx + rb * np.sin(tb); by = bot - (bot - top) * bulbs + rb * .12 * np.cos(tb)
        tw = (np.sin(TAU * 3 * t + bulbs * 90) * .5 + .5) ** 3
        splat(buf, bx, by, cols[np.arange(140) % 3], (.3 + tw) * (.35 + .65 * (np.cos(tb) * .5 + .5)) * 1.6)
        # star on top
        star = np.zeros_like(buf); splat(star, np.array([cx]), np.array([top - 26]), np.array([[1, .85, .5]], np.float32), np.array([60.0]))
        img = glowify(buf, 1.0, 4, 16) * .55 + glowify(star, 2, 10, 40) * (.30 + .05 * math.sin(TAU * 2 * t))
        # star rays
        yy = np.arange(H, dtype=np.float32)[:, None] - (top - 26); xx = np.arange(W, dtype=np.float32)[None, :] - cx
        ang = np.arctan2(yy, xx); dist = np.hypot(xx, yy) + 1
        rays = (np.cos(ang * 4 + TAU * t * .5) ** 60) * np.exp(-dist / 55) * .7
        img += rays[..., None] * np.array([1, .85, .5], np.float32)
        yield np.clip(img, 0, 1)

# ---------------------------------------------------------------- 5. red-green-gold light streaks (on black)
def light_streaks():
    rng = np.random.default_rng(14)
    xs = np.linspace(-60, W + 60, 4200, dtype=np.float32)
    ribbons = []
    palette = [np.array(c, np.float32) for c in ([1, .22, .18], [1, .75, .28], [.25, .95, .4], [1, .85, .6], [.9, .15, .2], [.4, 1, .55])]
    for i in range(9):
        ribbons.append(dict(y0=H * (.18 + .64 * i / 8) + rng.uniform(-30, 30), A=rng.uniform(50, 140), k=TAU / rng.uniform(900, 1700),
                            m=int(rng.choice([-1, 1])), ph=rng.uniform(0, TAU), col=palette[i % len(palette)], w=rng.uniform(.06, .12),
                            A2=rng.uniform(15, 40), k2=TAU / rng.uniform(300, 600), pulses=int(rng.integers(1, 3)), pp=rng.uniform(0, 1)))
    ns = 260; spx = rng.uniform(0, W, ns); spy = rng.uniform(0, H, ns); spk = rng.integers(1, 4, ns); spp = rng.uniform(0, TAU, ns)
    for f in range(N):
        t = f / N
        buf = np.zeros((H, W, 3), np.float32)
        for r in ribbons:
            y = r['y0'] + r['A'] * np.sin(r['k'] * xs + TAU * r['m'] * t + r['ph']) + r['A2'] * np.sin(r['k2'] * xs - TAU * 2 * r['m'] * t)
            u = (xs + 60) / (W + 120)
            amp = np.full_like(xs, r['w'] * .55)
            for p in range(r['pulses']):          # bright comets running along each streak
                head = (r['pulses'] * t + p / r['pulses'] + r['pp']) % 1
                d = (head - u) % 1; amp += np.exp(-d / .09) * (d < .5) * .9
            splat(buf, xs, y, np.tile(r['col'], (len(xs), 1)), amp)
            splat(buf, xs, y + 2, np.tile(r['col'] * .6 + .4, (len(xs), 1)), amp * .25)
        tw = (np.sin(TAU * spk * t + spp) * .5 + .5) ** 6
        splat(buf, spx, spy, np.tile(np.array([1, .9, .7], np.float32), (ns, 1)), tw * 1.4)
        img = glowify(buf, 1.0, 5, 22) * .6
        yield np.clip(img, 0, 1)

C = {
 'flying-reindeer-night-sky-loop': (reindeer, 1),
 'gingerbread-cookies-falling-loop': (gingerbread, 1),
 'nutcracker-soldiers-marching-loop': (nutcrackers, 1),
 'christmas-tree-light-spiral-loop': (tree_spiral, 0),
 'red-green-gold-light-streaks-loop': (light_streaks, 0),
}

if __name__ == '__main__':
    for name in sys.argv[1:]:
        gen, mode = C[name]
        if mode == 0: encode(name, gen())
        else: encode_raw(name, gen())
        print('done', name, flush=True)

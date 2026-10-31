"""Clips 62-101: holidays coming up + general. Usage: python3 pack4.py <name> ... (run from output folder)"""
import numpy as np, math, sys, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter
from pack import W, H, N, TAU, gradient, blob, tone, bokeh, flow, encode
from pack2 import encode_raw, GREEN, hsv, confetti, sparkles, balloons, countdown
from pack3 import to_img, bokeh_bg, tile_noise, lantern_sprite, petal, chinese_lanterns
from xmas import splat, glowify

GREEN8 = tuple(int(v * 255) for v in GREEN)
FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'

def green_img(): return Image.new('RGB', (W, H), GREEN8)
def u8(arr): return (np.clip(arr, 0, 1) ** (1 / 1.1) * 255).astype(np.uint8)

# ---------------------------------------------------------------- generic sprite motion
def fall(base, sprites, n, seed, cyc=(1, 2), sway=(20, 80), spin=(1, 2), flip=True, wobble=None, rise=False, sizes=(40, 90)):
    """sprites move down (or up) and wrap; spin = whole turns per loop, wobble = degrees of gentle rocking instead."""
    rng = np.random.default_rng(seed); M = 160; span = H + 2 * M
    ps = []
    for i in range(n):
        sz = rng.uniform(*sizes); spr = sprites[rng.integers(len(sprites))]
        s = spr.resize((int(sz), max(2, int(sz * spr.height / spr.width))), Image.LANCZOS)
        ps.append((s, rng.uniform(0, W), rng.uniform(0, span), int(rng.integers(cyc[0], cyc[1] + 1)), rng.uniform(*sway),
                   rng.uniform(0, TAU), int(rng.integers(spin[0], spin[1] + 1)) * rng.choice([-1, 1]), int(rng.integers(1, 4)), sz))
    ps.sort(key=lambda p: p[8])
    for f in range(N):
        t = f / N; c = base.convert('RGBA')
        for s, x0, y0, k, sw, ph, sp, fl, sz in ps:
            y = (y0 + (-1 if rise else 1) * k * span * t) % span - M
            x = x0 + sw * math.sin(TAU * t + ph)
            im = s
            if flip:
                sx = abs(math.cos(TAU * fl * t + ph)) * .8 + .2
                im = im.resize((max(2, int(im.width * sx)), im.height))
            ang = wobble * math.sin(TAU * t + ph) if wobble is not None else math.degrees(TAU * sp * t + ph)
            im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
            c.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
        yield np.asarray(c.convert('RGB'))

def hang(base, sprites, cfg, seed, string=(180, 150, 80, 255), amp=(2.5, 5)):
    """sprites hanging on strings from the top, rocking gently. cfg = [(fx, fy, height)]"""
    rng = np.random.default_rng(seed)
    items = []
    for i, (fx, fy, h) in enumerate(cfg):
        spr = sprites[i % len(sprites)]; s = spr.resize((int(h * spr.width / spr.height), int(h)), Image.LANCZOS)
        items.append((fx * W, fy * H, s, rng.uniform(*amp), int(rng.integers(1, 3)), rng.uniform(0, TAU)))
    items.sort(key=lambda it: it[2].height)
    for f in range(N):
        t = f / N; c = base.convert('RGBA'); d = ImageDraw.Draw(c)
        for x, y, s, a, k, ph in items:
            ang = a * math.sin(TAU * k * t + ph)
            d.line([(x, 0), (x, y)], fill=string, width=2)
            r = s.rotate(ang, resample=Image.BICUBIC, center=(s.width / 2, 0))
            c.alpha_composite(r, (int(x - s.width / 2), int(y)))
        yield np.asarray(c.convert('RGB'))

def with_glow(im, col, rad, strength=1.0):
    pad = int(rad * 2.5); big = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    a = im.getchannel('A'); g = Image.new('RGBA', im.size, col + (0,)); g.putalpha(a.point(lambda v: int(v * strength)))
    big.alpha_composite(g, (pad, pad)); big = big.filter(ImageFilter.GaussianBlur(rad)); big.alpha_composite(im, (pad, pad))
    return big

# ---------------------------------------------------------------- sprites
def coin(hole=True, col=(232, 180, 50)):
    S = 220; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    dark = tuple(int(v * .72) for v in col); light = tuple(min(255, int(v * 1.15) + 20) for v in col)
    d.ellipse([4, 4, S - 4, S - 4], fill=dark + (255,)); d.ellipse([16, 16, S - 16, S - 16], fill=col + (255,))
    d.ellipse([34, 34, S - 34, S - 34], outline=dark + (255,), width=6)
    if hole: d.rectangle([S * .4, S * .4, S * .6, S * .6], fill=(0, 0, 0, 0)); d.rectangle([S * .4 - 6, S * .4 - 6, S * .6 + 6, S * .6 + 6], outline=dark + (255,), width=6)
    else: d.ellipse([S * .3, S * .3, S * .7, S * .7], outline=light + (255,), width=5)
    d.arc([20, 20, S - 20, S - 20], 200, 260, fill=(255, 245, 200, 230), width=8)
    return im

def shamrock(col):
    S = 240; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2; sc = 3.1
    d.line([(c, c), (c + 22, c + 108)], fill=tuple(int(v * .75) for v in col) + (255,), width=10)
    for k in range(3):
        a0 = math.radians(-90 + 120 * k); ux, uy = math.cos(a0), math.sin(a0); vx, vy = -uy, ux
        pts = []
        for i in range(80):
            a = TAU * i / 80; hx = 16 * math.sin(a) ** 3; hy = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
            up = (hy + 17) * sc * .95; lat = hx * sc * .85
            pts.append((c + ux * up + vx * lat, c + uy * up + vy * lat))
        d.polygon(pts, fill=col + (255,))
        d.line([(c, c), (c + ux * 60, c + uy * 60)], fill=tuple(min(255, int(v * 1.25)) for v in col) + (160,), width=3)
    return im

def plum(col):
    S = 200; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    for k in range(5):
        a = math.radians(-90 + 72 * k); px, py = c + 46 * math.cos(a), c + 46 * math.sin(a)
        d.ellipse([px - 40, py - 40, px + 40, py + 40], fill=col + (245,))
    d.ellipse([c - 22, c - 22, c + 22, c + 22], fill=tuple(int(v * .8) for v in col) + (255,))
    for k in range(10):
        a = math.radians(36 * k); d.line([(c, c), (c + 34 * math.cos(a), c + 34 * math.sin(a))], fill=(255, 220, 120, 255), width=3)
        d.ellipse([c + 34 * math.cos(a) - 5, c + 34 * math.sin(a) - 5, c + 34 * math.cos(a) + 5, c + 34 * math.sin(a) + 5], fill=(255, 210, 80, 255))
    return im

def egg(col, band, seed):
    rng = np.random.default_rng(seed); S = 200; Hh = 260
    im = Image.new('RGBA', (S, Hh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(S / 2 + S * .46 * math.sin(a) * (1 - .12 * math.cos(a)), Hh * .52 - Hh * .46 * math.cos(a)) for a in np.linspace(0, TAU, 120)]
    d.polygon(pts, fill=col + (255,))
    mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).polygon(pts, fill=255)
    deco = Image.new('RGBA', im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(deco)
    y = Hh * rng.uniform(.4, .55)
    dd.line([(x, y + (14 if (x // 25) % 2 else -14)) for x in range(-25, S + 50, 25)], fill=band + (255,), width=12)
    for k in range(7):
        x, yy = rng.uniform(25, S - 25), rng.uniform(30, Hh * .35); dd.ellipse([x - 8, yy - 8, x + 8, yy + 8], fill=band + (255,))
    for k in range(7):
        x, yy = rng.uniform(25, S - 25), rng.uniform(Hh * .65, Hh * .9); dd.ellipse([x - 9, yy - 9, x + 9, yy + 9], fill=(255, 255, 255, 230))
    im.paste(deco, (0, 0), Image.composite(deco.getchannel('A'), Image.new('L', im.size, 0), mask))
    ImageDraw.Draw(im).ellipse([S * .26, Hh * .16, S * .4, Hh * .3], fill=(255, 255, 255, 110))
    return im

def snowflake(col=(235, 245, 255)):
    S = 240; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    for k in range(6):
        a = math.radians(60 * k); ex, ey = c + 108 * math.cos(a), c + 108 * math.sin(a)
        d.line([(c, c), (ex, ey)], fill=col + (255,), width=9)
        for r, L in ((.45, 34), (.72, 24)):
            bx, by = c + 108 * r * math.cos(a), c + 108 * r * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(55); d.line([(bx, by), (bx + L * math.cos(b), by + L * math.sin(b))], fill=col + (255,), width=7)
    d.ellipse([c - 16, c - 16, c + 16, c + 16], fill=col + (255,))
    return with_glow(im, (180, 210, 255), 6, .8)

def fanous(body=(255, 170, 60), seed=0):
    S = 4; w, h = 120, 300; im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    g = (205, 160, 70, 255); gd = (150, 110, 40, 255); X = lambda v: v * S
    d.ellipse([X(52), X(0), X(68), X(16)], outline=g, width=X(3))
    d.polygon([(X(60), X(14)), (X(22), X(70)), (X(98), X(70))], fill=g)                      # dome
    d.rectangle([X(16), X(68), X(104), X(78)], fill=gd)
    glass = body + (255,)
    d.polygon([(X(22), X(78)), (X(98), X(78)), (X(108), X(170)), (X(12), X(170))], fill=glass)   # body
    for xx in (40, 60, 80): d.line([(X(xx), X(78)), (X(xx + (xx - 60) * .3), X(170))], fill=gd, width=X(3))
    for yy in (110, 140): d.line([(X(18), X(yy)), (X(102), X(yy))], fill=gd, width=X(2))
    d.ellipse([X(35), X(95), X(85), X(160)], fill=(255, 245, 190, 140))
    d.rectangle([X(8), X(170), X(112), X(180)], fill=gd)
    d.polygon([(X(14), X(180)), (X(106), X(180)), (X(60), X(240))], fill=g)                  # bottom cone
    d.line([(X(60), X(240)), (X(60), X(262))], fill=g, width=X(3)); d.ellipse([X(54), X(258), X(66), X(270)], fill=g)
    im = im.resize((w, h), Image.LANCZOS)
    return with_glow(im, body, 18, .9)

def tulip(col, seed):
    S = 120; im = Image.new('RGBA', (S, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    dark = tuple(int(v * .75) for v in col)
    d.polygon([(20, 40), (30, 120), (90, 120), (100, 40), (80, 70), (60, 20), (40, 70)], fill=col + (255,))
    d.polygon([(45, 120), (60, 30), (75, 120)], fill=dark + (255,))
    d.ellipse([20, 70, 100, 140], fill=col + (255,))
    return im

# ---------------------------------------------------------------- scenes
def lantern_festival():
    base = to_img(bokeh_bg([.03, .01, .05], [.10, .03, .06], [[1, .6, .2], [1, .4, .2], [1, .85, .5]], 111, 40, .12))
    sprites = []
    for h in (90, 110, 130):
        im, gl = lantern_sprite(h); c = gl.copy(); c.alpha_composite(im); sprites.append(c)
    return fall(base, sprites, 34, 112, cyc=(1, 1), sway=(15, 50), flip=False, wobble=6, rise=True, sizes=(50, 150))

def coins_red():
    base = to_img(bokeh_bg([.12, .0, .01], [.28, .02, .03], [[1, .75, .25], [1, .5, .2]], 113, 40, .12))
    return fall(base, [coin(True), coin(True, (240, 195, 70))], 60, 114, cyc=(1, 2), sizes=(50, 110))

def coins_gold_green():
    base = to_img(bokeh_bg([.0, .08, .03], [.02, .20, .08], [[1, .85, .3], [.4, 1, .5]], 115, 40, .12))
    return fall(base, [coin(False), coin(False, (245, 200, 60))], 60, 116, cyc=(1, 2), sizes=(50, 110))

def plum_blossoms():
    base = to_img(bokeh_bg([.20, .01, .03], [.42, .04, .06], [[1, .75, .3], [1, .5, .5]], 117, 35, .10))
    cols = [(250, 120, 150), (255, 160, 180), (235, 70, 110), (255, 200, 210)]
    return fall(base, [plum(c) for c in cols], 70, 118, cyc=(1, 2), sizes=(30, 75))

def shamrocks():
    base = to_img(bokeh_bg([.0, .06, .02], [.01, .16, .06], [[.5, 1, .4], [1, .85, .3], [.3, .9, .4]], 119, 45, .12))
    cols = [(40, 170, 70), (70, 200, 90), (25, 140, 55), (110, 210, 100)]
    return fall(base, [shamrock(c) for c in cols], 50, 120, cyc=(1, 2), sizes=(60, 140))

def rose_petals(green=False):
    cols = [(200, 20, 40), (225, 40, 60), (170, 10, 30), (240, 70, 90)]
    base = green_img() if green else to_img(bokeh_bg([.08, .0, .02], [.20, .02, .05], [[1, .3, .4], [1, .6, .6]], 121, 35, .10))
    return fall(base, [petal(c) for c in cols], 70, 122, cyc=(1, 2), sizes=(55, 120))

def easter_eggs():
    base = to_img(bokeh_bg([.70, .88, .98], [.98, .93, .80], [[1, 1, 1], [1, .9, .95]], 123, 25, .06, light=True))
    pal = [((255, 190, 200), (255, 120, 150)), ((180, 220, 255), (90, 150, 240)), ((255, 235, 150), (250, 170, 60)),
           ((190, 240, 190), (90, 190, 110)), ((220, 200, 255), (150, 110, 230))]
    eggs = [egg(a, b, i) for i, (a, b) in enumerate(pal)]
    return fall(base, eggs, 34, 124, cyc=(1, 1), flip=False, wobble=25, sizes=(60, 120))

def snowflakes(green=False):
    base = green_img() if green else to_img(bokeh_bg([.04, .10, .25], [.10, .25, .45], [[.7, .85, 1], [1, 1, 1]], 125, 35, .10))
    sp = [snowflake(), snowflake((210, 230, 255))]
    return fall(base, sp, 55 if not green else 45, 126, cyc=(1, 1), flip=False, spin=(1, 1), sizes=(30, 110))

def rising_particles(cols, top, bot, seed, n=240):
    rng = np.random.default_rng(seed); bg = gradient(top, bot, .55); M = 40; span = H + 2 * M
    ps = [(rng.uniform(0, W), rng.uniform(0, span), rng.uniform(2, 9) if rng.uniform() < .85 else rng.uniform(14, 30),
           int(rng.integers(1, 3)), rng.uniform(15, 70), rng.uniform(0, TAU), int(rng.integers(1, 4)), np.array(cols[rng.integers(len(cols))]))
          for _ in range(n)]
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, r, cyc, sw, ph, tw, col in ps:
            y = (y0 - cyc * span * t) % span - M; x = x0 + sw * math.sin(TAU * t + ph)
            b = (.6 + .4 * math.sin(TAU * tw * t + ph)) * (1.6 if r < 10 else .35)
            blob(img, x, y, r, col, b, edge=.6 if r < 10 else .25, glow=1.0 if r < 10 else .2, rim=0)
        yield tone(img, 1.7)

def champagne():
    rng = np.random.default_rng(127); bg = gradient([.03, .02, .0], [.12, .08, .02], .5); M = 30; span = H + 2 * M
    streams = [rng.uniform(0, W) for _ in range(26)]
    ps = []
    for sx in streams:
        k = int(rng.integers(2, 4)); n = int(rng.integers(10, 20)); r0 = rng.uniform(3, 9)
        for j in range(n): ps.append((sx, j / n * span, r0 * rng.uniform(.6, 1.2), k, rng.uniform(0, TAU)))
    for _ in range(40): ps.append((rng.uniform(0, W), rng.uniform(0, span), rng.uniform(10, 22), 1, rng.uniform(0, TAU)))
    col = np.array([1, .82, .45])
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, r, k, ph in ps:
            y = (y0 - k * span * t) % span - M; x = x0 + 6 * math.sin(TAU * 3 * t + ph + y / 80)
            blob(img, x, y, r, col, .9, edge=.25, glow=.3, rim=.9)
            blob(img, x - r * .35, y - r * .35, max(1.5, r * .25), np.array([1, 1, 1]), .8, edge=1, glow=0, rim=0)
        yield tone(img, 1.7)

def rain():
    rng = np.random.default_rng(129); M = 200; span = H + 2 * M
    drops = [(rng.uniform(-200, W + 200), rng.uniform(0, span), rng.uniform(30, 90), int(rng.integers(3, 7)), rng.uniform(.25, 1)) for _ in range(500)]
    for f in range(N):
        t = f / N; im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
        for x0, y0, L, k, b in drops:
            y = (y0 + k * span * t) % span - M; x = x0 + (y - y0) * .12
            d.line([(x, y), (x + L * .12, y + L)], fill=int(250 * b), width=3 if b > .6 else 2)
        a = np.asarray(im.filter(ImageFilter.GaussianBlur(.6)), np.float32) / 255
        img = np.stack([a * .78, a * .85, a], -1) + np.array([.01, .012, .02])
        yield np.clip(img, 0, 1)

def sky_clouds(top, bot, ctint, seed, sun=None):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = gradient(top, bot, .15)
    if sun is not None:
        sx, sy, sc = sun; d = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
        sky = sky + (np.exp(-(d / 60) ** 2) * 1.2 + np.exp(-(d / 400) ** 2) * .35)[..., None] * np.array(sc)
    c1 = tile_noise(W, H, seed, 6); c2 = tile_noise(W, H, seed + 1, 6)
    fade = np.clip(1.15 - yy / H, 0, 1)
    for f in range(N):
        t = f / N
        a1 = np.clip((np.roll(c1, int(W * t), 1) - .48) * 2.4, 0, 1) * fade
        a2 = np.clip((np.roll(c2, int(2 * W * t) % W, 1) - .52) * 2.4, 0, 1) * fade
        img = sky.copy()
        for a, tint in ((a1, np.array(ctint) * .9), (a2, np.array(ctint))):
            shade = 1 - .25 * np.clip(np.roll(a, -18, 0) - a, 0, 1)
            img = img * (1 - a[..., None] * .85) + a[..., None] * .85 * tint * shade[..., None]
        yield np.clip(img, 0, 1)

def nebula():
    rng = np.random.default_rng(131); n1 = tile_noise(W, H, 132, 6); n2 = tile_noise(W, H, 133, 6)
    stars = np.zeros((H, W), np.float32); sx = rng.integers(0, W, 900); sy = rng.integers(0, H, 900)
    sb = rng.uniform(.2, 1, 900) ** 2; tw = rng.integers(1, 4, 900); tp = rng.uniform(0, TAU, 900)
    for f in range(N):
        t = f / N
        a = np.roll(n1, int(W * t), 1) ** 2.2; b = np.roll(n2, -int(W * t) % W, 1) ** 2.5
        img = np.array([.01, .005, .03]) + a[..., None] * np.array([.55, .15, .65]) + b[..., None] * np.array([.10, .30, .75])
        st = np.zeros((H, W), np.float32); np.add.at(st, (sy, sx), sb * (.5 + .5 * np.sin(TAU * tw * t + tp)))
        img = img + gaussian_filter(st, .8)[..., None] * 3
        yield tone(img, 1.5)

def rainbow_hills():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = gradient([.35, .62, .95], [.78, .90, 1.0], .1)
    cx, cy, R = W * .5, H * 1.05, H * .85
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    cols = [(1, .2, .2), (1, .55, .1), (1, .9, .2), (.2, .8, .3), (.2, .5, 1), (.45, .3, .9)]
    rb = np.zeros((H, W, 3), np.float32); bw = 26
    for i, c in enumerate(cols):
        rr = R - i * bw; rb += np.exp(-((d - rr) / (bw * .55)) ** 2)[..., None] * np.array(c)
    sky = sky * (1 - .55 * np.clip(rb.max(-1, keepdims=True), 0, 1)) + rb * .55
    hills = Image.new('RGBA', (W, H), (0, 0, 0, 0)); hd = ImageDraw.Draw(hills)
    for k, (base_y, amp, col) in enumerate([(.70, 60, (90, 170, 70)), (.80, 50, (60, 150, 60)), (.90, 40, (40, 125, 50))]):
        pts = [(x, H * base_y - amp * math.sin(x / W * (3 + k) + k) - 20 * math.sin(x / 140 + k)) for x in range(0, W + 20, 20)]
        hd.polygon(pts + [(W, H), (0, H)], fill=col + (255,))
    hm = np.asarray(hills, np.float32) / 255
    c1 = tile_noise(W, H, 135, 6); fade = np.clip(1 - yy / (H * .65), 0, 1)
    for f in range(N):
        t = f / N; a = np.clip((np.roll(c1, int(W * t), 1) - .5) * 2.6, 0, 1) * fade
        img = sky * (1 - a[..., None] * .9) + a[..., None] * .9 * np.array([1, 1, 1])
        img = img * (1 - hm[..., 3:]) + hm[..., :3] * hm[..., 3:]
        yield np.clip(img, 0, 1)

def crescent_scene(lanterns=True, green=False, bgcol=([.0, .03, .08], [.02, .12, .18])):
    rng = np.random.default_rng(137); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if green:
        base = green_img()
    else:
        sky = gradient(*bgcol, .45)
        mx, my, r = W * .5, H * .3, 120
        d1 = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2); d2 = np.sqrt((xx - mx - 50) ** 2 + (yy - my + 25) ** 2)
        cres = np.clip((r - d1) / 1.5, 0, 1) * np.clip((d2 - r * .88) / 1.5, 0, 1)
        glow = gaussian_filter(cres, 30) * 1.4 + gaussian_filter(cres, 90) * 1.2
        sky = sky + cres[..., None] * np.array([1, .88, .55]) + glow[..., None] * np.array([1, .8, .4]) * .5
        base_arr = sky
    if not green:
        nb = 500; sx = rng.integers(0, W, nb); sy = rng.integers(0, int(H * .9), nb); sb = rng.uniform(.2, 1, nb) ** 2
        tw = rng.integers(1, 4, nb); tp = rng.uniform(0, TAU, nb)
    sprites = [fanous((255, 170, 60)), fanous((255, 120, 70)), fanous((90, 200, 220)), fanous((255, 210, 90))]
    cfg = [(.07, .02, 300), (.2, .1, 380), (.35, .0, 270), (.65, .02, 290), (.8, .1, 390), (.93, .0, 300), (.27, .48, 200), (.73, .48, 210)] if lanterns else []
    rng2 = np.random.default_rng(138)
    items = []
    for i, (fx, fy, hgt) in enumerate(cfg):
        s = sprites[i % 4]; s = s.resize((int(hgt * s.width / s.height), int(hgt)), Image.LANCZOS)
        items.append((fx * W, fy * H, s, rng2.uniform(2.5, 5), int(rng2.integers(1, 3)), rng2.uniform(0, TAU)))
    for f in range(N):
        t = f / N
        if green: c = base.convert('RGBA')
        else:
            st = np.zeros((H, W), np.float32); np.add.at(st, (sy, sx), sb * (.5 + .5 * np.sin(TAU * tw * t + tp)))
            c = Image.fromarray(u8(base_arr + gaussian_filter(st, .8)[..., None] * 3)).convert('RGBA')
        d = ImageDraw.Draw(c)
        for x, y, s, a, k, ph in items:
            ang = a * math.sin(TAU * k * t + ph)
            d.line([(x, 0), (x, y + s.height * .08)], fill=(190, 150, 70, 255), width=2)
            r = s.rotate(ang, resample=Image.BICUBIC, center=(s.width / 2, s.height * .06))
            c.alpha_composite(r, (int(x - s.width / 2), int(y)))
        yield np.asarray(c.convert('RGB'))

def geometric():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    T = 150; im = Image.new('L', (W + T, H + T), 0); d = ImageDraw.Draw(im)
    for gy in range(-1, H // T + 2):
        for gx in range(-1, W // T + 2):
            cx, cy = gx * T + T / 2, gy * T + T / 2; r = T * .42
            sq1 = [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)]
            sq2 = [(cx, cy - r * 1.414), (cx + r * 1.414, cy), (cx, cy + r * 1.414), (cx - r * 1.414, cy)]
            d.polygon(sq1, outline=255, width=3); d.polygon(sq2, outline=255, width=3)
            d.ellipse([cx - r * .45, cy - r * .45, cx + r * .45, cy + r * .45], outline=255, width=2)
            d.line([(cx + T / 2, cy - 6), (cx + T / 2, cy + 6)], fill=255, width=2)
    lines = np.asarray(im.filter(ImageFilter.GaussianBlur(.7)), np.float32)[:H, :W] / 255
    bg = gradient([.0, .07, .09], [.01, .14, .16], .5)
    gold = np.array([1, .78, .35])
    for f in range(N):
        t = f / N
        band = np.exp(-(((xx + yy * .6) / W - (t * 2 % 1) * 2.0 + .3) / .12) ** 2)
        band = band + np.exp(-(((xx + yy * .6) / W - ((t * 2 + .5) % 1) * 1.6 + .3) / .12) ** 2) * .0
        img = bg + lines[..., None] * gold * (.45 + 1.1 * band[..., None]) + gaussian_filter(lines * band, 6)[..., None] * gold * 1.2
        yield tone(img, 1.6)

def tulips():
    rng = np.random.default_rng(141)
    sky = to_img(bokeh_bg([.45, .70, .98], [.90, .94, 1.0], [[1, 1, 1]], 142, 15, .05, light=True))
    cols = [(230, 40, 60), (255, 110, 150), (250, 200, 50), (170, 80, 200), (255, 140, 40), (250, 250, 245)]
    rows = []
    for r, (y, n, sz) in enumerate([(.62, 30, 50), (.75, 24, 70), (.92, 16, 100)]):
        for i in range(n):
            rows.append((rng.uniform(-.02, 1.02) * W, H * y + rng.uniform(-20, 20), sz * rng.uniform(.85, 1.15), cols[rng.integers(len(cols))], rng.uniform(0, TAU), r))
    rows.sort(key=lambda q: q[1])
    heads = {}
    for x, y, sz, col, ph, r in rows: heads[(col, int(sz))] = tulip(col, 0).resize((int(sz), int(sz * 1.25)), Image.LANCZOS)
    ground = (60, 140, 50)
    for f in range(N):
        t = f / N; c = sky.copy().convert('RGBA'); d = ImageDraw.Draw(c)
        d.rectangle([0, H * .6, W, H], fill=(95, 165, 70, 255))
        for x, y, sz, col, ph, r in rows:
            sway = math.sin(TAU * t + x / 300 + ph * .3) * sz * .18
            L = sz * 2.2; tx, ty = x + sway, y - L
            d.line([(x, y), ((x + tx) / 2 + sway * .2, (y + ty) / 2), (tx, ty)], fill=(50, 120, 45, 255), width=max(2, int(sz / 12)), joint='curve')
            d.polygon([(x, y), (x - sz * .45, y - L * .45), (x - sz * .05, y - L * .1)], fill=(70, 150, 60, 255))
            hdimg = heads[(col, int(sz))].rotate(-sway * .6, resample=Image.BICUBIC, expand=True)
            c.alpha_composite(hdimg, (int(tx - hdimg.width / 2), int(ty - hdimg.height * .75)))
        yield np.asarray(c.convert('RGB'))

def flames(img, pts, t, size=1.0, col=(1, .7, .25)):
    for i, (x, y, s) in enumerate(pts):
        fl = 1 + .12 * math.sin(TAU * 5 * t + i * 1.7) + .07 * math.sin(TAU * 9 * t + i * 2.3)
        sway = 2.5 * math.sin(TAU * 4 * t + i)
        h = 26 * s * size * fl; w = 9 * s * size
        R = max(w * 3, h * 1.3)
        x0b, x1b, y0b, y1b = max(0, int(x - R)), min(W, int(x + R)), max(0, int(y - h * 1.9)), min(H, int(y + h * .9))
        sx, sy = np.meshgrid(np.arange(x0b, x1b, dtype=np.float32), np.arange(y0b, y1b, dtype=np.float32))
        u = (sx - x - sway * np.clip((y - sy) / h, 0, 1)) / w; v = (y - sy) / h
        shape = np.exp(-(u / (1 - np.clip(v, 0, 1) * .85 + .05)) ** 2 * 1.5) * np.exp(-((v - .45) / .55) ** 2 * 2.2) * (v > -.15)
        core = np.exp(-(u / .5) ** 2 * 2) * np.exp(-((v - .25) / .25) ** 2)
        glow = np.exp(-((sx - x) ** 2 + (sy - y + h * .4) ** 2) / (h * .42) ** 2) * .45
        img[y0b:y1b, x0b:x1b] += shape[..., None] * np.array(col) * 1.4 + core[..., None] * np.array([1, .95, .8]) * .9 + glow[..., None] * np.array(col)

def menorah():
    rng = np.random.default_rng(143)
    bg = bokeh_bg([.01, .03, .10], [.03, .08, .22], [[.4, .6, 1], [.8, .85, 1], [.3, .45, .9]], 144, 45, .12)
    sil = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sil); cx = W / 2; by = H * .62
    d.rectangle([cx - 150, H * .9, cx + 150, H * .93], fill=255); d.polygon([(cx - 60, H * .9), (cx + 60, H * .9), (cx + 14, H * .82), (cx - 14, H * .82)], fill=255)
    d.rectangle([cx - 10, by - 40, cx + 10, H * .84], fill=255)
    tops = []
    for k in range(1, 5):
        r = 95 * k
        d.arc([cx - r, by - r, cx + r, by + r], 0, 180, fill=255, width=14)
        tops += [(cx - r, by), (cx + r, by)]
    tops.append((cx, by - 60))
    for x, y in tops: d.rectangle([x - 20, y - 8, x + 20, y + 4], fill=255)
    m = (np.asarray(sil.filter(ImageFilter.GaussianBlur(.8)), np.float32) / 255)[..., None]
    gold = np.array([.95, .75, .35])
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    shade = (1 - .35 * (yy / H))[..., None]
    base = bg * (1 - m) + m * gold * shade
    cand = Image.new('L', (W, H), 0); cd = ImageDraw.Draw(cand); fpts = []
    for x, y in tops:
        hgt = 70 if y < by - 30 else 58
        cd.rectangle([x - 8, y - 8 - hgt, x + 8, y - 8], fill=255); fpts.append((x, y - 8 - hgt - 4, 1.0))
    cm = (np.asarray(cand.filter(ImageFilter.GaussianBlur(.6)), np.float32) / 255)[..., None]
    base = base * (1 - cm) + cm * np.array([.92, .95, 1.0])
    for f in range(N):
        t = f / N; img = base.copy(); flames(img, fpts, t, 1.0)
        yield tone(img, 1.3)

def diyas():
    rng = np.random.default_rng(145)
    bg = bokeh_bg([.08, .01, .05], [.22, .04, .06], [[1, .6, .15], [1, .4, .3], [1, .8, .3], [.9, .3, .6]], 146, 50, .13)
    lamp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lamp); fpts = []
    xs = np.linspace(W * .08, W * .92, 7)
    for i, x in enumerate(xs):
        y = H * (.74 if i % 2 == 0 else .66); s = 1.15 if i % 2 == 0 else .95; w = 105 * s
        d.chord([x - w, y - w * .75, x + w, y + w * .55], 0, 180, fill=(170, 75, 35, 255))
        d.polygon([(x + w * .95, y - 2), (x + w * 1.25, y - w * .18), (x + w * .9, y + 6)], fill=(170, 75, 35, 255))
        d.chord([x - w * .92, y - w * .2, x + w * .92, y + w * .12], 0, 180, fill=(120, 45, 20, 255))
        for k in range(9):
            a = math.radians(15 + k * 18.5); px, py = x + w * .75 * math.cos(a), y + w * .32 * math.sin(a) + 6
            d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=[(255, 200, 60), (230, 60, 90), (60, 170, 220)][k % 3] + (255,))
        d.ellipse([x - w, y - 10, x + w, y + 12], fill=(205, 110, 50, 255)); d.ellipse([x - w * .85, y - 6, x + w * .85, y + 8], fill=(150, 60, 25, 255))
        fpts.append((x + w * 1.12, y - w * .18, 2.6 * s))
    lm = np.asarray(lamp, np.float32) / 255
    base = bg * (1 - lm[..., 3:]) + lm[..., :3] * lm[..., 3:]
    for f in range(N):
        t = f / N; img = base.copy(); flames(img, fpts, t, 1.0, (1, .62, .2))
        yield tone(img, 1.3)

def holi():
    rng = np.random.default_rng(147); T = 1.0; w, h = W // 4, H // 4
    cols = [hsv(x, .85) for x in (.95, .08, .14, .33, .52, .62, .8, .88)]
    bursts = []
    for i in range(10):
        t0 = i / 10 + rng.uniform(-.03, .03); cx, cy = rng.uniform(.15, .85) * w, rng.uniform(.25, .75) * h
        n = 70; ang = rng.uniform(0, TAU, n); sp = rng.uniform(.2, 1, n) * rng.uniform(60, 95)
        bursts.append((t0, cx, cy, np.cos(ang) * sp, np.sin(ang) * sp * .7, cols[i % len(cols)], rng.uniform(4, 9, n)))
    bg = gradient([.06, .03, .08], [.10, .05, .10], .5)
    small_bg = np.asarray(Image.fromarray((bg * 255).astype(np.uint8)).resize((w, h)), np.float32) / 255
    life = .45
    for f in range(N):
        t = f / N; buf = np.zeros((h, w, 3), np.float32)
        for t0, cx, cy, vx, vy, col, rs in bursts:
            for tl in (t0, t0 - 1, t0 + 1):
                a = (t - tl) / life
                if 0 <= a < 1:
                    e = 1 - (1 - a) ** 3
                    for j in range(len(vx)):
                        px, py = cx + vx[j] * e, cy + vy[j] * e - 8 * a; r = rs[j] * (1 + 2.2 * a)
                        x0b, x1b, y0b, y1b = int(max(0, px - 2 * r)), int(min(w, px + 2 * r)), int(max(0, py - 2 * r)), int(min(h, py + 2 * r))
                        if x0b >= x1b or y0b >= y1b: continue
                        gx, gy = np.meshgrid(np.arange(x0b, x1b, dtype=np.float32), np.arange(y0b, y1b, dtype=np.float32))
                        buf[y0b:y1b, x0b:x1b] += np.exp(-((gx - px) ** 2 + (gy - py) ** 2) / r ** 2)[..., None] * col * (1 - a) ** 1.3 * .35
        big = np.asarray(Image.fromarray((np.clip(1 - np.exp(-buf * 2.2), 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
        yield np.clip(bg + big, 0, 1)

def tree_forest():
    rng = np.random.default_rng(149)
    sky = gradient([.01, .02, .07], [.08, .12, .25], .4)
    st = np.zeros((H, W), np.float32)
    for _ in range(400): st[int(rng.uniform(0, H * .6)), int(rng.uniform(0, W))] = rng.uniform(.3, 1)
    sky = sky + gaussian_filter(st, .7)[..., None] * 2.5
    im = Image.fromarray((np.clip(sky, 0, 1) * 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im)
    for layer, (n, base_y, hmin, hmax, col, snowc) in enumerate([(26, .72, 160, 260, (25, 45, 60), (150, 170, 200)), (20, .84, 220, 340, (15, 32, 40), (200, 215, 235)), (12, 1.0, 320, 480, (8, 20, 25), (235, 242, 255))]):
        d.rectangle([0, H * base_y - 10, W, H], fill=col + (255,))
        for i in range(n):
            x = rng.uniform(-50, W + 50); hgt = rng.uniform(hmin, hmax); y = H * base_y; wdt = hgt * .42
            for k in range(4):
                ty = y - hgt * (k * .22); th = hgt * .38; tw = wdt * (1 - k * .2)
                d.polygon([(x - tw, ty), (x + tw, ty), (x, ty - th)], fill=col + (255,))
                d.polygon([(x - tw * .55, ty - th * .45), (x, ty - th), (x + tw * .55, ty - th * .45), (x + tw * .2, ty - th * .5), (x, ty - th * .38), (x - tw * .2, ty - th * .5)], fill=snowc + (255,))
        d.rectangle([0, H * base_y - 4, W, H * base_y + 6], fill=snowc + (255,))
    base = np.asarray(im.convert('RGB'), np.float32) / 255
    from pack2 import snow
    for fr in snow(base ** 1.1, 151): yield fr

def happy_new_year(year='2027'):
    rng = np.random.default_rng(153)
    bg = bokeh_bg([.02, .01, .03], [.08, .05, .03], [[1, .8, .35], [1, .9, .6], [.9, .7, .3]], 154, 45, .10)
    big = ImageFont.truetype(FONT, 330); small = ImageFont.truetype(FONT, 72)
    mask = Image.new('L', (W, H), 0); d = ImageDraw.Draw(mask)
    d.text((W / 2, H * .56), year, font=big, anchor='mm', fill=255)
    m2 = Image.new('L', (W, H), 0); ImageDraw.Draw(m2).text((W / 2, H * .25), 'HAPPY NEW YEAR', font=small, anchor='mm', fill=255)
    m = np.asarray(mask, np.float32) / 255; ms = np.asarray(m2, np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    grad = np.stack([np.ones_like(yy), .88 - .25 * (yy - H * .4) / (H * .35), .55 - .35 * (yy - H * .4) / (H * .35)], -1)
    shadow = gaussian_filter(m, 12)[..., None] * .6
    pts = [(rng.uniform(.18, .82) * W, rng.uniform(.12, .9) * H, rng.uniform(2, 5), int(rng.integers(1, 4)), rng.uniform(0, TAU)) for _ in range(90)]
    for f in range(N):
        t = f / N
        shine = np.exp(-(((xx - yy * .5) / W - (t % 1) * 1.8 + .4) / .05) ** 2)
        img = bg * (1 - shadow) + m[..., None] * grad * (.85 + .9 * shine[..., None]) + ms[..., None] * np.array([1, .95, .85])
        img = img + gaussian_filter(m * shine, 10)[..., None] * np.array([1, .85, .5]) * .8
        img = img * (1 - m[..., None] * 0)
        for x, y, r, k, ph in pts:
            s = max(0., math.sin(TAU * k * t + ph)) ** 3
            if s > .03: blob(img, x, y, r, np.array([1, .9, .6]), s * 1.4, edge=.6, glow=1.2, rim=0)
        yield np.clip(img, 0, 1.4) / 1.0

def marquee():
    inset = 70; per = []
    def edge(x0, y0, x1, y1, n):
        for s in np.linspace(0, 1, n, endpoint=False): per.append((x0 + (x1 - x0) * s, y0 + (y1 - y0) * s))
    edge(inset, inset, W - inset, inset, 24); edge(W - inset, inset, W - inset, H - inset, 13)
    edge(W - inset, H - inset, inset, H - inset, 24); edge(inset, H - inset, inset, inset, 13)
    n = len(per); bg = gradient([.03, .02, .02], [.08, .05, .03], .5)
    plate = Image.new('L', (W, H), 0); d = ImageDraw.Draw(plate)
    d.rounded_rectangle([inset - 40, inset - 40, W - inset + 40, H - inset + 40], radius=30, outline=255, width=48)
    pm = (np.asarray(plate.filter(ImageFilter.GaussianBlur(1)), np.float32) / 255)[..., None]
    base = bg * (1 - pm) + pm * np.array([.35, .24, .10])
    for f in range(N):
        t = f / N; img = base.copy()
        for i, (x, y) in enumerate(per):
            on = (i + int(t * 24)) % 3 != 0
            b = 1.4 if on else .35
            blob(img, x, y, 13, np.array([1, .82, .45]), b, edge=.5, glow=1.0 if on else .3, rim=0)
        yield tone(img, 1.6)

def fireworks(palette, seed=9):
    rng = np.random.default_rng(seed); T = 8.0; g = 110.0
    sky = gradient([.02, .0, .02], [.10, .02, .03], .4)
    shows = []
    for i in range(11):
        t0 = i * T / 11 + rng.uniform(-.15, .15); bx = rng.uniform(.15, .85) * W; by = rng.uniform(.18, .5) * H
        col = np.array(palette[rng.integers(len(palette))]); col2 = np.array(palette[rng.integers(len(palette))])
        n = 240; ang = rng.uniform(0, TAU, n); sp = rng.uniform(.15, 1, n) ** .75 * rng.uniform(400, 540)
        cs = np.where((np.arange(n) % 2 == 0)[:, None], col, col2)
        shows.append((t0, bx, by, np.cos(ang) * sp, np.sin(ang) * sp, cs, rng.uniform(.55, .8)))
    rise, life, k = 1.0, 2.4, 1.6
    for f in range(N):
        t = f / N * T; buf = np.zeros((H, W, 3), np.float32)
        for t0, bx, by, vx, vy, cs, fl in shows:
            for tl in (t0, t0 - T):
                tau = t - tl
                if 0 <= tau < rise:
                    s = tau / rise; tr = np.linspace(0, .12, 8)
                    yy_ = H - 40 - (H - 40 - by) * (1 - (1 - np.clip(s - tr, 0, 1)) ** 2)
                    splat(buf, np.full(8, bx), yy_, np.tile(np.array([1, .85, .6]), (8, 1)), np.linspace(.9, .1, 8))
                tb = tau - rise
                if 0 <= tb < life:
                    for back, al in ((0, 1.0), (.05, .55), (.1, .3), (.16, .15)):
                        tt = max(tb - back, 0); dr = (1 - math.exp(-k * tt)) / k
                        px = bx + vx * dr; py = by + vy * dr + .5 * g * tt * tt
                        fade = (1 - tb / life) ** 1.6 * al
                        flick = 1 if tb < life * fl else (0.4 + 0.6 * (np.sin(np.arange(len(px)) * 7 + f * 1.7) > 0))
                        splat(buf, px, py, cs, np.full(len(px), fade * 3.2) * flick)
                    if tb < .15: blob(buf, bx, by, 70, np.array([1, .9, .7]), (1 - tb / .15) * .45, edge=1, glow=.6, rim=0)
        light = tone(glowify(buf), 1.5)
        yield sky + gaussian_filter(light, (50, 50, 0)) * .9 + light

# ---------------------------------------------------------------- registry: name -> (generator, mode) ; mode 0 = float+gamma, 1 = uint8/raw, 2 = 300-frame raw
C = {
 # Lantern Festival & Lunar New Year
 'lantern-festival-rising-red-lanterns-loop': (lantern_festival, 1),
 'chinese-red-lanterns-green-screen-loop': (lambda: chinese_lanterns(True), 1),
 'lunar-new-year-gold-coins-falling-loop': (coins_red, 1),
 'lunar-new-year-red-gold-fireworks-loop': (lambda: fireworks([[1, .2, .15], [1, .75, .25], [1, .9, .55], [1, .45, .2]], 19), 0),
 'red-plum-blossoms-falling-loop': (plum_blossoms, 1),
 # Irish
 'st-patricks-falling-shamrocks-loop': (shamrocks, 1),
 'st-patricks-green-gold-confetti-loop': (lambda: confetti(gradient([.0, .06, .02], [.01, .14, .05], .5), [[.1, .7, .3], [.2, .85, .35], [1, .8, .3], [.95, .95, .9], [.05, .55, .2]], 155, 260), 0),
 'pot-of-gold-coins-falling-loop': (coins_gold_green, 1),
 'rainbow-over-green-hills-loop': (rainbow_hills, 0),
 'irish-green-white-orange-gradient-flow-loop': (lambda: flow(157, [[.02, .30, .12], [.10, .60, .30], [.95, .95, .92], [1.0, .62, .22], [.05, .40, .18]]), 0),
 # Middle East & Jewish
 'ramadan-lanterns-crescent-moon-loop': (lambda: crescent_scene(True), 1),
 'ramadan-lanterns-green-screen-loop': (lambda: crescent_scene(True, True), 1),
 'eid-gold-geometric-pattern-shimmer-loop': (geometric, 0),
 'crescent-moon-twinkling-stars-loop': (lambda: crescent_scene(False, False, ([.0, .01, .05], [.03, .06, .16])), 1),
 'teal-gold-eid-sparkles-loop': (lambda: sparkles(gradient([.0, .05, .07], [.0, .10, .12], .55), [[1, .8, .35], [1, .9, .55], [.9, .75, .4]], 158, 380), 0),
 'nowruz-spring-tulips-swaying-loop': (tulips, 1),
 'hanukkah-menorah-candles-loop': (menorah, 0),
 'hanukkah-blue-silver-bokeh-loop': (lambda: bokeh(159, [.01, .02, .08], [.02, .05, .15], [[.3, .5, 1], [.55, .7, 1], [.85, .9, 1], [1, 1, 1], [.4, .6, .95]]), 0),
 # India
 'diwali-diya-lamps-loop': (diyas, 0),
 'holi-color-powder-bursts-loop': (holi, 0),
 # Valentine, Easter, Carnival
 'red-rose-petals-falling-loop': (lambda: rose_petals(False), 1),
 'rose-petals-green-screen-loop': (lambda: rose_petals(True), 1),
 'red-valentine-bokeh-loop': (lambda: bokeh(161, [.06, .0, .02], [.14, .01, .04], [[1, .15, .25], [1, .35, .45], [1, .6, .7], [.9, .1, .2], [1, .85, .85]]), 0),
 'easter-pastel-eggs-falling-loop': (easter_eggs, 1),
 'carnival-mardi-gras-confetti-loop': (lambda: confetti(gradient([.03, .01, .06], [.08, .02, .10], .5), [[.55, .15, .75], [.1, .7, .3], [1, .78, .15], [.7, .3, .9], [.2, .85, .4]], 163, 280), 0),
 # Christmas & New Year
 'snowy-christmas-tree-forest-night-loop': (tree_forest, 0),
 'big-snowflakes-falling-loop': (lambda: snowflakes(False), 1),
 'snowflakes-green-screen-loop': (lambda: snowflakes(True), 1),
 'happy-new-year-2027-gold-loop': (happy_new_year, 0),
 'champagne-gold-bubbles-rising-loop': (champagne, 0),
 'gold-marquee-lights-frame-loop': (marquee, 0),
 'new-year-countdown-green-screen': (lambda: countdown(True), 2),
 # General
 'rain-falling-overlay-loop': (rain, 0),
 'blue-sky-white-clouds-loop': (lambda: sky_clouds([.20, .45, .85], [.62, .80, .98], [1, 1, 1], 165), 0),
 'golden-sunset-clouds-loop': (lambda: sky_clouds([.25, .15, .35], [1.0, .55, .25], [1, .72, .55], 167, (W * .5, H * .78, [1, .7, .35])), 0),
 'gold-particles-rising-loop': (lambda: rising_particles([[1, .8, .35], [1, .9, .55], [1, .7, .25]], [.01, .01, .01], [.07, .05, .02], 169), 0),
 'blue-particles-rising-tech-loop': (lambda: rising_particles([[.3, .7, 1], [.5, .85, 1], [.2, .5, 1]], [.0, .01, .04], [.01, .04, .10], 171), 0),
 'purple-space-nebula-stars-loop': (nebula, 0),
 'pastel-balloons-rising-loop': (lambda: balloons(False, [(255, 190, 200), (190, 220, 255), (255, 235, 160), (200, 240, 200), (225, 205, 255), (255, 210, 170)], ([.98, .90, .93], [.90, .95, 1.0]), 173), 1),
 'gold-silver-new-year-balloons-loop': (lambda: balloons(False, [(230, 185, 70), (245, 210, 110), (200, 205, 215), (235, 235, 240), (40, 40, 50)], ([.03, .03, .05], [.10, .08, .12]), 175), 1),
}

if __name__ == '__main__':
    for name in sys.argv[1:]:
        gen, mode = C[name]
        if mode == 0: encode(name, gen())
        elif mode == 1: encode_raw(name, gen())
        else: encode_raw(name, gen(), 300)
        print('done', name, flush=True)

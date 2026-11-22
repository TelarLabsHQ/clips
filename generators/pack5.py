"""Batch 5: gold & sparkle overlays, December, India & Yalda themes, storms.
Usage: python3 pack5.py <name> ...            (run from the output folder)
       CLIP_VERT=1 python3 pack5.py <name>-9x16  (vertical versions of the most-viewed overlays)"""
import numpy as np, math, sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter
from pack import W, H, N, TAU, gradient, blob, tone, flow, encode
import pack, pack2, pack4
from pack2 import encode_raw, sparkles, confetti, snow, lightleaks
from pack3 import bokeh_bg, star5
from pack4 import fall, with_glow, fireworks, rising_particles, rain
from xmas import splat, glowify

LORA_I = '/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf'
POP = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
BLACK = lambda: np.zeros((H, W, 3), np.float32)
u8 = lambda a: (np.clip(a, 0, 1) * 255).astype(np.uint8)

# ---------------------------------------------------------------- overlays on black (use Screen blend)
def shimmer(cols, seed, n=1100):
    """fine dust drifting diagonally, each speck twinkling"""
    rng = np.random.default_rng(seed); M = 30
    ps = np.column_stack([rng.uniform(0, W + 2 * M, n), rng.uniform(0, H + 2 * M, n)])
    k = rng.integers(1, 3, n); ph = rng.uniform(0, TAU, n); tw = rng.integers(1, 5, n)
    size = rng.uniform(.4, 1.6, n) ** 2; ci = rng.integers(len(cols), size=n); C = np.array(cols)[ci]
    for f in range(N):
        t = f / N; buf = np.zeros((H, W, 3), np.float32)
        x = (ps[:, 0] + 60 * np.sin(TAU * t + ph)) % (W + 2 * M) - M
        y = (ps[:, 1] - k * (H + 2 * M) * t) % (H + 2 * M) - M
        a = (np.maximum(0, np.sin(TAU * tw * t + ph)) ** 3) * size * 3.2 + .12 * size
        splat(buf, x, y, C, a)
        yield np.clip(tone(glowify(buf, 1.0, 3, 10), 1.4), 0, 1)

def blizzard():
    rng = np.random.default_rng(301); M = 120; spanY = H + 2 * M; spanX = W + 2 * M; fl = []
    for n, r0, r1, cyc, b in [(420, 1.5, 3, 2, .45), (220, 3, 6, 3, .7), (70, 7, 13, 4, .9)]:
        for _ in range(n):
            fl.append((rng.uniform(0, spanX), rng.uniform(0, spanY), rng.uniform(r0, r1), cyc, rng.uniform(10, 40), rng.uniform(0, TAU), b * rng.uniform(.7, 1.1)))
    col = np.array([.92, .96, 1.0])
    for f in range(N):
        t = f / N; img = np.zeros((H, W, 3), np.float32)
        for x0, y0, r, cyc, sw, ph, b in fl:
            y = (y0 + cyc * spanY * t) % spanY - M
            x = (x0 + cyc * spanX * .5 * t + sw * math.sin(TAU * 2 * t + ph)) % spanX - M   # wind pushes the snow sideways
            blob(img, x, y, r, col, b, edge=.5, glow=.25, rim=0)
        yield tone(img, 1.8)

def gold_fireworks_black():
    return fireworks([[1, .8, .35], [1, .9, .6], [1, .7, .25], [.95, .95, .9]], 311, sky=BLACK())

def gold_confetti_black():
    return confetti(BLACK(), [[1, .8, .3], [.95, .7, .2], [1, .88, .55], [.85, .85, .9], [1, .95, .8]], 313, 300)

# ---------------------------------------------------------------- December
def gold_stars():
    base = Image.fromarray(u8(bokeh_bg([.01, .02, .07], [.04, .05, .14], [[1, .7, .25], [1, .8, .35]], 321, 40, .09)))
    sprites = [with_glow(star5(c, 160), c, 18, .8) for c in [(255, 205, 90), (255, 225, 140), (245, 190, 70), (255, 240, 200)]]
    return fall(base, sprites, 46, 322, sway=(15, 60), spin=(1, 1), flip=False, sizes=(26, 80))

def merry_christmas():
    rng = np.random.default_rng(331)
    bg = bokeh_bg([.05, .0, .01], [.14, .02, .03], [[1, .8, .35], [1, .3, .25], [.3, .8, .4]], 332, 50, .11)
    big = ImageFont.truetype(LORA_I, 210); big.set_variation_by_axes([700])
    small = ImageFont.truetype(POP, 54)
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.text((W / 2, H * .47), 'Merry Christmas', font=big, anchor='mm', fill=255)
    m2 = Image.new('L', (W, H), 0); ImageDraw.Draw(m2).text((W / 2, H * .68), 'AND A HAPPY NEW YEAR', font=small, anchor='mm', fill=255)
    m = np.asarray(m, np.float32) / 255; ms = np.asarray(m2, np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    grad = np.stack([np.ones_like(yy), .86 - .22 * (yy - H * .4) / (H * .2), .5 - .3 * (yy - H * .4) / (H * .2)], -1)
    shadow = gaussian_filter(m + ms, 12)[..., None] * .6
    pts = [(rng.uniform(.1, .9) * W, rng.uniform(.1, .9) * H, rng.uniform(2, 5), int(rng.integers(1, 4)), rng.uniform(0, TAU)) for _ in range(110)]
    snow_pts = [(rng.uniform(0, W), rng.uniform(0, H + 40), rng.uniform(1.5, 4), int(rng.integers(1, 3)), rng.uniform(0, TAU)) for _ in range(160)]
    for f in range(N):
        t = f / N
        shine = np.exp(-(((xx - yy * .5) / W - (t % 1) * 1.8 + .4) / .05) ** 2)
        img = bg * (1 - shadow) + m[..., None] * grad * (.85 + .9 * shine[..., None]) + ms[..., None] * np.array([1, .93, .82])
        img = img + gaussian_filter(m * shine, 10)[..., None] * np.array([1, .85, .5]) * .8
        for x, y, r, k, ph in snow_pts:
            blob(img, x + 20 * math.sin(TAU * t + ph), (y + k * (H + 40) * t) % (H + 40) - 20, r, np.array([.95, .97, 1]), .55, edge=.5, glow=.3, rim=0)
        for x, y, r, k, ph in pts:
            s = max(0., math.sin(TAU * k * t + ph)) ** 3
            if s > .03: blob(img, x, y, r, np.array([1, .9, .6]), s * 1.4, edge=.6, glow=1.2, rim=0)
        yield np.clip(img, 0, 1.4)

# ---------------------------------------------------------------- India
def marigold(col, seed):
    """ruffled pom-pom flower: scalloped layers, darker toward the edge"""
    S = 240; rng = np.random.default_rng(seed); im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    for li, (R0, nsc, sh) in enumerate([(112, 22, .78), (96, 20, .86), (78, 18, .93), (58, 15, 1.0), (38, 12, 1.06), (20, 9, 1.1)]):
        ph = rng.uniform(0, TAU); pts = []
        for k in range(180):
            a = TAU * k / 180; r = R0 * (.86 + .14 * abs(math.sin(nsc * a / 2 + ph))) * rng.uniform(.97, 1.03)
            pts.append((c + r * math.cos(a), c + r * math.sin(a)))
        fill = tuple(min(255, int(v * sh)) for v in col) + (255,)
        d.polygon(pts, fill=fill)
        for k in range(nsc):   # fold lines between petals
            a = TAU * k / nsc + ph; d.line([(c + R0 * .55 * math.cos(a), c + R0 * .55 * math.sin(a)), (c + R0 * .95 * math.cos(a), c + R0 * .95 * math.sin(a))],
                                          fill=tuple(int(v * sh * .72) for v in col) + (200,), width=2)
    return im.filter(ImageFilter.GaussianBlur(.6))

def marigolds():
    base = Image.fromarray(u8(bokeh_bg([.10, .01, .02], [.24, .05, .02], [[1, .7, .2], [1, .5, .1], [1, .85, .4]], 341, 45, .12)))
    sprites = [marigold((255, 150, 20), 1), marigold((255, 190, 30), 2), marigold((250, 120, 15), 3), marigold((255, 205, 60), 4)]
    return fall(base, sprites, 34, 342, sway=(20, 70), spin=(1, 1), flip=False, sizes=(80, 170))

def mandala():
    """gold mandala turning by one symmetry step per loop, so the loop is seamless"""
    S = 1600; sym = 16
    im = Image.new('L', (S, S), 0); d = ImageDraw.Draw(im); c = S / 2
    def ring(r, w): d.ellipse([c - r, c - r, c + r, c + r], outline=255, width=w)
    for r, w in ((90, 6), (150, 4), (330, 5), (520, 4), (700, 6), (760, 3)): ring(r, w)
    for k in range(sym):
        a = TAU * k / sym
        def P(rr, da=0): return (c + rr * math.cos(a + da), c + rr * math.sin(a + da))
        d.polygon([P(150), P(330, .12), P(420), P(330, -.12)], outline=255, width=5)      # inner petals
        d.polygon([P(345), P(520, .1), P(640), P(520, -.1)], outline=255, width=5)        # outer petals
        d.line([P(90), P(150)], fill=255, width=4)
        x, y = P(600, TAU / sym / 2); d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=255)
        x, y = P(430, TAU / sym / 2); d.ellipse([x - 10, y - 10, x + 10, y + 10], outline=255, width=4)
        for j in range(3):
            x, y = P(700 + 0 * j, TAU / sym * (j / 3)); d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=255)
        x, y = P(45); d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=255)
    m = im.filter(ImageFilter.GaussianBlur(1.2)); R = int(H * .92)
    bg = gradient([.20, .01, .04], [.10, .0, .02], .6)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rng = np.random.default_rng(351); pts = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.5, 4), int(rng.integers(1, 4)), rng.uniform(0, TAU)) for _ in range(90)]
    for f in range(N):
        t = f / N
        r = m.rotate(.37 - 720 / sym * t, resample=Image.BICUBIC).resize((R, R), Image.LANCZOS)
        a = np.zeros((H, W), np.float32); ox, oy = (W - R) // 2, (H - R) // 2
        a[oy:oy + R, ox:ox + R] = np.asarray(r, np.float32) / 255
        shine = .75 + .5 * np.exp(-(((xx - W / 2) * math.cos(TAU * t) + (yy - H / 2) * math.sin(TAU * t)) / (W * .25) - 0) ** 2)
        gold = np.stack([np.ones_like(a), .78 * np.ones_like(a), .38 * np.ones_like(a)], -1)
        img = bg + a[..., None] * gold * shine[..., None] + gaussian_filter(a, 8)[..., None] * np.array([1, .7, .3]) * .35
        for x, y, rr, k, ph in pts:
            s = max(0., math.sin(TAU * k * t + ph)) ** 3
            if s > .03: blob(img, x, y, rr, np.array([1, .88, .55]), s * 1.2, edge=.6, glow=1.0, rim=0)
        yield np.clip(img, 0, 1.3)

def kites():
    """Makar Sankranti / Uttarayan: bright kites bobbing in a blue sky"""
    rng = np.random.default_rng(361)
    sky = np.asarray(Image.fromarray(u8(gradient([.25, .55, .92], [.75, .88, 1.0], .15))), np.float32) / 255
    cols = [(230, 40, 60), (255, 170, 0), (40, 160, 90), (150, 50, 190), (20, 120, 220), (255, 90, 150), (255, 220, 40)]
    ks = []
    for i in range(9):
        s = rng.uniform(.55, 1.15); x = (i + .5) / 9 * W + rng.uniform(-60, 60); y = rng.uniform(.12, .55) * H
        ks.append((x, y, s, cols[i % len(cols)], cols[(i + 3) % len(cols)], rng.uniform(0, TAU), int(rng.integers(1, 3)), rng.uniform(18, 45)))
    ks.sort(key=lambda k: k[2])
    for f in range(N):
        t = f / N; c = Image.fromarray(u8(sky)).convert('RGBA'); d = ImageDraw.Draw(c)
        for x0, y0, s, c1, c2, ph, k, amp in ks:
            x = x0 + amp * math.sin(TAU * k * t + ph); y = y0 + amp * .6 * math.sin(TAU * 2 * t + ph * 1.3)
            ang = .18 * math.sin(TAU * k * t + ph + .8); w, h = 70 * s, 85 * s
            def R(px, py): return (x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang))
            top, rt, bot, lt, mid = R(0, -h), R(w, -h * .1), R(0, h), R(-w, -h * .1), R(0, -h * .1)
            d.line([bot, (x0 * .6 + W * .2 + 40 * math.sin(ph), H + 10)], fill=(255, 255, 255, 150), width=2)
            d.polygon([top, rt, bot, lt], fill=c1 + (255,))
            d.polygon([top, rt, mid], fill=c2 + (255,)); d.polygon([lt, bot, mid], fill=c2 + (255,))
            d.line([top, bot], fill=(60, 30, 20, 200), width=max(1, int(3 * s))); d.line([lt, rt], fill=(60, 30, 20, 200), width=max(1, int(3 * s)))
            tx, ty = bot; d.polygon([(tx, ty), (tx - 14 * s, ty + 26 * s), (tx + 14 * s, ty + 26 * s)], fill=c2 + (255,))
        yield np.asarray(c.convert('RGB'))

def tricolor():
    return flow(371, [[1.0, .55, .15], [1.0, .62, .25], [.97, .97, .95], [.10, .55, .20], [.07, .45, .16]])

# ---------------------------------------------------------------- Yalda night (Iran, Dec 20/21)
def aril(seed):
    S = 120; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(60, 8), (100, 45), (92, 95), (60, 112), (28, 95), (20, 45)], fill=(170, 10, 40, 255))
    im = im.filter(ImageFilter.GaussianBlur(5)); a = im.getchannel('A').point(lambda v: 255 if v > 110 else int(v * 2.3))
    body = Image.new('RGBA', (S, S), (190, 15, 45, 0)); body.putalpha(a)
    g = ImageDraw.Draw(body); g.ellipse([36, 28, 58, 52], fill=(255, 170, 180, 230)); g.ellipse([62, 70, 74, 84], fill=(230, 60, 90, 200))
    return body

def yalda():
    base = Image.fromarray(u8(bokeh_bg([.07, .0, .02], [.18, .02, .05], [[1, .3, .35], [1, .75, .35], [.9, .2, .3]], 381, 45, .12)))
    sprites = [aril(i) for i in range(3)]
    return fall(base, sprites, 60, 382, sway=(10, 45), spin=(1, 1), flip=False, wobble=None, sizes=(34, 72))

# ---------------------------------------------------------------- storm
def storm():
    rng = np.random.default_rng(391)
    from pack3 import tile_noise
    nz = tile_noise(W // 4, H // 4, 392); nz = np.asarray(Image.fromarray((nz * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32) / H
    cloud = (nz * (1.1 - yy))[..., None] * np.array([.16, .17, .22]) + gradient([.02, .03, .05], [.04, .05, .07], .5)
    bolts = []
    for t0, x0 in ((.18, .3), (.24, .3), (.66, .72)):
        pts = [(x0 * W, 0)]; x = x0 * W
        for y in np.linspace(0, H * .75, 14)[1:]: x += rng.uniform(-60, 60); pts.append((x, y))
        bolts.append((t0, pts))
    rain_frames = rain()
    for f, rf in zip(range(N), rain_frames):
        t = f / N; flash = 0; img = cloud.copy()
        bolt = Image.new('L', (W, H), 0); bd = ImageDraw.Draw(bolt)
        for t0, pts in bolts:
            dt = t - t0
            if 0 <= dt < .05:
                e = (1 - dt / .05) ** 2; flash = max(flash, e); bd.line(pts, fill=int(255 * e), width=4)
        b = np.asarray(bolt.filter(ImageFilter.GaussianBlur(1)), np.float32) / 255
        img = img * (1 + 2.2 * flash) + flash * .12 + gaussian_filter(b, 14)[..., None] * np.array([.6, .7, 1]) * 1.2 + b[..., None]
        yield np.clip(img + rf * .55, 0, 1)

# ---------------------------------------------------------------- registry
C = {
 # overlays on black (Screen blend)
 'gold-dust-shimmer-overlay-loop': (lambda: shimmer([[1, .8, .35], [1, .9, .6], [1, .7, .3]], 301), 0),
 'rose-gold-glitter-sparkles-loop': (lambda: sparkles(BLACK(), [[1, .65, .6], [1, .78, .7], [.95, .55, .55], [1, .88, .8]], 303, 420), 0),
 'gold-confetti-shower-black-overlay-loop': (gold_confetti_black, 0),
 'gold-fireworks-black-overlay-loop': (gold_fireworks_black, 0),
 'heavy-snowfall-blizzard-overlay-loop': (blizzard, 0),
 'rainbow-prism-light-leaks-overlay-loop': (lambda: lightleaks(305, ([1, .25, .3], [1, .6, .15], [.3, .9, .4], [.25, .5, 1], [.7, .3, 1], [1, .9, .3])), 0),
 # December
 'gold-stars-falling-christmas-loop': (gold_stars, 1),
 'merry-christmas-gold-loop': (merry_christmas, 0),
 'yalda-night-pomegranate-seeds-loop': (yalda, 1),
 # India
 'marigold-flowers-falling-loop': (marigolds, 1),
 'gold-mandala-rotating-loop': (mandala, 0),
 'makar-sankranti-colorful-kites-loop': (kites, 1),
 'saffron-white-green-gradient-flow-loop': (tricolor, 0),
 # nature
 'thunderstorm-rain-lightning-loop': (storm, 0),
}
# 9:16 versions of the most-viewed overlays (render with CLIP_VERT=1)
V = {
 'gold-particles-rising-loop-9x16': (lambda: rising_particles([[1, .8, .35], [1, .9, .55], [1, .7, .25]], [.01, .01, .01], [.07, .05, .02], 169), 0),
 'gold-glitter-sparkles-loop-9x16': (pack.sparkles, 0),
 'falling-snow-black-overlay-loop-9x16': (lambda: snow(BLACK() + .0, 5), 0),
 'rain-falling-overlay-loop-9x16': (rain, 0),
 'warm-light-leaks-overlay-loop-9x16': (lightleaks, 0),
}

if __name__ == '__main__':
    for name in sys.argv[1:]:
        if name in V and not os.environ.get('CLIP_VERT'): sys.exit(f'{name}: run with CLIP_VERT=1')
        gen, mode = (V if name in V else C)[name]
        (encode if mode == 0 else encode_raw)(name, gen())
        print('done', name, flush=True)

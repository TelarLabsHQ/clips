"""Batch 5b: three more India clips and three more Christmas & New Year clips. Usage: python3 pack6.py <name> ..."""
import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter
from pack import W, H, N, TAU, gradient, blob, tone, encode
from pack2 import encode_raw, balloons
from pack3 import bokeh_bg
from pack4 import fall, hang, fireworks
from pack5 import marigold, u8, BLACK, POP
from xmas import splat, glowify

# ---------------------------------------------------------------- India
def rangoli():
    """colourful rangoli: filled petal rings turning in opposite directions (seamless: one symmetry step per loop)"""
    S = 1400; c = S / 2; sym = 12
    pal = [(236, 40, 90), (255, 160, 0), (30, 170, 120), (40, 110, 230), (160, 60, 200), (255, 215, 0), (255, 90, 40)]
    def layer(rings):
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for r0, r1, wid, col, shape in rings:
            for k in range(sym * (2 if shape == 'dot' else 1)):
                a = TAU * k / (sym * (2 if shape == 'dot' else 1))
                P = lambda rr, da=0: (c + rr * math.cos(a + da), c + rr * math.sin(a + da))
                if shape == 'petal': d.polygon([P(r0), P((r0 + r1) / 2, wid), P(r1), P((r0 + r1) / 2, -wid)], fill=col + (255,), outline=(255, 255, 255, 230))
                elif shape == 'drop': d.ellipse([P((r0 + r1) / 2)[0] - wid, P((r0 + r1) / 2)[1] - wid, P((r0 + r1) / 2)[0] + wid, P((r0 + r1) / 2)[1] + wid], fill=col + (255,), outline=(255, 255, 255, 230), width=3)
                else: x, y = P(r0); d.ellipse([x - wid, y - wid, x + wid, y + wid], fill=col + (255,))
        return im
    outer = layer([(470, 660, .14, pal[0], 'petal'), (600, 600, 26, pal[5], 'drop'), (680, 0, 9, (255, 255, 255), 'dot')])
    mid = layer([(260, 450, .2, pal[1], 'petal'), (300, 400, .09, pal[6], 'petal'), (470, 0, 8, (255, 255, 255), 'dot')])
    inner = layer([(70, 240, .32, pal[3], 'petal'), (110, 200, .14, pal[2], 'petal'), (250, 0, 7, pal[5], 'dot')])
    core = Image.new('RGBA', (S, S), (0, 0, 0, 0)); cd = ImageDraw.Draw(core)
    for r, col in ((80, pal[4]), (58, pal[5]), (34, pal[0]), (14, (255, 255, 255))): cd.ellipse([c - r, c - r, c + r, c + r], fill=col + (255,))
    bg = Image.fromarray(u8(bokeh_bg([.12, .03, .08], [.22, .06, .10], [[1, .6, .2], [1, .3, .5], [1, .8, .3]], 401, 40, .10)))
    R = int(H * .95); step = 360 / sym
    for f in range(N):
        t = f / N; img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        for L, sgn in ((outer, 1), (mid, -1), (inner, 1)):
            img.alpha_composite(L.rotate(.31 + sgn * step * t, resample=Image.BICUBIC))
        img.alpha_composite(core)
        pulse = 1 + .015 * math.sin(TAU * t)
        r = img.resize((int(R * pulse), int(R * pulse)), Image.LANCZOS)
        sh = Image.new('RGBA', r.size, (0, 0, 0, 0)); sh.putalpha(r.getchannel('A').point(lambda v: int(v * .5)).filter(ImageFilter.GaussianBlur(14)))
        out = bg.convert('RGBA'); ox, oy = (W - r.width) // 2, (H - r.height) // 2
        out.alpha_composite(sh, (ox + 6, oy + 10)); out.alpha_composite(r, (ox, oy))
        yield np.asarray(out.convert('RGB'))

def garland(n_flowers=11, size=46, seed=0):
    """a hanging string of marigolds ending in a small brass bell"""
    rng = np.random.default_rng(seed); fl = [marigold((255, 150 + int(rng.integers(0, 60)), 20), int(rng.integers(0, 99))).resize((size, size), Image.LANCZOS) for _ in range(n_flowers)]
    Hh = int(n_flowers * size * .78 + 60); im = Image.new('RGBA', (size + 20, Hh), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx = (size + 20) // 2
    d.line([(cx, 0), (cx, Hh - 50)], fill=(120, 80, 30, 255), width=2)
    for i, f in enumerate(fl): im.alpha_composite(f, (cx - size // 2, int(i * size * .78)))
    by = Hh - 46; d.polygon([(cx - 14, by + 34), (cx - 9, by + 6), (cx, by), (cx + 9, by + 6), (cx + 14, by + 34)], fill=(215, 160, 50, 255))
    d.ellipse([cx - 4, by + 32, cx + 4, by + 42], fill=(170, 110, 30, 255)); d.line([(cx - 14, by + 34), (cx + 14, by + 34)], fill=(250, 210, 110, 255), width=3)
    return im

def toran():
    """wedding entrance: marigold garlands swaying from a top border, room in the middle for text"""
    base = Image.fromarray(u8(bokeh_bg([.16, .02, .04], [.08, .01, .03], [[1, .75, .3], [1, .5, .2]], 411, 40, .10)))
    top = Image.new('RGBA', (W, 70), (0, 0, 0, 0)); td = ImageDraw.Draw(top)
    for i, x in enumerate(range(-20, W + 40, 44)): top.alpha_composite(marigold((255, 170 if i % 2 else 130, 20), i).resize((58, 58), Image.LANCZOS), (x, 4))
    base = base.convert('RGBA'); base.alpha_composite(top, (0, -6)); base = base.convert('RGB')
    xs = [.04, .12, .2, .28, .72, .8, .88, .96]; lens = [13, 10, 8, 6, 6, 8, 10, 13]
    sprites = [garland(n, 46, i) for i, n in enumerate(lens)]
    cfg = [(x, .02, s.height) for x, s in zip(xs, sprites)]
    return hang(base, sprites, cfg, 412, string=(120, 80, 30, 255), amp=(1.5, 3.5))

def tricolor_balloons():
    return balloons(False, [(255, 153, 51), (255, 255, 255), (19, 136, 8), (255, 170, 80), (40, 160, 40)], ([.30, .58, .92], [.80, .90, 1.0]), 421)

# ---------------------------------------------------------------- Christmas & New Year
def light_tree():
    """a Christmas tree made of twinkling lights spiralling up to a glowing star"""
    rng = np.random.default_rng(431); bg = gradient([.0, .02, .05], [.02, .05, .10], .55)
    cx, top, base_y, half = W / 2, H * .2, H * .94, H * .34
    n = 1500; s = np.sort(rng.uniform(0, 1, n)); turns = 7
    ang = TAU * turns * s + rng.uniform(-.06, .06, n); y = top + (base_y - top) * s ** .95 + rng.uniform(-6, 6, n)
    rad = half * s ** .95; x = cx + rad * np.cos(ang); depth = np.sin(ang)
    pal = np.array([[1, .2, .15], [1, .75, .2], [.2, .9, .35], [.3, .55, 1], [1, 1, .9], [1, .4, .8]])
    col = pal[rng.integers(len(pal), size=n)]; ph = rng.uniform(0, TAU, n); k = rng.integers(1, 4, n)
    snow = [(rng.uniform(0, W), rng.uniform(0, H + 40), rng.uniform(1.5, 4), int(rng.integers(1, 3)), rng.uniform(0, TAU)) for _ in range(130)]
    star = Image.new('L', (220, 220), 0); sd = ImageDraw.Draw(star)
    sd.polygon([(110 + (100 if i % 2 == 0 else 40) * math.sin(i * math.pi / 5), 110 - (100 if i % 2 == 0 else 40) * math.cos(i * math.pi / 5)) for i in range(10)], fill=255)
    sm = np.asarray(star.filter(ImageFilter.GaussianBlur(1)), np.float32) / 255
    for f in range(N):
        t = f / N; buf = np.zeros((H, W, 3), np.float32)
        tw = (.35 + .65 * np.maximum(0, np.sin(TAU * k * t + ph)) ** 2) * (.55 + .45 * (depth + 1) / 2)
        # a soft wave of light climbing the tree
        tw = tw * (1 + 1.2 * np.exp(-((s - (t % 1)) / .05) ** 2))
        splat(buf, x, y, col, tw * 5.0)
        img = bg + tone(glowify(buf, 1.3, 4.5, 18), 1.6)
        g = .9 + .25 * math.sin(TAU * 2 * t); y0, x0 = int(top - 110), int(cx - 110)
        img[y0:y0 + 220, x0:x0 + 220] += (sm[..., None] * np.array([1, .85, .4]) * g)
        img[y0 - 60:y0 + 280, x0 - 60:x0 + 280] += gaussian_filter(np.pad(sm, 60), 22)[..., None] * np.array([1, .8, .35]) * .9 * g
        for sx, sy, r, kk, p in snow:
            blob(img, sx + 18 * math.sin(TAU * t + p), (sy + kk * (H + 40) * t) % (H + 40) - 20, r, np.array([.9, .95, 1]), .5, edge=.5, glow=.3, rim=0)
        yield np.clip(img, 0, 1.3)

def gift(seed):
    rng = np.random.default_rng(seed)
    body = [(200, 30, 45), (25, 120, 60), (30, 70, 170), (230, 180, 40), (240, 240, 245), (150, 40, 150)][seed % 6]
    rib = [(255, 215, 90), (255, 255, 255), (220, 30, 40), (255, 215, 90), (200, 30, 45), (255, 215, 90)][seed % 6]
    S = 200; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([30, 70, 170, 185], fill=body + (255,)); d.rectangle([22, 50, 178, 80], fill=tuple(int(v * .85) for v in body) + (255,))
    d.rectangle([90, 50, 110, 185], fill=rib + (255,)); d.rectangle([22, 58, 178, 72], fill=rib + (255,))
    d.ellipse([52, 14, 100, 58], outline=rib + (255,), width=12); d.ellipse([100, 14, 148, 58], outline=rib + (255,), width=12)
    d.rectangle([30, 80, 170, 92], fill=(0, 0, 0, 40))
    return im

def gifts():
    base = Image.fromarray(u8(bokeh_bg([.04, .01, .02], [.12, .03, .04], [[1, .75, .3], [1, .25, .2], [.3, .8, .4]], 441, 45, .11)))
    return fall(base, [gift(i) for i in range(6)], 26, 442, sway=(20, 60), spin=(1, 1), flip=False, wobble=14, sizes=(70, 140))

def hny_fireworks(year='2027'):
    FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
    big = ImageFont.truetype(FONT, 300); small = ImageFont.truetype(POP, 66)
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).text((W / 2, H * .62), year, font=big, anchor='mm', fill=255)
    m2 = Image.new('L', (W, H), 0); ImageDraw.Draw(m2).text((W / 2, H * .36), 'HAPPY NEW YEAR', font=small, anchor='mm', fill=255)
    m = np.asarray(m, np.float32) / 255; ms = np.asarray(m2, np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    grad = np.stack([np.ones_like(yy), .9 - .3 * (yy - H * .5) / (H * .25), .6 - .4 * (yy - H * .5) / (H * .25)], -1)
    sky = gradient([.01, .0, .04], [.06, .02, .10], .4)
    for f, fw in zip(range(N), fireworks([[1, .8, .35], [1, .3, .3], [.4, .7, 1], [1, .9, .6], [.8, .4, 1]], 451, sky=sky)):
        t = f / N; shine = np.exp(-(((xx - yy * .5) / W - (t % 1) * 1.8 + .4) / .05) ** 2)
        a = m[..., None]
        img = fw * (1 - a * .9) + a * grad * (.8 + .9 * shine[..., None]) + ms[..., None] * np.array([1, .95, .85])
        img = img + gaussian_filter(m * (.3 + shine), 10)[..., None] * np.array([1, .8, .45]) * .5
        yield np.clip(img, 0, 1.3)

C = {
 'colorful-rangoli-pattern-rotating-loop': (rangoli, 1),
 'indian-wedding-marigold-garlands-loop': (toran, 1),
 'saffron-white-green-balloons-rising-loop': (tricolor_balloons, 1),
 'christmas-tree-of-lights-loop': (light_tree, 0),
 'christmas-gift-boxes-falling-loop': (gifts, 1),
 'happy-new-year-2027-fireworks-loop': (hny_fireworks, 0),
}

if __name__ == '__main__':
    for name in sys.argv[1:]:
        gen, mode = C[name]
        (encode if mode == 0 else encode_raw)(name, gen())
        print('done', name, flush=True)

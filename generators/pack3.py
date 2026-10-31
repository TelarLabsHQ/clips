"""World celebration clips. Usage: python3 pack3.py <name> ... (run from output folder)"""
import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFilter
from pack import W, H, N, TAU, gradient, blob, tone
from pack2 import encode_raw, GREEN, hsv

def to_img(arr):  # float linear-ish -> display uint8 image
    return Image.fromarray((np.clip(arr, 0, 1) ** (1 / 1.1) * 255).astype(np.uint8))

def bokeh_bg(top, bot, cols, seed, n=40, amp=.10, light=False):
    rng = np.random.default_rng(seed); bg = gradient(top, bot, .5); bk = np.zeros((H, W, 3), np.float32)
    for _ in range(n): blob(bk, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 120), np.array(cols[rng.integers(len(cols))]), amp, edge=.3, glow=.1)
    return np.clip(bg + bk, 0, 1) if light else tone(bg + bk, 1.6)

# ---------------- generic falling sprites ----------------
def faller(base, sprites, n, seed, cyc=(1, 2), sway=(20, 80), spin=(1, 2), flip=True, drift=0.0, rise=False, sizes=(40, 90)):
    rng = np.random.default_rng(seed); M = 120; span = H + 2 * M
    ps = []
    for i in range(n):
        sz = rng.uniform(*sizes); spr = sprites[rng.integers(len(sprites))]
        s = spr.resize((int(sz), int(sz * spr.height / spr.width)), Image.LANCZOS)
        ps.append((s, rng.uniform(0, W), rng.uniform(0, span), int(rng.integers(cyc[0], cyc[1] + 1)), rng.uniform(*sway),
                   rng.uniform(0, TAU), int(rng.integers(spin[0], spin[1] + 1)) * rng.choice([-1, 1]), int(rng.integers(1, 4)), sz))
    ps.sort(key=lambda p: p[8])
    for f in range(N):
        t = f / N; c = base.convert('RGBA')
        for s, x0, y0, k, sw, ph, sp, fl, sz in ps:
            y = (y0 + (-1 if rise else 1) * k * span * t) % span - M
            x = (x0 + sw * math.sin(TAU * t + ph) + drift * W * k * t) % (W + 2 * M) - M
            im = s
            if flip:
                sx = abs(math.cos(TAU * fl * t + ph)) * .8 + .2
                im = im.resize((max(2, int(im.width * sx)), im.height))
            im = im.rotate(math.degrees(TAU * sp * t + ph), resample=Image.BICUBIC, expand=True)   # whole turns per loop -> seamless
            c.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
        yield np.asarray(c.convert('RGB'))

def petal(col):
    S = 200; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = []
    for i in range(80):
        a = TAU * i / 80; r = 1 - .25 * max(0, math.cos(a)) ** 30          # notch at the tip
        pts.append((S / 2 + math.cos(a) * S * .46 * r, S / 2 + math.sin(a) * S * .30))
    d.polygon(pts, fill=col + (235,))
    d.line([(S * .1, S / 2), (S * .7, S / 2)], fill=tuple(min(255, int(v * 1.05)) for v in col) + (120,), width=4)
    return im.filter(ImageFilter.GaussianBlur(1.2))

def maple(col):
    S = 240; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    pts = []
    for i in range(200):
        a = TAU * i / 200
        lobes = .62 + .38 * abs(math.cos(2.5 * a)) ** .6 * (1 if math.sin(a) < .75 else .4)
        spikes = .07 * math.cos(15 * a)
        r = S * .44 * (lobes + spikes)
        pts.append((c + r * math.cos(a - math.pi / 2), c + r * math.sin(a - math.pi / 2) * .95))
    d.polygon(pts, fill=col + (255,))
    dark = tuple(int(v * .7) for v in col) + (200,)
    for a in (-90, -30, -150, 20, -210):
        d.line([(c, c + S * .1), (c + S * .36 * math.cos(math.radians(a)), c + S * .36 * math.sin(math.radians(a)))], fill=dark, width=4)
    d.line([(c, c + S * .1), (c, S * .98)], fill=dark, width=5)
    return im

def star5(col, S=200):
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    d.polygon([(c + (S * .48 if i % 2 == 0 else S * .19) * math.sin(i * math.pi / 5), c - (S * .48 if i % 2 == 0 else S * .19) * math.cos(i * math.pi / 5)) for i in range(10)], fill=col + (255,))
    return im

def sakura(green=False):
    cols = [(255, 183, 197), (255, 205, 215), (250, 160, 185), (255, 225, 230), (245, 140, 170)]
    sp = [petal(c) for c in cols]
    if green: base = Image.new('RGB', (W, H), tuple(int(v * 255) for v in GREEN))
    else: base = to_img(bokeh_bg([.50, .70, .95], [.98, .82, .88], [[1, .92, .96], [1, .8, .88], [1, 1, 1]], 71, 26, .07, light=True))
    return faller(base, sp, 110 if not green else 85, 72, cyc=(1, 2), sway=(30, 110), drift=.0, sizes=(32, 78))

def autumn():
    cols = [(220, 70, 30), (240, 130, 30), (250, 185, 50), (190, 50, 35), (170, 95, 40), (230, 100, 20)]
    sp = [maple(c) for c in cols]
    base = to_img(bokeh_bg([.10, .05, .02], [.30, .14, .04], [[1, .6, .2], [1, .8, .4], [.9, .4, .15]], 73, 45, .14))
    return faller(base, sp, 60, 74, cyc=(1, 1), sway=(40, 140), sizes=(40, 110))

def usa_stars():
    cols = [(220, 40, 55), (255, 255, 255), (40, 80, 200), (235, 235, 245)]
    sp = [star5(c) for c in cols]
    base = to_img(bokeh_bg([.01, .02, .08], [.03, .05, .16], [[.9, .2, .25], [.3, .45, 1], [1, 1, 1]], 75, 40, .12))
    return faller(base, sp, 110, 76, cyc=(1, 2), sway=(20, 70), sizes=(22, 60))

# ---------------- Chinese red lanterns ----------------
def lantern_sprite(h):
    w = int(h * .9); S = 4; im = Image.new('RGBA', (w * S, int(h * 1.7) * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = w * S / 2; top = h * .18 * S; bh = h * S
    d.line([(cx, 0), (cx, top)], fill=(200, 160, 70, 255), width=2 * S)
    d.rectangle([cx - w * S * .25, top, cx + w * S * .25, top + bh * .09], fill=(225, 175, 60, 255))
    d.ellipse([cx - w * S * .5, top + bh * .05, cx + w * S * .5, top + bh * .95], fill=(215, 30, 30, 255))
    for k in (-.32, -.12, .12, .32):                                     # ribs
        d.arc([cx - w * S * abs(k) * 1.5, top + bh * .06, cx + w * S * abs(k) * 1.5, top + bh * .94], 90 if k > 0 else 270, 270 if k > 0 else 90, fill=(160, 15, 20, 255), width=3 * S)
    d.ellipse([cx - w * S * .22, top + bh * .2, cx + w * S * .22, top + bh * .8], fill=(255, 90, 50, 120))   # inner glow
    d.rectangle([cx - w * S * .25, top + bh * .9, cx + w * S * .25, top + bh * .99], fill=(225, 175, 60, 255))
    for k in range(-4, 5):                                                # tassel
        d.line([(cx + k * S * 2.2, top + bh * .99), (cx + k * S * 2.6, top + bh * 1.45)], fill=(240, 60, 40, 255), width=2 * S)
    d.ellipse([cx - S * 6, top + bh * .97, cx + S * 6, top + bh * 1.05], fill=(225, 175, 60, 255))
    im = im.resize((w, int(h * 1.7)), Image.LANCZOS)
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([w * .02, h * .2, w * .98, h * 1.1], fill=(255, 80, 40, 150))
    return im, glow.filter(ImageFilter.GaussianBlur(h * .18))

def chinese_lanterns(green=False):
    rng = np.random.default_rng(81)
    base = Image.new('RGB', (W, H), tuple(int(v * 255) for v in GREEN)) if green else to_img(bokeh_bg([.04, .01, .03], [.14, .02, .03], [[1, .75, .25], [1, .35, .2], [1, .85, .5]], 82, 50, .14))
    cfg = [(.08, .02, 150), (.24, .10, 200), (.42, .00, 170), (.58, .08, 230), (.76, .03, 160), (.92, .12, 190), (.33, .45, 120), (.68, .42, 130), (.15, .5, 100), (.86, .5, 110)]
    ls = [(fx * W, fy * H, lantern_sprite(h), rng.uniform(2.5, 5), int(rng.integers(1, 3)), rng.uniform(0, TAU)) for fx, fy, h in cfg]
    ls.sort(key=lambda l: l[2][0].height)
    for f in range(N):
        t = f / N; c = base.convert('RGBA'); d = ImageDraw.Draw(c)
        for x, y, (spr, glow), amp, k, ph in ls:
            ang = amp * math.sin(TAU * k * t + ph); pulse = .8 + .2 * math.sin(TAU * 2 * t + ph)
            d.line([(x, 0), (x, y)], fill=(170, 130, 60, 255), width=2)
            for layer in ((spr,) if green else (glow, spr)):
                r = layer.rotate(ang, resample=Image.BICUBIC, center=(layer.width / 2, 0))
                if layer is glow: r.putalpha(r.getchannel('A').point(lambda v, p=pulse: int(v * p)))
                c.alpha_composite(r, (int(x - layer.width / 2), int(y)))
        yield np.asarray(c.convert('RGB'))

# ---------------- full moon + sky lanterns (Chuseok / Mid-Autumn) ----------------
def tile_noise(w, h, seed, octaves=5):
    rng = np.random.default_rng(seed); out = np.zeros((h, w), np.float32)
    for o in range(octaves):
        gw, gh = 4 * 2 ** o, 2 * 2 ** o
        g = rng.random((gh, gw)).astype(np.float32); g = np.concatenate([g, g[:, :1]], 1); g = np.concatenate([g, g[:1]], 0)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w + w // gw, h + h // gh), Image.BICUBIC)
        out += np.asarray(im, np.float32)[:h, :w] / 255 / 2 ** o
    return out / out.max()

def moon_lanterns():
    rng = np.random.default_rng(91); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = gradient([.01, .02, .07], [.06, .07, .18], .4)
    mx, my, mr = W * .72, H * .3, 150
    d = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2) / mr
    tex = tile_noise(W, H, 92, 6)
    moon = np.clip((1 - d) / .01, 0, 1) * (.85 + .15 * tex - .12 * np.clip(tile_noise(W, H, 93, 3) - .5, 0, 1))
    glow = np.exp(-(np.maximum(d - 1, 0) / .6) ** 2) * .25 + np.exp(-(np.maximum(d - 1, 0) / 2.5) ** 2) * .10
    base = sky + (moon[..., None] * np.array([1, .95, .80]) + glow[..., None] * np.array([1, .85, .55])) * .95
    stars = np.zeros((H, W), np.float32)
    for _ in range(300): stars[int(rng.uniform(0, H * .8)), int(rng.uniform(0, W))] = rng.uniform(.3, 1)
    from scipy.ndimage import gaussian_filter
    base += gaussian_filter(stars, .7)[..., None] * 2.5 * (moon < .01)[..., None]
    cloud = tile_noise(W, H // 2, 94, 6) ** 2.2
    vfade = (np.sin(np.linspace(0, math.pi, H // 2)) ** 1.5)[:, None].astype(np.float32)
    lan = []
    for _ in range(40):
        lan.append((rng.uniform(0, W), rng.uniform(0, H + 200), rng.uniform(10, 34), int(rng.integers(1, 2)), rng.uniform(10, 40), rng.uniform(0, TAU)))
    lan.sort(key=lambda l: l[2])
    for f in range(N):
        t = f / N; img = base.copy()
        sh = int(W * t) % W                                               # clouds drift one full width per loop
        cl = np.roll(cloud, sh, axis=1)
        band = np.zeros((H, W), np.float32); band[int(H * .12):int(H * .12) + H // 2] = cl * vfade
        a = np.clip((band - .25) * 1.6, 0, .85)[..., None]
        img = img * (1 - a * .7) + a * np.array([.12, .12, .2]) + a * glow[..., None] * np.array([1, .8, .5]) * .9
        for x0, y0, s, k, sw, ph in lan:
            y = (y0 - k * (H + 200) * t) % (H + 200) - 100; x = x0 + sw * math.sin(TAU * t + ph)
            fl = .85 + .15 * math.sin(TAU * 3 * t + ph * 3)
            x0b, x1b, y0b, y1b = int(max(0, x - s * 2.5)), int(min(W, x + s * 2.5)), int(max(0, y - s * 2.5)), int(min(H, y + s * 2.5))
            if x0b >= x1b or y0b >= y1b: continue
            sx, sy = np.meshgrid(np.arange(x0b, x1b, dtype=np.float32) - x, np.arange(y0b, y1b, dtype=np.float32) - y)
            v = sy / s; hw = s * (.42 + .16 * np.clip(v + .6, 0, 1.2))       # trapezoid, wider at the top? (narrow top)
            body = np.clip(hw - np.abs(sx) + .5, 0, 1) * np.clip(.6 - np.abs(v) + .02, 0, 1) / .62
            body = np.clip(body * 4, 0, 1)
            gl = np.exp(-(sx ** 2 + (sy - s * .2) ** 2) / (s * 1.2) ** 2) * .5
            img[y0b:y1b, x0b:x1b] += (body[..., None] * np.array([1, .62, .25]) * 1.1 + gl[..., None] * np.array([1, .55, .2])) * fl
        yield np.clip(img, 0, 1.5) / 1.0

# ---------------- Halloween moon + bats ----------------
def halloween():
    rng = np.random.default_rng(101); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = gradient([.05, .02, .10], [.30, .10, .20], .45)
    mx, my, mr = W * .5, H * .42, 230
    d = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2) / mr
    tex = tile_noise(W, H, 102, 6)
    moon = np.clip((1 - d) / .008, 0, 1) * (.8 + .2 * tex)
    glow = np.exp(-(np.maximum(d - 1, 0) / .5) ** 2) * .35 + np.exp(-(np.maximum(d - 1, 0) / 2) ** 2) * .15
    base = sky + moon[..., None] * np.array([1, .78, .35]) + glow[..., None] * np.array([1, .55, .2])
    sil = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(sil)
    hill = [(x, H - 150 - 60 * math.sin(x / W * 3.2) - 25 * math.sin(x / 90)) for x in range(0, W + 10, 10)]
    dd.polygon(hill + [(W, H), (0, H)], fill=255)
    def tree(x, y, L, a, w, depth):
        if depth == 0 or L < 8: return
        x2, y2 = x + L * math.cos(a), y - L * math.sin(a)
        dd.line([(x, y), (x2, y2)], fill=255, width=max(1, int(w)))
        for da in (rng.uniform(.25, .6), -rng.uniform(.25, .6)):
            tree(x2, y2, L * rng.uniform(.62, .78), a + da, w * .68, depth - 1)
    tree(260, H - 160, 170, math.pi / 2 + .05, 24, 9); tree(W - 300, H - 150, 150, math.pi / 2 - .08, 20, 9)
    for gx in (520, 600, 1300, 1400):                                     # gravestones
        gy = H - 150 - 60 * math.sin(gx / W * 3.2) - 25 * math.sin(gx / 90)
        dd.rounded_rectangle([gx - 26, gy - 70, gx + 26, gy + 10], radius=24, fill=255)
    sm = (np.asarray(sil.filter(ImageFilter.GaussianBlur(.8)), np.float32) / 255)[..., None]
    base = base * (1 - sm) + sm * np.array([.02, .01, .03])
    fog = tile_noise(W, H // 3, 103, 5) ** 1.5
    ffade = (np.linspace(0, 1, H // 3) ** 1.2)[:, None].astype(np.float32)
    bats = [(rng.uniform(0, W), rng.uniform(.12, .6) * H, rng.uniform(30, 70), int(rng.integers(1, 3)) * rng.choice([-1, 1]), int(rng.integers(5, 9)),
             rng.uniform(0, TAU), rng.uniform(20, 70)) for _ in range(14)]
    for f in range(N):
        t = f / N; img = base.copy()
        fl = np.roll(fog, int(W * t * 2) % W, axis=1)
        a = np.zeros((H, W), np.float32); a[H - H // 3:] = np.clip(fl - .35, 0, 1) * .6 * ffade
        img = img + a[..., None] * np.array([.35, .3, .45])
        c = to_img(img); dc = ImageDraw.Draw(c)
        for x0, y0, s, k, fk, ph, bob in bats:
            x = (x0 + k * (W + 200) * t) % (W + 200) - 100; y = y0 + bob * math.sin(TAU * 2 * t + ph)
            flap = math.sin(TAU * fk * t + ph)
            wy = -s * .55 * flap; dirn = 1 if k > 0 else -1
            body = [(x - s * .12, y), (x + s * .12, y), (x, y + s * .35)]
            wing_l = [(x - s * .1, y), (x - s * .55, y + wy - s * .1), (x - s * 1.1, y + wy * 1.1), (x - s * .8, y + wy * .5 + s * .15), (x - s * .5, y + wy * .3 + s * .2), (x - s * .1, y + s * .15)]
            wing_r = [(2 * x - px, py) for px, py in wing_l]
            col = (8, 4, 12)
            dc.polygon(wing_l, fill=col); dc.polygon(wing_r, fill=col); dc.polygon(body, fill=col)
            dc.ellipse([x - s * .13, y - s * .2, x + s * .13, y + s * .08], fill=col)
            dc.polygon([(x - s * .12, y - s * .12), (x - s * .07, y - s * .3), (x - s * .02, y - s * .12)], fill=col)
            dc.polygon([(x + s * .12, y - s * .12), (x + s * .07, y - s * .3), (x + s * .02, y - s * .12)], fill=col)
        yield np.asarray(c)

CLIPS = {
    'chinese-red-lanterns-lunar-new-year-loop': chinese_lanterns,
    'full-moon-sky-lanterns-chuseok-mid-autumn-loop': moon_lanterns,
    'falling-cherry-blossom-sakura-petals-loop': lambda: sakura(False),
    'cherry-blossom-petals-green-screen-loop': lambda: sakura(True),
    'halloween-full-moon-bats-loop': halloween,
    'falling-autumn-maple-leaves-loop': autumn,
    'red-white-blue-stars-falling-loop': usa_stars,
}
FLOAT = {'full-moon-sky-lanterns-chuseok-mid-autumn-loop'}

if __name__ == '__main__':
    for name in sys.argv[1:]:
        gen = CLIPS[name]()
        if name in FLOAT: gen = ((np.clip(fr, 0, 1) ** (1 / 1.1) * 255).astype(np.uint8) for fr in gen)
        encode_raw(name, gen); print('done', name, flush=True)

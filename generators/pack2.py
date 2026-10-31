"""Clips 17-50. Usage: python3 pack2.py <name> [...]  (run from the output folder)"""
import numpy as np, math, sys, subprocess, colorsys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter
from pack import W, H, N, TAU, FPS, gradient, encode, tone, blob, bokeh, flow

GREEN = np.array([0, 177, 64], np.float32) / 255
FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
def hsv(h, s=1, v=1): return np.array(colorsys.hsv_to_rgb(h % 1, s, v))

def encode_raw(name, frames, n=N):
    """frames already final 0..1 (no gamma) — used for exact chroma green."""
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{name}.mp4'], stdin=subprocess.PIPE)
    for i, img in enumerate(frames):
        fr = img if img.dtype == np.uint8 else (np.clip(img, 0, 1) * 255).astype(np.uint8)
        p.stdin.write(fr.tobytes())
        if i == n // 2: Image.fromarray(fr).save(f'{name}-poster.jpg', quality=90)
    p.stdin.close(); p.wait()

def on_green(frames, k=1.3):
    """light-on-black frames -> same light over chroma green (green stays exact where empty)."""
    for img in frames:
        fg = np.clip(img, 0, 1) ** (1 / 1.1)
        a = np.clip(fg.max(2, keepdims=True) * k, 0, 1)
        a = np.where(a < 0.04, 0, a)
        yield fg + GREEN * (1 - a)

# ---------- snow / sparkles with custom background ----------
def snow(bg, seed=3):
    rng = np.random.default_rng(seed); M = 60; span = H + 2 * M; fl = []
    for n, r0, r1, cyc, b in [(160, 2, 4, 1, .45), (110, 4, 7, 2, .7), (40, 8, 14, 3, .9)]:
        for _ in range(n):
            fl.append((rng.uniform(0, W), rng.uniform(0, span), rng.uniform(r0, r1), cyc, rng.uniform(15, 60),
                       int(rng.integers(1, 3)), rng.uniform(0, TAU), b * rng.uniform(.7, 1.1)))
    col = np.array([.92, .96, 1.0])
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, r, cyc, sw, sk, sp, b in fl:
            blob(img, x0 + sw * math.sin(TAU * sk * t + sp), (y0 + cyc * span * t) % span - M, r, col, b, edge=.5, glow=.25, rim=0)
        yield tone(img, 1.8)

def sparkles(bg, cols, seed=11, n=420):
    rng = np.random.default_rng(seed); pts = []
    for _ in range(n):
        pts.append((rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2.5, 6.5), int(rng.integers(1, 4)), rng.uniform(0, TAU),
                    np.array(cols[rng.integers(len(cols))]), rng.uniform(.5, 1.0)))
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, r, tw, tp, col, b in pts:
            x = (x0 + W * t) % (W + 40) - 20; y = y0 + 12 * math.sin(TAU * t + tp)
            s = max(0.0, math.sin(TAU * tw * t + tp)) ** 2 * b * 1.6
            if s < 0.02: continue
            blob(img, x, y, r, col, s, edge=.6, glow=.9, rim=0)
            L = int(r * 9 * min(s, 1.2)) + 1; xi, yi = int(x), int(y)
            for dx, dy in ((1, 0), (0, 1)):
                for k in range(-L, L + 1):
                    px, py = xi + k * dx, yi + k * dy
                    if 0 <= px < W and 0 <= py < H: img[py, px] += col * s * .9 * (1 - abs(k) / (L + 1)) ** 2
        yield tone(img, 1.7)

# ---------- confetti on any background (opaque pieces) ----------
def confetti(bg, cols, seed=21, n=240):
    rng = np.random.default_rng(seed); M = 60; span = H + 2 * M
    ps = [(rng.uniform(0, W), rng.uniform(0, span), rng.uniform(20, 36), rng.uniform(10, 17), int(rng.integers(1, 3)),
           int(rng.integers(1, 4)) * rng.choice([-1, 1]), int(rng.integers(2, 6)), rng.uniform(0, TAU), rng.uniform(20, 70),
           np.array(cols[rng.integers(len(cols))]) * rng.uniform(.85, 1)) for _ in range(n)]
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, L, Wd, cyc, rot, flip, ph, sw, col in ps:
            cx = x0 + sw * math.sin(TAU * t + ph); cy = (y0 + cyc * span * t) % span - M
            a = rot * TAU * t + ph; sc = abs(math.cos(flip * TAU * t + ph)) * .85 + .15
            hw, hh = L / 2, Wd / 2 * sc; R = int(max(hw, hh)) + 3
            x0b, x1b, y0b, y1b = int(max(0, cx - R)), int(min(W, cx + R)), int(max(0, cy - R)), int(min(H, cy + R))
            if x0b >= x1b or y0b >= y1b: continue
            sx, sy = np.meshgrid(np.arange(x0b, x1b, dtype=np.float32) - cx, np.arange(y0b, y1b, dtype=np.float32) - cy)
            u = sx * math.cos(a) + sy * math.sin(a); v = -sx * math.sin(a) + sy * math.cos(a)
            mask = (np.clip(hw - np.abs(u) + .5, 0, 1) * np.clip(hh - np.abs(v) + .5, 0, 1))[..., None]
            region = img[y0b:y1b, x0b:x1b]; region[:] = region * (1 - mask) + col * (.65 + .35 * sc) * mask
        yield img

# ---------- light rays with custom colours ----------
def rays(base, warm, seed=5, src=(-0.15, -0.25)):
    rng = np.random.default_rng(seed); h, w = H // 3, W // 3
    gy, gx = np.mgrid[0:h, 0:w].astype(np.float32); sx, sy = src[0] * w, src[1] * h
    ang = np.arctan2(gy - sy, gx - sx); dist = np.sqrt((gx - sx) ** 2 + (gy - sy) ** 2) / w
    beams = [(rng.uniform(8, 26), int(rng.integers(1, 3)) * rng.choice([-1, 1]), rng.uniform(0, TAU), rng.uniform(.4, 1)) for _ in range(6)]
    base = np.array(base); warm = np.array(warm)
    for f in range(N):
        t = f / N; v = np.zeros((h, w), np.float32)
        for k, m, ph, a in beams: v += a * np.clip(np.sin(k * ang + TAU * m * t + ph), 0, 1) ** 4
        v = v / 2.5 * np.exp(-dist * 1.3) + .35 * np.exp(-dist * 4)
        small = base + v[..., None] * warm
        yield np.asarray(Image.fromarray((np.clip(small, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255

# ---------- rising embers ----------
def embers():
    rng = np.random.default_rng(17); bg = gradient([.01, .005, .005], [.12, .03, .01], .5)
    bg += (np.exp(-((np.mgrid[0:H, 0:W][0] - H) / (H * .35)) ** 2) * .10)[..., None] * np.array([1, .35, .08])
    M = 40; span = H + 2 * M
    ps = [(rng.uniform(0, W), rng.uniform(0, span), rng.uniform(2.5, 7), int(rng.integers(1, 4)), rng.uniform(20, 90),
           int(rng.integers(1, 3)), rng.uniform(0, TAU), int(rng.integers(2, 7)), hsv(rng.uniform(.02, .11), rng.uniform(.75, 1)))
          for _ in range(300)]
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, r, cyc, sw, sk, ph, fk, col in ps:
            y = (y0 - cyc * span * t) % span - M
            x = x0 + sw * math.sin(TAU * sk * t + ph) + 20 * math.sin(TAU * 3 * t + ph * 2)
            fl = .55 + .45 * math.sin(TAU * fk * t + ph)
            life = min(1, (y + M) / (H * .9))                      # fade as they rise
            blob(img, x, y, r, col, 1.8 * fl * life, edge=.7, glow=1.3, rim=0)
        yield tone(img, 1.7)

# ---------- floating hearts ----------
def heart_sprite(size, col):
    S = size * 4; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = []
    for i in range(120):
        a = TAU * i / 120; x = 16 * math.sin(a) ** 3; y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((S / 2 + x * S / 38, S / 2 - y * S / 38))
    d.polygon(pts, fill=tuple(int(v * 255) for v in col) + (255,))
    hl = [(S * .36, S * .30), (S * .44, S * .30)]
    d.ellipse([S * .30, S * .26, S * .40, S * .36], fill=(255, 255, 255, 110))
    im = im.resize((size, size), Image.LANCZOS)
    return im, im.filter(ImageFilter.GaussianBlur(size * .12))

def hearts(bgcol=([.10, .02, .06], [.22, .04, .10]), green=False):
    rng = np.random.default_rng(23)
    base = Image.new('RGB', (W, H), tuple(int(v) for v in GREEN * 255)) if green else \
        Image.fromarray((np.clip(gradient(*bgcol, .5), 0, 1) ** (1 / 1.1) * 255).astype(np.uint8))
    cols = [[1, .25, .4], [1, .45, .6], [.95, .15, .3], [1, .65, .75], [1, .35, .5]]
    hs = []
    for _ in range(34):
        sz = int(rng.uniform(50, 150)); hs.append((rng.uniform(0, W), rng.uniform(0, H + 300), sz, heart_sprite(sz, cols[rng.integers(5)]),
                                                   int(rng.integers(1, 3)), rng.uniform(20, 60), rng.uniform(0, TAU), rng.uniform(8, 18)))
    hs.sort(key=lambda h: h[2])
    span = H + 300
    for f in range(N):
        t = f / N; c = base.convert('RGBA')
        for x0, y0, sz, (spr, glow), cyc, sw, ph, rot in hs:
            y = (y0 - cyc * span * t) % span - 150; x = x0 + sw * math.sin(TAU * t + ph)
            ang = rot * math.sin(TAU * t + ph)
            for layer in ((glow,) if green else (glow, glow)) + (spr,):
                r = layer.rotate(ang, resample=Image.BICUBIC); c.alpha_composite(r, (int(x - sz / 2), int(y - sz / 2)))
        yield np.asarray(c.convert('RGB'))

# ---------- bubbles ----------
def bubbles():
    rng = np.random.default_rng(29); bg = gradient([.02, .12, .25], [.01, .04, .10], .5); M = 120; span = H + 2 * M
    bs = [(rng.uniform(0, W), rng.uniform(0, span), rng.uniform(14, 80), int(rng.integers(1, 3)), rng.uniform(15, 50), rng.uniform(0, TAU),
           int(rng.integers(1, 3))) for _ in range(70)]
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, r, cyc, sw, ph, sk in bs:
            cx = x0 + sw * math.sin(TAU * sk * t + ph); cy = (y0 - cyc * span * t) % span - M
            x0b, x1b, y0b, y1b = int(max(0, cx - r - 3)), int(min(W, cx + r + 3)), int(max(0, cy - r - 3)), int(min(H, cy + r + 3))
            if x0b >= x1b or y0b >= y1b: continue
            sx, sy = np.meshgrid(np.arange(x0b, x1b, dtype=np.float32), np.arange(y0b, y1b, dtype=np.float32))
            d = np.sqrt((sx - cx) ** 2 + (sy - cy) ** 2) / r
            ring = np.exp(-((d - .96) / .05) ** 2) * .55 + np.clip(d, 0, 1) ** 6 * .18 * (d < 1)
            hlx, hly = cx - r * .4, cy - r * .4
            hl = np.exp(-(((sx - hlx) ** 2 + (sy - hly) ** 2) / (r * .16) ** 2)) * .8
            irid = np.stack([.75 + .25 * np.sin(sx / r * 3 + ph), .9 + .1 * np.sin(sy / r * 3), np.ones_like(sx)], -1)
            img[y0b:y1b, x0b:x1b] += (ring + hl)[..., None] * irid
        yield tone(img, 1.6)

# ---------- starry night with shooting star ----------
def starry():
    rng = np.random.default_rng(31); bg = gradient([.005, .01, .04], [.03, .04, .10], .4)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    band = np.exp(-(((yy - H * .9 + xx * .45) / (H * .22)) ** 2)) * .12          # faint milky band
    bg += band[..., None] * np.array([.6, .5, .9])
    nb = 900; sx = rng.uniform(0, W, nb); sy = rng.uniform(0, H, nb); sb = rng.uniform(.15, 1, nb) ** 2
    tw = rng.integers(1, 4, nb); tp = rng.uniform(0, TAU, nb)
    scol = np.array([hsv(rng.choice([.6, .62, .1, .0]), rng.uniform(0, .25)) for _ in range(nb)])
    big = np.argsort(-sb)[:40]
    for f in range(N):
        t = f / N; buf = np.zeros((H, W, 3), np.float32)
        a = sb * (.55 + .45 * np.sin(TAU * tw * t + tp))
        xi, yi = sx.astype(int), sy.astype(int)
        np.add.at(buf, (yi, xi), scol * a[:, None] * 4.0)
        light = gaussian_filter(buf, (.8, .8, 0)) * 3
        img = bg + light
        for i in big: blob(img, sx[i], sy[i], 3.5, scol[i], a[i] * 1.2, edge=1, glow=1.0, rim=0)
        for t0, x0, y0 in ((.18, .25, .12), (.62, .7, .08)):                       # two shooting stars
            s = (t - t0) / .07
            if 0 <= s <= 1:
                hx, hy = (x0 + .25 * s) * W, (y0 + .14 * s) * H
                for k in range(40):
                    q = k / 40; px, py = hx - q * .12 * W, hy - q * .067 * H
                    blob(img, px, py, 2.4, np.array([1, 1, 1]), (1 - q) ** 2 * math.sin(math.pi * s) * 1.2, edge=1, glow=.8, rim=0)
        yield tone(img, 1.6)

# ---------- balloons rising ----------
def balloons(green=False, cols=None, sky=([.35, .62, .92], [.75, .88, 1.0]), seed=37):
    rng = np.random.default_rng(seed)
    cols = cols or [(235, 50, 70), (255, 190, 40), (50, 140, 255), (40, 190, 120), (170, 80, 230), (255, 120, 40), (255, 110, 170)]
    bgimg = Image.new('RGB', (W, H), tuple(int(v) for v in GREEN * 255)) if green else \
        Image.fromarray((np.clip(gradient(sky[0], sky[1], .15), 0, 1) * 255).astype(np.uint8))
    span = H + 500
    bl = sorted([(rng.uniform(80, W - 80), rng.uniform(0, span), rng.uniform(55, 105), cols[rng.integers(len(cols))], rng.uniform(15, 45),
                  rng.uniform(0, TAU), int(rng.integers(1, 3))) for _ in range(26)], key=lambda b: b[2])
    for f in range(N):
        t = f / N; im = bgimg.copy().resize((W * 2, H * 2)); d = ImageDraw.Draw(im)
        for x0, y0, r, col, sw, ph, cyc in bl:
            cx = x0 + sw * math.sin(TAU * t + ph); cy = (y0 - cyc * span * t) % span - 250
            R = r * 2; X, Y = cx * 2, cy * 2
            pts = [(X + 6 * math.sin(TAU * (k / 30 * 1.5 + t) + ph) * (k / 30), Y + R * 1.2 + k * 10) for k in range(31)]
            d.line(pts, fill=(90, 90, 90) if not green else (40, 40, 40), width=3)
            d.polygon([(X, Y + R * 1.12), (X - 12, Y + R * 1.25), (X + 12, Y + R * 1.25)], fill=tuple(int(c * .8) for c in col))
            d.ellipse([X - R, Y - R * 1.2, X + R, Y + R * 1.18], fill=col)
            d.ellipse([X - R * .55, Y - R * .85, X - R * .15, Y - R * .3], fill=tuple(min(255, int(c + (255 - c) * .55)) for c in col))
        yield np.asarray(im.resize((W, H), Image.LANCZOS))

# ---------- floating dust particles (overlay) ----------
def dust():
    rng = np.random.default_rng(41); bg = gradient([.012, .012, .014], [.02, .018, .016], .6)
    ps = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.2, 9) ** 1.0, rng.uniform(40, 180), rng.uniform(30, 120),
           int(rng.integers(1, 3)) * rng.choice([-1, 1]), int(rng.integers(1, 3)) * rng.choice([-1, 1]), rng.uniform(0, TAU), rng.uniform(0, TAU))
          for _ in range(230)]
    col = np.array([1, .93, .82])
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, r, ax, ay, kx, ky, px, py in ps:
            x = x0 + ax * math.sin(TAU * kx * t + px); y = y0 + ay * math.sin(TAU * ky * t + py)
            focus = 1 if r < 3.5 else 3.5 / r                                       # big = out of focus, dimmer
            blob(img, x, y, r, col, 1.1 * focus, edge=.4 + .5 * (1 - focus), glow=.4, rim=0)
        yield tone(img, 1.5)

# ---------- light leaks (overlay) ----------
def lightleaks(seed=43, cols=([1, .45, .1], [1, .2, .15], [1, .75, .3], [.95, .25, .5])):
    rng = np.random.default_rng(seed); h, w = H // 8, W // 8
    gy, gx = np.mgrid[0:h, 0:w].astype(np.float32)
    bl = [(rng.uniform(-.2, 1.2) * w, rng.uniform(-.2, 1.2) * h, rng.uniform(.14, .32) * w, rng.uniform(.3, .6) * w, rng.uniform(.2, .5) * h,
           int(rng.integers(1, 3)), rng.uniform(0, TAU), np.array(cols[i % len(cols)])) for i in range(7)]
    for f in range(N):
        t = f / N; v = np.zeros((h, w, 3), np.float32)
        for x0, y0, r, ax, ay, k, ph, col in bl:
            cx = x0 + ax * math.sin(TAU * k * t + ph); cy = y0 + ay * math.cos(TAU * t + ph)
            a = .55 + .45 * math.sin(TAU * t + ph * 1.7)
            v += np.exp(-((gx - cx) ** 2 + (gy - cy) ** 2) / r ** 2)[..., None] * col * a
        v = 1 - np.exp(-v * 1.1)
        yield np.asarray(Image.fromarray((np.clip(v, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255

# ---------- retro perspective grid ----------
def grid():
    hz = int(H * .52); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = gradient([.03, .01, .10], [.30, .05, .35], 0)
    # sun with stripes
    sd = np.sqrt((xx - W / 2) ** 2 + (yy - hz + 40) ** 2) / 260
    sun = (sd < 1) & (yy < hz)
    stripes = ~((yy > hz - 170) & (((hz - yy) % 36) < (1 + (hz - 40 - yy).clip(0) * 0 + (170 - (hz - yy)).clip(0) / 12)))
    sung = (np.clip((yy - (hz - 300)) / 300, 0, 1))[..., None]
    suncol = np.array([1, .85, .25]) * (1 - sung) + np.array([1, .2, .55]) * sung
    sky = np.where((sun & stripes)[..., None], suncol, sky) + np.exp(-(sd / 1.6) ** 2)[..., None] * np.array([.35, .05, .25]) * (yy < hz)[..., None]
    g = yy > hz; dy = np.maximum(yy - hz, 1)
    z = 600 / dy                                                          # depth
    u = (xx - W / 2) / dy * 2.2                                           # lateral grid coordinate
    du = 2.2 / dy
    vd = np.abs(u - np.round(u)) / du                                     # pixel distance to vertical line
    vline = np.exp(-(vd / 1.3) ** 2) * g
    col = np.array([1, .2, .85]); col2 = np.array([.2, .9, 1])
    fog = np.clip(dy / (H - hz), 0, 1)[..., None] ** .6
    floor = np.array([.04, .0, .08])
    for f in range(N):
        t = f / N
        zz = z / 40 + t * 2                                               # 2 lines pass per loop -> seamless
        dz = 600 / dy ** 2 / 40
        hd = np.abs(zz - np.round(zz)) / dz
        hline = np.exp(-(hd / 1.3) ** 2) * g
        lines = np.clip(vline + hline, 0, 1)[..., None]
        glow = gaussian_filter(lines[..., 0], 4)[..., None] * 1.6
        groundc = col * (1 - fog) + col2 * fog * .0 + col * fog
        img = np.where(g[..., None], floor + (lines + glow) * groundc * (.35 + .65 * fog), sky)
        img = img + np.exp(-((yy - hz) / 6) ** 2)[..., None] * np.array([1, .4, .9]) * .8
        yield img

# ---------- plexus network ----------
def plexus(seed=47, col=(.35, .75, 1.0), bgc=([.01, .02, .06], [.02, .06, .12])):
    rng = np.random.default_rng(seed); bg = gradient(*bgc, .6); col = np.array(col); n = 110
    p = [(rng.uniform(-.05, 1.05) * W, rng.uniform(-.05, 1.05) * H, rng.uniform(30, 140), rng.uniform(30, 120), int(rng.integers(1, 3)) * rng.choice([-1, 1]),
          int(rng.integers(1, 3)), rng.uniform(0, TAU), rng.uniform(0, TAU)) for _ in range(n)]
    for f in range(N):
        t = f / N
        P = np.array([(x + ax * math.sin(TAU * kx * t + px), y + ay * math.cos(TAU * ky * t + py)) for x, y, ax, ay, kx, ky, px, py in p])
        lay = Image.new('L', (W * 2, H * 2), 0); d = ImageDraw.Draw(lay)
        D = np.sqrt(((P[:, None] - P[None]) ** 2).sum(-1))
        ii, jj = np.where((D < 300) & (np.triu(np.ones_like(D), 1) > 0))
        for i, j in zip(ii, jj):
            a = int(255 * (1 - D[i, j] / 300) ** 1.1)
            d.line([tuple(P[i] * 2), tuple(P[j] * 2)], fill=a, width=2)
        lines = np.asarray(lay.resize((W, H), Image.BILINEAR), np.float32) / 255 * 1.3
        img = bg + lines[..., None] * col
        for x, y in P: blob(img, x, y, 5, col, 1.8, edge=.6, glow=1.4, rim=0)
        img = img + gaussian_filter(lines, 6)[..., None] * col * .5
        yield tone(img, 1.6)

# ---------- hexagon tech pulse ----------
def hexagons():
    s = 46.0; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    q = (math.sqrt(3) / 3 * xx - yy / 3) / s; r = (2 / 3 * yy) / s
    # cube round
    x, z = q, r; y = -x - z
    rx, ry, rz = np.round(x), np.round(y), np.round(z)
    dx, dy, dz = np.abs(rx - x), np.abs(ry - y), np.abs(rz - z)
    m1 = (dx > dy) & (dx > dz); m2 = (~m1) & (dy > dz)
    rx = np.where(m1, -ry - rz, rx); rz = np.where(~m1 & ~m2, -rx - ry, rz)
    cx = s * math.sqrt(3) * (rx + rz / 2); cy = s * 1.5 * rz
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / s                  # 0 centre .. ~1 edge
    # hex edge distance via max of projections
    ax, ay = np.abs(xx - cx), np.abs(yy - cy)
    hd = np.maximum(ax, ax / 2 + ay * math.sqrt(3) / 2) / (s * math.sqrt(3) / 2)
    edge = np.exp(-((hd - 1.0) / .05) ** 2)
    bg = gradient([.01, .02, .05], [.02, .04, .09], .6)
    rng = np.random.default_rng(53); hid = (rx * 73856093 + rz * 19349663) % 997
    ph = (hid / 997 * TAU).astype(np.float32); col = np.array([.2, .7, 1.0])
    for f in range(N):
        t = f / N
        wave = np.clip(np.sin(TAU * (cx / W * 1.2 - t * 2) + np.sin(cy / H * 3)), 0, 1) ** 6        # sweeping band
        spark = np.clip(np.sin(ph * 3 + TAU * 2 * t), 0, 1) ** 30                                    # random hex blinks
        fill = (wave * .35 + spark * .5) * (hd < .93)
        img = bg + edge[..., None] * col * (.25 + .8 * wave)[..., None] + fill[..., None] * col * .6
        yield tone(img, 1.6)

# ---------- countdown 10 -> 1 (10 s, not a loop) ----------
def countdown(green=False):
    n = 300; f_big = ImageFont.truetype(FONT, 360)
    bgarr = (np.clip(gradient([.03, .02, .06], [.10, .04, .10], .6), 0, 1) ** (1 / 1.1) * 255).astype(np.uint8)
    for f in range(n):
        sec = f // 30; u = (f % 30) / 30; num = 10 - sec
        im = Image.new('RGB', (W, H), tuple(int(v * 255) for v in GREEN)) if green else Image.fromarray(bgarr)
        d = ImageDraw.Draw(im)
        R = 330; box = [W / 2 - R, H / 2 - R, W / 2 + R, H / 2 + R]
        d.arc(box, 0, 360, fill=(70, 60, 50) if not green else (20, 20, 20), width=14)
        d.arc(box, -90, -90 + 360 * (1 - u), fill=(255, 200, 70), width=14)
        sc = 1 + .25 * max(0, 1 - u * 5)                                   # pop at each new number
        txt = Image.new('RGBA', (900, 800), (0, 0, 0, 0)); td = ImageDraw.Draw(txt)
        td.text((450, 400), str(num), font=f_big, fill=(255, 214, 110, 255), anchor='mm')
        txt = txt.resize((int(900 * sc), int(800 * sc)), Image.LANCZOS)
        a = int(255 * min(1, u * 8)) if sec > 0 else 255
        al = txt.getchannel('A').point(lambda v: v * a // 255); txt.putalpha(al)
        im.paste(txt, (int(W / 2 - txt.width / 2), int(H / 2 - txt.height / 2) + 20), txt)
        yield np.asarray(im)

# ---------- hanging Christmas ornaments ----------
def ornament(size, col):
    S = size * 4; im = Image.new('RGBA', (S, int(S * 1.2)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2; top = S * .2
    d.rectangle([c - S * .1, top - S * .1, c + S * .1, top + S * .04], fill=(210, 180, 90, 255))
    d.ellipse([c - S * .04, top - S * .19, c + S * .04, top - S * .09], outline=(210, 180, 90, 255), width=max(2, S // 80))
    d.ellipse([S * .05, top, S * .95, top + S * .9], fill=tuple(int(v * 255) for v in col) + (255,))
    dark = tuple(int(v * 255 * .7) for v in col) + (255,)
    for yy_ in (.38, .62):
        d.rectangle([S * .07, top + S * .9 * yy_ - S * .025, S * .93, top + S * .9 * yy_ + S * .025], fill=(240, 210, 120, 255))
    d.ellipse([S * .22, top + S * .12, S * .4, top + S * .3], fill=(255, 255, 255, 150))
    im = im.resize((size, int(size * 1.2)), Image.LANCZOS)
    return im

def ornaments():
    rng = np.random.default_rng(59)
    bgf = gradient([.02, .04, .03], [.08, .02, .03], .5)
    bk = np.zeros((H, W, 3), np.float32)
    for _ in range(45): blob(bk, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 120), hsv(rng.choice([.0, .1, .12, .33])), .12, edge=.25, glow=.1)
    base = Image.fromarray((np.clip(tone(bgf + bk, 1.6), 0, 1) ** (1 / 1.1) * 255).astype(np.uint8))
    cols = [[.85, .1, .12], [.95, .7, .15], [.1, .55, .25], [.75, .75, .8], [.2, .35, .85]]
    cfg = [(.08, .30, 130), (.2, .55, 160), (.33, .25, 110), (.47, .45, 190), (.62, .28, 120), (.75, .6, 150), (.9, .35, 140), (.55, .75, 100), (.15, .82, 90)]
    os_ = [(fx * W, fy * H, sz, ornament(sz, cols[i % 5]), rng.uniform(3, 7), int(rng.integers(1, 3)), rng.uniform(0, TAU)) for i, (fx, fy, sz) in enumerate(cfg)]
    for f in range(N):
        t = f / N; c = base.convert('RGBA'); d = ImageDraw.Draw(c)
        for x, y, sz, spr, amp, k, ph in os_:
            ang = amp * math.sin(TAU * k * t + ph)
            topy = y - sz * .25
            ex = x + math.sin(math.radians(-ang)) * 0
            d.line([(x, 0), (x, topy)], fill=(200, 170, 90, 200), width=2)
            r = spr.rotate(ang, resample=Image.BICUBIC, center=(sz / 2, 0), expand=False)
            c.alpha_composite(r, (int(x - sz / 2), int(topy)))
        yield np.asarray(c.convert('RGB'))

# ---------- fiesta banderitas ----------
def banderitas(green=False):
    rng = np.random.default_rng(61)
    cols = [(230, 40, 50), (255, 200, 30), (40, 110, 230), (40, 180, 90), (255, 120, 30), (220, 60, 160), (250, 250, 250)]
    if green: base = Image.new('RGB', (W * 2, H * 2), tuple(int(v * 255) for v in GREEN))
    else: base = Image.fromarray((np.clip(gradient([.25, .55, .92], [.70, .86, 1.0], .1), 0, 1) * 255).astype(np.uint8)).resize((W * 2, H * 2))
    rows = [(-.02, .10, 1.02, .06, 150), (-.02, .30, 1.02, .22, 170), (-.02, .52, 1.02, .44, 150)] if not green else [(-.02, .05, 1.02, .05, 160), (-.02, .28, 1.02, .26, 150)]
    flags = []
    for ri, (x0, y0, x1, y1, sag) in enumerate(rows):
        nflag = 22
        for i in range(nflag):
            s = (i + .5) / nflag
            flags.append((ri, s, cols[(i + ri * 3) % len(cols)], rng.uniform(0, TAU)))
    def rowpt(ri, s, t):
        x0, y0, x1, y1, sag = rows[ri]
        sway = 10 * math.sin(TAU * (t + ri * .3))
        return ((x0 + (x1 - x0) * s) * W * 2, ((y0 + (y1 - y0) * s) * H + sag * 4 * s * (1 - s) + sway * 4 * s * (1 - s)) * 2)
    for f in range(N):
        t = f / N; im = base.copy(); d = ImageDraw.Draw(im)
        for ri in range(len(rows)):
            d.line([rowpt(ri, s, t) for s in np.linspace(0, 1, 80)], fill=(60, 50, 40), width=5)
        for ri, s, col, ph in flags:
            nflag = 22; hw = .5 / nflag * .92
            a, b = rowpt(ri, s - hw, t), rowpt(ri, s + hw, t)
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            L = 120 * 2 * (.9 + .1 * math.sin(TAU * 2 * t + ph))
            tipx = mx + 26 * math.sin(TAU * 2 * t + ph) * 2
            d.polygon([a, b, (tipx, my + L)], fill=col)
            d.polygon([a, ((a[0] + tipx) / 2, (a[1] + my + L) / 2), (mx, my)], fill=tuple(int(c * .88) for c in col))
        yield np.asarray(im.resize((W, H), Image.LANCZOS))

# ---------- registry ----------
G = lambda: np.zeros((H, W, 3), np.float32)
CLIPS = {
    'purple-violet-bokeh-loop': (lambda: bokeh(81, [.03, .01, .07], [.07, .02, .10], [[.65, .35, 1], [.8, .5, 1], [.55, .25, .9], [1, .6, .95], [.9, .8, 1]]), 0),
    'teal-aqua-bokeh-loop': (lambda: bokeh(83, [.0, .04, .05], [.01, .07, .08], [[.2, .9, .85], [.3, 1, .95], [.15, .7, .9], [.6, 1, .9], [.9, 1, 1]]), 0),
    'silver-white-bokeh-loop': (lambda: bokeh(85, [.03, .03, .04], [.06, .06, .07], [[.9, .92, 1], [1, 1, 1], [.75, .8, .9], [1, .95, .88], [.85, .9, 1]]), 0),
    'rainbow-party-bokeh-loop': (lambda: bokeh(87, [.02, .02, .05], [.05, .02, .06], [[1, .25, .3], [1, .7, .15], [.3, .9, .4], [.25, .55, 1], [.8, .35, 1], [1, .45, .8]]), 0),
    'red-gold-lunar-new-year-bokeh-loop': (lambda: bokeh(89, [.08, .0, .01], [.16, .01, .02], [[1, .75, .2], [1, .85, .4], [1, .3, .15], [1, .6, .1], [1, .95, .6]]), 0),
    'navy-gold-graduation-bokeh-loop': (lambda: bokeh(91, [.01, .02, .08], [.02, .04, .14], [[1, .8, .3], [1, .9, .55], [.9, .7, .25], [.7, .8, 1], [1, .95, .8]]), 0),
    'emerald-gold-bokeh-loop': (lambda: bokeh(93, [.0, .05, .03], [.01, .09, .05], [[1, .8, .3], [.3, 1, .55], [.2, .8, .4], [1, .9, .55], [.6, 1, .7]]), 0),
    'ocean-teal-gradient-flow-loop': (lambda: flow(101, [[.0, .10, .20], [.0, .35, .45], [.1, .65, .70], [.45, .90, .85], [.0, .20, .35]]), 0),
    'pastel-dream-gradient-flow-loop': (lambda: flow(103, [[.95, .75, .85], [.80, .75, .98], [.70, .88, 1.0], [1.0, .88, .78], [.90, .70, .90]]), 0),
    'black-gold-luxury-gradient-flow-loop': (lambda: flow(105, [[.02, .02, .02], [.20, .13, .03], [.70, .50, .15], [1.0, .82, .45], [.10, .07, .02]]), 0),
    'crimson-red-gradient-flow-loop': (lambda: flow(107, [[.08, .0, .02], [.45, .02, .08], [.85, .10, .15], [1.0, .35, .30], [.25, .0, .05]]), 0),
    'fresh-green-gradient-flow-loop': (lambda: flow(109, [[.02, .20, .10], [.10, .50, .25], [.45, .80, .30], [.85, .95, .50], [.05, .35, .25]]), 0),
    'aurora-night-gradient-flow-loop': (lambda: flow(111, [[.01, .02, .06], [.0, .35, .30], [.15, .85, .55], [.40, .25, .75], [.02, .05, .15]]), 0),
    'falling-snow-green-screen-loop': (lambda: on_green(snow(G())), 1),
    'falling-snow-black-overlay-loop': (lambda: snow(G() + .0, 5), 0),
    'silver-blue-glitter-sparkles-loop': (lambda: sparkles(gradient([.01, .01, .03], [.02, .03, .06], .6), [[.85, .9, 1], [.6, .75, 1], [1, 1, 1]], 12), 0),
    'gold-sparkles-green-screen-loop': (lambda: on_green(sparkles(G(), [[1, .8, .35], [1, .9, .5], [1, .7, .3]], 13, 300)), 1),
    'confetti-green-screen-loop': (lambda: confetti(np.zeros((H, W, 3), np.float32) + (GREEN ** 1.1), [[1, .26, .38], [1, .76, .16], [.24, .56, 1], [.86, .38, 1], [1, .55, .2], [1, 1, 1]], 22), 0),
    'gold-silver-new-year-confetti-loop': (lambda: confetti(gradient([.01, .01, .03], [.04, .03, .06], .5), [[1, .8, .3], [.95, .7, .2], [.85, .85, .9], [1, 1, 1], [.75, .75, .8]], 24, 280), 0),
    'heavenly-white-light-rays-loop': (lambda: rays([.06, .07, .10], [.85, .92, 1.0], 7, (.5, -.35)), 0),
    'rising-fire-embers-loop': (embers, 0),
    'floating-hearts-loop': (lambda: hearts(), 1),
    'floating-hearts-green-screen-loop': (lambda: hearts(green=True), 1),
    'floating-bubbles-loop': (bubbles, 0),
    'starry-night-shooting-stars-loop': (starry, 0),
    'birthday-balloons-rising-loop': (lambda: balloons(), 1),
    'balloons-rising-green-screen-loop': (lambda: balloons(True), 1),
    'floating-dust-particles-overlay-loop': (dust, 0),
    'warm-light-leaks-overlay-loop': (lightleaks, 0),
    'retro-neon-grid-sunset-loop': (grid, 0),
    'blue-tech-network-plexus-loop': (plexus, 0),
    'blue-hexagon-tech-pulse-loop': (hexagons, 0),
    'new-year-countdown-10-to-1': (countdown, 2),
    'hanging-christmas-ornaments-loop': (ornaments, 1),
    'fiesta-banderitas-flags-loop': (lambda: banderitas(), 1),
    'fiesta-banderitas-green-screen-loop': (lambda: banderitas(True), 1),
}

if __name__ == '__main__':
    for name in sys.argv[1:]:
        gen, mode = CLIPS[name]
        if mode == 0: encode(name, gen())
        elif mode == 1: encode_raw(name, gen())
        else: encode_raw(name, gen(), 300)
        print('done', name, flush=True)

"""Christmas / New Year seamless 8 s 1080p loops. Usage: python3 xmas.py <name> ..."""
import numpy as np, math, sys, colorsys
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter
from pack import W, H, N, TAU, gradient, encode, tone, blob

def hsv(h, s=1, v=1): return np.array(colorsys.hsv_to_rgb(h % 1, s, v))
def smooth(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

def splat(buf, xs, ys, cols, amps):
    """add points (bilinear) into a float buffer"""
    ok = (xs >= 0) & (xs < W - 1) & (ys >= 0) & (ys < H - 1)
    xs, ys, cols, amps = xs[ok], ys[ok], cols[ok], amps[ok]
    x0 = xs.astype(int); y0 = ys.astype(int); fx = xs - x0; fy = ys - y0
    for dx, dy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        np.add.at(buf, (y0 + dy, x0 + dx), cols * (w * amps)[:, None])

def glowify(buf, core=1.4, mid=5, wide=18):
    return gaussian_filter(buf, (core, core, 0)) * 6 + gaussian_filter(buf, (mid, mid, 0)) * 3 + gaussian_filter(buf, (wide, wide, 0)) * 2.2

# ---------------- 1. parol light sequence ----------------
def parol():
    cx, cy = W / 2, H / 2
    bg = gradient([.015, .02, .05], [.04, .015, .04], .6)
    # bulb layout: rings + star outline + centre
    groups = []
    def ring(r, n, off=0):
        a = np.arange(n) / n * TAU + off
        return np.stack([cx + r * np.sin(a), cy - r * np.cos(a)], 1), a
    R = [470, 360, 255]
    for i, (r, n) in enumerate(zip(R, (72, 56, 40))):
        p, a = ring(r, n); groups.append(dict(p=p, ang=a, ring=i))
    star = []; sang = []
    outer, inner = 205, 88
    vtx = [(cx + (outer if k % 2 == 0 else inner) * math.sin(k * math.pi / 5), cy - (outer if k % 2 == 0 else inner) * math.cos(k * math.pi / 5)) for k in range(10)]
    for k in range(10):
        (x0, y0), (x1, y1) = vtx[k], vtx[(k + 1) % 10]
        for s in np.linspace(0, 1, 6, endpoint=False):
            x, y = x0 + (x1 - x0) * s, y0 + (y1 - y0) * s; star.append((x, y)); sang.append(math.atan2(x - cx, cy - y) % TAU)
    groups.append(dict(p=np.array(star), ang=np.array(sang), ring=3))
    p, a = ring(45, 14); groups.append(dict(p=p, ang=a, ring=4))
    # static frame: wire circles, star outline and capiz panels (low-res masks for the panel glow)
    frame = Image.new('L', (W, H), 0); d = ImageDraw.Draw(frame)
    for r in R + [520, 300, 200]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=3)
    for k in range(20):
        a = k / 20 * TAU; d.line([(cx + 200 * math.sin(a), cy - 200 * math.cos(a)), (cx + 520 * math.sin(a), cy - 520 * math.cos(a))], fill=255, width=2)
    d.polygon(vtx, outline=255)
    fr = (np.asarray(frame.filter(ImageFilter.GaussianBlur(.8)), np.float32) / 255)[..., None] * np.array([.55, .42, .22]) * .55
    h4, w4 = H // 4, W // 4; gy, gx = np.mgrid[0:h4, 0:w4].astype(np.float32) * 4
    rr = np.sqrt((gx - cx) ** 2 + (gy - cy) ** 2); th = np.arctan2(gx - cx, cy - gy) % TAU
    band = np.select([rr < 200, rr < 300, rr < 360, rr < 470, rr < 520], [0, 1, 2, 3, 4], -1)
    sector = (th / TAU * 20).astype(int)
    pal = [hsv(0.0), hsv(.33), hsv(.15, .9), hsv(.6), hsv(.85, .8)]
    def pattern(k, u, ring, ang, i):
        n = len(ang)
        if k == 0:   # rainbow chase around each ring
            b = .2 + .8 * np.maximum(0, np.cos(TAU * (ang / TAU * 4 - u * (2 if ring % 2 == 0 else -2)))) ** 6
            col = np.stack([hsv(h) for h in ang / TAU + u]); return b, col
        if k == 1:   # radial pulse outwards
            ph = (ring if ring < 3 else (-.6 if ring == 3 else -1.2)) / 3
            b = np.full(n, .15 + .85 * max(0, math.sin(TAU * (u * 2 - ph))) ** 3)
            col = np.tile(pal[ring % 5], (n, 1)); return b, col
        if k == 2:   # alternating flash
            on = ((np.arange(n) + (i if ring != 3 else 0)) % 2 == (int(u * 8) % 2))
            b = np.where(on, 1.0, .12); col = np.tile(pal[(ring + 2) % 5], (n, 1)); return b, col
        b = np.full(n, .9)           # colour wheel spin
        col = np.stack([hsv(h, .9) for h in ang / TAU * 2 - u * 2 + ring * .1]); return b, col
    for f in range(N):
        t = f / N; seg = int(t * 4); u = t * 4 - seg; nxt = (seg + 1) % 4; mix = smooth((u - .82) / .18)
        img = bg + fr
        ringlight = np.zeros(5); ringcol = np.zeros((5, 3))
        for g in groups:
            b0, c0 = pattern(seg, u, g['ring'], g['ang'], f)
            if mix > 0:
                b1, c1 = pattern(nxt, 0.0, g['ring'], g['ang'], f); b0 = b0 * (1 - mix) + b1 * mix; c0 = c0 * (1 - mix) + c1 * mix
            for (x, y), b, c in zip(g['p'], b0, c0):
                blob(img, x, y, 11 if g['ring'] < 3 else 9, c, b * 1.3, edge=.45, glow=.55, rim=0)
            ringlight[min(g['ring'], 4)] = b0.mean(); ringcol[min(g['ring'], 4)] = c0.mean(0)
        # capiz panels glow with the light of nearby bulbs
        pan = np.zeros((h4, w4, 3), np.float32)
        lights = [ringlight[3], ringlight[2], ringlight[1], ringlight[0], ringlight[0]]
        cols = [ringcol[3], ringcol[2], ringcol[1], ringcol[0], ringcol[0]]
        capiz = [[hsv(.0, .85), hsv(.13, .9)], [hsv(.33, .8), hsv(.6, .8)], [hsv(.85, .7), hsv(.13, .9)], [hsv(.6, .8), hsv(.0, .85)], [hsv(.13, .9), hsv(.33, .8)]]
        for bnd in range(5):
            for alt in (0, 1):
                m = (band == bnd) & ((sector + bnd) % 2 == alt)
                c = capiz[bnd][alt] * .7 + cols[bnd] * .3
                pan[m] += c * lights[bnd] * (.22 if bnd != 2 else .13) * (1 if alt == 0 else .7)
        pan = np.asarray(Image.fromarray((np.clip(pan, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
        yield tone(img + pan, 1.7)

# ---------------- 2. twinkling string lights ----------------
def strings():
    rng = np.random.default_rng(4); bg = gradient([.02, .02, .05], [.05, .03, .05], .5)
    bk = np.zeros((H, W, 3), np.float32)          # static far bokeh
    for _ in range(40):
        blob(bk, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 110), hsv(rng.choice([.0, .08, .12, .33, .6])), .10, edge=.25, glow=.1)
    bg = bg + bk
    cols = [hsv(0), hsv(.33), hsv(.6), hsv(.13), hsv(.05), hsv(.85, .7)]
    bulbs = []; wire = Image.new('L', (W, H), 0); d = ImageDraw.Draw(wire)
    for k, (y0, sag, phase) in enumerate([(120, 210, 0), (430, 240, .5), (760, 200, .2)]):
        pts = []
        for x in np.linspace(-60, W + 60, 200):
            s = (x + 60) / (W + 120); pts.append((x, y0 + sag * 4 * s * (1 - s) + 25 * math.sin(TAU * (s * 2 + phase))))
        d.line(pts, fill=255, width=3)
        for j, x in enumerate(np.arange(-20, W + 20, 78) + k * 26):
            s = (x + 60) / (W + 120); y = y0 + sag * 4 * s * (1 - s) + 25 * math.sin(TAU * (s * 2 + phase))
            bulbs.append((x, y + 16, cols[(j + k) % len(cols)], j, k, rng.uniform(0, TAU), int(rng.integers(1, 4))))
    wm = (np.asarray(wire.filter(ImageFilter.GaussianBlur(.7)), np.float32) / 255)[..., None]
    bg = bg * (1 - wm * .8) + wm * np.array([.06, .07, .05])
    for f in range(N):
        t = f / N; img = bg.copy()
        for x, y, col, j, k, ph, tw in bulbs:
            chase = max(0, math.cos(TAU * (j / 9 - t * 4 + k / 3))) ** 4
            twinkle = .55 + .45 * math.sin(TAU * tw * t + ph)
            b = .35 + .65 * max(chase, twinkle * .8)
            blob(img, x, y, 9, col, b * 1.4, edge=.5, glow=1.1, rim=0)       # bulb + halo
            blob(img, x, y - 15, 4, np.array([.12, .12, .1]), 1, edge=1, glow=0, rim=0)  # socket
        yield tone(img, 1.8)

# ---------------- 3. light border frame (dark and green-screen versions) ----------------
def border(green=False):
    inset = 46; per = []
    def edge(x0, y0, x1, y1, n):
        for s in np.linspace(0, 1, n, endpoint=False): per.append((x0 + (x1 - x0) * s, y0 + (y1 - y0) * s))
    edge(inset, inset, W - inset, inset, 40); edge(W - inset, inset, W - inset, H - inset, 22)
    edge(W - inset, H - inset, inset, H - inset, 40); edge(inset, H - inset, inset, inset, 22)
    n = len(per); cols = [hsv(0), hsv(.33), hsv(.13), hsv(.6), hsv(.05)]
    if green:
        bg = np.zeros((H, W, 3), np.float32) + np.array([0, 1.0, 0])
    else:
        bg = gradient([.03, .02, .05], [.07, .03, .05], .35)
    wire = np.zeros((H, W), np.float32); wire[inset - 1:inset + 2, inset:W - inset] = 1; wire[H - inset - 1:H - inset + 2, inset:W - inset] = 1
    wire[inset:H - inset, inset - 1:inset + 2] = 1; wire[inset:H - inset, W - inset - 1:W - inset + 2] = 1
    for f in range(N):
        t = f / N; light = np.zeros((H, W, 3), np.float32)
        for i, (x, y) in enumerate(per):
            chase = max(0, math.cos(TAU * (i / n * 6 - t * 4))) ** 6
            b = .3 + .7 * chase
            blob(light, x, y, 10, cols[i % 5], b * 1.5, edge=.5, glow=1.0, rim=0)
        lit = tone(light, 1.8)
        base = bg * (1 - wire[..., None] * .9) + wire[..., None] * np.array([.12, .1, .07])
        if green:   # lights over chroma green; keep the green pure where there is no light
            a = np.clip(lit.max(2, keepdims=True) * 1.15, 0, 1); yield base * (1 - a) + lit * a / np.maximum(a, 1e-3) * a
        else:
            yield base + lit * (1 - base)

# ---------------- 4. New Year fireworks ----------------
def fireworks():
    rng = np.random.default_rng(9); T = 8.0; g = 110.0
    sky = gradient([.01, .01, .04], [.04, .03, .08], .4)
    city = Image.new('L', (W, H), 0); d = ImageDraw.Draw(city); x = 0
    while x < W:                                       # generic skyline silhouette
        w = rng.uniform(40, 130); h = rng.uniform(60, 260); d.rectangle([x, H - h, x + w, H], fill=255); x += w + rng.uniform(0, 12)
    cm = (np.asarray(city, np.float32) / 255)[..., None]
    win = np.zeros((H, W, 3), np.float32)
    for _ in range(500):                              # lit windows
        wx, wy = int(rng.uniform(0, W)), int(rng.uniform(H - 250, H - 8))
        if cm[wy, wx, 0] > .5: win[wy:wy + 3, wx:wx + 2] = np.array([1, .8, .4]) * rng.uniform(.2, .6)
    shows = []
    for i in range(11):
        t0 = i * T / 11 + rng.uniform(-.15, .15); bx = rng.uniform(.15, .85) * W; by = rng.uniform(.15, .45) * H
        col = hsv(rng.choice([0, .08, .14, .33, .55, .62, .8, .9]), .85); col2 = hsv(rng.uniform(), .7) if rng.uniform() < .5 else col
        n = 240; ang = rng.uniform(0, TAU, n); sp = rng.uniform(.15, 1, n) ** .75 * rng.uniform(400, 540)
        cs = np.where((np.arange(n) % 2 == 0)[:, None], col, col2)
        shows.append((t0, bx, by, np.cos(ang) * sp, np.sin(ang) * sp, cs, rng.uniform(.55, .8)))
    rise = 1.0; life = 2.4; k = 1.6
    for f in range(N):
        t = f / N * T; buf = np.zeros((H, W, 3), np.float32)
        for t0, bx, by, vx, vy, cs, fl in shows:
            for tl in (t0, t0 - T):                      # include the previous loop for a seamless wrap
                tau = t - tl
                if 0 <= tau < rise:                      # rocket climbing
                    s = tau / rise; ys = H - 40 - (H - 40 - by) * (1 - (1 - s) ** 2)
                    tr = np.linspace(0, .12, 8)
                    yy_ = H - 40 - (H - 40 - by) * (1 - (1 - np.clip(s - tr, 0, 1)) ** 2)
                    splat(buf, np.full(8, bx), yy_, np.tile(np.array([1, .85, .6]), (8, 1)), np.linspace(.9, .1, 8))
                tb = tau - rise
                if 0 <= tb < life:
                    for back, al in ((0, 1.0), (.05, .55), (.1, .3), (.16, .15)):
                        tt = max(tb - back, 0); dr = (1 - math.exp(-k * tt)) / k
                        px = bx + vx * dr; py = by + vy * dr + .5 * g * tt * tt
                        fade = (1 - tb / life) ** 1.6 * al
                        flick = 1 if tb < life * fl else (0.4 + 0.6 * (np.sin(np.arange(len(px)) * 7 + f * 1.7) > 0))
                        splat(buf, px, py, cs, np.full(len(px), fade * 2.6) * flick)
                    if tb < .15: blob(buf, bx, by, 60, np.array([1, .9, .7]), (1 - tb / .15) * .35, edge=1, glow=.6, rim=0)
        light = tone(glowify(buf), 1.4)
        haze = gaussian_filter(light, (60, 60, 0)) * .8
        img = sky + haze + light
        img = img * (1 - cm) + cm * (np.array([.01, .01, .02]) + haze * .3 + win)
        yield img

CLIPS = {
    'parol-light-sequence-loop': parol,
    'twinkling-christmas-string-lights-loop': strings,
    'christmas-light-border-frame-loop': lambda: border(False),
    'christmas-light-border-frame-greenscreen-loop': lambda: border(True),
    'new-year-fireworks-city-loop': fireworks,
}
if __name__ == '__main__':
    for name in sys.argv[1:]:
        encode(name, CLIPS[name]()); print('done', name, flush=True)

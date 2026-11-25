"""Batch 7: winter designs (snow globe, northern lights over mountains, frosty window frame)
and vertical 9:16 versions of the most-visited clips.
Usage: python3 pack7.py <name> ...                   (run from an empty output folder)
       CLIP_VERT=1 python3 pack7.py <name>-9x16 ...   (vertical versions)"""
import numpy as np, math, sys, os
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter
from pack import W, H, N, TAU, gradient, tone, encode
import pack2, pack4, pack5
from pack2 import encode_raw
from pack3 import tile_noise
from xmas import splat, glowify

S = min(W, H)          # size reference, so every design works in 16:9 and 9:16
u8 = lambda a: (np.clip(a, 0, 1) * 255).astype(np.uint8)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def up(arr, w=W, h=H):
    """resize a float HxWx3 array"""
    return np.stack([np.asarray(Image.fromarray(arr[..., c].astype(np.float32), 'F').resize((w, h), Image.BICUBIC)) for c in range(arr.shape[2])], -1)

# ---------------------------------------------------------------- 1. snow globe
def snow_globe():
    cx, cy, R = W / 2, H * (0.44 if H < W else 0.45), S * 0.34
    bg = gradient([.02, .03, .08], [.05, .04, .10], .7)
    rng = np.random.default_rng(71)
    # soft warm lights far behind
    for _ in range(26):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(S * .02, S * .06)
        c = np.array([1, .75, .4]) if rng.random() < .6 else np.array([.5, .6, 1])
        bg += (np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (2 * r * r)))[..., None] * c * rng.uniform(.05, .14)).astype(np.float32)
    # the little scene inside the globe (drawn at 2x, then reduced)
    K = 2; sz = int(2 * R * K)
    sc = Image.new('RGBA', (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(sc)
    gy = sz * .70
    d.ellipse([-sz * .15, gy, sz * 1.15, sz * 1.25], fill=(232, 240, 252, 255))                       # snowy ground
    for tx, th in [(.26, .30), (.36, .22), (.70, .27), (.80, .19)]:                                   # pine trees
        bx, h = sz * tx, sz * th
        for k in range(3):
            w = h * (.55 - k * .13); ty = gy - h * (k * .28)
            d.polygon([(bx - w / 2, ty + 6), (bx + w / 2, ty + 6), (bx, ty - h * .45)], fill=(22, 70, 52, 255))
            d.polygon([(bx - w * .28, ty - h * .18), (bx + w * .28, ty - h * .18), (bx, ty - h * .45)], fill=(236, 242, 250, 255))
    hx, hw, hh = sz * .44, sz * .20, sz * .12                                                        # cottage
    d.rectangle([hx, gy - hh, hx + hw, gy + 4], fill=(120, 62, 40, 255))
    d.polygon([(hx - hw * .12, gy - hh), (hx + hw * 1.12, gy - hh), (hx + hw / 2, gy - hh - hh * .75)], fill=(240, 245, 252, 255))
    d.rectangle([hx + hw * .15, gy - hh * .62, hx + hw * .40, gy - hh * .25], fill=(255, 196, 90, 255))
    d.rectangle([hx + hw * .58, gy - hh * .62, hx + hw * .83, gy - hh * .25], fill=(255, 196, 90, 255))
    d.rectangle([hx + hw * .70, gy - hh * 1.35, hx + hw * .84, gy - hh * .8], fill=(110, 58, 40, 255))
    sc = sc.resize((int(2 * R), int(2 * R)), Image.LANCZOS)
    scene = np.zeros((H, W, 4), np.float32)
    x0, y0 = int(cx - R), int(cy - R); a = np.asarray(sc, np.float32) / 255
    scene[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    # warm window glow
    wg = np.exp(-(((xx - (x0 + (hx + hw / 2) / K)) ** 2 + (yy - (y0 + (gy - hh * .45) / K)) ** 2) / (2 * (R * .16) ** 2)))[..., None] * np.array([1, .6, .25]) * .35
    r2 = ((xx - cx) ** 2 + (yy - cy) ** 2) / (R * R)
    inside = np.clip((1 - r2) * 60, 0, 1)[..., None]
    interior = gradient([.05, .08, .20], [.10, .16, .32], 0) * 1.0
    glass_shade = np.clip(r2, 0, 1)[..., None] ** 3 * np.array([.25, .35, .5])                      # brighter rim of the glass
    rim = np.exp(-((np.sqrt(r2) - 1) ** 2) / (2 * .012 ** 2))[..., None] * np.array([.6, .75, 1]) * .55
    ang = np.arctan2(yy - cy, xx - cx)
    spec = (np.exp(-((np.sqrt(r2) - .82) ** 2) / (2 * .035 ** 2)) * np.clip(np.cos(ang + 2.3), 0, 1) ** 6)[..., None] * .55   # highlight, upper left
    # base
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(base)
    by = cy + R * .86; bw1, bw2, bh = R * 1.02, R * 1.30, R * .42
    bd.polygon([(cx - bw1, by), (cx + bw1, by), (cx + bw2, by + bh), (cx - bw2, by + bh)], fill=(150, 98, 40, 255))
    bd.rectangle([cx - bw2 * 1.04, by + bh, cx + bw2 * 1.04, by + bh + R * .09], fill=(120, 76, 30, 255))
    bd.line([(cx - bw1 * .98, by + bh * .32), (cx + bw1 * .98, by + bh * .32)], fill=(222, 176, 92, 255), width=max(2, int(S * .006)))
    base = np.asarray(base.filter(ImageFilter.GaussianBlur(1)), np.float32) / 255
    bshade = np.clip(1 - (np.abs(xx - cx) / (R * 1.4)) ** 2, .45, 1)[..., None]
    still = bg * (1 - inside) + inside * (interior * (1 - scene[..., 3:]) + scene[..., :3] * scene[..., 3:] + wg)
    still = still + inside * glass_shade
    still = still * (1 - base[..., 3:]) + base[..., :3] * bshade * base[..., 3:]
    still = still + rim * (1 - base[..., 3:]) + spec
    # swirling snow inside the globe: every flake orbits a whole number of times per loop, so it repeats seamlessly
    n = 900; rng = np.random.default_rng(7)
    th0 = rng.uniform(0, TAU, n); rr = np.sqrt(rng.uniform(.02, .80, n)); k = rng.choice([-1, 1], n) * rng.integers(1, 3, n)
    bob = rng.uniform(.03, .10, n); ph = rng.uniform(0, TAU, n); m = rng.integers(1, 3, n)
    size = rng.uniform(.4, 1.3, n) ** 2
    # a few soft flakes outside the globe, drifting down
    no = 120; ox = rng.uniform(0, W, no); oy = rng.uniform(0, H, no); osp = rng.integers(1, 3, no); osz = rng.uniform(.5, 1.6, no)
    for f in range(N):
        t = f / N
        th = th0 + TAU * k * t
        r = rr + bob * np.sin(TAU * m * t + ph)
        x = cx + R * .9 * r * np.cos(th); y = cy + R * .9 * r * np.sin(th) * .92 + R * .05
        buf = np.zeros((H, W, 3), np.float32)
        splat(buf, x, y, np.ones((n, 3), np.float32) * [.95, .97, 1], size * 1.6)
        fl = gaussian_filter(buf, (1.1, 1.1, 0)) * 3 + gaussian_filter(buf, (3, 3, 0)) * .8
        buf2 = np.zeros((H, W, 3), np.float32)
        splat(buf2, (ox + 30 * np.sin(TAU * t + ox)) % W, (oy + osp * H * t) % H, np.ones((no, 3), np.float32) * [.8, .85, 1], osz)
        out = still + fl * inside * .9 + (gaussian_filter(buf2, (4, 4, 0)) * 9) * (1 - inside)
        yield np.clip(tone(out, 1.6), 0, 1)

# ---------------------------------------------------------------- 2. northern lights over snowy mountains
def northern_lights():
    rng = np.random.default_rng(23)
    sky = gradient([.005, .01, .03], [.02, .06, .10], .4)
    sky = sky + np.exp(-(((yy / H) - (.47 if W > H else .50)) / .12) ** 2)[..., None] * np.array([.01, .05, .045])   # faint glow near the horizon
    ns = int(W * H / 2600); sx = rng.uniform(0, W, ns); sy = rng.uniform(0, H * .75, ns); sa = rng.uniform(.05, .6, ns) ** 2; sp = rng.uniform(0, TAU, ns); sk = rng.integers(1, 4, ns)
    # mountains: jagged ridges (random points joined by straight lines, several octaves), snow on the high parts
    def ridge(seed, n0):
        r = np.random.default_rng(seed); out = np.zeros(W, np.float32); xs = np.arange(W)
        for o in range(5):
            k = n0 * 2 ** o + 1; pts = r.uniform(-1, 1, k)
            out += np.interp(xs, np.linspace(0, W, k), pts) / 1.9 ** o
        return out / np.abs(out).max()
    vert = H > W
    layers = []
    for top, amp, col, seed, n0 in [(.50 if not vert else .52, .17 if not vert else .09, (.18, .24, .36), 3, 3), (.62 if not vert else .60, .12 if not vert else .07, (.10, .14, .24), 5, 4)]:
        rr = ridge(seed, n0); ridge_y = H * top - H * amp * rr
        m = gaussian_filter((yy >= ridge_y[None, :]).astype(np.float32), .8)
        depth = (yy - ridge_y[None, :])
        hi = np.clip((rr - .05) / .6, 0, 1)[None, :]                                   # how high this part of the ridge is
        cn = np.asarray(Image.fromarray(tile_noise(W // 4, H // 4, seed + 20).astype(np.float32), 'F').resize((W, H), Image.BICUBIC))
        cap = np.clip((H * .055 * hi * (0.6 + cn) - depth) / (H * .01), 0, 1) * (depth >= 0)
        lit = (1.12 - .35 * np.clip(depth / (H * .3), 0, 1))[..., None]
        shade = np.array(col) * lit * (1 - cap[..., None]) + np.array([.62, .70, .84]) * cap[..., None] * lit
        layers.append((m[..., None], shade))
    # a row of dark pine trees along the shore
    pines = Image.new('L', (W, H), 0); pd = ImageDraw.Draw(pines); fy0 = int(H * (.74 if not vert else .66)); x = 0
    while x < W:
        h = H * rng.uniform(.012, .035) * (1 if not vert else .8); w = h * rng.uniform(.38, .5)
        pd.polygon([(x - w / 2, fy0 + 1), (x + w / 2, fy0 + 1), (x, fy0 - h)], fill=255); x += w * rng.uniform(.35, .9)
    pm = gaussian_filter(np.asarray(pines, np.float32) / 255, .6)[..., None]
    layers.append((pm, np.zeros((H, W, 3), np.float32) + np.array([.02, .03, .05])))
    # a frozen lake in front mirrors the sky, the aurora and the mountains; a thin snowy shore separates them
    fy = int(H * (.74 if not vert else .66))
    src = np.clip(2 * fy - np.arange(fy, H), 0, H - 1)
    fade = np.linspace(.55, .30, H - fy)[:, None, None]
    shore = np.exp(-((yy - fy) / (H * .004)) ** 2)[..., None] * np.array([.55, .62, .75])
    # aurora, computed small then enlarged
    w4, h4 = W // 4, H // 4; X = np.arange(w4)[None, :] / w4; Y = np.arange(h4)[:, None] / h4
    base_y = .31 if H < W else .27; hgt = .24 if H < W else .20
    # uneven rays that shimmer in place (each column brightens and dims on its own rhythm)
    pr = gaussian_filter(rng.random(w4), .9); pr = (pr - pr.min()) / (pr.max() - pr.min())
    rays = (.35 + .65 * pr ** 1.4)[None, :]; rk = rng.integers(1, 3, w4)[None, :]; rph = gaussian_filter(rng.uniform(0, TAU, w4), 2)[None, :] * 3
    for f in range(N):
        t = f / N
        wv = 1 if H < W else .45     # a narrow vertical frame makes the same wave look steeper
        yb = base_y + wv * (.025 * np.sin(TAU * (1.3 * X + t)) + .018 * np.sin(TAU * (2.7 * X - t) + 1) + .01 * np.sin(TAU * (5.1 * X + 2 * t) + 2))
        env = .55 + .45 * np.sin(TAU * (.8 * X + t) + .5)
        stri = rays * (.72 + .28 * np.sin(TAU * rk * t + rph))
        above = np.clip(yb - Y, 0, None) / hgt
        I = np.where(Y < yb, np.exp(-above * 2.2), np.exp(-((Y - yb) / .035) ** 2)) * env * stri
        mixc = np.clip(above, 0, 1)[..., None]
        col = np.array([.15, 1, .55]) * (1 - mixc) + np.array([.55, .25, .95]) * mixc
        A = gaussian_filter(I[..., None] * col, (2, .6, 0)).astype(np.float32)
        A = up(A) * 1.1
        buf = np.zeros((H, W, 3), np.float32)
        splat(buf, sx, sy, np.ones((ns, 3), np.float32), sa * (.6 + .4 * np.sin(TAU * sk * t + sp)))
        img = sky + gaussian_filter(buf, (.8, .8, 0)) * 3 + A
        for m, shade in layers:
            img = img * (1 - m) + shade * m
        ref = gaussian_filter(img[src], (2.5, 1.2, 0)) * fade + np.array([.02, .03, .05])
        img[fy:] = ref
        img = img + shore
        yield np.clip(tone(img, 1.5), 0, 1)

# ---------------------------------------------------------------- 3. frosty window frame (on black, for Screen blend)
def frost_frame():
    rng = np.random.default_rng(41)
    edge = np.minimum.reduce([xx, W - xx, yy, H - yy]) / S
    nz = tile_noise(W // 2, H // 2, 41); nz = np.asarray(Image.fromarray(nz.astype(np.float32), 'F').resize((W, H), Image.BICUBIC))
    fine = tile_noise(W, H, 42, octaves=7)
    # feather-like crystals growing inward from the edges
    ferns = Image.new('L', (W, H), 0); d = ImageDraw.Draw(ferns)
    def branch(x, y, a, L, depth):
        """a frost feather: a straight stem with short side spikes at about 60 degrees, like ice crystals"""
        if depth == 0 or L < 5: return
        x2, y2 = x + L * math.cos(a), y + L * math.sin(a)
        d.line([(x, y), (x2, y2)], fill=int(120 + 30 * depth), width=1 if depth < 3 else 2)
        for t in np.arange(.12, .95, .09):
            for s in (-1, 1):
                if rng.random() < .8:
                    branch(x + (x2 - x) * t, y + (y2 - y) * t, a + s * (1.05 + rng.uniform(-.08, .08)), L * .30 * (1.1 - t), depth - 1)
    for _ in range(int(95 * (W + H) / 3000)):
        side = rng.integers(4)
        if side == 0: x, y, a = rng.uniform(0, W), 0, math.pi / 2
        elif side == 1: x, y, a = rng.uniform(0, W), H, -math.pi / 2
        elif side == 2: x, y, a = 0, rng.uniform(0, H), 0
        else: x, y, a = W, rng.uniform(0, H), math.pi
        branch(x, y, a + rng.uniform(-.7, .7), S * rng.uniform(.06, .17), 3)
    ferns = np.asarray(ferns.filter(ImageFilter.GaussianBlur(.8)), np.float32) / 255
    col = np.array([.80, .90, 1.0])
    ns = 700; px, py = rng.uniform(0, W, ns), rng.uniform(0, H, ns); pk = rng.integers(1, 4, ns); pph = rng.uniform(0, TAU, ns)
    ped = np.minimum.reduce([px, W - px, py, H - py]) / S
    for f in range(N):
        t = f / N
        reach = .17 + .025 * np.sin(TAU * t)                     # the frost breathes in and out a little
        m = np.clip((reach + .10 * (nz - .5) - edge) / .05, 0, 1)
        crystals = np.clip((fine - .70) / .2, 0, 1) ** 2
        tex = m * (.02 + .18 * crystals) + ferns * 1.3 * np.clip((reach + .12 - edge) / .05, 0, 1)
        img = tex[..., None] * col
        buf = np.zeros((H, W, 3), np.float32)
        on = ped < reach
        splat(buf, px[on], py[on], np.ones((on.sum(), 3), np.float32), (np.maximum(0, np.sin(TAU * pk[on] * t + pph[on])) ** 6) * 1.6)
        img = img + glowify(buf, 1.0, 3, 9) * .5
        yield np.clip(tone(img, 1.4), 0, 1)

C = {
 'snow-globe-swirling-snow-loop': (snow_globe, 0),
 'northern-lights-snowy-mountains-loop': (northern_lights, 0),
 'frosty-window-frame-overlay-loop': (frost_frame, 0),
}
# 9:16 versions (render with CLIP_VERT=1)
V = {
 'snow-globe-swirling-snow-loop-9x16': (snow_globe, 0),
 'northern-lights-snowy-mountains-loop-9x16': (northern_lights, 0),
 'frosty-window-frame-overlay-loop-9x16': (frost_frame, 0),
 'new-year-countdown-10-to-1-9x16': (pack2.countdown, 2),
 'gold-dust-shimmer-overlay-loop-9x16': pack5.C['gold-dust-shimmer-overlay-loop'],
 'aurora-night-gradient-flow-loop-9x16': pack2.CLIPS['aurora-night-gradient-flow-loop'],
 'snowy-christmas-tree-forest-night-loop-9x16': pack4.C['snowy-christmas-tree-forest-night-loop'],
 'rising-fire-embers-loop-9x16': pack2.CLIPS['rising-fire-embers-loop'],
 'rainbow-prism-light-leaks-overlay-loop-9x16': pack5.C['rainbow-prism-light-leaks-overlay-loop'],
}

if __name__ == '__main__':
    for name in sys.argv[1:]:
        if name in V and not os.environ.get('CLIP_VERT'): sys.exit(f'{name}: run with CLIP_VERT=1')
        gen, mode = (V if name in V else C)[name]
        if mode == 0: encode(name, gen())
        elif mode == 1: encode_raw(name, gen())
        else: encode_raw(name, gen(), 300)
        print('done', name, flush=True)

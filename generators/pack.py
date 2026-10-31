"""Starter pack of seamless 8-second 1080p motion-graphic loops. Usage: python3 pack.py <name> [<name> ...]"""
import numpy as np, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS, SECS = 1920, 1080, 30, 8
N = FPS * SECS
TAU = 2 * math.pi
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def gradient(top, bot, vig=0.5):
    g = (yy / H)[..., None]
    bg = np.array(top) * (1 - g) + np.array(bot) * g
    v = 1 - vig * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)
    return (bg * np.clip(v, 0, 1)[..., None]).astype(np.float32)

def encode(name, frames):
    out = f'{name}.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                          '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i, img in enumerate(frames):
        fr = (np.clip(img, 0, 1) ** (1 / 1.1) * 255).astype(np.uint8)
        p.stdin.write(fr.tobytes())
        if i == N // 2:
            Image.fromarray(fr).save(f'{name}-poster.jpg', quality=90)
    p.stdin.close(); p.wait()

def tone(img, k=2.0):
    return 1 - np.exp(-img * k)

def blob(img, cx, cy, r, col, a, edge=0.12, glow=0.12, rim=0.35):
    x0, x1 = int(max(0, cx - 2.7 * r)), int(min(W, cx + 2.7 * r + 1))
    y0, y1 = int(max(0, cy - 2.7 * r)), int(min(H, cy + 2.7 * r + 1))
    if x0 >= x1 or y0 >= y1: return
    sx, sy = np.meshgrid(np.arange(x0, x1, dtype=np.float32), np.arange(y0, y1, dtype=np.float32))
    d = np.sqrt((sx - cx) ** 2 + (sy - cy) ** 2) / r
    m = np.clip((1 - d) / edge, 0, 1) * (0.85 + 0.15 * (1 - d))
    if rim: m = m + np.exp(-((d - 0.93) / 0.07) ** 2) * rim * (d < 1.1)
    if glow: m = m + np.exp(-(d / 1.1) ** 2) * glow
    img[y0:y1, x0:x1] += (m * a)[..., None] * col

# ---------- bokeh family ----------
def bokeh(seed, top, bot, palette, rise=1):
    rng = np.random.default_rng(seed); bg = gradient(top, bot, 0.55); M = 140; span = H + 2 * M; parts = []
    for layer, (n, r0, r1, cyc, b) in enumerate([(24, 70, 120, 1, .30), (32, 34, 70, 1, .55), (30, 12, 30, 2, .95)]):
        for _ in range(n):
            parts.append((rng.uniform(-M, W + M), rng.uniform(0, span), rng.uniform(r0, r1), cyc, rng.uniform(10, 45),
                          int(rng.integers(1, 3)), rng.uniform(0, TAU), int(rng.integers(1, 4)), rng.uniform(0, TAU),
                          b * rng.uniform(.7, 1.15), np.array(palette[rng.integers(len(palette))]), (.18, .12, .08)[layer]))
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, r, cyc, sw, sk, sp, tw, tp, b, col, e in parts:
            y = (y0 - rise * cyc * span * t) % span - M
            blob(img, x0 + sw * math.sin(TAU * sk * t + sp), y, r, col, b * (.72 + .28 * math.sin(TAU * tw * t + tp)), e)
        yield tone(img)

# ---------- falling snow ----------
def snow():
    rng = np.random.default_rng(3); bg = gradient([.03, .07, .16], [.10, .16, .30], 0.45); M = 60; span = H + 2 * M; fl = []
    for n, r0, r1, cyc, b in [(160, 2, 4, 1, .45), (110, 4, 7, 2, .7), (40, 8, 14, 3, .9)]:
        for _ in range(n):
            fl.append((rng.uniform(0, W), rng.uniform(0, span), rng.uniform(r0, r1), cyc, rng.uniform(15, 60),
                       int(rng.integers(1, 3)), rng.uniform(0, TAU), b * rng.uniform(.7, 1.1)))
    col = np.array([.92, .96, 1.0])
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, r, cyc, sw, sk, sp, b in fl:
            y = (y0 + cyc * span * t) % span - M
            blob(img, x0 + sw * math.sin(TAU * sk * t + sp), y, r, col, b, edge=.5, glow=.25, rim=0)
        yield tone(img, 1.8)

# ---------- gold glitter sparkles ----------
def sparkles():
    rng = np.random.default_rng(11); bg = gradient([.02, .02, .04], [.06, .03, .02], 0.6); pts = []
    for _ in range(420):
        pts.append((rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2.5, 6.5), int(rng.integers(1, 4)), rng.uniform(0, TAU),
                    np.array([1.0, rng.uniform(.68, .88), rng.uniform(.25, .5)]), rng.uniform(.5, 1.0)))
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, r, tw, tp, col, b in pts:
            x = (x0 + W * t) % (W + 40) - 20; y = y0 + 12 * math.sin(TAU * t + tp)
            s = max(0.0, math.sin(TAU * tw * t + tp)) ** 2 * b * 1.6
            if s < 0.02: continue
            blob(img, x, y, r, col, s, edge=.6, glow=.9, rim=0)
            L = int(r * 9 * min(s, 1.2)) + 1                                   # four-point glint
            xi, yi = int(x), int(y)
            for dx, dy in ((1, 0), (0, 1)):
                for k in range(-L, L + 1):
                    px, py = xi + k * dx, yi + k * dy
                    if 0 <= px < W and 0 <= py < H:
                        img[py, px] += col * s * 0.9 * (1 - abs(k) / (L + 1)) ** 2
        yield tone(img, 1.7)

# ---------- smooth gradient flow ----------
def flow(seed, stops):
    rng = np.random.default_rng(seed); h, w = H // 4, W // 4
    gy, gx = np.mgrid[0:h, 0:w].astype(np.float32); gx /= w; gy /= h
    waves = [(rng.uniform(1, 3.5), rng.uniform(-2, 2), int(rng.integers(1, 3)) * rng.choice([-1, 1]), rng.uniform(0, TAU)) for _ in range(5)]
    stops = np.array(stops, dtype=np.float32); ns = len(stops) - 1
    for f in range(N):
        t = f / N; v = np.zeros((h, w), np.float32)
        for kx, ky, m, ph in waves:
            v += np.sin(TAU * (kx * gx + ky * gy) + TAU * m * t + ph + 1.2 * np.sin(TAU * (gy * 1.3 + t) + ph))
        v = (v / len(waves) * 0.9 + 1) / 2
        idx = np.clip(v * ns, 0, ns - 1e-4); i = idx.astype(int); fr = (idx - i)[..., None]
        fr = fr * fr * (3 - 2 * fr)
        small = stops[i] * (1 - fr) + stops[i + 1] * fr
        big = np.asarray(Image.fromarray((np.clip(small, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
        yield big ** 1.1

# ---------- soft light rays ----------
def rays():
    rng = np.random.default_rng(5); h, w = H // 3, W // 3
    gy, gx = np.mgrid[0:h, 0:w].astype(np.float32); sx, sy = -0.15 * w, -0.25 * h
    ang = np.arctan2(gy - sy, gx - sx); dist = np.sqrt((gx - sx) ** 2 + (gy - sy) ** 2) / w
    beams = [(rng.uniform(8, 26), int(rng.integers(1, 3)) * rng.choice([-1, 1]), rng.uniform(0, TAU), rng.uniform(.4, 1)) for _ in range(6)]
    base = np.array([.05, .03, .02]); warm = np.array([1.0, .78, .45])
    for f in range(N):
        t = f / N; v = np.zeros((h, w), np.float32)
        for k, m, ph, a in beams:
            v += a * np.clip(np.sin(k * ang + TAU * m * t + ph), 0, 1) ** 4
        v = v / 2.5 * np.exp(-dist * 1.3) + 0.35 * np.exp(-dist * 4)
        small = base + v[..., None] * warm
        big = np.asarray(Image.fromarray((np.clip(small, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
        yield big

# ---------- confetti ----------
def confetti():
    rng = np.random.default_rng(21); bg = gradient([.04, .03, .10], [.10, .04, .14], 0.5); M = 60; span = H + 2 * M
    cols = [[1, .26, .38], [1, .76, .16], [.2, .78, .52], [.24, .56, 1], [.86, .38, 1], [1, .55, .2]]
    ps = [(rng.uniform(0, W), rng.uniform(0, span), rng.uniform(20, 36), rng.uniform(10, 17), int(rng.integers(1, 3)),
           int(rng.integers(1, 4)) * rng.choice([-1, 1]), int(rng.integers(2, 6)), rng.uniform(0, TAU), rng.uniform(20, 70),
           np.array(cols[rng.integers(len(cols))]) * rng.uniform(.8, 1)) for _ in range(240)]
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
            mask = np.clip(hw - np.abs(u) + .5, 0, 1) * np.clip(hh - np.abs(v) + .5, 0, 1)
            shade = .65 + .35 * sc
            region = img[y0b:y1b, x0b:x1b]
            region[:] = region * (1 - mask[..., None]) + (col * shade) * mask[..., None]
        yield img

# ---------- glowing star lanterns (parol-inspired) ----------
def star_sprite(size, body, inner):
    S = size * 4; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    pts = [(c + (S * .42 if i % 2 == 0 else S * .18) * math.sin(i * math.pi / 5), c - (S * .42 if i % 2 == 0 else S * .18) * math.cos(i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill=tuple(int(v * 255) for v in body) + (255,))
    pts2 = [(c + (S * .25 if i % 2 == 0 else S * .11) * math.sin(i * math.pi / 5), c - (S * .25 if i % 2 == 0 else S * .11) * math.cos(i * math.pi / 5)) for i in range(10)]
    d.polygon(pts2, fill=tuple(int(v * 255) for v in inner) + (255,))
    for sgn in (-1, 1):                                                  # two tails
        d.line([(c + sgn * S * .06, c + S * .2), (c + sgn * S * .14, c + S * .49)], fill=tuple(int(v * 255) for v in body) + (255,), width=max(2, S // 60))
    im = im.resize((size * 2, size * 2), Image.LANCZOS)
    glow = im.filter(ImageFilter.GaussianBlur(size * .18))
    return im, glow

def lanterns():
    rng = np.random.default_rng(8); bg = gradient([.02, .03, .09], [.08, .03, .08], .5)
    cfg = [(.12, .28, 150, [1, .55, .2]), (.30, .18, 110, [1, .8, .3]), (.50, .32, 190, [1, .35, .3]), (.70, .2, 120, [.4, .8, 1]),
           (.88, .3, 160, [1, .72, .25]), (.22, .62, 90, [.95, .45, .8]), (.62, .66, 100, [1, .85, .4]), (.82, .7, 80, [.5, 1, .6])]
    lams = []
    for fx, fy, sz, col in cfg:
        body = np.array(col); inner = np.clip(body * .5 + .55, 0, 1)
        lams.append((fx * W, fy * H, sz, star_sprite(sz, body, inner), rng.uniform(4, 9), int(rng.integers(1, 3)), rng.uniform(0, TAU), int(rng.integers(1, 3))))
    for f in range(N):
        t = f / N
        canvas = Image.fromarray((np.clip(bg, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
        for x, y, sz, (spr, glow), amp, k, ph, pk in lams:
            ang = amp * math.sin(TAU * k * t + ph)
            pulse = .8 + .2 * math.sin(TAU * pk * t + ph)
            d = ImageDraw.Draw(canvas); d.line([(x, 0), (x, y - sz * .9)], fill=(120, 110, 100, 120), width=2)
            for layer, alpha in ((glow, pulse), (spr, 1.0)):
                r = layer.rotate(ang, resample=Image.BICUBIC, center=(sz, sz * .1))
                if alpha < 1:
                    a = r.getchannel('A').point(lambda v, al=alpha: int(v * al)); r.putalpha(a)
                canvas.alpha_composite(r, (int(x - sz), int(y - sz)))
                if layer is glow: canvas.alpha_composite(r, (int(x - sz), int(y - sz)))
        yield np.asarray(canvas.convert('RGB'), np.float32) / 255

# ---------- fireflies ----------
def fireflies():
    rng = np.random.default_rng(13); bg = gradient([.01, .04, .05], [.02, .09, .06], .5)
    grass = Image.new('L', (W, H), 0); d = ImageDraw.Draw(grass)
    for i in range(900):
        x = rng.uniform(0, W); h = rng.uniform(60, 260); lean = rng.uniform(-50, 50)
        d.polygon([(x - 4, H), (x + 4, H), (x + lean, H - h)], fill=255)
    gm = (np.asarray(grass.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255)[..., None]
    bg = bg * (1 - gm) + np.array([.005, .015, .012]) * gm
    flies = [(rng.uniform(.05, .95) * W, rng.uniform(.25, .85) * H, rng.uniform(30, 120), rng.uniform(20, 70), int(rng.integers(1, 3)),
              int(rng.integers(1, 3)), rng.uniform(0, TAU), rng.uniform(0, TAU), int(rng.integers(1, 4)), rng.uniform(5, 9)) for _ in range(95)]
    col = np.array([.75, 1.0, .35])
    for f in range(N):
        t = f / N; img = bg.copy()
        for x0, y0, ax, ay, kx, ky, px, py, pk, r in flies:
            x = x0 + ax * math.sin(TAU * kx * t + px); y = y0 + ay * math.sin(TAU * ky * t + py)
            s = max(0.0, math.sin(TAU * pk * t + px)) ** 2
            if s > .02: blob(img, x, y, r, col, s * 2.2, edge=.7, glow=1.4, rim=0)
        yield tone(img, 1.6)

CLIPS = {
    'christmas-red-green-bokeh-loop': lambda: bokeh(31, [.02, .04, .03], [.07, .02, .03], [[1, .22, .2], [1, .35, .25], [.2, .85, .4], [.35, 1, .5], [1, .85, .45]]),
    'cool-blue-bokeh-loop': lambda: bokeh(41, [.01, .02, .06], [.02, .05, .10], [[.3, .6, 1], [.45, .8, 1], [.6, .5, 1], [.8, .9, 1], [.3, .9, .95]]),
    'pink-rose-bokeh-loop': lambda: bokeh(51, [.06, .02, .05], [.10, .03, .07], [[1, .45, .65], [1, .6, .75], [1, .75, .85], [.95, .4, .5], [1, .85, .7]]),
    'falling-snow-night-loop': snow,
    'gold-glitter-sparkles-loop': sparkles,
    'blue-purple-gradient-flow-loop': lambda: flow(61, [[.05, .06, .25], [.20, .15, .60], [.45, .25, .85], [.15, .55, .95], [.05, .20, .45]]),
    'sunset-gradient-flow-loop': lambda: flow(71, [[.35, .05, .25], [.85, .25, .30], [1.0, .55, .25], [1.0, .80, .45], [.60, .15, .35]]),
    'warm-light-rays-loop': rays,
    'celebration-confetti-loop': confetti,
    'glowing-christmas-star-lanterns-loop': lanterns,
    'fireflies-night-loop': fireflies,
}

if __name__ == '__main__':
    for name in sys.argv[1:]:
        encode(name, CLIPS[name]()); print('done', name, flush=True)

"""Ambient, seamlessly looping animation for still illustrations.
Every motion is periodic in t in [0,1), so frame N == frame 0 (perfect loop)."""
import sys, subprocess, math
import numpy as np, cv2

FPS, SECS = 24, 8
N = FPS * SECS
TAU = 2 * math.pi

def rng(seed):
    return np.random.default_rng(seed)

# ---------------------------------------------------------------- masks
def box_mask(shape, boxes):
    m = np.zeros(shape[:2], np.float32)
    for x0, y0, x1, y1 in boxes:
        m[y0:y1, x0:x1] = 1
    return m

def color_mask(img, boxes, fn, exclude=(), feather=4):
    B, G, R = [img[..., i].astype(np.int32) for i in range(3)]
    m = fn(R, G, B).astype(np.float32) * box_mask(img.shape, boxes)
    if exclude:
        m *= 1 - box_mask(img.shape, exclude)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return cv2.GaussianBlur(m, (0, 0), feather)[..., None]

def tile_noise(h, w, sigma, seed):
    """Smooth random field that wraps around horizontally and vertically."""
    r = rng(seed).random((h, w)).astype(np.float32)
    p = int(sigma * 4)
    n = cv2.GaussianBlur(np.pad(r, p, mode='wrap'), (0, 0), sigma)[p:p + h, p:p + w]
    n = (n - n.min()) / (n.max() - n.min() + 1e-6)
    return n

# ---------------------------------------------------------------- effects on the picture
class Water:
    def __init__(self, img, mask, amp=2.0, wl=26, glint=22, glint_color=(255, 255, 255), seed=1):
        self.m, self.amp, self.wl, self.g = mask, amp, wl, glint
        h, w = img.shape[:2]
        self.yy, self.xx = np.mgrid[0:h, 0:w].astype(np.float32)
        self.ph = tile_noise(h, w, 18, seed) * TAU  # breaks up straight bands
        self.gc = np.array(glint_color, np.float32)
        gn = tile_noise(h, w, 10, seed + 7)
        self.gm = np.clip((gn - 0.55) / 0.2, 0, 1)  # glints only in scattered patches
        lum = img.astype(np.float32).mean(axis=2) / 255
        self.gm *= np.clip((0.92 - lum) / 0.2, 0, 1)  # none on near-white paper

    def apply(self, base, out, t):
        yy, xx, a = self.yy, self.xx, self.amp
        dx = a * np.sin(TAU * (yy / self.wl + t) + self.ph) + 0.5 * a * np.sin(TAU * (yy / (self.wl * 0.47) - 2 * t))
        dy = 0.35 * a * np.sin(TAU * (xx / (self.wl * 3.1) + t) + self.ph)
        disp = cv2.remap(base, xx + dx, yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        s = np.sin(TAU * (xx / 57 + yy / 9 - t) + self.ph * 2) * np.sin(TAU * (xx / 31 - yy / 13 + 2 * t))
        gl = cv2.GaussianBlur((np.clip(s, 0, 1) ** 10).astype(np.float32), (0, 0), sigmaX=4, sigmaY=0.8) * 2.2 * self.g * self.gm
        disp = disp.astype(np.float32) + gl[..., None] * (self.gc / 255)
        return out * (1 - self.m) + disp * self.m

class Glow:
    """Lanterns / warm lights flicker and bloom."""
    def __init__(self, img, mask, color=(60, 140, 255), strength=0.10, bloom=0.5, seed=3):
        self.m = mask
        self.halo = cv2.GaussianBlur(mask, (0, 0), 18)[..., None] if mask.ndim == 3 else None
        self.halo = cv2.GaussianBlur(mask[..., 0], (0, 0), 22)[..., None]
        self.col = np.array(color, np.float32)
        self.s, self.b = strength, bloom
        r = rng(seed); self.p = r.random(3) * TAU

    def apply(self, base, out, t):
        f = 0.6 * math.sin(TAU * 2 * t + self.p[0]) + 0.3 * math.sin(TAU * 5 * t + self.p[1]) + 0.2 * math.sin(TAU * 11 * t + self.p[2])
        out = out * (1 + self.s * f * self.m)
        return out + self.halo * self.col * (self.b * (0.75 + 0.25 * f))

class Dapple:
    """Moving sunlight dapples on bright areas (leaves swaying overhead)."""
    def __init__(self, img, mask, strength=0.09, seed=5):
        h, w = img.shape[:2]
        self.m, self.s = mask, strength
        self.n = tile_noise(h, w, 22, seed) * 2 - 1
        self.n2 = tile_noise(h, w, 40, seed + 1) * 2 - 1

    def apply(self, base, out, t):
        h, w = self.n.shape
        a = np.roll(self.n, int(round(t * w)), axis=1)
        b = np.roll(self.n2, -int(round(t * h)), axis=0)
        k = 1 + self.s * (0.6 * a + 0.4 * b)[..., None] * self.m
        return out * k

# ---------------------------------------------------------------- particles (screen space)
def sprite(kind, size, color, r):
    s = int(size * 4) | 1
    c = s // 2
    sp = np.zeros((s, s, 4), np.float32)
    col = np.array(color, np.float32)
    if kind in ('petal', 'leaf', 'marigold'):
        ax = (size * (0.55 if kind != 'leaf' else 0.8), size * (0.32 if kind != 'leaf' else 0.22))
        a = np.zeros((s, s), np.float32)
        cv2.ellipse(a, (c, c), (int(ax[0] * 2), int(ax[1] * 2)), 0, 0, 360, 1, -1, cv2.LINE_AA)
        if kind == 'petal':  # notch at the tip like a cherry petal
            cv2.circle(a, (c + int(ax[0] * 2), c), max(1, int(ax[1] * 0.7)), 0, -1, cv2.LINE_AA)
        a = cv2.GaussianBlur(a, (0, 0), 1.0)
        shade = np.linspace(0.85, 1.12, s)[None, :, None]
        sp[..., :3] = np.clip(col * shade, 0, 255)
        sp[..., 3] = a
    elif kind == 'confetti':
        a = np.zeros((s, s), np.float32)
        cv2.rectangle(a, (c - int(size * 1.0), c - int(size * 0.5)), (c + int(size * 1.0), c + int(size * 0.5)), 1, -1, cv2.LINE_AA)
        sp[..., :3] = col; sp[..., 3] = cv2.GaussianBlur(a, (0, 0), 0.8)
    elif kind in ('glow', 'sparkle'):
        yy, xx = np.mgrid[0:s, 0:s] - c
        d = np.sqrt(xx ** 2 + yy ** 2) / (size * 1.6)
        a = np.exp(-d ** 2 * 3) * 0.9
        if kind == 'sparkle':
            ray = np.exp(-(np.abs(xx) / 1.2) ** 2) * np.exp(-(np.abs(yy) / (size * 1.4))) + np.exp(-(np.abs(yy) / 1.2) ** 2) * np.exp(-(np.abs(xx) / (size * 1.4)))
            a = np.clip(a * 0.7 + ray, 0, 1)
        sp[..., :3] = col; sp[..., 3] = a
    return sp

def blit(dst, sp, x, y, alpha, angle=0.0, sx=1.0, add=False):
    s = sp.shape[0]
    if angle or sx != 1.0:
        M = cv2.getRotationMatrix2D((s / 2, s / 2), angle, 1.0)
        M[:, :2] *= np.array([[sx], [1.0]]) if False else 1
        sp = cv2.warpAffine(sp, M, (s, s), flags=cv2.INTER_LINEAR)
        if sx != 1.0:  # flip/tumble: squash vertically after rotation
            sp = cv2.resize(sp, (s, max(1, int(s * abs(sx)))))
            pad = (s - sp.shape[0]) // 2
            sp = cv2.copyMakeBorder(sp, pad, s - sp.shape[0] - pad, 0, 0, cv2.BORDER_CONSTANT, 0)
    h, w = dst.shape[:2]
    x0, y0 = int(x) - s // 2, int(y) - s // 2
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(w, x0 + s), min(h, y0 + s)
    if xa >= xb or ya >= yb:
        return
    p = sp[ya - y0:yb - y0, xa - x0:xb - x0]
    a = p[..., 3:4] * alpha
    if add:
        dst[ya:yb, xa:xb] += p[..., :3] * a
    else:
        dst[ya:yb, xa:xb] = dst[ya:yb, xa:xb] * (1 - a) + p[..., :3] * a

class Fall:
    """Falling/tumbling things. Loops: each particle crosses the frame k times per loop."""
    def __init__(self, W, H, n, kind, colors, size=(7, 13), speed=(1, 2), sway=30, slant=0.25,
                 region=None, alpha=0.95, seed=7, rise=False):
        r = rng(seed)
        self.W, self.H = W, H
        x0, y0, x1, y1 = region or (0, 0, W, H)
        self.top, self.span = y0 - 40, (y1 - y0) + 80
        self.p = []
        for i in range(n):
            sz = r.uniform(*size)
            col = colors[r.integers(len(colors))]
            self.p.append(dict(sp=sprite(kind, sz, col, r), x=r.uniform(x0 - 60, x1 + 60), ph=r.random(),
                               k=int(r.integers(speed[0], speed[1] + 1)), sw=r.uniform(0.4, 1) * sway,
                               sp_ph=r.random(), rot=int(r.integers(1, 3)) * r.choice([-1, 1]), fl=int(r.integers(1, 4)),
                               a0=r.uniform(0, 360)))
        self.slant, self.alpha, self.rise, self.kind = slant, alpha, rise, kind

    def draw(self, frame, t):
        for q in self.p:
            u = (q['ph'] + q['k'] * t) % 1.0
            y = self.top + u * self.span
            if self.rise:
                y = self.top + (1 - u) * self.span
            x = q['x'] + self.slant * (y - self.top) + q['sw'] * math.sin(TAU * (2 * t + q['sp_ph']))
            ang = q['a0'] + 360 * q['rot'] * t
            fl = math.cos(TAU * (q['fl'] * t + q['sp_ph']))
            fl = math.copysign(max(0.25, abs(fl)), fl)
            fade = min(1, u * 8, (1 - u) * 8) if self.rise else 1
            blit(frame, q['sp'], x, y, self.alpha * fade, ang, fl if self.kind != 'glow' else 1)

class Float:
    """Glowing dots / sparkles that drift around a home position and pulse (fireflies, dust, glints)."""
    def __init__(self, W, H, n, kind, colors, size=(3, 6), region=None, drift=25, alpha=0.9, seed=9, add=True):
        r = rng(seed)
        x0, y0, x1, y1 = region or (0, 0, W, H)
        self.p = [dict(sp=sprite(kind, r.uniform(*size), colors[r.integers(len(colors))], r),
                       x=r.uniform(x0, x1), y=r.uniform(y0, y1), ph=r.random(4), k=int(r.integers(1, 3)),
                       d=r.uniform(0.4, 1) * drift) for _ in range(n)]
        self.alpha, self.add = alpha, add

    def draw(self, frame, t):
        for q in self.p:
            ph = q['ph']
            x = q['x'] + q['d'] * math.sin(TAU * (t + ph[0]))
            y = q['y'] + q['d'] * 0.6 * math.sin(TAU * (q['k'] * t + ph[1]))
            pulse = 0.5 + 0.5 * math.sin(TAU * (q['k'] * 2 * t + ph[2]))
            blit(frame, q['sp'], x, y, self.alpha * pulse ** 1.5, add=self.add)

class Birds:
    """Small gull silhouettes gliding across the sky with flapping wings; wraps around."""
    def __init__(self, W, H, n, band, color=(90, 90, 95), size=(9, 15), seed=11, direction=1, laps=1):
        r = rng(seed)
        self.W, self.col, self.dir, self.laps = W, color, direction, laps
        self.p = [dict(x=r.random(), y=r.uniform(*band), s=r.uniform(*size), f=int(r.integers(4, 7)),
                       ph=r.random(), bob=r.uniform(4, 10)) for _ in range(n)]

    def draw(self, frame, t):
        span = self.W + 120
        for q in self.p:
            u = (q['x'] + self.dir * self.laps * t) % 1.0
            x = u * span - 60
            y = q['y'] + q['bob'] * math.sin(TAU * (2 * t + q['ph']))
            s = q['s']
            wing = math.sin(TAU * (q['f'] * t + q['ph']))  # -1..1
            tip = -s * 0.55 * wing
            pts = np.array([[x - s, y + tip], [x - s * 0.45, y - s * 0.12 + tip * 0.35], [x, y + s * 0.18],
                            [x + s * 0.45, y - s * 0.12 + tip * 0.35], [x + s, y + tip]], np.float32)
            ov = frame.copy()
            cv2.polylines(ov, [np.round(pts * 4).astype(np.int32)], False, self.col, max(2, int(s / 5)), cv2.LINE_AA, shift=2)
            frame[:] = frame * 0.15 + ov * 0.85

# ---------------------------------------------------------------- render
def render(name, img_path, size, focus, zoom, effects, layers, crf=18):
    base = cv2.imread(img_path).astype(np.float32)
    H, W = base.shape[:2]
    assert (W, H) == size, (W, H, size)
    fx, fy = focus
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
           f'out/{name}.mp4']
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N):
        t = i / N
        out = base.copy()
        for e in effects:
            out = e.apply(base, out, t)
        z = 1 + zoom * (1 - math.cos(TAU * t)) / 2
        M = np.array([[z, 0, fx * (1 - z)], [0, z, fy * (1 - z)]], np.float32)
        frame = cv2.warpAffine(out, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        for l in layers:
            l.draw(frame, t)
        p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    print('rendered', name, flush=True)

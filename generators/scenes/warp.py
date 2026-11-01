"""Puppet-style motion for still illustrations: soft-masked rotations, bobs and breathing,
plus rolling waves. Everything is periodic in t, so loops stay seamless."""
import sys, math, subprocess
import numpy as np, cv2
from animate import TAU, N, FPS

def smooth_weight(W, H, cx, cy, rx, ry):
    x0, x1 = max(0, int(cx - rx)), min(W, int(cx + rx) + 1)
    y0, y1 = max(0, int(cy - ry)), min(H, int(cy + ry) + 1)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    u = np.clip((1.0 - d) / 0.45, 0, 1)
    w = u * u * (3 - 2 * u)  # smoothstep: full strength in the middle, soft edge
    return (y0, y1, x0, x1), xx, yy, w

class Warp:
    """deformers (in source coords, scaled by k):
       ('sway', cx, cy, rx, ry, deg, px, py, speed, phase)   rotate around pivot
       ('bob', cx, cy, rx, ry, dx, dy, speed, phase)          move back and forth
       ('breathe', cx, cy, rx, ry, frac, anchor_y, speed, phase)  stretch up from anchor"""
    def __init__(self, W, H, deformers, k=1.0):
        self.W, self.H, self.items = W, H, []
        self.gx, self.gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        for d in deformers:
            kind, cx, cy, rx, ry = d[0], d[1] * k, d[2] * k, d[3] * k, d[4] * k
            sl, xx, yy, w = smooth_weight(W, H, cx, cy, rx, ry)
            if kind == 'sway':
                _, _, _, _, _, deg, px, py, sp, ph = d
                self.items.append((kind, sl, xx - px * k, yy - py * k, w, deg, sp, ph))
            elif kind == 'bob':
                _, _, _, _, _, dx, dy, sp, ph = d
                self.items.append((kind, sl, None, None, w, (dx, dy), sp, ph))
            elif kind == 'breathe':
                _, _, _, _, _, frac, ay, sp, ph = d
                self.items.append((kind, sl, None, yy - ay * k, w, frac, sp, ph))

    def maps(self, t):
        dx = np.zeros((self.H, self.W), np.float32); dy = np.zeros_like(dx)
        for kind, (y0, y1, x0, x1), rx_, ry_, w, a, sp, ph in self.items:
            s = math.sin(TAU * (sp * t + ph))
            if kind == 'sway':
                th = math.radians(a * s); c, si = math.cos(th), math.sin(th)
                # source sample = R(-th)(p - pivot) + pivot  ->  displacement = p - sample
                sx = c * rx_ + si * ry_; sy = -si * rx_ + c * ry_
                dx[y0:y1, x0:x1] += w * (rx_ - sx); dy[y0:y1, x0:x1] += w * (ry_ - sy)
            elif kind == 'bob':
                dx[y0:y1, x0:x1] += w * a[0] * s; dy[y0:y1, x0:x1] += w * a[1] * s
            else:  # breathe: points above the anchor move up a little
                dy[y0:y1, x0:x1] += w * (a * (0.5 + 0.5 * s)) * ry_
        return self.gx - dx, self.gy - dy

    def apply(self, base, t):
        mx, my = self.maps(t)
        return cv2.remap(base, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

class Swell:
    """Rolling waves: bands of displacement travel toward the shore, foam brightens as they pass."""
    def __init__(self, img, mask, amp=5.0, wl=70, speed=2, foam=0.12, slant=0.0):
        h, w = img.shape[:2]
        self.m, self.amp, self.wl, self.sp, self.foam, self.sl = mask, amp, wl, speed, foam, slant
        self.yy, self.xx = np.mgrid[0:h, 0:w].astype(np.float32)
        lum = img.astype(np.float32).mean(axis=2)
        self.fm = (np.clip((lum - 170) / 60, 0, 1))[..., None]

    def apply(self, base, out, t):
        ph = TAU * ((self.yy + self.sl * self.xx) / self.wl - self.sp * t)
        dy = self.amp * np.sin(ph); dx = 0.5 * self.amp * np.sin(ph * 0.5 + TAU * self.xx / 400)
        disp = cv2.remap(base, self.xx - dx, self.yy - dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        disp = disp * (1 + self.foam * np.sin(ph - 0.6)[..., None] * self.fm)
        return out * (1 - self.m) + disp * self.m

def render_w(name, img_path, size, focus, zoom, effects, layers, warp=None, crf=18, outdir='out'):
    base0 = cv2.imread(img_path).astype(np.float32)
    H, W = base0.shape[:2]
    fx, fy = focus
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
           f'{outdir}/{name}.tmp.mp4']
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N):
        t = i / N
        base = warp.apply(base0, t) if warp else base0
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
    import os
    os.replace(f'{outdir}/{name}.tmp.mp4', f'{outdir}/{name}.mp4')
    print('rendered', name, flush=True)

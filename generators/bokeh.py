import numpy as np, subprocess, sys

W, H, FPS, SECS = 1920, 1080, 30, 8
N = FPS * SECS
rng = np.random.default_rng(7)
out = sys.argv[1]

# background: deep navy to plum vertical gradient + soft vignette
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
top = np.array([0.020, 0.030, 0.075]); bot = np.array([0.075, 0.025, 0.070])
g = (yy / H)[..., None]
bg = top * (1 - g) + bot * g
vig = 1 - 0.55 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)
bg = bg * np.clip(vig, 0, 1)[..., None]

palette = np.array([
    [1.00, 0.72, 0.18], [1.00, 0.58, 0.12], [1.00, 0.82, 0.38],
    [1.00, 0.45, 0.22], [1.00, 0.62, 0.45], [1.00, 0.90, 0.60]])

M = 140  # margin so particles wrap off-screen
parts = []
for layer, (count, rmin, rmax, cycles, bright) in enumerate([
        (24, 70, 120, 1, 0.30),   # far, big and soft
        (32, 34, 70, 1, 0.55),
        (30, 12, 30, 2, 0.95)]):  # near, small and bright
    for _ in range(count):
        parts.append(dict(
            x0=rng.uniform(-M, W + M), y0=rng.uniform(0, H + 2 * M),
            r=rng.uniform(rmin, rmax), cyc=cycles,
            sway=rng.uniform(10, 45), sk=int(rng.integers(1, 3)), sp=rng.uniform(0, 2 * np.pi),
            tw=int(rng.integers(1, 4)), tp=rng.uniform(0, 2 * np.pi),
            b=bright * rng.uniform(0.7, 1.15), col=palette[rng.integers(len(palette))],
            edge=0.18 if layer == 0 else 0.12 if layer == 1 else 0.08))

def disc(img, cx, cy, r, col, a, edge):
    x0, x1 = int(max(0, cx - 2.7*r)), int(min(W, cx + 2.7*r + 1))
    y0, y1 = int(max(0, cy - 2.7*r)), int(min(H, cy + 2.7*r + 1))
    if x0 >= x1 or y0 >= y1:
        return
    sx, sy = np.meshgrid(np.arange(x0, x1, dtype=np.float32), np.arange(y0, y1, dtype=np.float32))
    d = np.sqrt((sx - cx) ** 2 + (sy - cy) ** 2) / r
    body = np.clip((1 - d) / edge, 0, 1)                      # soft-edged disc
    rim = np.exp(-((d - 0.93) / 0.07) ** 2) * 0.35 * (d < 1.1)  # faint bright rim, like a lens
    centre = 0.85 + 0.15 * (1 - d)                             # slightly brighter middle
    glow = np.exp(-(d / 1.1) ** 2) * 0.12                     # soft halo around each light
    m = (body * centre + rim + glow) * a
    img[y0:y1, x0:x1] += m[..., None] * col

proc = subprocess.Popen([
    'ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
    stdin=subprocess.PIPE)

span = H + 2 * M
for f in range(N):
    t = f / N  # 0..1, loops exactly
    img = bg.copy()
    for p in parts:
        y = (p['y0'] - p['cyc'] * span * t) % span - M      # rises and wraps off-screen
        x = p['x0'] + p['sway'] * np.sin(2 * np.pi * p['sk'] * t + p['sp'])
        a = p['b'] * (0.72 + 0.28 * np.sin(2 * np.pi * p['tw'] * t + p['tp']))
        disc(img, x, y, p['r'], p['col'], a, p['edge'])
    img = 1 - np.exp(-img * 2.0)                              # gentle tone mapping
    frame = (np.clip(img, 0, 1) ** (1 / 1.1) * 255).astype(np.uint8)
    proc.stdin.write(frame.tobytes())
    if f == 0:
        from PIL import Image
        Image.fromarray(frame).save(out.replace('.mp4', '-poster.jpg'), quality=90)
proc.stdin.close(); proc.wait()
print('done')

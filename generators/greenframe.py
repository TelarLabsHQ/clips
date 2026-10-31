"""Christmas string-lights border frame on chroma green, seamless 8 s loop."""
import numpy as np, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFilter

W, H = int(sys.argv[1]), int(sys.argv[2])
OUT = sys.argv[3]
FPS, SECS = 30, 8
N = FPS * SECS
SS = 2                       # supersample for smooth edges
GREEN = (0, 177, 64)         # standard chroma green
rng = np.random.default_rng(11)

COLORS = [(235, 35, 40), (255, 185, 30), (40, 105, 255), (255, 80, 175), (255, 236, 200), (255, 120, 20)]

m = 64 * min(W, H) / 1080          # inset of the wire from the edge
depth = 30 * min(W, H) / 1080      # sag of each scallop
spacing = 165 * min(W, H) / 1080
rb = 22 * min(W, H) / 1080         # bulb radius

# edges: start point, end point, inward normal
edges = [((m, m), (W - m, m), (0, 1)), ((W - m, m), (W - m, H - m), (-1, 0)),
         ((W - m, H - m), (m, H - m), (0, -1)), ((m, H - m), (m, m), (1, 0))]
wires, bulbs = [], []
for (x0, y0), (x1, y1), (nx, ny) in edges:
    L = math.hypot(x1 - x0, y1 - y0)
    k = max(2, round(L / spacing))
    for i in range(k):
        pts = []
        for j in range(21):
            f = j / 20
            u = (i + f) / k
            s = depth * math.sin(math.pi * f)
            pts.append((x0 + (x1 - x0) * u + nx * s, y0 + (y1 - y0) * u + ny * s))
        wires.append(pts)
        u = (i + 0.5) / k
        cx, cy = x0 + (x1 - x0) * u + nx * depth, y0 + (y1 - y0) * u + ny * depth
        if all(math.hypot(cx - bx, cy - by) > rb * 4.5 for bx, by, _, _ in bulbs):
            bulbs.append((cx, cy, nx, ny))

nb = len(bulbs)
cols = [COLORS[i % len(COLORS)] for i in range(nb)]
tw = rng.integers(1, 4, nb); tp = rng.uniform(0, 2 * np.pi, nb)

def frame(t):
    img = Image.new('RGB', (W * SS, H * SS), GREEN)
    halo = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img); hd = ImageDraw.Draw(halo)
    for pts in wires:
        d.line([(x * SS, y * SS) for x, y in pts], fill=(28, 30, 26), width=int(3 * SS * rb / 15), joint='curve')
    for i, (cx, cy, nx, ny) in enumerate(bulbs):
        # chase wave around the frame (3 laps per loop) plus a gentle personal twinkle
        chase = 0.5 + 0.5 * math.cos(2 * math.pi * (3 * t - 4 * i / nb))
        lvl = 0.48 + 0.52 * (0.65 * chase ** 2 + 0.35 * (0.5 + 0.5 * math.sin(2 * math.pi * tw[i] * t + tp[i])))
        c = cols[i]
        lit = tuple(int(min(255, v * lvl + 255 * 0.25 * lvl ** 3)) for v in c)
        # socket cap between wire and bulb
        sx, sy = cx + nx * rb * 0.55, cy + ny * rb * 0.55
        r = rb * 0.5 * SS
        d.rounded_rectangle([sx * SS - r, sy * SS - r, sx * SS + r, sy * SS + r], radius=r * 0.3, fill=(60, 62, 58))
        bx, by = cx + nx * rb * 1.6, cy + ny * rb * 1.6
        R = rb * SS
        # tight halo, only when bright (kept small so keying stays clean)
        hr = R * (1.6 + 0.5 * lvl)
        hd.ellipse([bx * SS - hr, by * SS - hr, bx * SS + hr, by * SS + hr], fill=c + (int(120 * lvl ** 2),))
        d.ellipse([bx * SS - R, by * SS - R, bx * SS + R, by * SS + R], fill=lit)
        hl = R * 0.32
        hx, hy = bx * SS - R * 0.35, by * SS - R * 0.35
        d.ellipse([hx - hl, hy - hl, hx + hl, hy + hl], fill=tuple(int(v + (255 - v) * 0.6 * lvl) for v in lit))
    halo = halo.filter(ImageFilter.GaussianBlur(R * 0.5))
    base = img.convert('RGBA')
    # put halos under the bulbs: composite halo, then redraw bulbs on top by using a mask of bulb pixels
    merged = Image.alpha_composite(base, halo)
    mask = Image.new('L', img.size, 0); md = ImageDraw.Draw(mask)
    for pts in wires:
        md.line([(x * SS, y * SS) for x, y in pts], fill=255, width=int(3 * SS * rb / 15), joint='curve')
    for cx, cy, nx, ny in bulbs:
        bx, by = cx + nx * rb * 1.6, cy + ny * rb * 1.6
        md.ellipse([bx * SS - R, by * SS - R, bx * SS + R, by * SS + R], fill=255)
        sx, sy = cx + nx * rb * 0.55, cy + ny * rb * 0.55; r = rb * 0.5 * SS
        md.rectangle([sx * SS - r, sy * SS - r, sx * SS + r, sy * SS + r], fill=255)
    merged.paste(base, (0, 0), mask)
    return merged.convert('RGB').resize((W, H), Image.LANCZOS)

proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                         '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                         '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for f in range(N):
    im = frame(f / N)
    if f == 15:
        im.save(OUT.replace('.mp4', '-poster.jpg'), quality=90)
    proc.stdin.write(im.tobytes())
proc.stdin.close(); proc.wait()
print('done', OUT, nb, 'bulbs')

#!/usr/bin/env python3
"""'The Rainy Day Book' - a 90-second narrated mood piece built from Telar Clips scenes + overlays."""
import os, sys, json, numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/claude/promo-apps')
from compose import say
from year import F, lora, wrap_center, run, W, H, FPS, SC, CL

X = 1.2
OUT = '/home/claude/clips/rainybook'; os.makedirs(OUT, exist_ok=True)
# scene, cx0, cx1, zoom0, zoom1, overlays[(file, mode)], ambience, narration
CH = [
 ('rainy-day-reading-girl-cat-scene', .42, .62, 1.0, 1.06, [('rain-falling-overlay-loop', 'screen-soft')], 'rain',
  "Rain on the window. A lamp, a blanket, a sleepy cat. And a book she hasn't finished yet."),
 ('rainy-lantern-alley-night-scene', .35, .62, 1.0, 1.05, [('rain-falling-overlay-loop', 'screen')], 'rain',
  "On the first page, a little street, glowing in the rain."),
 ('cherry-blossom-river-bridge-scene', .30, .66, 1.04, 1.0, [('cherry-blossom-petals-green-screen-loop', 'key')], 'wind',
  "She turns the page, and the rain turns into petals."),
 ('mediterranean-steps-bougainvillea-sea-scene', .40, .66, 1.0, 1.05, [('floating-dust-particles-overlay-loop', 'screen')], 'sea',
  "Down warm white steps, to a sea so blue it hums."),
 ('tropical-cove-sunset-outrigger-scene', .55, .80, 1.05, 1.0, [('floating-dust-particles-overlay-loop', 'screen')], 'sea',
  "A little boat is waiting, right at the edge of sunset."),
 ('starry-lake-cabin-milky-way-scene', .40, .70, 1.0, 1.05, [('gold-sparkles-green-screen-loop', 'key')], 'night',
  "It drifts all night, under a river of stars."),
 ('irish-cottage-rainbow-hills-scene', .36, .62, 1.04, 1.0, [], 'wind',
  "By morning, there's a rainbow, and a cottage on the hill."),
 ('snowy-alpine-christmas-village-scene', .45, .70, 1.0, 1.05, [('falling-snow-black-overlay-loop', 'screen')], 'wind',
  "And on the very last page? Snow, and warm windows. And home."),
 ('rainy-day-reading-girl-cat-scene', .70, .80, 1.0, 1.12, [('rain-falling-overlay-loop', 'screen-soft')], 'rain',
  "Outside, the rain keeps falling. Inside, the story keeps going. Goodnight."),
]
LEAD = 1.3

def caption_png(i, text, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.rectangle((0, 1250, W, 1640), fill=(0, 0, 0, 120)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(60)))
    d = ImageDraw.Draw(im)
    wrap_center(d, 1330, text, lora(58, True, 500), (255, 250, 240), maxw=900)
    if i == 0:
        sd2 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sd2).ellipse((80, 260, 1000, 720), fill=(0, 0, 0, 120))
        im.alpha_composite(sd2.filter(ImageFilter.GaussianBlur(70))); d = ImageDraw.Draw(im)
        wrap_center(d, 360, 'The', lora(70, True, 500), (255, 230, 190))
        wrap_center(d, 440, 'Rainy Day Book', lora(112, False, 700), (255, 255, 255))
    if i == len(CH) - 1:
        f3 = F('Poppins-Regular.ttf', 26)
        wrap_center(d, 1700, 'Scenes & overlays from Telar Clips', f3, (215, 210, 225))
        wrap_center(d, 1738, 'Illustrated scenes made with AI-assisted illustration', f3, (215, 210, 225))
    im.save(path)

def render(i, c, D, cap_in, cap_out):
    scene, cx0, cx1, z0, z1, ovs = c[:6]
    png = f'{OUT}/t{i:02d}.png'; caption_png(i, c[7], png)
    tmp, dst = f'{OUT}/c{i:02d}.tmp.mp4', f'{OUT}/c{i:02d}.mp4'
    SH = 2880; SW = int(1920 * SH / 1080)
    s = f"(0.5-0.5*cos(PI*t/{D:.2f}))"
    CW = int(SH * W / H)
    x0 = min(max(cx0 * SW - CW / 2, 0), SW - CW); x1 = min(max(cx1 * SW - CW / 2, 0), SW - CW)
    xe = f"{x0:.1f}+({x1 - x0:.1f})*{s}"
    ins = ['-stream_loop', '-1', '-i', SC + scene + '.mp4']
    fc = (f"[0:v]fps={FPS},scale={SW}:{SH}:flags=bicubic,"
          f"crop={CW}:{SH}:'{xe}':0,scale={W}:{H}:flags=lanczos,setsar=1[b0];")
    last = '[b0]'
    for k, (f_, mode) in enumerate(ovs, 1):
        ins += ['-stream_loop', '-1', '-i', CL + f_ + '.mp4']
        if mode == 'key':
            fc += f'[{k}:v]fps={FPS},scale=-2:1920,crop={W}:{H},colorkey=0x00B140:0.28:0.08,despill=type=green[o{k}];{last}[o{k}]overlay[b{k}];'
        else:
            op = 0.85
            if mode == 'screen-soft':   # indoor: rain only in the window area (top), faded toward the room
                op = 1.0; mk = f",geq=lum='lum(X,Y)*clip(1.15-Y/{H*0.55},0,1)*0.75':cb=128:cr=128"
            else: mk = ''
            fc += (f'[{k}:v]fps={FPS},scale=-2:1920,crop={W}:{H}{mk},format=gbrp[o{k}];{last}format=gbrp[g{k}];'
                   f'[g{k}][o{k}]blend=all_mode=screen:all_opacity={op},format=yuv420p[b{k}];')
        last = f'[b{k}]'
    ti = len(ovs) + 1
    ins += ['-framerate', str(FPS), '-loop', '1', '-t', f'{D:.3f}', '-i', png]
    fade = f'fade=in:st={cap_in:.2f}:d=0.6:alpha=1,fade=out:st={cap_out:.2f}:d=0.6:alpha=1'
    fc += f'[{ti}:v]format=rgba,{fade}[t];{last}[t]overlay,format=yuv420p'
    if i == 0: fc += ',fade=in:st=0:d=1.2'
    if i == len(CH) - 1: fc += f',fade=out:st={D - 2.0:.2f}:d=2.0'
    fc += '[v]'
    run([*ins, '-filter_complex', fc, '-map', '[v]', '-t', f'{D:.3f}', '-r', str(FPS),
         '-c:v', 'libx264', '-crf', '15', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp])
    os.replace(tmp, dst); return dst

def ambience(kind, n, sr, rng):
    w = rng.standard_normal(n)
    if kind == 'rain':
        hp = w - np.convolve(w, np.ones(6) / 6, 'same')                 # hiss
        drops = np.zeros(n); idx = rng.integers(0, n, n // 900); drops[idx] = rng.uniform(.3, 1, len(idx))
        drops = np.convolve(drops, np.exp(-np.arange(200) / 30) * rng.standard_normal(200), 'same')
        return hp * .05 + drops * .04
    lp = np.convolve(w, np.ones(80) / 80, 'same') * 6
    t = np.arange(n) / sr
    if kind == 'sea': return lp * (0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 6.5)) ** 2) * .06
    if kind == 'wind': return lp * (0.6 + 0.4 * np.sin(2 * np.pi * t / 9)) * .035
    return lp * .015                                                        # quiet night

if __name__ == '__main__':
    lens = []
    for i, c in enumerate(CH):
        p = f'{OUT}/v{i:02d}.wav'
        if not os.path.exists(p): say(c[7], p, speed=0.92)
        lens.append(sf.info(p).duration)
    D = [max(10.8, LEAD + L + 2.0) for L in lens]; D[0] += 2.5; D[-1] += 2.0
    starts = np.cumsum([0] + [d - X for d in D[:-1]]); T = starts[-1] + D[-1]
    lead = [LEAD + (2.5 if i == 0 else 0) for i in range(len(CH))]
    print('total', round(T, 1), [round(d, 1) for d in D])
    if sys.argv[1:] == ['plan']: sys.exit()
    only = sys.argv[1:]
    files = []
    for i, c in enumerate(CH):
        dst = f'{OUT}/c{i:02d}.mp4'
        if only and str(i) not in only and os.path.exists(dst): files.append(dst); continue
        files.append(render(i, c, D[i], lead[i] - 0.5, min(lead[i] + lens[i] + 0.6, D[i] - 1.4))); print('chapter', i)
    ins = sum([['-i', f] for f in files], []); fc, last, off = '', '[0:v]', 0
    for i in range(1, len(files)):
        off += D[i - 1] - X; fc += f'{last}[{i}:v]xfade=transition=fade:duration={X}:offset={off:.3f}[x{i}];'; last = f'[x{i}]'
    run([*ins, '-filter_complex', fc.rstrip(';'), '-map', last, '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast',
         '-pix_fmt', 'yuv420p', '-r', str(FPS), f'{OUT}/video.mp4'])
    sr = 24000; n = int(T * sr); voice = np.zeros(n); amb = np.zeros(n); rng = np.random.default_rng(7)
    for i, c in enumerate(CH):
        a, _ = sf.read(f'{OUT}/v{i:02d}.wav'); s = int((starts[i] + lead[i]) * sr); voice[s:s + len(a)] += a[:n - s]
        s0, m = int(starts[i] * sr), int(D[i] * sr); m = min(m, n - s0)
        env = np.minimum(1, np.minimum(np.arange(m) / (X * sr), (m - np.arange(m)) / (X * sr)))
        amb[s0:s0 + m] += ambience(c[6], m, sr, rng) * env
    t = np.arange(n) / sr; amb *= np.minimum(1, np.minimum(t / 1.5, (T - t) / 2.0))
    mix = voice + amb
    sf.write(f'{OUT}/mix.wav', mix / max(1, np.abs(mix).max()) * 0.9, sr)
    final = '/home/claude/clips/the-rainy-day-book.mp4'
    run(['-i', f'{OUT}/video.mp4', '-i', f'{OUT}/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
         '-af', 'loudnorm=I=-14:TP=-1.5,aresample=48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final])
    print(final)

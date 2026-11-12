#!/usr/bin/env python3
"""'A Year of Celebrations' - 2-minute showcase made only from published Telar Clips."""
import os, sys, json, subprocess, numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, '/home/claude/promo-apps'); from compose import say

W, H, FPS, X = 1080, 1920, 30, 0.8          # X = crossfade length
OUT = '/home/claude/clips/year'; os.makedirs(OUT, exist_ok=True)
SC, CL = '/home/claude/scenes/upload/', '/home/claude/clips/out/'
GF = '/usr/share/fonts/truetype/google-fonts/'
def F(name, size): return ImageFont.truetype(GF + name, size)
def lora(size, it=False, wt=600):
    f = F('Lora-Italic-Variable.ttf' if it else 'Lora-Variable.ttf', size)
    try: f.set_variation_by_axes([wt])
    except Exception: pass
    return f

GOLD = (255, 181, 71)
# key, scene, cx0, cx1, overlay(file, mode), month, greeting, narration, caption overlay name
CH = [
 ('intro', 'starry-lake-cabin-milky-way-scene', .40, .62, ('gold-sparkles-green-screen-loop', 'key'), '', '',
  "This is a year of celebrations. Every scene you'll see is free, from Telar Clips.", 'Gold sparkles (green screen)'),
 ('ny', 'new-year-sparkler-boy-rooftop-scene', .50, .62, ('confetti-green-screen-loop', 'key'), 'January', 'Happy New Year',
  "January starts with a wish, and a sky full of sparks.", 'Confetti (green screen)'),
 ('lny', 'lunar-new-year-qipao-girl-lantern-scene', .44, .56, ('gold-sparkles-green-screen-loop', 'key'), 'Lunar New Year', 'Wishing you luck',
  "Red lanterns glow, and the whole street wishes you luck.", 'Gold sparkles (green screen)'),
 ('val', 'valentines-umbrella-kids-rain-scene', .62, .76, ('floating-hearts-green-screen-loop', 'key'), 'February', 'Be my Valentine',
  "In February, love shows up, even in the rain.", 'Floating hearts (green screen)'),
 ('stp', 'st-patricks-boy-shamrocks-rainbow-scene', .28, .55, ('gold-sparkles-green-screen-loop', 'key'), 'March', "Happy St. Patrick's Day",
  "March goes green, chasing rainbows over the hills.", 'Gold sparkles (green screen)'),
 ('ram', 'ramadan-girl-lantern-crescent-scene', .34, .52, ('ramadan-lanterns-green-screen-loop', 'key'), 'Ramadan', 'Ramadan Mubarak',
  "Under a crescent moon, a little lantern lights the way.", 'Ramadan lanterns (green screen)'),
 ('spr', 'cherry-blossom-picnic-girl-scene', .55, .76, ('cherry-blossom-petals-green-screen-loop', 'key'), 'April', 'Hello, spring',
  "Spring brings blossoms, and long, slow afternoons.", 'Cherry blossom petals (green screen)'),
 ('bday', 'twins-birthday-cake-candles-scene', .30, .70, ('balloons-rising-green-screen-loop', 'key'), 'Any day', 'Happy Birthday',
  "Make a wish! Birthdays are better with balloons.", 'Balloons rising (green screen)'),
 ('sum', 'beach-boy-sandcastle-waves-scene', .40, .66, None, 'July', 'Summer days',
  "Summer is waves, sandcastles, and salty air.", ''),
 ('sch', 'back-to-school-boy-walking-scene', .30, .46, None, 'September', 'Back to school',
  "September. New shoes, new books, new friends.", ''),
 ('aut', 'autumn-park-bench-golden-light-scene', .40, .58, ('floating-dust-particles-overlay-loop', 'screen'), 'October', 'Golden autumn',
  "Autumn paints the whole park in gold.", 'Floating dust (overlay)'),
 ('rain', 'rainy-day-reading-girl-cat-scene', .62, .78, ('rain-falling-overlay-loop', 'screen'), 'November', 'Cozy days',
  "Some days are just for stories, and a sleepy cat.", 'Rain falling (overlay)'),
 ('diw', 'diwali-temple-oil-lamps-dusk-scene', .22, .50, ('gold-sparkles-green-screen-loop', 'key'), 'Diwali', 'Happy Diwali',
  "A thousand little lamps light up Diwali.", 'Gold sparkles (green screen)'),
 ('xg', 'christmas-girl-gift-tree-scene', .36, .52, ('snowflakes-green-screen-loop', 'key'), 'December', 'Merry Christmas',
  "December comes wrapped in snow, and gifts.", 'Snowflakes (green screen)'),
 ('xv', 'snowy-alpine-christmas-village-scene', .45, .70, ('christmas-lights-frame-green-screen-9x16', 'key9'), 'Christmas Eve', 'Home for the holidays',
  "And every year finds its way back home.", 'Christmas lights frame (green screen)'),
 ('nye', 'harbour-new-year-fireworks-scene', .50, .60, ('new-year-countdown-green-screen', 'keyc'), "New Year's Eve", '',
  "So here's to the next one. Ten, nine, eight, and counting.", 'New Year countdown (green screen)'),
 ('cta', None, 0, 0, None, '', '',
  "Mix scenes, green screens, and overlays. All free, at clips dot telar labs dot net.", ''),
]
PRETTY = lambda s: s.replace('-scene', '').replace('-', ' ').title().replace("St Patricks", "St. Patrick's")

def wrap_center(d, y, text, font, fill, shadow=True, maxw=960):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=font) > maxw and cur: lines.append(cur); cur = w_
        else: cur = t
    lines.append(cur)
    for ln in lines:
        tw = d.textlength(ln, font=font); x = (W - tw) / 2
        if shadow:
            for r, a in ((6, 90), (3, 140)):
                pass
        d.text((x, y), ln, font=font, fill=fill); y += int(font.size * 1.18)
    return y

def text_png(c, path):
    key, scene, *_ , month, greet, line, cap = c
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    # soft dark glow behind the title area for legibility
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    d = ImageDraw.Draw(im)
    if key == 'intro':
        sd.ellipse((40, 300, 1040, 900), fill=(0, 0, 0, 120))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(80)))
        f1 = F('Poppins-Bold.ttf', 34); t = 'TELAR CLIPS PRESENTS'
        d.text(((W - d.textlength(t, font=f1)) / 2, 470), t, font=f1, fill=GOLD)
        y = wrap_center(d, 530, 'A Year of', lora(104, True), (255, 255, 255))
        y = wrap_center(d, y - 10, 'Celebrations', lora(128, False, 700), (255, 255, 255))
        f2 = F('Poppins-Regular.ttf', 38)
        wrap_center(d, y + 30, 'made only with free scenes, green screens & overlays', f2, (235, 230, 245), maxw=820)
    elif key != 'cta':
        sd.ellipse((60, 140, 1020, 640), fill=(0, 0, 0, 110))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(70)))
        f1 = F('Poppins-Bold.ttf', 36); t = month.upper()
        tw = d.textlength(t, font=f1); d.text(((W - tw) / 2, 290), t, font=f1, fill=GOLD)
        d.line(((W - tw) / 2, 345, (W + tw) / 2, 345), fill=GOLD + (200,), width=3)
        if greet: wrap_center(d, 370, greet, lora(96, True, 600), (255, 255, 255), maxw=940)
    if key not in ('cta',):
        # template recipe chip
        fa, fb = F('Poppins-Bold.ttf', 25), F('Poppins-Medium.ttf', 31)
        l1, l2 = 'SCENE', PRETTY(scene)
        l3 = ('+ ' + cap) if cap else ''
        wbox = max(d.textlength(l2, font=fb), d.textlength(l3, font=fb) if l3 else 0) + 64
        hbox = 150 if l3 else 106; x0, y0 = 56, 1410
        bg = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bg)
        bd.rounded_rectangle((x0, y0, x0 + wbox, y0 + hbox), 26, fill=(14, 10, 24, 175))
        im.alpha_composite(bg); d = ImageDraw.Draw(im)
        d.text((x0 + 32, y0 + 16), l1, font=fa, fill=GOLD)
        d.text((x0 + 32, y0 + 48), l2, font=fb, fill=(255, 255, 255))
        if l3: d.text((x0 + 32, y0 + 94), l3, font=fb, fill=(190, 230, 200))
    im.save(path)

def cta_png(path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ic = Image.open('/home/claude/promo-apps/icon-telarlabs-home.png').convert('RGBA').resize((200, 200))
    im.alpha_composite(ic, ((W - 200) // 2, 330))
    y = wrap_center(d, 580, 'Make your own', lora(110, True), (255, 255, 255))
    y = wrap_center(d, y + 10, 'Scenes · Green screens · Overlays', F('Poppins-Medium.ttf', 40), (235, 228, 245))
    y = wrap_center(d, y + 6, 'Free for personal & commercial use', F('Poppins-Regular.ttf', 36), (200, 194, 214))
    f = F('Poppins-Bold.ttf', 58); t = 'clips.telarlabs.net'; tw = d.textlength(t, font=f)
    d.rounded_rectangle(((W - tw) / 2 - 44, y + 60, (W + tw) / 2 + 44, y + 170), 55, fill=GOLD)
    d.text(((W - tw) / 2, y + 76), t, font=f, fill=(30, 18, 34))
    f3 = F('Poppins-Regular.ttf', 28)
    wrap_center(d, 1330, 'Motion graphic by Telar Labs', f3, (180, 174, 196))
    wrap_center(d, 1372, 'Illustrated scenes made with AI-assisted illustration', f3, (180, 174, 196))
    im.save(path)

def run(a): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)

def render(i, c, D):
    key, scene, cx0, cx1, ov = c[:5]
    png = f'{OUT}/t{i:02d}.png'; tmp = f'{OUT}/c{i:02d}.tmp.mp4'; dst = f'{OUT}/c{i:02d}.mp4'
    (cta_png if key == 'cta' else lambda p: text_png(c, p))(png)
    if key == 'cta':
        ins = ['-stream_loop', '-1', '-i', CL + 'purple-space-nebula-stars-loop.mp4',
               '-stream_loop', '-1', '-i', CL + 'gold-sparkles-green-screen-loop.mp4']
        fc = (f'[0:v]fps={FPS},scale=-2:1920,crop={W}:{H},eq=brightness=-0.08[b];'
              f'[1:v]fps={FPS},scale=-2:1920,crop={W}:{H},colorkey=0x00B140:0.28:0.08,despill=type=green[o];[b][o]overlay[v0];')
        ti = 2
    else:
        # pan across the 16:9 scene at 2.67x resolution for smooth sub-pixel motion
        SH = 2880; SW = int(1920 * SH / 1080); CW = int(SH * W / H)
        x0, x1 = cx0 * SW - CW / 2, cx1 * SW - CW / 2
        x0 = min(max(x0, 0), SW - CW); x1 = min(max(x1, 0), SW - CW)
        e = f"({x0:.1f}+({x1 - x0:.1f})*(0.5-0.5*cos(PI*t/{D:.2f})))"
        ins = ['-stream_loop', '-1', '-i', SC + scene + '.mp4']
        fc = f'[0:v]fps={FPS},scale={SW}:{SH}:flags=bicubic,crop={CW}:{SH}:{e}:0,scale={W}:{H}:flags=lanczos[b];'
        ti = 1
        if ov:
            f_, mode = ov; ins += ['-stream_loop', '-1', '-i', CL + f_ + '.mp4']; ti = 2
            fit = f'scale=-2:1920,crop={W}:{H}' if mode != 'key9' else f'scale={W}:{H}'
            if mode == 'keyc': fit = f'scale={W}:-2,pad={W}:{H}:0:(oh-ih)/2+120:color=0x00B140'
            if mode.startswith('key'):
                fc += f'[1:v]fps={FPS},{fit},colorkey=0x00B140:0.28:0.08,despill=type=green[o];[b][o]overlay[v0];'
            else:
                fc += f'[1:v]fps={FPS},{fit},format=gbrp[o];[b]format=gbrp[bb];[bb][o]blend=all_mode=screen,format=yuv420p[v0];'
        else: fc += '[b]null[v0];'
    ins += ['-framerate', str(FPS), '-loop', '1', '-t', f'{D:.3f}', '-i', png]
    fc += f'[{ti}:v]format=rgba,fade=in:st=0.5:d=0.7:alpha=1[t];[v0][t]overlay,format=yuv420p[v]'
    run([*ins, '-filter_complex', fc, '-map', '[v]', '-t', f'{D:.3f}', '-r', str(FPS),
         '-c:v', 'libx264', '-crf', '15', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp])
    os.replace(tmp, dst); return dst

def pad_music(T, sr=24000):
    t = np.arange(int(T * sr)) / sr; out = np.zeros_like(t)
    prog = [(261.63, 329.63, 392.0), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66)]
    bar = 4.0
    for k in range(int(T / bar) + 1):
        ch = prog[k % 4]; s = int(k * bar * sr); n = int((bar + 1.5) * sr); tt = np.arange(n) / sr
        env = np.minimum(tt / 1.2, 1) * np.exp(-np.maximum(tt - bar, 0) * 2.5)
        seg = sum(np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2.003 * tt) for f in ch) * env * .05
        seg += np.sin(2 * np.pi * ch[0] / 2 * tt) * env * .06
        if s >= len(out): continue
        e = min(len(out), s + n); out[s:e] += seg[:e - s]
        for j, f in enumerate((ch[0] * 2, ch[1] * 2, ch[2] * 2, ch[1] * 2)):   # music-box notes
            s2 = s + int(j * sr); n2 = int(1.6 * sr); t2 = np.arange(n2) / sr
            note = np.sin(2 * np.pi * f * t2) * np.exp(-t2 * 3.2) * .045
            if s2 >= len(out): continue
            e2 = min(len(out), s2 + n2); out[s2:e2] += note[:e2 - s2]
    fade = np.minimum(1, np.minimum(t / 2, (T - t) / 2.5)); return out * fade, sr

if __name__ == '__main__':
    only = sys.argv[1:]
    # 1) narration, durations
    lens = []
    for i, c in enumerate(CH):
        p = f'{OUT}/v{i:02d}.wav'
        if not os.path.exists(p): say(c[7], p, speed=1.0)
        lens.append(sf.info(p).duration)
    LEAD = 0.9
    D = [max(7.6, LEAD + L + 1.6) for L in lens]; D[-1] = LEAD + lens[-1] + 1.4 + X
    D[0] = max(D[0], 8.5)
    starts = np.cumsum([0] + [d - X for d in D[:-1]])
    T = starts[-1] + D[-1]; print('total', round(T, 2), [round(d, 1) for d in D])
    json.dump(dict(D=D, starts=list(starts)), open(f'{OUT}/plan.json', 'w'))
    if only and only[0] == 'plan': sys.exit()
    # 2) chapters
    files = []
    for i, c in enumerate(CH):
        dst = f'{OUT}/c{i:02d}.mp4'
        if only and str(i) not in only and os.path.exists(dst): files.append(dst); continue
        files.append(render(i, c, D[i])); print('chapter', i, c[0])
    # 3) crossfade join
    ins = sum([['-i', f] for f in files], [])
    fc, last, off = '', '[0:v]', 0
    for i in range(1, len(files)):
        off += D[i - 1] - X; tag = f'[x{i}]'
        fc += f'{last}[{i}:v]xfade=transition=fade:duration={X}:offset={off:.3f}{tag};'; last = tag
    if not (only and only[0] == 'audio'): run([*ins, '-filter_complex', fc.rstrip(';'), '-map', last, '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast',
         '-pix_fmt', 'yuv420p', '-r', str(FPS), '-movflags', '+faststart', f'{OUT}/video.mp4'])
    # 4) audio: narration over music, ducked
    sr = 24000; m, _ = pad_music(T, sr); voice = np.zeros_like(m)
    for i in range(len(CH)):
        a, r = sf.read(f'{OUT}/v{i:02d}.wav'); s = int((starts[i] + LEAD) * sr); voice[s:s + len(a)] += a[:len(voice) - s]
    env = np.convolve((np.abs(voice) > 0.01).astype(float), np.ones(int(.4 * sr)) / int(.4 * sr), 'same')
    duck = 1 - 0.55 * np.clip(env * 3, 0, 1)
    mix = voice + m * duck * 0.9
    sf.write(f'{OUT}/mix.wav', mix / max(1, np.abs(mix).max()) * 0.9, sr)
    final = '/home/claude/clips/promo-telar-clips-year-of-celebrations.mp4'
    run(['-i', f'{OUT}/video.mp4', '-i', f'{OUT}/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
         '-af', 'loudnorm=I=-14:TP=-1.5,aresample=48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final])
    print(final)

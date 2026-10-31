"""Build a 9:16 TikTok preview reel from the Christmas clips."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = '/tmp/claude-0/-home-claude/c4c42cf4-7f0e-5510-8275-f3b972cef798/scratchpad/clips/'
HERE = '/home/claude/clips/'
W, H = 1080, 1920
os.makedirs(HERE + 'reel', exist_ok=True)
B = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
M = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'

def font(p, s): return ImageFont.truetype(p, s)

def card(name, items):
    """items: list of (kind, text, y, size) — kind: 'pill', 'big', 'small', 'sample'"""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d, sd = ImageDraw.Draw(img), ImageDraw.Draw(sh)
    for kind, text, y, size in items:
        if kind == 'pill':
            f = font(B, size)
            tw = d.textlength(text, font=f)
            px, py = 34, 18
            x0 = (W - tw) / 2 - px
            box = [x0, y, x0 + tw + 2 * px, y + size + 2 * py + 8]
            d.rounded_rectangle(box, radius=(size + 2 * py) / 2, fill=(255, 255, 255, 240))
            d.text((W / 2, y + py + size / 2 + 6), text, font=f, fill=(150, 20, 30, 255), anchor='mm')
            continue
        f = font(B if kind in ('big', 'sample') else M, size)
        col = (255, 255, 255, 255) if kind != 'sample' else (255, 236, 190, 255)
        for i, line in enumerate(text.split('\n')):
            yy = y + i * size * 1.12
            for dx, dy in ((0, 6),):
                sd.text((W / 2 + dx, yy + dy), line, font=f, fill=(0, 0, 0, 200), anchor='ma')
            d.text((W / 2, yy), line, font=f, fill=col, anchor='ma')
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    out = Image.alpha_composite(sh, img)
    out.save(HERE + 'reel/' + name + '.png')
    return HERE + 'reel/' + name + '.png'

VERT = 'scale=-2:1920,crop=1080:1920'
SQUARE = ('crop=1080:1080,split=3[sq][t][b];[t]crop=1080:2:0:0,scale=1080:330[top];'
          '[b]crop=1080:2:0:1078,scale=1080:510[bot];[top][sq][bot]vstack=3')

def seg(n, src, start, dur, vf, png, key=None):
    out = f'{HERE}reel/s{n}.mp4'
    inputs = ['-ss', str(start), '-t', str(dur), '-i', src]
    if key:   # key: background clip for green-screen compositing
        inputs += ['-ss', '0', '-t', str(dur), '-i', key]
        fc = (f'[1:v]{VERT}[bg];[0:v]chromakey=0x00B140:0.13:0.06,despill=type=green[fg];'
              f'[bg][fg]overlay[v0];')
        pi = 2
    else:
        fc = f'[0:v]{vf}[v0];'
        pi = 1
    inputs += ['-loop', '1', '-t', str(dur), '-i', png]
    fc += f'[{pi}:v]format=rgba,fade=t=in:st=0.05:d=0.3:alpha=1[t];[v0][t]overlay,fps=30,format=yuv420p[v]'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', fc, '-map', '[v]',
                    '-t', str(dur), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', out], check=True)
    return out

segs = []
segs.append(seg(1, SRC + 'christmas-red-green-bokeh-loop.mp4', 0, 2.6, VERT, card('c1', [
    ('pill', 'FREE DOWNLOAD', 560, 44),
    ('big', 'Christmas\nbackgrounds', 680, 112),
    ('small', 'for your Pasko videos', 960, 54)])))
segs.append(seg(2, SRC + 'golden-bokeh-lights-loop.mp4', 0, 3, VERT, card('c2', [
    ('pill', '1  ·  Golden bokeh', 330, 40),
    ('sample', 'Maligayang\nPasko!', 760, 130)])))
segs.append(seg(3, SRC + 'parol-light-sequence-loop.mp4', 0, 3, SQUARE, card('c3', [
    ('pill', '2  ·  Parol lights', 180, 40),
    ('sample', 'Simbang Gabi', 1440, 96)])))
segs.append(seg(4, SRC + 'glowing-christmas-star-lanterns-loop.mp4', 0, 3, VERT, card('c4', [
    ('pill', '3  ·  Star lanterns', 150, 40),
    ('sample', 'Noche Buena\nsa Pamilya', 975, 92)])))
segs.append(seg(5, SRC + 'falling-snow-night-loop.mp4', 0, 2.6, VERT, card('c5', [
    ('pill', '4  ·  Falling snow', 330, 40),
    ('sample', 'Happy\nHolidays', 760, 130)])))
green = HERE + 'christmas-lights-frame-green-screen-9x16.mp4'
segs.append(seg(6, green, 0, 1.8, 'null', card('c6', [
    ('pill', '5  ·  Green screen frame', 330, 40),
    ('big', 'Before', 840, 120)])))
segs.append(seg(7, green, 1.8, 2.6, None, card('c7', [
    ('pill', '5  ·  Green screen frame', 330, 40),
    ('small', 'After: green removed', 640, 54),
    ('sample', 'Merry\nChristmas!', 800, 130)]), key=SRC + 'christmas-red-green-bokeh-loop.mp4'))
segs.append(seg(8, SRC + 'gold-glitter-sparkles-loop.mp4', 0, 3.2, VERT, card('c8', [
    ('big', 'All FREE', 600, 140),
    ('small', 'No sign-up  ·  OK for commercial use', 800, 44),
    ('pill', 'LINK IN BIO', 940, 52),
    ('small', 'by Telar Labs', 1160, 40)])))

with open(HERE + 'reel/list.txt', 'w') as f:
    f.writelines(f"file '{s}'\n" for s in segs)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', HERE + 'reel/list.txt',
                '-c', 'copy', '-movflags', '+faststart', HERE + 'tiktok-preview-christmas-backgrounds.mp4'], check=True)
print('done')

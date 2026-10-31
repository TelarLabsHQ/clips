"""TikTok / Reels promo (9:16) for Telar Clips: holiday season, illustrated scenes, green screen demo, CTA.
Usage: python3 reel2.py [site-text]"""
import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SITE = sys.argv[1] if len(sys.argv) > 1 else 'telarclips.pages.dev'
C = '/home/claude/clips/out/'
S = '/home/claude/scenes2/out/'
OUT = '/home/claude/clips/reel2/'
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
B = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
M = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
F = lambda p, s: ImageFont.truetype(p, s)

GOLD, CREAM, WHITE = (255, 196, 92), (255, 238, 205), (255, 255, 255)

def text_png(name, items, shade=0):
    """items: (kind, text, y, size[, colour]); kinds: pill, big, mid, small, site. shade: darken the top N px."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if shade:
        g = ImageDraw.Draw(sh)
        for yy in range(shade):
            g.line([(0, yy), (W, yy)], fill=(0, 0, 0, int(150 * min(1, (shade - yy) / (shade * 0.45)))))
    d, sd = ImageDraw.Draw(img), ImageDraw.Draw(sh)
    for it in items:
        kind, text, y, size = it[:4]
        col = it[4] if len(it) > 4 else WHITE
        if kind in ('pill', 'site'):
            f = F(B, size); tw = d.textlength(text, font=f); px, py = 36, 20
            x0 = (W - tw) / 2 - px; box = [x0, y, x0 + tw + 2 * px, y + size + 2 * py + 6]
            fill = (255, 196, 92, 255) if kind == 'site' else (255, 255, 255, 235)
            sd.rounded_rectangle([box[0], box[1] + 8, box[2], box[3] + 8], radius=60, fill=(0, 0, 0, 150))
            d.rounded_rectangle(box, radius=(box[3] - box[1]) / 2, fill=fill)
            d.text((W / 2, (box[1] + box[3]) / 2 + 2), text, font=f, fill=(40, 22, 8, 255) if kind == 'site' else (150, 30, 40, 255), anchor='mm')
            continue
        f = F(B if kind in ('big', 'mid') else M, size)
        for i, line in enumerate(text.split('\n')):
            yy = y + i * size * 1.1
            sd.text((W / 2, yy + 6), line, font=f, fill=(0, 0, 0, 210), anchor='ma')
            d.text((W / 2, yy), line, font=f, fill=col + (255,), anchor='ma')
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    p = OUT + name + '.png'
    Image.alpha_composite(sh, img).save(p)
    return p

def card_assets():
    """Rounded-corner mask and soft shadow for the 16:9 'card' layout (1000x562)."""
    cw, ch, r = 1000, 562, 36
    m = Image.new('L', (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=r, fill=255)
    m.save(OUT + 'mask.png')
    s = Image.new('RGBA', (W, ch + 160), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([40, 90, 40 + cw, 90 + ch], radius=r, fill=(0, 0, 0, 200))
    s.filter(ImageFilter.GaussianBlur(28)).save(OUT + 'shadow.png')
card_assets()

FULL = 'scale=-2:1920,crop=1080:1920'
def run(args):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *args], check=True)

def seg(n, src, dur, png, mode='full', start=0, cx=None, key_bg=None, card_y=640):
    tmp, out = f'{OUT}s{n}.tmp.mp4', f'{OUT}s{n}.mp4'
    ins = ['-ss', str(start), '-t', str(dur), '-i', src]
    crop = FULL if cx is None else f'scale=-2:1920,crop=1080:1920:{cx}:0'
    if key_bg:  # green screen: key the 9:16 frame over a background
        ins += ['-t', str(dur), '-i', key_bg]
        fc = f'[1:v]fps={FPS},{crop}[bg];[0:v]fps={FPS},chromakey=0x00B140:0.13:0.06,despill=type=green[fg];[bg][fg]overlay[v0];'
        nxt = 2
    elif mode == 'card':
        ins += ['-loop', '1', '-i', OUT + 'mask.png', '-loop', '1', '-i', OUT + 'shadow.png']
        fc = (f'[0:v]fps={FPS},split[a][b];[a]{FULL},boxblur=30:2,eq=brightness=-0.18:saturation=1.2[bg];'
              f'[b]scale=1000:562,format=rgba[c];[1:v]format=gray[m];[c][m]alphamerge[card];'
              f'[bg][2:v]overlay=0:{card_y - 90}[bs];[bs][card]overlay=40:{card_y}:shortest=1[v0];')
        nxt = 3
    else:
        fc = f'[0:v]fps={FPS},{crop}[v0];'
        nxt = 1
    ins += ['-loop', '1', '-t', str(dur), '-i', png]
    # text slides up 40px and fades in over 0.35s
    fc += (f'[{nxt}:v]format=rgba,fade=t=in:st=0.1:d=0.35:alpha=1[t];'
           f"[v0][t]overlay=x=0:y='max(0,40-120*t)',trim=duration={dur},format=yuv420p[v]")
    run([*ins, '-filter_complex', fc, '-map', '[v]', '-r', str(FPS), '-t', str(dur),
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', tmp])
    os.replace(tmp, out)
    return out

segs = [
    # 1 hook
    seg(1, S + 'alpine-christmas.mp4', 2.6, text_png('t1', [
        ('pill', 'FREE DOWNLOAD', 300, 44),
        ('big', 'Christmas video\nbackgrounds', 430, 108),
        ('small', 'for greetings, reels & church videos', 690, 46, CREAM)], shade=900), cx=1100),
    # 2 illustrated scene (card)
    seg(2, S + 'xmas-girl.mp4', 2.8, text_png('t2', [
        ('pill', 'NEW: illustrated scenes', 300, 40),
        ('mid', 'Merry Christmas!', 1260, 96, CREAM),
        ('small', 'add your own greeting', 1390, 44)]), mode='card'),
    # 3 bokeh full
    seg(3, C + 'golden-bokeh-lights-loop.mp4', 2.4, text_png('t3', [
        ('pill', 'Bokeh lights', 300, 40),
        ('big', 'Happy\nHolidays', 720, 140, CREAM)])),
    # 4 green screen before
    seg(4, '/home/claude/clips/christmas-lights-frame-green-screen-9x16.mp4', 1.5, text_png('t4', [
        ('pill', 'Green screen', 300, 40),
        ('big', 'Before', 820, 120)])),
    # 5 green screen after, keyed over the snowy village
    seg(5, '/home/claude/clips/christmas-lights-frame-green-screen-9x16.mp4', 2.5, text_png('t5', [
        ('pill', 'Green screen', 300, 40),
        ('mid', 'After: green removed in CapCut', 640, 54),
        ('big', 'Season\'s\nGreetings', 760, 120, CREAM)], shade=1100), start=1.5, key_bg=S + 'alpine-christmas.mp4'),
    # 6 New Year (card)
    seg(6, S + 'harbour-fireworks.mp4', 2.6, text_png('t6', [
        ('pill', 'New Year', 300, 40),
        ('mid', 'Happy New Year!', 1260, 96, CREAM)]), mode='card'),
    # 7 sparkler boy (card)
    seg(7, S + 'sparkler-boy.mp4', 2.4, text_png('t7', [
        ('pill', 'Cute characters too', 300, 40),
        ('mid', 'Cheers to 2027!', 1260, 92, CREAM)]), mode='card'),
    # 8 lunar new year (card)
    seg(8, S + 'qipao-girl.mp4', 2.4, text_png('t8', [
        ('pill', 'Lunar New Year · Ramadan · Valentine\'s', 300, 36),
        ('mid', 'Every holiday,\nevery culture', 1240, 84, CREAM)]), mode='card'),
    # 9 CTA
    seg(9, C + 'gold-glitter-sparkles-loop.mp4', 3.6, text_png('t9', [
        ('big', '100+ clips\nall FREE', 470, 128),
        ('small', 'No sign-up  ·  OK for commercial use', 790, 44, CREAM),
        ('site', SITE, 900, 56),
        ('small', 'Link in bio  ·  by Telar Labs', 1060, 40)])),
]

lst = OUT + 'list.txt'
open(lst, 'w').writelines(f"file '{s}'\n" for s in segs)
final = '/home/claude/clips/telar-clips-tiktok-promo.mp4'
run(['-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', final + '.tmp.mp4'])
os.replace(final + '.tmp.mp4', final)
print('done', final)

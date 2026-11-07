"""Seven 9:16 promo reels for Telar Clips, one per creator use case, with AI narration (Kokoro).
Usage: python3 promos.py [site-text] [video-number ...]"""
import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SITE = sys.argv[1] if len(sys.argv) > 1 else 'clips.telarlabs.net'
ONLY = [int(a) for a in sys.argv[2:]]
C = '/home/claude/clips/out/'
S = '/home/claude/scenes2/out/'
G9 = '/home/claude/clips/christmas-lights-frame-green-screen-9x16.mp4'
ROOT = '/home/claude/clips/promos/'
W, H, FPS = 1080, 1920, 30
FONTS = {
    'B': '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
    'M': '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf',
    'serif': '/home/claude/fonts/Playfair-Bold.woff',
    'serifi': '/home/claude/fonts/Playfair-Italic.woff',
    'script': '/home/claude/fonts/Dancing-Bold.woff',
    'bebas': '/home/claude/fonts/Bebas.woff',
}
WHITE, CREAM, GOLD, INK = (255, 255, 255), (255, 238, 205), (255, 196, 92), (40, 22, 8)

_K = None
def say(text, path, speed=1.05, voice='af_heart'):
    """Narrate with Kokoro (Apache-2.0). 'Telar' is read teh-LAR."""
    global _K
    import soundfile as sf
    from kokoro_onnx import Kokoro
    if _K is None: _K = Kokoro('/tmp/kok/kokoro-v1.0.onnx', '/tmp/kok/voices-v1.0.bin')
    ph = _K.tokenizer.phonemize(text, 'en-us').replace('tˈɛlɚ', 'tɛlˈɑːɹ').replace('ʔn', 'tən')
    a, sr = _K.create(ph, voice=voice, speed=speed, is_phonemes=True)
    sf.write(path, a, sr); return path

def wav_len(p):
    import soundfile as sf
    i = sf.info(p); return i.frames / i.samplerate

SITE_SAY = 'clips dot Telar Labs dot net'
LINES = {
 '1-quotes-verses': [
   'Making quote or Bible verse videos? Keep them moving.',
   'Use a soft gradient for your daily quotes.',
   'A golden sky for Bible verses.',
   'Space and stars for fun facts.',
   'And a starry night for poems and song lyrics.',
   f'Free, no sign-up, okay for commercial use. {SITE_SAY}.'],
 '2-greetings': [
   'Make a greeting video in one minute. Just add a name.',
   'Birthdays with balloons and confetti.',
   'Graduation congratulations.',
   'Fiesta greetings with colorful flags.',
   'Sweet anniversary messages.',
   'And Christmas greetings for the whole family.',
   f'Free greeting backgrounds at {SITE_SAY}.'],
 '3-intros-outros': [
   'Need an intro, an outro, or a title card for your channel?',
   'Welcome your viewers back.',
   'Break your video into parts.',
   'Show your episode titles.',
   'And end with a thank you and a subscribe button.',
   f'Free intro and outro backgrounds at {SITE_SAY}. Link in bio!'],
 '4-green-screen': [
   'Add green screen effects over any video, for free.',
   None, 'Confetti for celebrations.',
   None, 'Falling snow for Christmas.',
   None, 'Floating hearts for love notes.',
   None, 'And glowing light frames.',
   f'For CapCut, Canva and Premiere. Free at {SITE_SAY}.'],
 '5-livestream': [
   'Streaming on Twitch, YouTube or Facebook Live?',
   'Show a starting soon screen while people join.',
   'A be right back screen for your breaks.',
   'And a thank you screen at the end.',
   f'Free stream screens and loops at {SITE_SAY}. Link in bio!'],
 '6-lofi-ambient': [
   'Making lofi, study or sleep videos? These calm scenes loop forever.',
   'A rainy afternoon.',
   'A quiet night.',
   'A calm spring morning.',
   f'Seamless loops you can repeat for hours. Free at {SITE_SAY}.'],
 '7-church-school-events': [
   'Free backgrounds for church, school and events.',
   'Worship song lyrics on soft, heavenly light.',
   'Graduation programs.',
   'Christmas programs on the LED wall.',
   'Tributes and slideshows.',
   f'Free backgrounds for your next program at {SITE_SAY}. Link in bio!'],
}

def T(t, y, size, font='B', color=WHITE, kind='text', **kw):
    return dict(t=t, y=y, size=size, font=font, color=color, kind=kind, **kw)

def text_png(path, items, shade=0, bottom_shade=0):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d, sd = ImageDraw.Draw(img), ImageDraw.Draw(sh)
    for yy in range(shade):
        sd.line([(0, yy), (W, yy)], fill=(0, 0, 0, int(160 * min(1, (shade - yy) / (shade * 0.45)))))
    for k in range(bottom_shade):
        yy = H - 1 - k
        sd.line([(0, yy), (W, yy)], fill=(0, 0, 0, int(160 * min(1, (bottom_shade - k) / (bottom_shade * 0.45)))))
    for it in items:
        f = ImageFont.truetype(FONTS[it['font']], it['size'])
        lines = it['t'].split('\n'); lh = it['size'] * it.get('lh', 1.15)
        if it['kind'] in ('pill', 'site', 'button'):
            tw = d.textlength(it['t'], font=f); px, py = 38, 20
            x0 = (W - tw) / 2 - px; box = [x0, it['y'], x0 + tw + 2 * px, it['y'] + it['size'] + 2 * py + 6]
            fill = {'pill': (255, 255, 255, 235), 'site': GOLD + (255,), 'button': (230, 33, 41, 255)}[it['kind']]
            tc = {'pill': (150, 30, 40), 'site': INK, 'button': WHITE}[it['kind']]
            sd.rounded_rectangle([box[0], box[1] + 8, box[2], box[3] + 8], radius=60, fill=(0, 0, 0, 150))
            d.rounded_rectangle(box, radius=(box[3] - box[1]) / 2 if it['kind'] != 'button' else 18, fill=fill)
            d.text((W / 2, (box[1] + box[3]) / 2 + 2), it['t'], font=f, fill=tc + (255,), anchor='mm')
            continue
        if it['kind'] == 'box':  # dark translucent panel behind the text block
            tw = max(d.textlength(l, font=f) for l in lines)
            bh = lh * len(lines)
            d.rounded_rectangle([(W - tw) / 2 - 50, it['y'] - 34, (W + tw) / 2 + 50, it['y'] + bh + 24], radius=28, fill=(0, 0, 0, 120))
        for i, line in enumerate(lines):
            yy = it['y'] + i * lh
            sd.text((W / 2, yy + 6), line, font=f, fill=(0, 0, 0, 220), anchor='ma')
            d.text((W / 2, yy), line, font=f, fill=it['color'] + (255,), anchor='ma')
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    Image.alpha_composite(sh, img).save(path)
    return path

def assets(out):
    cw, ch, r = 1000, 562, 36
    m = Image.new('L', (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=r, fill=255)
    m.save(out + 'mask.png')
    s = Image.new('RGBA', (W, ch + 160), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([40, 90, 40 + cw, 90 + ch], radius=r, fill=(0, 0, 0, 200))
    s.filter(ImageFilter.GaussianBlur(28)).save(out + 'shadow.png')

def vcrop(cx=None):
    return 'scale=-2:1920,crop=1080:1920' + (f':{cx}:0' if cx is not None else '')

def run(args):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *args], check=True)

class Reel:
    def __init__(self, name, speed=1.1):
        self.name, self.dir, self.segs, self.speed = name, ROOT + name + '/', [], speed
        os.makedirs(self.dir, exist_ok=True); assets(self.dir)

    def seg(self, src, dur, items, mode='full', start=0, cx=None, key_bg=None, bg_cx=None, card_y=640, shade=0, bottom_shade=0, tail=0.5):
        n = len(self.segs) + 1
        line = LINES[self.name][n - 1] if self.name in LINES else None
        wav = say(line, f'{self.dir}v{n}.wav', self.speed) if line else None
        if wav: dur = round(max(min(dur, 2.2), wav_len(wav) + tail), 2)
        png = text_png(f'{self.dir}t{n}.png', items, shade, bottom_shade)
        tmp, out = f'{self.dir}s{n}.tmp.mp4', f'{self.dir}s{n}.mp4'
        ins = ['-stream_loop', '-1', '-ss', str(start), '-t', str(dur), '-i', src]
        if key_bg:
            ins += ['-stream_loop', '-1', '-t', str(dur), '-i', key_bg]
            fg = 'null' if src.endswith('9x16.mp4') else vcrop(cx)
            fc = (f'[1:v]fps={FPS},{vcrop(bg_cx)}[bg];[0:v]fps={FPS},{fg},chromakey=0x00B140:0.13:0.06,despill=type=green[fg];'
                  f'[bg][fg]overlay=shortest=1[v0];')
            nxt = 2
        elif mode == 'card':
            ins += ['-loop', '1', '-i', self.dir + 'mask.png', '-loop', '1', '-i', self.dir + 'shadow.png']
            fc = (f'[0:v]fps={FPS},split[a][b];[a]{vcrop()},boxblur=30:2,eq=brightness=-0.18:saturation=1.2[bg];'
                  f'[b]scale=1000:562,format=rgba[c];[1:v]format=gray[m];[c][m]alphamerge[card];'
                  f'[bg][2:v]overlay=0:{card_y - 90}[bs];[bs][card]overlay=40:{card_y}:shortest=1[v0];')
            nxt = 3
        else:
            fg = 'null' if src.endswith('9x16.mp4') else vcrop(cx)
            fc = f'[0:v]fps={FPS},{fg}[v0];'
            nxt = 1
        ins += ['-loop', '1', '-t', str(dur), '-i', png]
        fc += (f'[{nxt}:v]format=rgba,fade=t=in:st=0.08:d=0.35:alpha=1[t];'
               f"[v0][t]overlay=x=0:y='max(0,40-120*t)',trim=duration={dur},format=yuv420p[v]")
        run([*ins, '-filter_complex', fc, '-map', '[v]', '-r', str(FPS), '-t', str(dur),
             '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', tmp])
        os.replace(tmp, out)
        aud = (['-i', wav, '-filter_complex', f'[1:a]adelay=200|200,apad,atrim=0:{dur},aformat=sample_rates=48000:channel_layouts=stereo[a]', '-map', '0:v', '-map', '[a]']
               if wav else ['-f', 'lavfi', '-t', str(dur), '-i', 'anullsrc=r=48000:cl=stereo', '-map', '0:v', '-map', '1:a'])
        run(['-i', out, *aud, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', str(dur), tmp])
        os.replace(tmp, out); self.segs.append(out)

    def cta(self, line, sub='No sign-up  ·  OK for commercial use'):
        self.seg(C + 'gold-glitter-sparkles-loop.mp4', 3.4, [
            T(line, 470, 104), T(sub, 800, 42, 'M', CREAM),
            T(SITE, 900, 56, kind='site'), T('Link in bio  ·  by Telar Labs', 1060, 40, 'M')], tail=1.4)

    def save(self):
        lst = self.dir + 'list.txt'
        open(lst, 'w').writelines(f"file '{s}'\n" for s in self.segs)
        final = f'/home/claude/clips/promo-{self.name}-voice.mp4'
        run(['-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-shortest', '-movflags', '+faststart', final + '.tmp.mp4'])
        os.replace(final + '.tmp.mp4', final); print('done', final, flush=True)

def hook(r, src, title, sub, **kw):
    r.seg(src, 2.6, [T('FREE BACKGROUNDS', 300, 44, kind='pill'), T(title, 430, 100), T(sub, 690, 44, 'M', CREAM)], shade=900, **kw)

# ------------------------------------------------------------------ 1. text videos
def v1():
    r = Reel('1-quotes-verses')
    hook(r, C + 'sunset-gradient-flow-loop.mp4', 'for quotes, verses\n& "did you know"', 'Keep your text videos moving')
    r.seg(C + 'pastel-dream-gradient-flow-loop.mp4', 2.6, [T('Quote', 300, 38, kind='pill'),
          T('Small steps\nevery day still\nmove you forward.', 700, 96, 'serif', lh=1.2)])
    r.seg(C + 'golden-sunset-clouds-loop.mp4', 2.8, [T('Bible verse', 300, 38, kind='pill'),
          T('This is the day which\nthe LORD hath made;\nwe will rejoice and\nbe glad in it.', 640, 74, 'serif', lh=1.25),
          T('Psalm 118:24', 1060, 44, 'serifi', CREAM)])
    r.seg(C + 'purple-space-nebula-stars-loop.mp4', 2.6, [T('Did you know?', 300, 38, kind='pill'),
          T('Honey found in\nancient Egyptian tombs\nwas still edible.', 720, 78, lh=1.2)])
    r.seg(C + 'starry-night-shooting-stars-loop.mp4', 2.6, [T('Poem & lyric videos', 300, 38, kind='pill'),
          T('"Hope" is the thing\nwith feathers', 740, 88, 'serifi'), T('Emily Dickinson', 1000, 44, 'M', CREAM)])
    r.cta('Free loops\nfor text videos')
    r.save()

# ------------------------------------------------------------------ 2. greetings
def v2():
    r = Reel('2-greetings')
    hook(r, C + 'birthday-balloons-rising-loop.mp4', 'Greetings in\n1 minute', 'Add a name and a message. Done.')
    r.seg(C + 'celebration-confetti-loop.mp4', 2.4, [T('Birthday', 300, 38, kind='pill'),
          T('Happy 7th\nBirthday, Mia!', 720, 120, 'script', CREAM)])
    r.seg(C + 'navy-gold-graduation-bokeh-loop.mp4', 2.4, [T('Graduation', 300, 38, kind='pill'),
          T('Congratulations,\nGrad!', 740, 100, 'serif', GOLD)])
    r.seg(C + 'fiesta-banderitas-flags-loop.mp4', 2.4, [T('Fiesta', 300, 38, kind='pill'),
          T('Happy Fiesta!', 800, 120, 'script')], shade=1100)
    r.seg(C + 'pink-rose-bokeh-loop.mp4', 2.4, [T('Anniversary', 300, 38, kind='pill'),
          T('Happy 25th\nAnniversary', 740, 110, 'script')])
    r.seg(S + 'xmas-girl.mp4', 2.6, [T('Christmas', 300, 38, kind='pill'),
          T('Merry Christmas', 1260, 96, 'script', CREAM), T('from the Santos family', 1400, 46, 'M')], mode='card')
    r.cta('Free greeting\nbackgrounds')
    r.save()

# ------------------------------------------------------------------ 3. intros & outros
def v3():
    r = Reel('3-intros-outros')
    hook(r, C + 'retro-neon-grid-sunset-loop.mp4', 'for intros, outros\n& title cards', 'Channel openers, section breaks, end screens')
    r.seg(C + 'aurora-night-gradient-flow-loop.mp4', 2.4, [T('Intro', 300, 38, kind='pill'),
          T('WELCOME BACK', 760, 150, 'bebas'), T('to the channel', 920, 52, 'M', CREAM)])
    r.seg(C + 'blue-purple-gradient-flow-loop.mp4', 2.4, [T('Section break', 300, 38, kind='pill'),
          T('PART 2', 720, 220, 'bebas'), T('Setting up the studio', 960, 52, 'M', CREAM)])
    r.seg(C + 'black-gold-luxury-gradient-flow-loop.mp4', 2.4, [T('Title card', 300, 38, kind='pill'),
          T('EPISODE 12', 740, 170, 'bebas', GOLD), T('Our first family trip', 940, 52, 'M')])
    r.seg(C + 'golden-bokeh-lights-loop.mp4', 2.6, [T('End screen', 300, 38, kind='pill'),
          T('Thanks for watching!', 720, 82), T('SUBSCRIBE', 900, 64, 'B', kind='button')])
    r.cta('Free intro & outro\nbackgrounds')
    r.save()

# ------------------------------------------------------------------ 4. green screen
def v4():
    r = Reel('4-green-screen')
    hook(r, C + 'confetti-green-screen-loop.mp4', 'Green screen\neffects', 'Drop them over any video')
    pairs = [(C + 'confetti-green-screen-loop.mp4', S + 'sparkler-boy.mp4', 'Confetti', 1300),
             (C + 'snowflakes-green-screen-loop.mp4', S + 'alpine-christmas.mp4', 'Snowflakes', 1100),
             (C + 'floating-hearts-green-screen-loop.mp4', S + 'umbrella-kids.mp4', 'Hearts', 1500),
             (G9, S + 'harbour-fireworks.mp4', 'Light frames', 900)]
    for fg, bg, label, bcx in pairs:
        r.seg(fg, 1.1, [T(label, 300, 38, kind='pill'), T('Before', 820, 120)])
        r.seg(fg, 1.9, [T(label, 300, 38, kind='pill'), T('After', 820, 120, color=CREAM)], start=1.1, key_bg=bg, bg_cx=bcx, shade=700)
    r.cta('Free green\nscreen clips', 'Works in CapCut, Canva Pro & Premiere')
    r.save()

# ------------------------------------------------------------------ 5. livestream
def v5():
    r = Reel('5-livestream')
    hook(r, C + 'purple-space-nebula-stars-loop.mp4', 'for your\nlivestream', 'Twitch · YouTube · Facebook Live')
    r.seg(C + 'blue-tech-network-plexus-loop.mp4', 2.6, [T('Before the stream', 300, 38, kind='pill'),
          T('STARTING\nSOON', 700, 200, 'bebas', lh=0.95), T('grab a snack, we go live in a minute', 1110, 42, 'M', CREAM)])
    r.seg(S + 'ramadan-town.mp4', 2.6, [T('On a break', 300, 38, kind='pill'),
          T('BE RIGHT\nBACK', 700, 200, 'bebas', lh=0.95)], cx=1200, shade=900)
    r.seg(C + 'cool-blue-bokeh-loop.mp4', 2.6, [T('After the stream', 300, 38, kind='pill'),
          T('THANKS FOR\nWATCHING', 700, 180, 'bebas', lh=0.95), T('see you next stream!', 1090, 46, 'M', CREAM)])
    r.cta('Free stream\nscreens & loops')
    r.save()

# ------------------------------------------------------------------ 6. lofi & ambient
def v6():
    r = Reel('6-lofi-ambient', speed=0.95)
    hook(r, S + 'alpine-christmas.mp4', 'for lofi, study\n& sleep videos', 'Calm scenes that loop forever', cx=1100)
    for src, label, title, cx in [(S + 'umbrella-kids.mp4', 'Rainy day', 'rainy afternoon\nstudy session', 1300),
                                  (S + 'ramadan-town.mp4', 'Night', 'quiet night\nsleep & focus', 1200),
                                  (S + 'sakura-river.mp4', 'Spring', 'calm spring\nmorning', 900)]:
        r.seg(src, 2.8, [T(label, 300, 38, kind='pill'), T(title, 1180, 84, 'serifi', lh=1.15),
              T('1 hour loop', 1440, 46, 'M', CREAM)], cx=cx, bottom_shade=900)
    r.cta('Free ambient\nscene loops', 'Seamless loops: repeat them for hours')
    r.save()

# ------------------------------------------------------------------ 7. church, school & events
def v7():
    r = Reel('7-church-school-events')
    hook(r, C + 'heavenly-white-light-rays-loop.mp4', 'for church, school\n& events', 'Lyrics, programs, LED walls, slideshows')
    r.seg(C + 'heavenly-white-light-rays-loop.mp4', 2.8, [T('Worship lyrics', 300, 38, kind='pill'),
          T('Amazing grace!\nHow sweet the sound\nthat saved a wretch\nlike me!', 640, 82, 'serif', kind='box', lh=1.25)])
    r.seg(C + 'navy-gold-graduation-bokeh-loop.mp4', 2.6, [T('Graduation', 300, 38, kind='pill'),
          T('Congratulations,\nClass of 2027!', 760, 92, 'serif', GOLD)])
    r.seg(C + 'twinkling-christmas-string-lights-loop.mp4', 2.6, [T('LED wall', 300, 38, kind='pill'),
          T('Welcome to our\nChristmas Program', 760, 90, 'B', CREAM)])
    r.seg(C + 'silver-white-bokeh-loop.mp4', 2.6, [T('Tributes & slideshows', 300, 38, kind='pill'),
          T('Forever in\nour hearts', 760, 110, 'script')])
    r.cta('Free backgrounds\nfor your program')
    r.save()

if __name__ == '__main__':
    fns = [v1, v2, v3, v4, v5, v6, v7]
    for i, f in enumerate(fns, 1):
        if not ONLY or i in ONLY:
            f()

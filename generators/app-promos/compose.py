"""Narrated 9:16 promos for PizarraPad, QuizPolice and DraftTrail from recorded app footage.
Usage: python3 compose.py [video-key ...]"""
import os, sys, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf
from kokoro_onnx import Kokoro

W, H, FPS = 1080, 1920, 30
HERE = '/home/claude/promo-apps/'; RAW = HERE + 'raw/'; WORK = HERE + 'work/'; OUT = '/home/claude/clips/'
os.makedirs(WORK, exist_ok=True)
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'; FM = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
APPS = {
  'pp': dict(name='PizarraPad', url='pizarrapad.telarlabs.net', icon='icon-pizarrapad.png', c=(94, 211, 154), bg1=(10, 34, 24), bg2=(22, 70, 48), tag='Free online whiteboard'),
  'qp': dict(name='QuizPolice', url='quizpolice.telarlabs.net', icon='icon-quizpolice.png', c=(127, 166, 255), bg1=(12, 18, 40), bg2=(30, 46, 98), tag='Free quiz monitoring'),
  'ts': dict(name='Telar Stories', url='telarlabs.net', icon='icon-telarlabs-home.png', c=(255, 143, 163), bg1=(30, 14, 28), bg2=(78, 32, 64), tag='Narrated story videos for kids'),
  'tc': dict(name='Telar Clips', url='clips.telarlabs.net', icon='icon-telarlabs-home.png', c=(255, 181, 71), bg1=(24, 16, 30), bg2=(70, 40, 60), tag='Free motion backgrounds'),
  'tl': dict(name='Telar Labs', url='telarlabs.net', icon='icon-telarlabs-home.png', c=(255, 170, 120), bg1=(28, 14, 30), bg2=(80, 36, 62), tag='Free tools for creators'),
  'tx': dict(name='Tixward', url='tixward.telarlabs.net', icon='icon-tixward.png', c=(255, 138, 76), bg1=(32, 14, 6), bg2=(96, 38, 12), tag='Event tickets & bookings'),
  'dt': dict(name='DraftTrail', url='drafttrail.telarlabs.net', icon='icon-drafttrail.png', c=(196, 155, 255), bg1=(22, 14, 40), bg2=(56, 34, 96), tag='Free writing-process recorder'),
}
SAY_FIX = [('ɹˈuːpˈaɪə', 'ɹuːpˈiːə'), ('jˈuːən', 'juːˈɑːn'), ('tˈɛlɚ', 'tɛlˈɑːɹ'), ('pˈɪzæɹə', 'pɪsˈɑːɹə'), ('ɹˈɪʔn', 'ɹˈɪtən'), ('ʔn', 'tən')]   # Telar = teh-LAR, Pizarra = pi-SAH-rah
_K = None
def say(text, path, speed=1.1):
    global _K
    if _K is None: _K = Kokoro('/tmp/kok/kokoro-v1.0.onnx', '/tmp/kok/voices-v1.0.bin')
    ph = _K.tokenizer.phonemize(text, 'en-us')
    for a, b in SAY_FIX: ph = ph.replace(a, b)
    a, sr = _K.create(ph, voice='af_heart', speed=speed, is_phonemes=True)
    sf.write(path, a, sr); return len(a) / sr

def run(args): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *args], check=True)
def dims(p):
    o = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', p]).decode().split(',')
    return int(o[0]), int(o[1])
def dur_of(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

def grad(a):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(a['bg1'][i] * (1 - t) + a['bg2'][i] * t) for i in range(3)))
    glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse([-300, -500, W + 300, 700], fill=70)
    im.paste(Image.new('RGB', (W, H), a['c']), (0, 0), glow.filter(ImageFilter.GaussianBlur(160)))
    return im.convert('RGBA')

def wrap_lines(d, text, font, maxw):
    out = []
    for para in text.split('\n'):
        words, line = para.split(), ''
        for w in words:
            t = (line + ' ' + w).strip()
            if d.textlength(t, font=font) > maxw and line: out.append(line); line = w
            else: line = t
        out.append(line)
    return out

def shadow_text(im, xy, text, font, fill, anchor='ma'):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 5), text, font=font, fill=(0, 0, 0, 170), anchor=anchor)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); ImageDraw.Draw(im).text(xy, text, font=font, fill=fill, anchor=anchor)

def layout(kind, sw, sh):
    if kind == 'land': cw = 1000; ch = round(cw * sh / sw); return (W - cw) // 2, 700, cw, ch, 30
    if kind == 'big': cw = 1000; ch = round(cw * sh / sw); return (W - cw) // 2, 560, cw, ch, 30
    if kind == 'tall': cw = 880; ch = round(cw * sh / sw); return (W - cw) // 2, 470, cw, ch, 26
    ch = 1150; cw = round(ch * sw / sh); return (W - cw) // 2, 500, cw, ch, 44   # phone

def frame_png(a, s, kind, box, path):
    x, y, cw, ch, r = box; im = grad(a); d = ImageDraw.Draw(im)
    # step pill + headline
    top = 200 if kind != 'land' else 260
    if s.get('pill'):
        f = ImageFont.truetype(FB, 36); tw = d.textlength(s['pill'], font=f)
        d.rounded_rectangle([(W - tw) / 2 - 30, top - 80, (W + tw) / 2 + 30, top - 20], radius=30, fill=a['c'])
        d.text((W / 2, top - 50), s['pill'], font=f, fill=a['bg1'], anchor='mm')
    fh = ImageFont.truetype(FB, s.get('hsize', 76 if kind != 'land' else 84))
    lines = wrap_lines(d, s['head'], fh, 960)
    lh = fh.size * 1.14; hy = top + 10
    for i, l in enumerate(lines): shadow_text(im, (W / 2, hy + i * lh), l, fh, (255, 255, 255))
    # card shadow / phone bezel
    pad = 16 if kind == 'phone' else 0
    shd = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shd).rounded_rectangle([x - pad, y - pad + 18, x + cw + pad, y + ch + pad + 18], radius=r + pad, fill=(0, 0, 0, 150))
    im.alpha_composite(shd.filter(ImageFilter.GaussianBlur(30)))
    if kind == 'phone':
        d = ImageDraw.Draw(im); d.rounded_rectangle([x - pad, y - pad, x + cw + pad, y + ch + pad], radius=r + pad, fill=(18, 18, 22))
    # caption under landscape cards
    if kind in ('land', 'big') and s.get('say'):
        fc = ImageFont.truetype(FM, 50 if kind == 'big' else 44)
        for i, l in enumerate(wrap_lines(d, s['say'], fc, 940)[:4]):
            shadow_text(im, (W / 2, y + ch + 70 + i * 66), l, fc, (235, 235, 245))
    im.save(path)
    m = Image.new('L', (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=r, fill=255); m.save(path + '.mask.png')

def cta_png(a, s, path):
    im = grad(a); d = ImageDraw.Draw(im)
    ic = Image.open(HERE + a['icon']).convert('RGBA').resize((220, 220)); im.alpha_composite(ic, ((W - 220) // 2, 430))
    shadow_text(im, (W / 2, 700), a['name'], ImageFont.truetype(FB, 120), a['c'])
    shadow_text(im, (W / 2, 860), s.get('head', a['tag']), ImageFont.truetype(FM, 50), (255, 255, 255))
    f = ImageFont.truetype(FB, 56); tw = d.textlength(a['url'], font=f)
    d.rounded_rectangle([(W - tw) / 2 - 40, 990, (W + tw) / 2 + 40, 1090], radius=50, fill=(255, 196, 92))
    d.text((W / 2, 1040), a['url'], font=f, fill=(40, 22, 8), anchor='mm')
    shadow_text(im, (W / 2, 1160), s.get('sub', 'Free  ·  No sign-up  ·  Link in bio'), ImageFont.truetype(FM, 42), (230, 230, 240))
    shadow_text(im, (W / 2, 1240), 'by Telar Labs', ImageFont.truetype(FM, 38), (200, 200, 215))
    im.save(path)

def segment(a, s, n, tag):
    wav = f'{WORK}{tag}-v{n}.wav'; L = say(s['say'], wav, s.get('speed', 1.05)) if s.get('say') else 0
    dur = round(max(s.get('min', 2.2), L + (1.4 if s.get('cta') else 0.55)), 2)
    png, out = f'{WORK}{tag}-f{n}.png', f'{WORK}{tag}-s{n}.mp4'
    aud = ['-i', wav] if L else ['-f', 'lavfi', '-t', str(dur), '-i', 'anullsrc=r=24000:cl=mono']
    afl = f'[A]adelay=200,apad,atrim=0:{dur},aformat=sample_rates=48000:channel_layouts=stereo[a]'
    if s.get('cta'):
        cta_png(a, s, png)
        fc = (f"[0:v]scale=1188:2112,zoompan=z='min(1.0+0.0006*on,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},trim=duration={dur},format=yuv420p[v];"
              + afl.replace('[A]', '[1:a]'))
        run(['-loop', '1', '-framerate', str(FPS), '-t', str(dur), '-i', png, *aud, '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
             '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k', '-t', str(dur), out])
        return out
    src = RAW + s['clip'] + '.mp4'; sw, sh = dims(src); kind = s.get('kind') or ('phone' if sw < 500 else 'tall' if sh > sw else 'land')
    crop = ''
    if s.get('crop'):  # e.g. 1.2 = crop the landscape clip to a 6:5 frame, centred (or at cx)
        cw0 = round(sh * s['crop']); cx0 = s.get('cx', (sw - cw0) // 2); crop = f'crop={cw0}:{sh}:{cx0}:0,'; sw = cw0; kind = 'big'
    box = layout(kind, sw, sh); x, y, cw, ch, r = box; frame_png(a, s, kind, box, png)
    sp = s.get('speed_v', 1.0); st = s.get('start', 0)
    fc = (f"[1:v]setpts=(PTS-STARTPTS)/{sp},fps={FPS},{crop}scale={cw}:{ch}:flags=lanczos,tpad=stop_mode=clone:stop_duration=60,trim=duration={dur},format=rgba[c];"
          f"[2:v]format=gray[m];[c][m]alphamerge[cr];[0:v][cr]overlay={x}:{y}:shortest=1,format=yuv420p[v];" + afl.replace('[A]', '[3:a]'))
    run(['-loop', '1', '-t', str(dur), '-i', png, '-ss', str(st), '-i', src, '-loop', '1', '-t', str(dur), '-i', png + '.mask.png', *aud,
         '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-r', str(FPS), '-c:v', 'libx264', '-crf', '19', '-preset', 'medium',
         '-c:a', 'aac', '-b:a', '160k', '-t', str(dur), out])
    return out

def build(key, app, segs):
    a = APPS[app]; parts = [segment(a, s, i + 1, key) for i, s in enumerate(segs)]
    lst = f'{WORK}{key}.txt'; open(lst, 'w').writelines(f"file '{p}'\n" for p in parts)
    final = f'{OUT}promo-{key}.mp4'
    run(['-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000',
         '-shortest', '-movflags', '+faststart', final])
    print('done', final, round(dur_of(final), 1), 's', flush=True)

PP_SITE = 'pizarra pad dot Telar Labs dot net'
VIDEOS = {
 'pizarrapad-1-no-smartboard': ('pp', [
   dict(clip='pp_b', head='No smartboard?\nNo problem.', say='No smartboard in your classroom? No problem.'),
   dict(clip='pp_a', head='Turn any TV or projector into a whiteboard', say='PizarraPad turns any TV or projector into a free whiteboard.'),
   dict(clip='pp_c', head='Whiteboard, blackboard or greenboard', say='Write with a finger, stylus or mouse, on a white, black or green board.'),
   dict(clip='pp_f', head='Pens, shapes, text, pictures & a laser pointer', say='Add shapes, text and pictures, and point with the laser.'),
   dict(cta=True, head='Free online whiteboard for teachers', sub='No sign-up  ·  Works offline  ·  Link in bio',
        say=f"Free, no sign-up, and it works offline. {PP_SITE}."),
 ]),
 'pizarrapad-2-online-class': ('pp', [
   dict(clip='pp_d', head='Teaching online?', say='Teaching online, or tutoring from home?'),
   dict(clip='pp_c', head='Share it in Zoom or Google Meet', say='Open PizarraPad and share your screen in Zoom or Google Meet. Your students see a real blackboard.'),
   dict(clip='pp_d', head='Grid and lined paper', say='Use grid paper for math, and lined paper for writing practice.'),
   dict(clip='pp_e', start=4.0, head='Save each page as a picture', say='Then save each page as a picture, and send it to your class.'),
   dict(cta=True, head='Free online blackboard & greenboard', sub='No sign-up  ·  English, Español, 中文  ·  Link in bio',
        say=f"Free, no sign-up, at {PP_SITE}."),
 ]),
 'quizpolice-1-who-left-the-quiz': ('qp', [
   dict(clip='qp_b', head='Online quiz… or open-book quiz?', say='Giving quizzes on Google Forms? Who is searching for the answers?'),
   dict(clip='qp_c', head='See who leaves the quiz tab, live', say='QuizPolice shows you, live, who leaves the quiz tab, and for how long.'),
   dict(clip='qp_d', start=1.6, head='Students get a warning every time', say='Students see a warning every time they leave the quiz.'),
   dict(clip='qp_e', head='3 exits? The quiz locks until you unlock it', say='After three exits, the quiz locks until you unlock it.'),
   dict(cta=True, head='Free quiz monitoring', sub='Google Forms  ·  Microsoft Forms  ·  Wayground',
        say='Free for Google and Microsoft Forms. Quiz Police dot Telar Labs dot net.'),
 ]),
 'quizpolice-2-how-it-works': ('qp', [
   dict(clip='qp_a', pill='Step 1', head='Paste your quiz link', say='Monitor a quiz in one minute. Step one: paste your Google Forms link.'),
   dict(clip='qp_a', start=5.5, pill='Step 2', head='Share the code or QR code', say='Step two: share the code, or the QR code, with your class.'),
   dict(clip='qp_b', pill='Step 3', head='Students join on any phone', say='Step three: students join on any phone or laptop. No accounts needed.'),
   dict(clip='qp_c', head='Watch your class live', say='Then watch your class live, and download the results.'),
   dict(cta=True, head='Free quiz monitoring', sub='No student accounts  ·  Link in bio', say='Try it free at Quiz Police dot Telar Labs dot net.'),
 ]),
 'drafttrail-1-did-ai-write-this': ('dt', [
   dict(clip='dt_b', head='Did AI write this essay?', say='Wondering if an essay was copied, or written by AI?'),
   dict(clip='dt_a', speed_v=3.0, head='Students write in DraftTrail', say='With DraftTrail, students write on a page that records how they write.'),
   dict(clip='dt_b', head='Big pastes get flagged', say='Big pastes and essays with no editing get flagged for you to check.'),
   dict(clip='dt_c', start=4.5, head='Replay how it was written', say='You can even replay the whole essay, with the pasted parts highlighted.'),
   dict(cta=True, head='Free writing-process recorder', sub='Nothing is uploaded  ·  Link in bio', say="It's free, and nothing is uploaded. Draft Trail dot Telar Labs dot net."),
 ]),
 'drafttrail-2-prove-its-yours': ('dt', [
   dict(clip='dt_a', head='Students: show your work is really yours', say='Students, worried your essay will be mistaken for AI?'),
   dict(clip='dt_a', start=6, speed_v=3.0, head='Write in DraftTrail', say='Write it in DraftTrail. It records your typing and corrections, on your device.'),
   dict(clip='dt_a', start=41, head='Hand in your DraftTrail file', say='Then hand in your DraftTrail file with your essay.'),
   dict(clip='dt_d', head='Your teacher sees your real process', say='Your teacher sees your real writing process. No flags. Just your work.'),
   dict(cta=True, head='Free writing-process recorder', sub='Nothing is uploaded  ·  Link in bio', say='Free at Draft Trail dot Telar Labs dot net.'),
 ]),
}
VIDEOS['telar-stories-trailer'] = ('ts', [
   dict(clip='st_mira', pill='Coming soon', head='Make your own story videos', say='Coming soon from Telar Labs: Telar Stories.'),
   dict(clip='ts_all', start=3.7, speed_v=1.7, head='Pick a scene and characters', say='Pick a scene, add characters, and move them anywhere.'),
   dict(clip='ts_all', start=11.9, speed_v=1.25, head='Type your story. A free AI voice reads it.', say='Type your story, and a friendly AI voice reads it aloud.'),
   dict(clip='st_sheep', start=0.5, head='Bible stories, lessons & bedtime tales', say='Perfect for Sunday school, classrooms and bedtime.'),
   dict(clip='ts_all', start=45.9, head='Download your video', say='Then download your video, and share it.'),
   dict(cta=True, head='Coming soon', sub='Free  ·  Follow for updates',
        say="Telar Stories. Free, and coming soon. Follow us so you don't miss it!"),
])

VIDEOS['telar-stories-teaser-2'] = ('ts', [
   dict(clip='st2_star', crop=1.2, pill='Coming soon', head='Story videos for kids, ready to play', say='Story time is coming to Telar Labs!'),
   dict(clip='st2_angel', crop=1.2, head='Bible stories', say='Bible stories, like The First Christmas.'),
   dict(clip='st2_gift', crop=1.2, cx=170, head='Stories about kindness', say='Kindness stories, like The Christmas Gift.'),
   dict(clip='st2_sheep', crop=1.2, head='Lessons kids remember', say='And lessons kids remember, like The Lost Sheep.'),
   dict(clip='st2_mira', crop=1.2, cx=360, head='Every story has a voice', say='Every story comes with a friendly voice. Just press play!'),
   dict(cta=True, head='Coming soon', sub='Free  ·  Follow for updates', say="Telar Stories. Free, and coming soon. Follow us so you don't miss it!"),
])

VIDEOS['telar-stories-teaser-3'] = ('ts', [
   dict(clip='st3_animals', crop=1.5, pill='New stories', head='Two by two, into the ark!', say='New stories are coming to Telar Stories!'),
   dict(clip='st3_dove', crop=1.2, cx=0, head="Noah's Ark", say="Like Noah's Ark, with animals, a dove, and a rainbow promise."),
   dict(clip='st3_pierogi', crop=1.2, cx=0, head='Friends Around the World', say='And Friends Around the World, where kids say hello in their own language.'),
   dict(clip='st3_lunch', crop=1.2, head='Kindness, sharing & cultures', say='Stories about kindness, sharing, and new friends.'),
   dict(clip='st3_hands', crop=1.2, head='Ready to play, with a friendly voice', say='Each one is ready to play, with a friendly voice.'),
   dict(cta=True, head='Coming soon', sub='Free  ·  Follow for updates', say="Telar Stories. Free, and coming soon. Follow us so you don't miss it!"),
])

VIDEOS['drafttrail-3-live-in-class'] = ('dt', [
   dict(clip='dt3_setup', pill='New', head='Live in-class writing', say='Essays written in class? Now you can watch the writing live.'),
   dict(clip='dt3_student', head='Students join with a code', say='Students join with a code and write in DraftTrail.'),
   dict(clip='dt3_dashc', start=2.8, head='See exits and pastes as they happen', say='You see who leaves the page, and who pastes text, as it happens.'),
   dict(clip='dt3_timeup', start=3.0, head="Time's up? Essays are handed in", say="When time's up, every essay is handed in automatically."),
   dict(clip='dt3_review', start=1.2, head='Replay how each was written', say='Then replay how each one was written.'),
   dict(cta=True, head='Free writing-process recorder', sub='Homework or live in class  ·  Link in bio', say='Free at Draft Trail dot Telar Labs dot net.'),
])

VIDEOS['drafttrail-4-term-papers'] = ('dt', [
   dict(clip='dt4_setup', pill='New', head='Term papers & case studies', say='Term papers and case studies? DraftTrail does those now.'),
   dict(clip='dt4_cite', start=0.3, head='Cite in one click', say='Cite in one click, in Chicago, A-P-A, or MLA.'),
   dict(clip='dt4_quote', start=0.6, head='Pasted quotes get cited', say='Pasted quotes get quotation marks and a citation.'),
   dict(clip='dt4_preview', start=0.8, head='Real footnotes & bibliography', say='Download it in Word, with real footnotes.'),
   dict(clip='dt4_review', head='See every writing session', say='And teachers see every writing session.'),
   dict(cta=True, head='Free writing-process recorder', sub='Essays · Term papers · Case studies', say='Free at Draft Trail dot Telar Labs dot net.'),
])

VIDEOS['telar-stories-simple'] = ('ts', [
   dict(clip='st_mira', pill='Coming soon', head='Simple story videos. No editing skills.', say='Want to share a story, without learning video editing?'),
   dict(clip='ts_all', start=3.7, speed_v=1.7, head='Pick a picture. Add characters.', say='Pick a picture, and add your characters.'),
   dict(clip='ts_all', start=11.9, speed_v=1.25, head='Type a line. A voice reads it.', say='Type a line, and a friendly voice reads it.'),
   dict(clip='st_sheep', start=0.5, head='Like a picture book that talks', say='Like a picture book that talks. Gentle movement, not big animation.'),
   dict(clip='ts_all', start=45.9, head='Make your video in one click', say='Then make your video in one click.'),
   dict(cta=True, head='Simple storytelling, made easy', sub='Free  ·  Coming soon  ·  Follow for updates', say='Telar Stories. Simple, free, and coming soon.'),
])

VIDEOS['telar-labs-for-creators'] = ('tl', [
   dict(clip='rb_ex', kind='phone', pill='For creators', head='Free tools for your TikToks & Reels', say='Making TikToks or Reels? Here are two free tools.'),
   dict(clip='tc_pick', head='Telar Clips: backgrounds & green screens', say='Telar Clips has free moving backgrounds and green screens.'),
   dict(clip='year_ex', kind='phone', head='Mix them into your own videos', say='Mix them into your own creations.'),
   dict(clip='ts_all', start=11.9, speed_v=1.25, pill='Coming soon', head='Telar Stories: type it, hear it', say='And Telar Stories turns your words into a narrated story video.'),
   dict(clip='st_mira', head='No pro editing needed', say='No pro editing needed.'),
   dict(cta=True, head='Free tools for creators', sub='Telar Clips  ·  Telar Stories (coming soon)', say='Find them free at Telar Labs dot net.'),
])

VIDEOS['drafttrail-5-full'] = ('dt', [
   dict(clip='dt_b', pill='Free for teachers', head='Did AI write this essay?', say='Wondering if an essay was copied, or written by AI?'),
   dict(clip='dt_a', speed_v=3.0, head='Students write in DraftTrail', say='DraftTrail records every pause and edit as students write.'),
   dict(clip='dt_b', head='Big pastes get flagged', say='Big pastes and no-edit essays get flagged.'),
   dict(clip='dt3_dashc', start=2.8, head='See who leaves the page', say='In class, see who leaves the page, and who pastes, as it happens.'),
   dict(clip='dt_c', start=4.5, head='Replay how it was written', say='Replay any essay, with pasted parts highlighted.'),
   dict(clip='dt4_cite', start=0.3, pill='New', head='Term papers, with citations', say='New: term papers, with citations in Chicago, A-P-A, or MLA.'),
   dict(clip='dt4_quote', start=0.6, head='Cited quotes vs. real copying', say='Cited quotes are marked, so real copying stands out.'),
   dict(clip='dt4_review', head='Every writing session, over days', say='You see every writing session, even over weeks.'),
   dict(cta=True, head='Free writing-process recorder', sub='No sign-up  ·  Nothing uploaded  ·  Link in bio', say='Try it free, at Draft Trail dot Telar Labs dot net.'),
])

VIDEOS['drafttrail-4-term-papers-long'] = ('dt', [
   dict(clip='dt4_setup', pill='New', head='Term papers & case studies', say='Assigning a term paper or a case study? DraftTrail can handle it now.'),
   dict(clip='dt4_setup', start=1.5, head='Set the style, word goal & sections', say='Choose the citation style, a word goal, and the sections.'),
   dict(clip='dt4_cite', start=0.3, head='Cite in one click', say='Students cite in one click, in Chicago, A-P-A, or MLA.'),
   dict(clip='dt4_quote', start=0.6, head='Pasted quotes get cited', say='Pasted quotes get quotation marks and a citation.'),
   dict(clip='dt_b', head='Uncited pastes are still flagged', say='But pasted text with no source is still flagged for you.'),
   dict(clip='dt4_preview', start=0.8, head='Real footnotes & bibliography', say='Papers download in Word, with real footnotes.'),
   dict(clip='dt4_review', head='Every writing session, over days', say='And you see every writing session, even over weeks.'),
   dict(cta=True, head='Free writing-process recorder', sub='Essays · Term papers · Case studies', say='Free at Draft Trail dot Telar Labs dot net.'),
])

VIDEOS['telar-clips-how-to'] = ('tc', [
   dict(clip='tc_home', pill='Free', head='Moving backgrounds in 3 easy steps', say="Need a moving background for your video? Here's how, for free."),
   dict(clip='tc_pick', pill='Step 1', head='Pick a clip', say='Step one: pick a clip on Telar Clips.'),
   dict(clip='tc_dl', pill='Step 2', head='Download it free', say='Step two: download it. No sign-up needed.'),
   dict(clip='ex_bday', kind='phone', pill='Step 3', head='Add your text', say='Step three: add your text in CapCut or Canva.'),
   dict(clip='ex_xmas', kind='phone', head='Or use a green screen effect', say='Or add a green screen effect over your own video.'),
   dict(cta=True, head='Free backgrounds & green screens', sub='No sign-up  ·  Link in bio', say='Free at clips dot Telar Labs dot net.'),
])

VIDEOS['tixward-tickets'] = ('tx', [
   dict(clip='tx_event', start=1.0, speed_v=1.35, pill='Free for most events', head='Sell tickets. Get paid directly.', say='Selling tickets to your event? With Tixward, buyers pay you directly.'),
   dict(clip='tx_cur', start=0.2, head='Price it in your own currency', say='Price tickets in your own currency: dollars, euros, rupiah, yuan, pesos, and more.'),
   dict(clip='tx_pay', start=1.2, speed_v=1.5, head='They pay your e-wallet or bank QR', say='Buyers pay your e-wallet or bank QR, and send the receipt.'),
   dict(clip='tx_approve', crop=1.25, cx=150, start=0.8, head='You check it. Tap Approve.', say='You check it, and tap Approve.'),
   dict(clip='tx_ticket', head='They get a QR ticket', say='They get a QR ticket on their phone.'),
   dict(clip='tx_door', start=1.3, speed_v=1.5, head='Scan it at the door', say='Scan it at the door, with any phone.'),
   dict(clip='tx_shows', start=0.5, pill='Film showings', head='Several screenings & places', say='Showing a film? Add several screenings and places, each with its own seats.'),
   dict(cta=True, head='Event tickets, paid directly to you', sub='Promo rates until May 31, 2027  ·  Link in bio', say='Tixward. Free for most events. Promo rates end May thirty-first, so start early.'),
])

VIDEOS['tixward-bookings'] = ('tx', [
   dict(clip='bk_page', start=0.6, speed_v=1.2, pill='Free to use', head='Bookings for courts & rooms', say='Renting out courts, rooms, or a studio? Take bookings with Tixward, for free.'),
   dict(clip='bk_pick', start=0.3, head='Pick a time, and how long', say='Customers pick a court, a time, and how long.'),
   dict(clip='bk_custom', start=0.3, pill='Your own time slots', head='Equal slots, or your own', say='Use equal slots, or set your own, like eight to nine, or ten to twelve.'),
   dict(clip='bk_book', start=0.5, speed_v=1.3, head='Pay now, or pay on-site', say='They pay when they book, or on-site.'),
   dict(clip='bk_sched', crop=1.25, cx=170, start=0.6, head='Your schedule. No double bookings.', say='You see every booking, add walk-ins, and never double-book.'),
   dict(clip='bk_block', crop=1.25, cx=170, start=0.5, speed_v=1.3, head='Block times for maintenance', say='Block times for maintenance, and set days off.'),
   dict(clip='bk_desk', start=0.6, head='Front desk check-in', say="At the front desk, staff see today's bookings and collect on-site payments."),
   dict(cta=True, head='Free bookings for courts, rooms & more', sub='No Tixward fees  ·  Link in bio', say='Tixward bookings. Free to use, with no Tixward fees.'),
])

VIDEOS['tixward-conferences'] = ('tx', [
   dict(clip='cf_event', start=0.0, pill='Conferences · Workshops · Trainings', head='Tickets for your next conference', say='Running a conference, workshop, or training? Try Tixward.'),
   dict(clip='cf_event', start=2.2, head='Early bird, regular & student', say='Offer early bird, regular, and student tickets.'),
   dict(clip='cf_q', start=0.4, pill='Your own questions', head='Ask their teacher & section', say="Ask each attendee their teacher and section, so you know who's coming."),
   dict(clip='cf_sessions', start=0.3, head='Sessions with limited seats', say='Run sessions in different rooms, each with limited seats.'),
   dict(clip='cf_list', crop=1.0, cx=170, start=0.3, head='Attendee list for name tags & certificates', say='Download your attendee list for name tags and certificates.'),
   dict(clip='cf_sheet', crop=1.0, cx=240, start=1.4, pill='Print-ready', head='Sign-in sheets, one page per teacher', say='Print sign-in sheets for the registration desk, with one page per teacher.'),
   dict(clip='cf_desk', start=1.2, speed_v=1.4, head='Quick check-in at registration', say='Then check everyone in, on any phone.'),
   dict(cta=True, head='Tickets for conferences & trainings', sub='Promo rates until May 31, 2027  ·  Link in bio', say='Tixward. Free for most events, with promo rates until May thirty-first.'),
])

VIDEOS['tixward-funrun'] = ('tx', [
   dict(clip='fr_event', start=0.0, pill='Fun runs · Charity runs · Races', head='Race slots for your fun run', say='Organizing a fun run? Sell race slots with Tixward, and runners pay you directly.'),
   dict(clip='fr_event', start=2.4, head='Kids 1K, 3K, 5K & 10K', say='Offer kids, 3K, 5K, and 10K categories.'),
   dict(clip='fr_q', start=0.3, pill='Your own questions', head='Ask shirt size & emergency contact', say='Ask each runner their shirt size and emergency contact.'),
   dict(clip='fr_list', crop=1.0, cx=10, start=0.3, head='Count shirts by size', say='See how many shirts to order in each size, at a glance.'),
   dict(clip='fr_sheet', crop=1.0, cx=270, start=1.4, pill='Print-ready', head='Race kit claim sheets by size', say='Print race kit claim sheets, one page per shirt size.'),
   dict(clip='fr_desk', start=1.2, speed_v=1.4, head='Race-day check-in on any phone', say='On race day, check runners in at the start line, on any phone.'),
   dict(cta=True, head='Tickets for fun runs & races', sub='Promo rates until May 31, 2027  ·  Link in bio', say='Tixward. Free for most events, with promo rates until May thirty-first.'),
])

VIDEOS['tixward-small'] = ('tx', [
   dict(clip='sm_chat', start=0.3, pill='Small events · 20 to 60 people', head='Still using a form and a group chat?', say="Still running a small event with a form and a group chat? Who has paid, which screenshot is whose, and is it full yet?"),
   dict(clip='sm_left', start=0.3, pill='Paid · 40 seats', head='Sales stop at your limit', say="With Tixward, set forty seats. When they're gone, sales stop on their own."),
   dict(clip='sm_approve', start=0.5, head='Approve payments in one tap', say='Approve each payment in one tap, and buyers get their QR tickets.'),
   dict(clip='sm_free', start=0.3, pill='Free · 60 seats', head='Free events, never overbooked', say='A free seminar for parents? Sign-ups stop at sixty, and everyone gets a ticket on their phone.'),
   dict(clip='sm_door', start=0.6, head='Easy check-in on any phone', say="At the door, scan tickets on any phone and see exactly who's in."),
   dict(cta=True, head='Tickets for small events', sub='Free for small events  ·  Link in bio', say='Tixward. Free for small events, and free events are always free.'),
])



if __name__ == '__main__':
    for k, (app, segs) in VIDEOS.items():
        if len(sys.argv) < 2 or any(x in k for x in sys.argv[1:]): build(k, app, segs)

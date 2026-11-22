"""Original diagrams for the telarlabs.net guides, drawn as HTML and screenshotted."""
import os, subprocess, json
OUT = '/home/claude/shots/guides/'
D = '/home/claude/shots/diag/'; os.makedirs(D, exist_ok=True)
CSS = """@font-face{font-family:P;src:url(file:///usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf)}
@font-face{font-family:P;font-weight:600;src:url(file:///usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf)}
@font-face{font-family:P;font-weight:800;src:url(file:///usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf)}
*{box-sizing:border-box}body{margin:0;background:#1f1b27;color:#f4f1f8;font:18px/1.45 P,sans-serif;width:1200px}
.card{padding:44px 48px}h1{font-size:30px;margin:0 0 6px;font-weight:800}.sub{color:#a8a1b1;margin:0 0 28px;font-size:17px}
.acc{color:#ffb547}.mut{color:#a8a1b1}.row{display:flex;gap:22px}.box{background:#16131c;border:2px solid #2e2936;border-radius:16px;padding:22px 24px}
.tag{display:inline-block;padding:3px 12px;border-radius:999px;font-size:14px;font-weight:600}
.foot{margin-top:26px;color:#a8a1b1;font-size:15px}"""
def page(name, body, h=None):
    f = D + name + '.html'
    open(f, 'w').write(f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><body><div class="card" id="c">{body}</div>')
    return name

pages = []
# ---------- Google Forms settings checklist
rows = [('Settings → Make this a quiz', 'On', 'Unlocks answer keys and grade release'),
        ('Release grades', 'Later, after manual review', 'Nobody sees answers until everyone is done'),
        ('Limit to 1 response', 'On', 'Needs students to sign in with Google'),
        ('Shuffle question order', 'On', 'Found under Presentation'),
        ('Shuffle option order', 'On, per question', 'In each question’s three-dot menu'),
        ('Locked mode', 'If you have managed Chromebooks', 'Blocks other tabs until submitting'),
        ('Accepting responses', 'Off after the quiz', 'Stops late answers once answers are shared')]
tr = ''.join(f'<tr><td><b>{a}</b><div class="mut" style="font-size:15px">{c}</div></td><td><span class="tag" style="background:#2a3a24;color:#b9f0a0">{b}</span></td></tr>' for a, b, c in rows)
pages.append(page('d-gforms-checklist', f'''<h1>Google Forms quiz: the settings checklist</h1><p class="sub">Most of these are off by default. Turn them on before you share the link.</p>
<style>table{{width:100%;border-collapse:collapse}}td{{padding:14px 10px;border-top:1px solid #2e2936;vertical-align:top}}td:last-child{{text-align:right;white-space:nowrap}}</style>
<table>{tr}</table><div class="foot">Telar Labs guide · Menu names may change slightly as Google updates Forms.</div>'''))
# ---------- Offline tools
col = lambda title, color, sub, items: f'<div class="box" style="flex:1;border-color:{color}"><div class="tag" style="background:{color};color:#16131c">{title}</div><p class="mut" style="margin:12px 0 10px;font-size:16px">{sub}</p>' + ''.join(f'<div style="padding:7px 0;border-top:1px solid #2e2936">{i}</div>' for i in items) + '</div>'
pages.append(page('d-offline-tools', f'''<h1>Which classroom tools still work without internet?</h1><p class="sub">Test each one at home with Wi-Fi turned off.</p>
<div class="row">{col('Fully online', '#ff8a7a', 'Stop when the connection drops', ['Video streaming', 'Live online quizzes', 'Shared cloud documents', 'Most AI tools'])}
{col('Offline after first visit', '#ffb547', 'Open once while online, then they keep working', ['Some web apps, like PizarraPad', 'Board pages saved on your device', 'Apps installed from the browser'])}
{col('Fully offline', '#8fe08a', 'Files saved on your laptop or phone', ['Downloaded videos (where allowed)', 'Slides saved as PDF', 'Worksheets and pictures'])}</div>
<div class="foot">Telar Labs guide · Teaching when the Wi-Fi drops</div>'''))
# ---------- Video shapes
def frame(w, h, label, size, uses, color):
    return f'''<div style="display:flex;flex-direction:column;align-items:center;gap:12px;flex:1"><div style="width:{w}px;height:{h}px;border:3px solid {color};border-radius:14px;display:grid;place-items:center;background:#16131c">
<div style="text-align:center"><div style="font-size:30px;font-weight:800;color:{color}">{label}</div><div class="mut" style="font-size:15px">{size}</div></div></div><div style="text-align:center;font-size:16px;max-width:300px">{uses}</div></div>'''
pages.append(page('d-video-shapes', f'''<h1>The three video shapes you need</h1><p class="sub">Drawn to scale. Pick the shape before you film.</p>
<div class="row" style="align-items:flex-end">{frame(180, 320, '9:16', '1080 × 1920', 'TikTok, Instagram Reels, YouTube Shorts, Facebook Reels and Stories', '#ffb547')}
{frame(400, 225, '16:9', '1920 × 1080', 'YouTube videos, projectors, TVs, presentations', '#7fb2ff')}
{frame(220, 220, '1:1', '1080 × 1080', 'Square posts in Instagram and Facebook feeds', '#8fe08a')}
{frame(200, 250, '4:5', '1080 × 1350', 'Taller feed posts that fill more of a phone screen', '#d79bff')}</div>
<div class="foot">Telar Labs guide · Platforms change their recommendations from time to time.</div>'''))
# ---------- Safe zones on a 9:16 frame (scaled 1080x1920 -> 270x480)
s = .25
pages.append(page('d-safe-zones', f'''<div class="row" style="align-items:center;gap:56px"><div style="position:relative;width:{1080*s}px;height:{1920*s}px;border:3px solid #ffb547;border-radius:18px;background:#16131c;overflow:hidden;flex:none">
<div style="position:absolute;left:0;right:0;top:0;height:{200*s}px;background:rgba(255,120,110,.28)"></div>
<div style="position:absolute;left:0;right:0;bottom:0;height:{380*s}px;background:rgba(255,120,110,.28)"></div>
<div style="position:absolute;right:0;top:{200*s}px;bottom:{380*s}px;width:{150*s}px;background:rgba(255,120,110,.28)"></div>
<div style="position:absolute;left:{40*s}px;right:{190*s}px;top:{640*s}px;height:{640*s}px;border:2px dashed #8fe08a;border-radius:10px;display:grid;place-items:center;text-align:center;color:#8fe08a;font-weight:800;font-size:17px">Titles, prices,<br>dates and links<br>go here</div>
</div><div style="max-width:620px"><h1>Safe zones on vertical video</h1><p class="sub">The app draws its own buttons and text over your video. Rough guide for a 1080 × 1920 video:</p>
<div style="padding:9px 0;border-top:1px solid #2e2936"><b class="acc">Top ~200 px:</b> status bar and app header</div>
<div style="padding:9px 0;border-top:1px solid #2e2936"><b class="acc">Bottom ~350–400 px:</b> caption, account name and music</div>
<div style="padding:9px 0;border-top:1px solid #2e2936"><b class="acc">Right ~150 px:</b> like, comment and share buttons</div>
<div style="padding:9px 0;border-top:1px solid #2e2936"><b style="color:#8fe08a">Middle third:</b> the safe place for anything people must read</div>
<div class="foot">Telar Labs guide · Check by watching a test export inside the app.</div></div></div>'''))
# ---------- Recap storyboard
shots = [('0–5 s', 'Title', 'Event name and date over a looping background or your best wide shot'), ('5–15 s', 'The setting', 'Venue sign, decorations, people arriving'),
         ('15–35 s', 'Main moments', 'Opening, performances, the speaker, awards'), ('35–50 s', 'Reactions', 'Applause, laughter, families filming'), ('50–60 s', 'Thank you', 'Group photo, volunteers, next event date')]
cards = ''.join(f'<div class="box" style="flex:1;padding:16px"><div style="height:110px;border-radius:10px;background:linear-gradient(135deg,#2e2650,#4a2b3a);display:grid;place-items:center;font-size:36px;font-weight:800;color:#ffb547">{i+1}</div><div class="acc" style="margin-top:12px;font-size:14px;font-weight:600">{t}</div><div style="font-weight:800">{a}</div><div class="mut" style="font-size:15px">{b}</div></div>' for i, (t, a, b) in enumerate(shots))
pages.append(page('d-recap-storyboard', f'<h1>A one-minute recap, shot by shot</h1><p class="sub">Plan these before the event, and give one or two people the list.</p><div class="row" style="gap:14px">{cards}</div><div class="foot">Telar Labs guide · Film 3–10 second clips; you will use only a second or two of most.</div>'))
# ---------- Reunion timeline
steps = [('4–6 months', 'Form a committee, pick a date, start finding classmates'), ('3 months', 'Budget, ticket price, book the venue'), ('2 months', 'Open registration and collect payments'),
         ('1 month', 'Reminders, program, old photos, name tags'), ('2 weeks', 'Close registration, final headcount, guest list'), ('The night', 'Welcome table, quick check-in, group photo'), ('After', 'Thank-yous, report, keep the contact list')]
tl = ''.join(f'<div style="flex:1;position:relative;padding-top:34px"><div style="position:absolute;top:6px;left:0;width:18px;height:18px;border-radius:50%;background:#ffb547;box-shadow:0 0 0 5px #3a2f1a"></div><div class="acc" style="font-weight:800;font-size:17px">{a}</div><div style="font-size:15px;padding-right:12px">{b}</div></div>' for a, b in steps)
pages.append(page('d-reunion-timeline', f'<h1>Reunion planning timeline</h1><p class="sub">Work backward from the date. Most of the work is finding people and collecting payments.</p><div style="position:relative"><div style="position:absolute;top:14px;left:9px;right:0;height:3px;background:#2e2936"></div><div class="row" style="gap:6px">{tl}</div></div><div class="foot">Telar Labs guide · Class reunion planning checklist</div>'))
# ---------- Projector setups
dev = lambda a, link, b, note: f'''<div class="box" style="flex:1"><div style="display:flex;align-items:center;gap:10px;font-weight:800;font-size:19px"><span>{a}</span><span class="acc" style="flex:1;text-align:center;font-size:14px;border-bottom:3px dashed #ffb547;padding-bottom:4px">{link}</span><span>{b}</span></div><p class="mut" style="margin:14px 0 0;font-size:15px">{note}</p></div>'''
pages.append(page('d-projector-setups', f'''<h1>Three ways to turn a screen into a whiteboard</h1><p class="sub">All you need is a screen the class can see, a device to write on, and a browser.</p>
<div class="row">{dev('Laptop', 'HDMI cable', 'Projector', 'Easiest. Press Windows + P and choose Duplicate. A cheap pen tablet makes handwriting easy.')}
{dev('Tablet', 'Cast / AirPlay', 'Smart TV', 'Walk around while you write. A stylus gives natural, pressure-sensitive lines.')}
{dev('Phone', 'USB-C to HDMI', 'Projector', 'No Wi-Fi needed. Many phones and tablets work with a simple adapter.')}</div>
<div class="foot">Telar Labs guide · Turn a projector or TV into a classroom whiteboard</div>'''))
json.dump(pages, open(D + 'pages.json', 'w'))
print(pages)

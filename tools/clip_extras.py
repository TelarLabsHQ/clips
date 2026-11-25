"""Extra, clip-specific content for each clip page: colors taken from the clip itself, text ideas that fit
its theme, a link to the other orientation, clips that pair well with it, and quick answers."""
import os, re, hashlib, colorsys, html
from PIL import Image

E = html.escape

def _h(s, salt=''):
    return int(hashlib.md5((salt + s).encode()).hexdigest(), 16)

# ------------------------------------------------------------ colors
def _hex(rgb): return '#%02X%02X%02X' % rgb
def _lum(rgb):
    r, g, b = [x / 255 for x in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

NAMES = [((0, 15), 'red'), ((15, 45), 'orange'), ((45, 66), 'gold'), ((66, 160), 'green'), ((160, 200), 'teal'),
         ((200, 255), 'blue'), ((255, 290), 'purple'), ((290, 335), 'pink'), ((335, 361), 'red')]
def color_name(rgb):
    h, l, s = colorsys.rgb_to_hls(*[x / 255 for x in rgb])
    if l < .1: return 'near black'
    if l > .9: return 'near white'
    if s < .15: return 'gray' if .25 < l < .75 else ('charcoal' if l <= .25 else 'pale gray')
    deg = h * 360
    n = next(name for (a, b), name in NAMES if a <= deg < b)
    if n in ('orange', 'red') and (l < .35 or (l < .45 and s < .5)) and not (n == 'red' and s > .6): n = 'brown'
    if n == 'gold' and s < .45 and l > .55: n = 'cream'
    return ('dark ' if l < .28 else 'light ' if l > .72 else '') + n

def palette(poster, skip_dark=False, skip_green=False):
    im = Image.open(poster).convert('RGB')
    if skip_dark:   # overlays: only the light parts count, and they are small, so look at the bright pixels of a larger copy
        big = im.copy(); big.thumbnail((640, 640))
        px = [p for p in big.getdata() if _lum(p) > .22]
        if len(px) > 50:
            src = Image.new('RGB', (len(px), 1)); src.putdata(px)
        else:
            src = big
        im.thumbnail((160, 160))
        q = src.quantize(colors=10, method=Image.Quantize.MEDIANCUT)
    else:
        im.thumbnail((160, 160)); q = None
    q = q or im.quantize(colors=10, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette(); counts = sorted(q.getcolors(), reverse=True)
    tot = sum(n for n, _ in counts); out = []
    for n, i in counts:
        rgb = tuple(pal[i * 3:i * 3 + 3])
        if skip_dark and _lum(rgb) < .07: continue
        if skip_green and rgb[1] > 120 and rgb[1] > rgb[0] * 1.6 and rgb[1] > rgb[2] * 1.3: continue
        if any(sum((a - b) ** 2 for a, b in zip(rgb, o[0])) < 900 for o in out): continue
        out.append((rgb, n / tot))
        if len(out) == 5: break
    return out, im

def _chroma(rgb): return (max(rgb) - min(rgb)) / 255

def accent(im, dark):
    """A highlight color that stands out on this clip: a vivid color from the clip, or a lighter/deeper shade of its main hue."""
    q = im.quantize(colors=16, method=Image.Quantize.MEDIANCUT); pal = q.getpalette()
    cols = [(n, tuple(pal[i * 3:i * 3 + 3])) for n, i in q.getcolors()]; tot = sum(n for n, _ in cols)
    ok = [(n, rgb) for n, rgb in cols if n / tot > .01 and _chroma(rgb) > .3 and ((_lum(rgb) > .45) if dark else (_lum(rgb) < .3))]
    if ok: return max(ok, key=lambda x: _chroma(x[1]) * (x[0] / tot) ** .3)[1], False
    n, rgb = max(cols, key=lambda x: _chroma(x[1]) * (x[0] / tot) ** .5)
    h, l, s = colorsys.rgb_to_hls(*[x / 255 for x in rgb])
    r = colorsys.hls_to_rgb(h, .72 if dark else .3, max(s, .55))
    return tuple(round(x * 255) for x in r), True

def tint(pal):
    """Main hue of an overlay's visible light."""
    vis = [(rgb, sh) for rgb, sh in pal if _lum(rgb) > .15] or pal
    rgb = max(vis, key=lambda p: (_chroma(p[0]) + .08) * _lum(p[0]) * p[1] ** .5)[0]
    n = color_name(rgb).replace('light ', '').replace('dark ', '')
    return ('warm orange' if n == 'brown' else n) if _chroma(rgb) > .15 else 'white'

def center_lum(im):
    w, h = im.size
    c = im.crop((w // 4, h // 3, 3 * w // 4, 2 * h // 3)).resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
    return _lum(c)

def colors_html(c, poster, k):
    if k == 'green' or not os.path.exists(poster): return ''
    pal, im = palette(poster, skip_dark=(k == 'overlay'))
    if not pal: return ''
    sw = ''.join(f'<button type="button" class="sw" data-hex="{_hex(rgb)}" title="Copy {_hex(rgb)}">'
                 f'<i style="background:{_hex(rgb)}"></i><b>{_hex(rgb)}</b><span>{color_name(rgb)}</span></button>' for rgb, _ in pal)
    if k == 'overlay':
        t = tint(pal)
        tip = ('These are the light colors in the overlay. Its light is close to white with only a slight tint, so it suits almost any footage.' if t == 'white' else
               f'These are the light colors in the overlay. On Screen blend they add a {t} glow to your footage, so it suits videos with {t} or neutral tones.')
    else:
        dark = center_lum(im) < .5
        vivid, made = accent(im, dark)
        src = (f'a {"lighter" if dark else "deeper"} shade of the clip’s own {color_name(vivid).replace("light ", "").replace("dark ", "")}'
               if made else 'taken from the clip itself')
        if dark:
            tip = (f'The middle of the frame is dark, so <b>white or cream text</b> (#FFF8EC) reads best. For one highlighted word, '
                   f'try <b>{_hex(vivid)}</b>, {src}.')
        else:
            tip = (f'The middle of the frame is fairly bright, so <b>dark text</b> (#1D1B24) or white text with a soft shadow reads best. '
                   f'For one highlighted word, try <b>{_hex(vivid)}</b>, {src}.')
    return (f'<h2>Colors in this clip</h2><p class="muted small">Taken from the clip. Tap a color to copy its code for your text, '
            f'thumbnail or slides.</p><div class="swatches">{sw}</div><p>{tip}</p>')

# ------------------------------------------------------------ text ideas
# (keywords, theme, ideas). The first theme whose keyword appears in the clip's id, title or tags wins.
THEMES = [
 (['countdown'], 'countdown', ['Countdown to 2027 starts now!', 'Ready? Here we go… Happy New Year!', 'Last seconds of 2026 with you',
   'See you on the other side of midnight', 'Thank you, 2026. Hello, 2027!', 'Put your countdown right before the big reveal']),
 (['lunar new year', 'chinese new year', 'seollal', 'lantern festival', 'yuanxiao', 'qipao'], 'lunar',
  ['Happy Lunar New Year!', 'Gong Xi Fa Cai! Wishing you a prosperous year', 'Health, luck and happiness in the Year of the Goat',
   'Happy Lantern Festival to you and your family', 'May your year be bright as a red lantern', 'New year, new blessings, same family']),
 (['parol', 'pasko', 'simbang gabi'], 'pasko', ['Maligayang Pasko at Manigong Bagong Taon!', 'Merry Christmas from our family to yours',
   'Simbang Gabi starts tonight. See you there!', 'Ang Pasko ay pagmamahalan', 'Our Christmas program starts at 6 PM',
   'Light up Christmas with love']),
 (['christmas', 'snow globe', 'ornament', 'gift boxes'], 'christmas', ['Merry Christmas and a happy New Year!', 'Wishing you a warm and joyful Christmas',
   'Join us for our Christmas program', 'Christmas sale: up to 30% off this week', 'Peace on earth, joy at home', 'From our home to yours, Merry Christmas',
   'Thank you for a wonderful year. Merry Christmas!', 'Gift exchange this Friday! Bring a $10 gift']),
 (['new year', '2027', 'champagne', 'fireworks'], 'newyear', ['Happy New Year 2027!', 'Cheers to new beginnings', 'Thank you for an amazing 2026',
   'New year, new goals. Let’s go!', 'Wishing you a year full of good news', 'Our New Year’s Eve party starts at 9 PM']),
 (['indian wedding', 'mehndi', 'toran', 'haldi'], 'indianwedding', ['Together with our families, we invite you to celebrate our wedding',
   'Mehndi night: Friday, 7 PM', 'Save the date', 'Haldi ceremony this Saturday morning', 'Two families, one celebration', 'Shubh Vivah']),
 (['diwali', 'deepavali', 'rangoli', 'pongal'], 'diwali', ['Happy Diwali!', 'Shubh Deepavali to you and your family', 'May the festival of lights brighten your home',
   'Light, joy and sweets. Happy Diwali!', 'Diwali sale this weekend', 'Wishing you prosperity this Diwali']),
 (['ramadan', 'eid'], 'ramadan', ['Ramadan Kareem', 'Eid Mubarak to you and your family', 'Wishing you a blessed Ramadan',
   'Iftar together this Friday', 'May this Eid bring peace and joy', 'Ramadan Mubarak from all of us']),
 (['hanukkah', 'chanukah'], 'hanukkah', ['Happy Hanukkah!', 'Chag Sameach!', 'Eight nights of light and love', 'Wishing you a bright Festival of Lights',
   'Join us for our menorah lighting', 'Light one more candle tonight']),
 (['valentine', 'hearts', 'rose petals'], 'valentine', ['Happy Valentine’s Day', 'You make every day brighter', 'Happy Hearts Day, friends!',
   'Valentine’s special: book a table for two', 'Love, always', 'To my favorite person']),
 (['wedding', 'anniversary', 'rose gold', 'debut'], 'wedding', ['Save the date', 'Happy anniversary to the best couple', 'Forever starts today',
   'Join us as we celebrate love', 'Happy 18th birthday!', 'Thank you for celebrating with us']),
 (["st. patrick", 'irish', 'ireland', 'shamrock', 'pot of gold'], 'patrick', ['Happy St. Patrick’s Day!', 'Sláinte!', 'Wishing you the luck of the Irish',
   'Green is our color today', 'St. Patrick’s Day party starts at 6 PM', 'May luck follow you all year']),
 (['easter'], 'easter', ['Happy Easter!', 'He is risen!', 'Easter egg hunt this Sunday at 10 AM', 'Wishing you hope and joy this Easter',
   'Join us for Easter Sunday service', 'Spring blessings to you and your family']),
 (['halloween'], 'halloween', ['Happy Halloween!', 'Trick or treat!', 'Costume party this Friday', 'Spooky season is here', 'Enter if you dare…',
   'Treats for everyone who visits our booth']),
 (['fourth of july', 'red white and blue'], 'july4', ['Happy Fourth of July!', 'Happy Independence Day', 'Fireworks at the park tonight at 9 PM',
   'Land of the free, home of the brave', 'Fourth of July sale all weekend', 'Celebrate with family and friends']),
 (['republic day', 'saffron white green'], 'india', ['Happy Republic Day!', 'Happy Independence Day, India', 'Jai Hind', 'Proud of our roots',
   'Celebrating unity in diversity', 'Our school’s flag ceremony starts at 8 AM']),
 (['holi'], 'holi', ['Happy Holi!', 'Bura na mano, Holi hai!', 'Wishing you a colorful Holi', 'Play safe, play with colors', 'Holi party this Saturday',
   'Spread colors, spread joy']),
 (['nowruz'], 'nowruz', ['Nowruz Mobarak!', 'Happy Persian New Year', 'A fresh start this spring', 'Wishing you a happy Nowruz', 'New day, new year',
   'Spring has arrived']),
 (['yalda'], 'yalda', ['Happy Yalda Night!', 'Shab-e Yalda Mobarak', 'On the longest night, we gather', 'Pomegranates, poems and family',
   'Warm wishes on the longest night', 'Light returns tomorrow']),
 (['chuseok', 'mid-autumn'], 'chuseok', ['Happy Chuseok!', 'Happy Mid-Autumn Festival', 'May your family be as full as the moon', 'Mooncakes and moonlight',
   'Wishing you a bright harvest moon', 'Together under the full moon']),
 (['makar sankranti', 'uttarayan', 'kite'], 'kites', ['Happy Makar Sankranti!', 'Happy Uttarayan!', 'Let your dreams fly high', 'Kite festival this Sunday',
   'Sweet til-gul and high-flying kites', 'Reach for the sky this year']),
 (['mardi gras', 'carnival'], 'carnival', ['Happy Mardi Gras!', 'Carnival starts now!', 'Let the good times roll', 'Masks on, music up', 'Parade this Saturday at noon',
   'Celebrate with color']),
 (['graduation', 'moving up'], 'graduation', ['Congratulations, graduates!', 'Class of 2027', 'The tassel was worth the hassle', 'Moving up ceremony: March 28, 9 AM',
   'We are so proud of you', 'Recognition day highlights']),
 (['birthday', 'baby shower', 'balloons'], 'birthday', ['Happy birthday!', 'You’re invited to my 7th birthday party', 'Another year of awesome',
   'It’s a girl! Join our baby shower', 'Make a wish!', 'Party starts at 3 PM. See you there!']),
 (['church', 'worship', 'heavenly', 'chapel', 'choir', 'sunday school'], 'church', ['Welcome to Sunday service', 'You are loved', 'Join our choir this Saturday',
   'Sunday school starts at 9 AM', 'Give thanks to the Lord, for He is good', 'Let your light shine']),
 (['back to school', 'classroom', 'teacher'], 'school', ['Welcome back, students!', 'First day of school', 'Today’s lesson', 'Class rules', 'Quiz time!',
   'Great job this week, class!']),
 (['sakura', 'cherry blossom', 'plum blossom', 'tulips', 'spring'], 'spring', ['Hello, spring!', 'Fresh starts bloom here', 'Happy hanami', 'Spring sale this week',
   'New season, new chapter', 'Bloom where you are planted']),
 (['autumn', 'thanksgiving', 'maple'], 'autumn', ['Happy Thanksgiving!', 'Grateful for you', 'Hello, autumn', 'Fall sale: 20% off this weekend', 'Cozy season is here',
   'Thank you for being part of our year']),
 (['snow', 'winter', 'frost', 'northern lights', 'aurora', 'blizzard'], 'winter', ['Hello, winter', 'Stay warm out there', 'Season’s greetings', 'Winter sale starts today',
   'Under the northern lights', 'Cozy nights ahead']),
 (['rain', 'storm', 'thunder', 'lofi', 'reading'], 'rain', ['Rainy day, cozy mood', 'Study with me', 'Lo-fi beats to relax to', 'Stay dry and stay safe',
   'Story time', 'Class is suspended today. Stay safe!']),
 (['beach', 'tropical', 'summer', 'golden hour', 'mediterranean', 'island'], 'summer', ['Hello, summer!', 'Summer vacation starts now', 'Island time', 'Summer sale: up to 40% off',
   'Wish you were here', 'Our summer camp starts June 8']),
 (['stars', 'night sky', 'space', 'nebula', 'fireflies', 'moon', 'milky way'], 'night', ['Good night', 'Dream big', 'Reach for the stars', 'Quiet nights, big dreams',
   'Story time before bed', 'You are my sunshine, even at night']),
 (['tech', 'ai', 'plexus', 'network', 'hexagon', 'corporate', 'synthwave', 'retro'], 'tech', ['Welcome to our webinar', 'Product launch: coming soon', 'Q4 results',
   'The future is now', 'Introducing our new app', 'Live in 5 minutes']),
 (['fiesta', 'banderitas', 'bunting'], 'fiesta', ['Happy fiesta!', 'Welcome to our town fiesta', 'Garden party this Saturday', 'Come and celebrate with us',
   'Food, music and good friends', 'Our barangay fiesta is on May 15']),
 (['confetti', 'party', 'celebration'], 'party', ['Congratulations!', 'We did it!', 'Thank you for 1,000 followers!', 'Big announcement coming…', 'Party time!',
   'Winners announced!']),
 (['embers', 'fire', 'flames'], 'cinematic', ['Coming soon', 'The legend begins', 'Rise up', 'Chapter one', 'Never give up', 'Official trailer']),
 (['inspirational', 'light rays', 'sunbeams'], 'inspire', ['Good morning! Make today count', 'Every day is a fresh start', 'Thank you for being here',
   'Believe you can and you’re halfway there', 'Quote of the day', 'Welcome to our new beginning']),
 (['gold', 'glitter', 'luxury', 'elegant', 'sparkle', 'marquee'], 'luxury', ['You’re invited', 'Grand opening this Saturday', 'And the award goes to…',
   'An evening to remember', 'New collection now available', 'Thank you for celebrating with us']),
]
FALLBACK = ['Welcome to our channel', 'Coming soon', 'Thank you for watching', 'Quote of the day', 'Subscribe for more', 'Big announcement', 'Today’s topic', 'Stay tuned']

def theme(c):
    text = ' '.join([c['id'].replace('-', ' '), c['title'].lower(), ' '.join(t.lower() for t in c['tags'])])
    for kws, key, ideas in THEMES:
        if any(re.search(r'(?<![a-z])' + re.escape(k), text) for k in kws): return key, ideas
    return 'general', FALLBACK

def pick(seq, n, salt):
    return sorted(seq, key=lambda x: _h(x, salt))[:n]

def ideas_html(c, k):
    _, ideas = theme(c)
    chosen = pick(ideas, 3, c['id'])
    where = {'green': 'This clip will sit on top of your video, so keep text in the area the effect leaves open.',
             'overlay': 'Put your text on the track between your footage and this overlay, so the effect glows over the words too.'}.get(k,
             'Put your text on the open part of the frame, in the colors suggested below.' if k != 'scene' else 'Most scenes leave open space on one side. Put your text there.')
    li = ''.join(f'<li>“{E(t)}”</li>' for t in chosen)
    return f'<h2>Text ideas</h2><ul class="ideas">{li}</ul><p class="muted small">Free to copy and change. {where}</p>'

# ------------------------------------------------------------ pairs, other version, quick answers
def other_version(c, byid):
    o = byid.get(c['id'][:-5]) if c['id'].endswith('-9x16') else byid.get(c['id'] + '-9x16')
    if not o and c['id'].endswith('-16x9'): o = byid.get(c['id'][:-5] + '-9x16')
    if not o and c['id'].endswith('-9x16'): o = byid.get(c['id'][:-5] + '-16x9')
    return o

def pairs(c, clips, kind):
    t, _ = theme(c); mine = {x.lower() for x in c['tags']}
    k = kind(c)
    want = {'overlay', 'green'} if k in ('background', 'scene') else {'background', 'scene'}
    pool = [x for x in clips if x['id'] != c['id'] and kind(x) in want and not x['id'].endswith('-9x16') and not x['id'].endswith('-16x9')]
    def score(x):
        return (3 if theme(x)[0] == t else 0) + len(mine & {y.lower() for y in x['tags']} - {'loop', 'background', 'overlay', 'vertical', '9:16', 'tiktok', 'reels'})
    pool.sort(key=lambda x: (-score(x), _h(x['id'], c['id'])))
    return pool[:3]

def pairs_html(c, clips, kind):
    ps = pairs(c, clips, kind); k = kind(c)
    if not ps: return ''
    why = (lambda x: 'Add it on top with Screen blend.' if kind(x) == 'overlay' else 'Key out the green and lay it on top.') if k in ('background', 'scene') \
        else (lambda x: 'Use it as the background underneath.')
    li = ''.join(f'<li><a href="/clip/{x["id"]}/"><img src="/media/poster/{x["id"]}.webp" alt="" loading="lazy" width="96" height="54"><span>{E(x["title"])}</span></a>'
                 f'<small>{why(x)}</small></li>' for x in ps)
    head = 'Overlays to add on top' if k in ('background', 'scene') else 'Backgrounds to use it with'
    return f'<h2>{head}</h2><ul class="pairs">{li}</ul>'

def faq_html(c, k, other, aspect):
    a = aspect(c); q = []
    if other:
        q.append(('Is there a ' + ('vertical' if a == '16:9' else 'horizontal') + ' version?',
                  f'Yes. <a href="/clip/{other["id"]}/">{E(other["title"])}</a> is the same design made for '
                  + ('TikTok, Reels and Shorts (9:16).' if a == '16:9' else 'YouTube, slides and TV screens (16:9).')))
    elif a == '16:9':
        q.append(('Can I use it for TikTok or Reels?', 'Yes. Set your project to 9:16 and zoom the clip to fill the frame. '
                  + ('The edges will be cropped, so keep your subject near the center.' if k != 'scene' else 'Choose the part of the scene you like best; the motion still loops.')))
    elif a == '9:16':
        q.append(('Can I use it for YouTube?', 'It is made for vertical video. In a 16:9 project, place it on one side or blur a copy behind it to fill the frame.'))
    if c['loop']:
        q.append(('How do I make it longer?', f'Copy the clip and place the copies end to end. Each one is {c["duration"]:g} seconds and the end matches the start, '
                  f'so {round(60 / c["duration"])} copies make a smooth background of about one minute with no visible jump.'))
    else:
        q.append(('Does it loop?', f'No. It plays once over {c["duration"]:g} seconds, so place it where you want the moment to happen.'))
    if k == 'overlay':
        q.append(('Why is the background black?', 'Black disappears with the Screen blend mode, leaving only the light. That keeps the file small and the edges soft.'))
    elif k == 'green':
        q.append(('Which green is it?', 'Chroma green #00B140. Pick it with the eyedropper in your editor’s chroma key tool.'))
    else:
        q.append(('Does it have sound?', 'No. It is silent so you can add your own music or voice.'))
    return '<h2>Quick answers</h2><dl class="qa">' + ''.join(f'<dt>{t}</dt><dd>{d}</dd>' for t, d in q) + '</dl>'

CSS = '''
.swatches{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 12px}
.sw{display:flex;align-items:center;gap:8px;background:var(--bg2);border:1px solid var(--line);border-radius:10px;padding:6px 10px 6px 6px;color:var(--text);font:inherit;font-size:13px;cursor:pointer}
.sw i{width:26px;height:26px;border-radius:6px;border:1px solid rgba(255,255,255,.18)}.sw b{font-weight:600;font-family:ui-monospace,Menlo,monospace}.sw span{color:var(--muted)}
.sw.ok b::after{content:" ✓ copied";color:var(--green);font-family:var(--body)}
.ideas{margin:8px 0;padding-left:20px}.ideas li{margin:4px 0;font-size:17px}
.pairs{list-style:none;padding:0;margin:8px 0;display:grid;gap:10px}
.pairs li{display:flex;flex-wrap:wrap;align-items:center;gap:4px 12px;background:var(--bg2);border:1px solid var(--line);border-radius:12px;padding:8px}
.pairs a{display:flex;align-items:center;gap:12px;font-weight:600}.pairs img{width:96px;height:54px;object-fit:cover;border-radius:8px;background:#000}
.pairs small{color:var(--muted);flex-basis:100%;padding-left:108px}
@media(max-width:480px){.pairs small{padding-left:0}}
.qa dt{font-weight:600;margin-top:12px}.qa dd{margin:4px 0 0;color:#d6cfc6}
'''
JS = ('<script>document.querySelectorAll(".sw").forEach(function(b){b.onclick=function(){var h=b.dataset.hex;'
      '(navigator.clipboard?navigator.clipboard.writeText(h):Promise.reject()).catch(function(){}).then(function(){'
      'document.querySelectorAll(".sw.ok").forEach(function(x){x.classList.remove("ok")});b.classList.add("ok")})}})</script>')

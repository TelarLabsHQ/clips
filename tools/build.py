#!/usr/bin/env python3
"""Builds the static site into public/ from data/clips.json and site.config.json.
Run:  python3 tools/build.py
No packages needed (standard library only)."""
import json, os, re, html, shutil
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'public')
CFG = json.load(open(os.path.join(ROOT, 'site.config.json')))
CLIPS = json.load(open(os.path.join(ROOT, 'data', 'clips.json')))
E = lambda s: html.escape(str(s), quote=True)
URL = CFG['site_url'].rstrip('/')
MEDIA = CFG['media_base']
NAME = CFG['site_name']

CAT_ORDER = ['World Celebrations', 'Illustrated Scenes', 'Christmas & New Year', 'Green Screen', 'Bokeh Lights', 'Gradients', 'Overlays',
             'Celebrations & Events', 'Nature & Seasons', 'Tech & Abstract']
CAT_BLURB = {
    'Christmas & New Year': 'Snow, string lights, ornaments, fireworks and a New Year countdown for your holiday greetings and promos.',
    'World Celebrations': 'Holidays from around the world: Lunar New Year and the Lantern Festival, Ramadan and Eid, Hanukkah, Diwali, Holi, Nowruz, St. Patrick\'s Day, Carnival, Easter, cherry blossom season, Chuseok, Halloween, the Fourth of July and the Filipino parol.',
    'Illustrated Scenes': 'Illustrated scenes with gentle motion, perfect as story backgrounds, video greetings or reel openers: festivals, travel spots and cute characters from around the world.',
    'Green Screen': 'Pure chroma green (#00B140) clips you can drop over any video and key out in CapCut, Canva, Premiere or DaVinci Resolve.',
    'Bokeh Lights': 'Soft out-of-focus lights in many colors, perfect behind titles, quotes and greetings.',
    'Gradients': 'Smooth, slowly flowing color gradients for intros, presentations and social posts.',
    'Overlays': 'Light rays, light leaks, sparkles, snow, dust and embers to lay over your footage with Screen blend mode.',
    'Celebrations & Events': 'Confetti, balloons, hearts and graduation colors for birthdays, weddings, debuts and awards.',
    'Nature & Seasons': 'Autumn leaves, fireflies, bubbles and starry skies for seasonal greetings, relaxing, sleep, kids and storytelling videos.',
    'Tech & Abstract': 'Network lines, hexagons and retro neon grids for tech, gaming and corporate videos.',
}

# ---------------------------------------------------------------- Telar Labs family links
FAMILY = [f for f in CFG.get('family', []) if f['name'] != CFG['site_name']]
HUB = CFG.get('studio_url', '')

def family_row():
    if not FAMILY: return ''
    head = f'<a href="{E(HUB)}">More from {E(CFG["studio"])}</a>' if HUB else f'More from {E(CFG["studio"])}'
    links = ''.join(f'<a href="{E(f["url"])}" title="{E(f["blurb"])}">{E(f["name"])}</a>' for f in FAMILY)
    return f'<div class="wrap family"><span class="family-h">{head}:</span>{links}</div>'

def family_promo(title):
    if not FAMILY: return ''
    links = ''.join(f'<a href="{E(f["url"])}"><b>{E(f["name"])}</b><span>{E(f["blurb"])}</span></a>' for f in FAMILY)
    return f'<section class="wrap section family-promo"><h2>{title}</h2><div class="family-links">{links}</div></section>'

def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
CATS = [c for c in CAT_ORDER if any(x['category'] == c for x in CLIPS)]
GREEN_ALSO = lambda c: c['green_screen'] and c['category'] != 'Green Screen'

def in_cat(c, cat):
    return c['category'] == cat or (cat == 'Green Screen' and c['green_screen'])

def kind(c):
    if c['green_screen']: return 'green'
    if c.get('illustrated'): return 'scene'
    if c['category'] == 'Overlays' or 'overlay' in c['id']: return 'overlay'
    return 'background'

def vertical(c): return c['height'] >= c['width'] * 1.7

def aspect(c):
    w, h = c['width'], c['height']
    if w * 9 == h * 16: return '16:9'
    if w * 16 == h * 9: return '9:16'
    if w == h: return '1:1'
    if w * 5 == h * 4: return '4:5'
    return f'{w}×{h}'

def res_label(c):
    a = aspect(c)
    if a == '16:9' and c['width'] >= 1920: return 'Full HD'
    if a == '9:16' and c['height'] >= 1920: return 'Full HD, vertical 9:16'
    return {'1:1': 'HD square 1:1', '4:5': 'HD portrait 4:5'}.get(a, 'HD')

# ---------------------------------------------------------------- layout
LOGO = ('<svg class="logo-mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="var(--accent)"/>'
        '<path d="M8 11h16M8 16h16M8 21h16" stroke="#1b1206" stroke-width="2.6" stroke-linecap="round"/>'
        '<path d="M12 7v18M20 7v18" stroke="#1b1206" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="3 3"/></svg>')

def ad(key, cls='ad'):
    slot = CFG['ad_slots'].get(key, '')
    if not (CFG['adsense_client'] and slot): return ''
    return (f'<div class="{cls}"><span class="ad-label">Advertisement</span><ins class="adsbygoogle" style="display:block" '
            f'data-ad-client="{E(CFG["adsense_client"])}" data-ad-slot="{E(slot)}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
            '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></div>')

def page(path, title, desc, body, extra_head='', og_image=None):
    canonical = URL + path
    full_title = title if title.endswith(NAME) else f'{title} | {NAME}'
    og = og_image or URL + '/media/poster/golden-bokeh-lights-loop.webp'
    ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={E(CFG["adsense_client"])}" '
           'crossorigin="anonymous"></script>') if CFG['adsense_client'] else ''
    cfa = (f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{{"token": "{E(CFG["cloudflare_analytics_token"])}"}}\'></script>'
           if CFG['cloudflare_analytics_token'] else '')
    nav = ''.join(f'<a href="/category/{slug(c)}/">{E(c.replace(" & New Year", "").replace(" & Events", "").replace(" & Abstract", "").replace("World ", ""))}</a>'
                  for c in ['World Celebrations', 'Christmas & New Year', 'Green Screen', 'Overlays'])
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{E(canonical)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{E(NAME)}">
<meta property="og:title" content="{E(full_title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{E(canonical)}"><meta property="og:image" content="{E(og)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#121016">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
{ads}{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap top-in">
    <a class="logo" href="/">{LOGO}<span>{E(NAME)}</span></a>
    <nav class="nav">{nav}<a href="/how-to-use/">How to use</a></nav>
    <a class="btn btn-sm" href="/#browse">Browse all</a>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap foot-in">
    <div>
      <a class="logo" href="/">{LOGO}<span>{E(NAME)}</span></a>
      <p class="muted">{E(CFG["tagline"])}. Free to download, no sign-up, OK for personal and commercial projects.</p>
    </div>
    <div class="foot-cols">
      <div><h4>Browse</h4>{''.join(f'<a href="/category/{slug(c)}/">{E(c)}</a>' for c in CATS[:5])}</div>
      <div><h4>More</h4>{''.join(f'<a href="/category/{slug(c)}/">{E(c)}</a>' for c in CATS[5:])}<a href="/how-to-use/">How to use</a></div>
      <div><h4>{E(CFG["studio"])}</h4><a href="/about/">About</a><a href="/license/">License</a><a href="/privacy/">Privacy policy</a><a href="/contact/">Contact</a></div>
    </div>
  </div>
  {family_row()}<div class="wrap fine">&copy; {date.today().year} {E(CFG["studio"])}. Motion graphics and illustrated scenes by {E(CFG["studio"])}.</div>
</footer>
<script src="/assets/site.js" defer></script>
{cfa}
</body>
</html>'''
    out = os.path.join(PUB, path.strip('/'), 'index.html') if path.endswith('/') else os.path.join(PUB, path.strip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(doc)

# ---------------------------------------------------------------- parts
def badges(c):
    b = []
    if c['green_screen']: b.append('<span class="badge badge-green">Green screen</span>')
    if c.get('illustrated'): b.append('<span class="badge badge-ill">Illustrated</span>')
    if aspect(c) != '16:9': b.append(f'<span class="badge">{aspect(c)}</span>')
    b.append(f'<span class="badge">{"Loop" if c["loop"] else str(int(c["duration"])) + "s"}</span>')
    return ''.join(b)

def thumb_bg(c):
    return f' style="background:{c["pad"]}"' if c.get('pad') else ''

def card(c):
    text = ' '.join([c['title'], c['category'], ' '.join(c['tags'])]).lower()
    cats = '|'.join(x for x in CATS if in_cat(c, x))
    return (f'<a class="card" href="/clip/{c["id"]}/" data-cats="{E(cats)}" data-text="{E(text)}">'
            f'<div class="thumb{" thumb-v" if (vertical(c) or c.get("pad") == "#ffffff") else ""}"{thumb_bg(c)}><img src="/media/poster/{c["id"]}.webp" alt="{E(c["title"])} preview" loading="lazy" width="{c["width"] // 3}" height="{c["height"] // 3}">'
            f'<video muted loop playsinline preload="none" data-src="/media/preview/{c["id"]}.mp4"></video>'
            f'<div class="badges">{badges(c)}</div></div>'
            f'<div class="card-meta"><h3>{E(c["title"])}</h3><span>{E(c["category"])}</span></div></a>')

def grid(clips, ad_key=None, every=12):
    out = []
    for i, c in enumerate(clips):
        out.append(card(c))
        if ad_key and (i + 1) % every == 0 and i + 1 < len(clips):
            a = ad(ad_key, 'ad ad-grid')
            if a: out.append(a)
    return '<div class="grid">' + ''.join(out) + '</div>'

HOWTO = {
 'green': ('How to use this green screen clip', [
   ('CapCut (phone or desktop)', 'Add your main video first. Tap <b>Overlay → Add overlay</b> and choose this clip. Select it, tap <b>Remove BG → Chroma key</b>, pick the green, then raise <b>Intensity</b> until the green disappears and <b>Shadow</b> to clean the edges.'),
   ('Canva', 'Place your background or video, then add this clip on top. Select it and choose <b>Edit → BG Remover</b> (Canva Pro). For a free option, use CapCut instead.'),
   ('Premiere Pro / DaVinci Resolve', 'Put the clip on the track above your footage. In Premiere use <b>Ultra Key</b> and pick the green; in Resolve use the <b>3D Keyer</b> or <b>Delta Keyer</b>.')]),
 'overlay': ('How to use this overlay', [
   ('Put it above your video', 'Place this clip on the track above your footage or photo, stretched to the full frame.'),
   ('Set the blend mode to Screen', 'The black parts disappear and only the light stays. CapCut: select the overlay → <b>Blend → Screen</b>. Premiere: <b>Effect Controls → Opacity → Blend mode → Screen</b>. Canva: <b>Transparency</b> works, but Screen blend needs CapCut or a desktop editor.'),
   ('Adjust the strength', 'Lower the overlay opacity to 40–80% for a subtle look, or keep it at 100% for a bold effect.')]),
 'scene': ('How to use this illustrated scene', [
   ('Use it as a background', 'Add the clip as the first layer. It loops seamlessly, so you can repeat it for a longer greeting, story or lesson.'),
   ('Add your title or greeting', 'Most scenes leave open sky or space on one side. Put your text there, with a soft shadow so it stays readable.'),
   ('Make it vertical if needed', 'For TikTok, Reels or Shorts, set the project to 9:16 and zoom in on the part of the scene you like best. The motion still loops smoothly.')]),
 'background': ('How to use this background', [
   ('Put it on the bottom track', 'Add the clip as the first layer of your video. It is a seamless loop, so you can repeat it as many times as you need without a visible jump.'),
   ('Add your text or photo on top', 'Type your greeting, quote, title or announcement over it. Light text with a soft shadow reads best on darker backgrounds.'),
   ('Make it vertical if needed', 'For TikTok, Reels or Shorts, set the project to 9:16 and zoom the clip to fill the frame. The motion still loops smoothly.')]),
}

def jsonld(c):
    d = {"@context": "https://schema.org", "@type": "VideoObject", "name": c['title'], "description": c['description'],
         "thumbnailUrl": [f"{URL}/media/poster/{c['id']}.webp"], "uploadDate": CFG['launch_date'],
         "duration": f"PT{int(round(c['duration']))}S", "contentUrl": MEDIA + c['file'],
         "isFamilyFriendly": True, "keywords": ', '.join(c['tags']),
         "creator": {"@type": "Organization", "name": CFG['studio']},
         "license": URL + "/license/"}
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'

def clip_page(c):
    k = kind(c); h, steps = HOWTO[k]
    related = [x for x in CLIPS if x['id'] != c['id'] and (x['category'] == c['category'] or (c['green_screen'] and x['green_screen']))][:8]
    if len(related) < 8: related += [x for x in CLIPS if x['id'] != c['id'] and x not in related][:8 - len(related)]
    res = f'{c["width"]}×{c["height"]}'
    spec = [('Resolution', f'{res} ({res_label(c)})'),
            ('Length', f'{c["duration"]:g} seconds' + (', seamless loop' if c['loop'] else '')),
            ('Frame rate', f'{c.get("fps", 30)} fps'), ('Format', 'MP4 (H.264)'),
            ('Background', 'Chroma green #00B140' if c['green_screen'] else ('Black (use Screen blend)' if k == 'overlay' else 'Included')),
            ('Price', 'Free, no sign-up')]
    tags = ''.join(f'<a class="tag" href="/?q={E(t)}#browse">{E(t)}</a>' for t in c['tags'])
    body = f'''
<div class="wrap crumbs"><a href="/">Home</a> <span>/</span> <a href="/category/{slug(c["category"])}/">{E(c["category"])}</a> <span>/</span> {E(c["title"])}</div>
<section class="wrap clip">
  <div class="clip-main">
    <div class="player{" player-v" if vertical(c) else (" player-s" if aspect(c) != "16:9" else "")}"{f' style="aspect-ratio:{c["width"]}/{c["height"]}"' if aspect(c) not in ("16:9", "9:16") else ""}>
      <video src="/media/preview/{c["id"]}.mp4" poster="/media/poster/{c["id"]}.webp" autoplay muted loop playsinline controls></video>
    </div>
    <p class="preview-note muted">Preview is lower quality. The download is the full {res} file.</p>
    <h1>{E(c["title"])}</h1>
    <div class="badges badges-inline">{badges(c)}{"" if c["category"] == "Green Screen" else f'<span class="badge">{E(c["category"])}</span>'}</div>
    <a class="btn btn-big mobile-dl" href="{E(MEDIA + c["file"])}" data-download="{E(c["file"])}" download>Download free MP4</a>
    <p class="lead">{E(c["description"])}</p>
    <h2>Good for</h2>
    <p>{E(c["uses"])}.</p>
    <h2>{h}</h2>
    <ol class="steps">{''.join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in steps)}</ol>
    <p class="muted small">More tips in our <a href="/how-to-use/">how-to-use guide</a>.</p>
    <h2>Tags</h2>
    <div class="tags">{tags}</div>
  </div>
  <aside class="clip-side">
    <div class="panel">
      <a class="btn btn-big" href="{E(MEDIA + c["file"])}" data-download="{E(c["file"])}" download>
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M12 3v12m0 0l-5-5m5 5l5-5M5 21h14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        Download free MP4</a>
      <table class="spec">{''.join(f'<tr><th>{a}</th><td>{b}</td></tr>' for a, b in spec)}</table>
      <div class="license-box">
        <strong>Free for personal and commercial use.</strong>
        Use it in YouTube, TikTok, Facebook, ads, school and church projects. Credit is appreciated but not required.
        Please don't resell or re-upload the clip by itself. <a href="/license/">Full license</a>
      </div>
    </div>
    {ad("clip_below_download", "ad ad-side")}
  </aside>
</section>
<section class="wrap section">
  <div class="section-head"><h2>More like this</h2><a href="/category/{slug(c["category"])}/">See all {E(c["category"])} →</a></div>
  {grid(related)}
</section>'''
    page(f'/clip/{c["id"]}/', f'{c["title"]} – Free {"Green Screen" if c["green_screen"] else ("Animated Illustration" if c.get("illustrated") else "Stock Video")} Download',
         c['description'][:155], body, jsonld(c), f"{URL}/media/poster/{c['id']}.webp")

HOLIDAYS = [('Diwali', 'diwali'), ('Thanksgiving', 'thanksgiving'), ('Hanukkah', 'hanukkah'), ('Christmas', 'christmas'), ('New Year', 'new year'),
            ('Lunar New Year', 'lunar new year'), ('Lantern Festival', 'lantern festival'), ("Valentine's Day", 'valentine'), ('Ramadan & Eid', 'ramadan'),
            ('Carnival', 'carnival'), ("St. Patrick's Day", 'patrick'), ('Holi', 'festival of colors'), ('Nowruz', 'nowruz'), ('Easter', 'easter'),
            ('Cherry blossom', 'sakura'), ('Chuseok', 'chuseok'), ('Halloween', 'halloween'), ('Fourth of July', 'fourth of july')]

def holiday_chips():
    return '<div class="chips chips-wrap">' + ''.join(f'<a class="chip" href="/?q={E(q)}#browse">{E(n)}</a>' for n, q in HOLIDAYS) + '</div>'

def chips():
    return ('<div class="chips" role="group" aria-label="Filter by category"><button class="chip is-on" data-cat="">All</button>' +
            ''.join(f'<button class="chip" data-cat="{E(c)}">{E(c)}</button>' for c in CATS) + '</div>')

# ---------------------------------------------------------------- pages
def home():
    pick = ['diwali-diya-lamps-loop', 'falling-autumn-maple-leaves-loop', 'hanukkah-menorah-candles-loop', 'snowy-christmas-tree-forest-night-loop',
            'happy-new-year-2027-gold-loop', 'lantern-festival-rising-red-lanterns-loop', 'ramadan-lanterns-crescent-moon-loop', 'st-patricks-falling-shamrocks-loop']
    byid = {c['id']: c for c in CLIPS}
    xmas = [byid[i] for i in pick if i in byid]
    if len(xmas) < 8: xmas += [c for c in CLIPS if c['category'] == 'World Celebrations' and c not in xmas][:8 - len(xmas)]
    n = len(CLIPS)
    body = f'''
<section class="hero">
  <video class="hero-bg" src="/media/preview/golden-bokeh-lights-loop.mp4" autoplay muted loop playsinline aria-hidden="true"></video>
  <div class="hero-shade"></div>
  <div class="wrap hero-in">
    <p class="eyebrow">{n} free clips · Full HD · No sign-up</p>
    <h1>Free motion backgrounds, illustrated scenes &amp; green screens</h1>
    <p class="hero-sub">Seamless loops and animated illustrations for your greetings, intros, reels, and school, church or community videos. Download, drop into CapCut or Canva, done.</p>
    <form class="search" action="/" method="get" role="search">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      <input type="search" name="q" id="q" placeholder="Search: snow, lanterns, sakura, confetti, green screen…" aria-label="Search clips" autocomplete="off">
    </form>
    <div class="hero-pills"><a href="/category/world-celebrations/">World celebrations</a><a href="/category/illustrated-scenes/">Illustrated scenes</a><a href="/category/christmas-new-year/">Christmas &amp; New Year</a><a href="/category/green-screen/">Green screen</a><a href="/category/overlays/">Overlays</a><a href="/category/bokeh-lights/">Bokeh</a></div>
  </div>
</section>
<section class="wrap section">
  <div class="section-head"><h2>Coming up: holidays around the world</h2><a href="/category/world-celebrations/">See all →</a></div>
  {grid(xmas)}
  <h3 class="sub-head">Browse by holiday</h3>
  {holiday_chips()}
</section>
<section class="wrap section">
  <div class="section-head"><h2>New: illustrated scenes</h2><a href="/category/illustrated-scenes/">See all →</a></div>
  <p class="muted section-sub">{E(CAT_BLURB['Illustrated Scenes'])}</p>
  {grid([c for c in CLIPS if c.get('illustrated')][:8])}
</section>
{ad("home_grid", "wrap ad")}
<section class="wrap section" id="browse">
  <div class="section-head"><h2>Browse all clips</h2><span class="muted" id="count">{n} clips</span></div>
  {chips()}
  {grid(CLIPS, "list_grid")}
  <p class="empty muted" id="empty" hidden>No clips match that search yet. Try "lights", "green" or "loop".</p>
</section>
<section class="wrap section why">
  <div><h3>Really free</h3><p>No account, no watermark, no credit required. Use them for personal and commercial videos.</p></div>
  <div><h3>Made to loop</h3><p>Every background and illustrated scene is a seamless 8-second loop, so you can stretch it under a long greeting or stream.</p></div>
  <div><h3>For every culture</h3><p>Lunar New Year, Chuseok, sakura season, Halloween, Christmas, the Fourth of July and more, with new clips before every major holiday.</p></div>
</section>'''
    body += family_promo('For teachers: free classroom tools')
    page('/', f'{NAME} – Free Motion Backgrounds, Illustrated Scenes & Green Screens',
         f'Download {n} free HD motion backgrounds, animated illustrated scenes, overlays and green screen clips: Christmas, Lunar New Year, Halloween, sakura, bokeh, confetti, snow and more. No sign-up, OK for commercial use.', body)

def category(cat):
    cl = [c for c in CLIPS if in_cat(c, cat)]
    others = ''.join(f'<a class="chip" href="/category/{slug(c)}/">{E(c)}</a>' for c in CATS if c != cat)
    body = f'''
<div class="wrap crumbs"><a href="/">Home</a> <span>/</span> {E(cat)}</div>
<section class="wrap section page-head">
  <h1>{"Free animated illustrated scenes" if cat == "Illustrated Scenes" else f"Free {E(cat)} clips"}</h1>
  <p class="lead">{E(CAT_BLURB[cat])}</p>
  <p class="muted">{len(cl)} clips · Full HD · free download</p>
</section>
{('<section class="wrap section"><h2>Browse by holiday</h2>' + holiday_chips() + '</section>') if cat == 'World Celebrations' else ''}
<section class="wrap section">{grid(cl, "list_grid")}</section>
<section class="wrap section"><h2>Other categories</h2><div class="chips">{others}</div></section>'''
    page(f'/category/{slug(cat)}/', f'Free {cat} Stock Video Clips', f'{CAT_BLURB[cat]} {len(cl)} free HD clips, no sign-up.', body)

def prose(path, title, desc, inner):
    page(path, title, desc, f'<div class="wrap crumbs"><a href="/">Home</a> <span>/</span> {E(title)}</div><article class="wrap prose">{inner}</article>')

def static_pages():
    st = CFG['studio']; mail = CFG['contact_email']
    prose('/about/', 'About', f'About {NAME} by {st}.', f'''
<h1>About {E(NAME)}</h1>
<p class="lead">{E(NAME)} is a small library of free motion backgrounds, illustrated scenes, overlays and green screen clips from {E(st)}, an independent studio.</p>
<p>We started it because creators, teachers, churches and small businesses everywhere keep needing the same things: red lanterns for a Lunar New Year greeting, a full moon for Chuseok, falling sakura for a spring post, bats for a Halloween invite, a parol for a Filipino Christmas, confetti for a giveaway winner, a calm loop behind a quote. The big stock sites have millions of clips, but the good holiday ones are often hard to find or need a paid plan.</p>
<p>Every clip is made by {E(st)} for this site; nothing is copied from other sites or stock libraries. Our illustrated scenes are designed by {E(st)} with AI-assisted illustration, then animated and finished by us. They are free to download without an account, and you can use them in personal and commercial projects. See the <a href="/license/">license</a> for the details.</p>
<h2>What you'll find</h2>
<ul>{''.join(f'<li><a href="/category/{slug(c)}/">{E(c)}</a>: {E(CAT_BLURB[c])}</li>' for c in CATS)}</ul>
<h2>New clips every week</h2>
<p>We add new clips regularly, especially before holidays like Lunar New Year, Valentine's Day, cherry blossom season, Chuseok, Halloween, Christmas and New Year. Have an idea for a clip you need? <a href="/contact/">Tell us</a>, and we may make it.</p>
<h2>How the site is supported</h2>
<p>{E(NAME)} is free because it shows ads. The ads help pay for hosting and the time it takes to make new clips.</p>''')
    prose('/contact/', 'Contact', f'Contact {NAME}.', f'''
<h1>Contact us</h1>
<p class="lead">Questions, clip requests or problems with a download? We'd love to hear from you.</p>
<p>Email: <a href="mailto:{E(mail)}">{E(mail)}</a></p>
<p>We usually reply within two to three working days.</p>
<h2>Requesting a clip</h2>
<p>Tell us what the clip is for, the colors or mood you want, and whether you need it as a green screen or vertical (9:16). We can't promise every request, but we read them all and use them to plan new clips.</p>
<h2>Reporting a problem</h2>
<p>If a download doesn't work or you think a clip breaks a rule, email us with the clip's page link and we'll look into it quickly.</p>''')
    prose('/license/', 'License', f'License for clips downloaded from {NAME}.', f'''
<h1>License</h1>
<p class="lead">All clips on {E(NAME)} are free to use in personal and commercial projects. No sign-up, no payment and no credit required.</p>
<h2>You can</h2>
<ul>
<li>Use the clips in videos on YouTube, TikTok, Facebook, Instagram and other platforms, including monetized channels.</li>
<li>Use them in ads, product videos, presentations, school projects, church services and events.</li>
<li>Edit them: cut, crop, recolor, speed up, add text, combine with other footage.</li>
<li>Use them in client work you are paid for.</li>
</ul>
<h2>You can't</h2>
<ul>
<li>Sell, re-upload or share the clips on their own, or as part of a stock, template or wallpaper collection, without major changes.</li>
<li>Claim the clips as your own original work, or register them with a content ID system.</li>
<li>Use the clips in a trademark, logo or brand identity.</li>
<li>Use them in content that is illegal, hateful, or misleading.</li>
</ul>
<h2>Credit</h2>
<p>Credit is not required, but it helps us a lot. If you'd like to, write: <em>Background by {E(NAME)}</em>.</p>
<h2>No warranty</h2>
<p>The clips are provided as they are. {E(st)} is not responsible for how the clips are used.</p>
<p class="muted">Last updated {E(CFG["launch_date"])}.</p>''')
    ads_txt = ('<p>We use Google AdSense to show ads. Google and its partners use cookies to show ads based on your visits to this and other websites. '
               'You can turn off personalized ads in <a href="https://adssettings.google.com" rel="noopener">Google Ads Settings</a>, and learn more at '
               '<a href="https://policies.google.com/technologies/partner-sites" rel="noopener">How Google uses information from sites that use its services</a>.</p>')
    prose('/privacy/', 'Privacy Policy', f'Privacy policy for {NAME}.', f'''
<h1>Privacy policy</h1>
<p class="lead">{E(NAME)} is run by {E(st)}. This page explains what information is collected when you visit.</p>
<h2>No accounts</h2>
<p>You can browse and download every clip without creating an account. We don't ask for your name, email or payment details to download.</p>
<h2>Advertising</h2>
{ads_txt}
<p>Visitors in the European Economic Area, the UK and Switzerland are shown a consent message before personalized ads are used.</p>
<h2>Analytics</h2>
<p>We may use privacy-friendly analytics (Cloudflare Web Analytics) to count page views. It doesn't use cookies and doesn't track you across websites.</p>
<h2>Hosting and logs</h2>
<p>The site and clips are hosted on Cloudflare. Like any website, their servers may record basic technical information such as IP address, browser type and the pages requested, to keep the service secure and working.</p>
<h2>Emails</h2>
<p>If you email us, we use your email address only to reply to you.</p>
<h2>Children</h2>
<p>The site is for a general audience. We don't knowingly collect personal information from children.</p>
<h2>Contact</h2>
<p>Questions about privacy: <a href="mailto:{E(mail)}">{E(mail)}</a></p>
<p class="muted">Last updated {E(CFG["launch_date"])}.</p>''')
    prose('/how-to-use/', 'How to Use Green Screens, Overlays and Loop Backgrounds',
          'Step-by-step guide to using green screen clips, light overlays and looping backgrounds in CapCut, Canva, Premiere and DaVinci Resolve.', f'''
<h1>How to use our clips</h1>
<p class="lead">Our clips come in four kinds. Here's how to use each one in the editors most people use: CapCut, Canva, Premiere Pro and DaVinci Resolve.</p>
<nav class="toc"><a href="#backgrounds">Loop backgrounds</a><a href="#green">Green screen clips</a><a href="#overlays">Overlays (Screen blend)</a><a href="#scenes">Illustrated scenes</a><a href="#vertical">Vertical videos</a><a href="#tips">Tips</a></nav>
<h2 id="backgrounds">1. Loop backgrounds</h2>
<p>Bokeh lights, gradients, lanterns and starry skies are full backgrounds. Put them on the bottom layer and add your text, photo or logo on top.</p>
<ol><li>Start a new project and import the clip.</li><li>Put it on the first (lowest) track.</li><li>Add text on top. Light text with a soft shadow reads best on dark backgrounds.</li>
<li>Need it longer than 8 seconds? Copy and paste the clip end to end. Each one is a seamless loop, so you won't see the cut.</li></ol>
<h2 id="green">2. Green screen clips</h2>
<p>Green screen clips have a solid chroma green background (#00B140). You remove the green so only the snow, confetti, balloons or frame stays on top of your own video.</p>
<h3>CapCut (free)</h3>
<ol><li>Add your main video or photo first.</li><li>Tap <b>Overlay → Add overlay</b> and pick the green screen clip.</li><li>With the overlay selected, tap <b>Remove BG → Chroma key</b>.</li><li>Use the color picker on the green. Raise <b>Intensity</b> until the green is gone, then <b>Shadow</b> to soften the edges.</li></ol>
<h3>Canva</h3>
<p>Add the clip above your design and use <b>Edit → BG Remover</b>. This needs Canva Pro. If you're on the free plan, key the clip in CapCut first and export.</p>
<h3>Premiere Pro</h3>
<p>Place the clip on the track above your footage, apply <b>Ultra Key</b>, and click the green with the eyedropper. Adjust <b>Matte Generation</b> if any green edge remains.</p>
<h3>DaVinci Resolve</h3>
<p>On the Edit page, select the clip and open <b>Inspector → Video</b>, or use the <b>3D Keyer</b> on the Color page and draw across the green.</p>
<h2 id="overlays">3. Overlays (Screen blend)</h2>
<p>Overlays like light leaks, dust, embers, sparkles and snow on black are made to sit on top of your video. The <b>Screen</b> blend mode hides the black and keeps only the light.</p>
<ol><li>Put the overlay on the track above your video.</li><li>CapCut: select it → <b>Blend → Screen</b>. Premiere: <b>Effect Controls → Opacity → Blend Mode → Screen</b>. Resolve: <b>Inspector → Composite Mode → Screen</b>.</li><li>Lower the opacity for a softer effect.</li></ol>
<h2 id="scenes">4. Illustrated scenes</h2>
<p>Illustrated scenes are animated storybook pictures with gentle motion: falling snow, glowing lanterns, fireworks, rain and petals. They are Full HD 16:9 and loop seamlessly.</p>
<ol><li>Put the scene on the bottom track as your background.</li><li>Add your greeting or title in the open sky or empty side of the picture.</li>
<li>For vertical videos, set the project to 9:16 and zoom in on the part of the scene you like best.</li></ol>
<h2 id="vertical">5. Making vertical videos (TikTok, Reels, Shorts)</h2>
<p>Most clips are horizontal 16:9. For a vertical video, set your project to <b>9:16</b> and zoom the clip until it fills the screen. Bokeh, gradients, snow and confetti still look great cropped. Some clips, like the Christmas lights frame, also come in a ready-made vertical version.</p>
<h2 id="tips">Tips</h2>
<ul><li>Keep important text away from the bottom and right edges on TikTok and Reels, where the buttons and captions sit.</li>
<li>Match the mood: gold bokeh for formal greetings, confetti for winners and birthdays, soft gradients for quotes.</li>
<li>Exports look best at 1080p and 30 fps, the same as our clips.</li></ul>
<p>Still stuck? <a href="/contact/">Send us a message</a>.</p>''')

def extras():
    os.makedirs(os.path.join(PUB, 'assets'), exist_ok=True)
    open(os.path.join(PUB, 'favicon.svg'), 'w').write(LOGO.replace('class="logo-mark" ', 'xmlns="http://www.w3.org/2000/svg" ').replace('var(--accent)', '#ffb547'))
    urls = ['/', '/how-to-use/', '/about/', '/license/', '/privacy/', '/contact/'] + [f'/category/{slug(c)}/' for c in CATS] + [f'/clip/{c["id"]}/' for c in CLIPS]
    open(os.path.join(PUB, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'<url><loc>{URL}{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    open(os.path.join(PUB, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {URL}/sitemap.xml\n')
    if CFG['adsense_client']:
        pub = CFG['adsense_client'].replace('ca-', '')
        open(os.path.join(PUB, 'ads.txt'), 'w').write(f'google.com, {pub}, DIRECT, f08c47fec0942fa0\n')
    open(os.path.join(PUB, '_headers'), 'w').write('/media/*\n  Cache-Control: public, max-age=31536000, immutable\n/assets/*\n  Cache-Control: public, max-age=86400\n')
    page('/404.html', 'Page not found', 'This page does not exist.',
         '<section class="wrap prose"><h1>Page not found</h1><p class="lead">That page doesn\'t exist, but there are plenty of free clips.</p><p><a class="btn" href="/">Go to the homepage</a></p></section>')

if __name__ == '__main__':
    for d in ('clip', 'category', 'about', 'contact', 'license', 'privacy', 'how-to-use'):
        shutil.rmtree(os.path.join(PUB, d), ignore_errors=True)
    home(); [clip_page(c) for c in CLIPS]; [category(c) for c in CATS]; static_pages(); extras()
    print(f'Built {len(CLIPS)} clip pages, {len(CATS)} categories into public/')

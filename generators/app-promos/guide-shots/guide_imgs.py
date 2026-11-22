"""Crop screenshots/diagrams into WebP and place them as figures in the telarlabs.net guides."""
from PIL import Image
import os, re
S = '/home/claude/shots/guides/'; G = '/home/claude/telarlabs-home/guides/'; O = '/home/claude/telarlabs-home/public/guides/img/'
os.makedirs(O, exist_ok=True)

def save(src, out, crop=None, maxw=1440, pair=None):
    im = Image.open(S + src + '.png').convert('RGB')
    if crop: im = im.crop(crop)
    if pair:  # second phone screenshot side by side
        im2 = Image.open(S + pair[0] + '.png').convert('RGB')
        if pair[1]: im2 = im2.crop(pair[1])
        gap = 24; c = Image.new('RGB', (im.width + im2.width + gap, max(im.height, im2.height)), (22, 19, 28))
        c.paste(im, (0, 0)); c.paste(im2, (im.width + gap, 0)); im = c
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(O + out + '.webp', 'WEBP', quality=82, method=6)
    return im.size

def fig(out, size, alt, cap, phone=False):
    w, h = size
    return (f'\n<figure class="gfig{" phone" if phone else ""}"><img src="/guides/img/{out}.webp" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async">'
            f'<figcaption>{cap}</figcaption></figure>')

PLAN = [
 # slug, anchor (inserted after), image args, alt, caption, phone
 ('reduce-cheating-online-quizzes', 'with the time and how long they were away.', ('qp-dashboard', 'qp-dashboard', (0, 0, 1800, 1050)),
  'QuizPolice teacher dashboard showing students answering, one who left the quiz and one locked after three exits',
  'The QuizPolice teacher dashboard during a quiz: who is answering, who just left, and who was locked after three exits. Sample class.', False),
 ('google-forms-quiz-settings', 'This checklist goes through the settings in the order you’ll find them.', ('d-gforms-checklist', 'gforms-checklist', None),
  'Checklist of Google Forms quiz settings: make it a quiz, release grades later, limit to one response, shuffle questions and options, locked mode, stop accepting responses',
  'The seven settings at a glance. Each one is explained step by step below.', False),
 ('google-forms-quiz-settings', 'and student data is deleted after 30 days.', ('qp-join', 'qp-join', (0, 0, 780, 1120)),
  'QuizPolice student screen with name, section and a notice that leaving the quiz is recorded',
  'What students see before a monitored quiz starts: they know exits are recorded, and how many are allowed.', True),
 ('writing-process-age-of-ai', 'lots of time away from the page.', ('dt-review-flagged', 'drafttrail-review', (130, 470, 1670, 1290)),
  'DraftTrail review screen showing a submission flagged for a large paste and 54 percent of text pasted without a citation',
  'Reviewing a submission in DraftTrail: a large paste is flagged as a reason to ask, with the writing time, revisions and pauses alongside. Sample essays.', False),
 ('projector-tv-classroom-whiteboard', 'but the setups work with most browser-based boards.', ('d-projector-setups', 'projector-setups', None),
  'Three setups: laptop to projector by HDMI cable, tablet to smart TV by casting, phone to projector with a USB-C to HDMI adapter',
  'Three common setups. Start with whichever devices your classroom already has.', False),
 ('projector-tv-classroom-whiteboard', 'Save a page and share it with students who were absent.</li>\n</ul>', ('pp-lesson', 'pizarrapad-lesson', None),
  'A blackboard-style PizarraPad page with a photosynthesis diagram, labels, arrows and a highlighted word equation',
  'A prepared lesson page on a dark board in PizarraPad: shapes, arrows, labels and a highlighter make diagrams easy to read from the back row.', False),
 ('whiteboard-activities-projector-classroom', 'Ask each student to explain their choice in one sentence.', ('pp-activity', 'pizarrapad-sort-activity', None),
  'A greenboard page with two boxes, Living and Non-living, items sorted into each, and one answer circled',
  'Activity 5 on a greenboard: two boxes, items sorted by the class, and one answer circled with the reason.', False),
 ('teaching-when-wifi-drops', 'Files saved on your laptop or phone: PDFs, slides, videos and pictures.</li>\n</ul>', ('d-offline-tools', 'offline-tools', None),
  'Three groups of classroom tools: fully online, offline after the first visit, and fully offline',
  'Sort your tools into these three groups before the lesson, then plan a backup for the first group.', False),
 ('video-sizes-tiktok-reels-shorts-youtube', 'where a taller post takes up more of the screen than a wide one.</li>\n</ul>', ('d-video-shapes', 'video-shapes', None),
  'Four video frames drawn to scale: 9:16 vertical, 16:9 wide, 1:1 square and 4:5 portrait, with the platforms that use each',
  'The shapes side by side, drawn to scale.', False),
 ('video-sizes-tiktok-reels-shorts-youtube', 'A quick way to check: export a test, watch it on your phone inside the app, and pause at each title.', ('d-safe-zones', 'safe-zones', None),
  'A 9:16 frame with the top, bottom and right edges shaded as unsafe and the middle marked for titles and text',
  'Keep anything people must read inside the middle of a vertical video.', False),
 ('school-event-recap-video', '<li><b>The ending.</b> A group photo, the cleanup crew, the empty hall at night.</li>\n</ol>', ('d-recap-storyboard', 'recap-storyboard', None),
  'A five-part storyboard for a one-minute recap: title, setting, main moments, reactions and thank you, with timings',
  'A simple one-minute structure. Give a copy to whoever is filming.', False),
 ('sell-tickets-buyers-pay-you-directly', 'Unpaid reservations expire after the time you choose, and the seats go back on sale.</li>\n</ul>', ('tx-send-proof', 'tixward-pay-and-send-proof', (0, 0, 780, 1500)),
  'Tixward buyer page showing the order, the amount to pay, the time left to pay and the organizer’s e-wallet',
  'What the buyer sees after reserving: how much to pay, to whom, and how long they have to send proof.', True),
 ('sell-tickets-buyers-pay-you-directly', 'What the buyer sees after reserving', ('tx-payments-to-check', 'tixward-payments-to-check', (90, 520, 1560, 1140)),
  'Tixward organizer page listing payments to check, each with a reference number, amount, buyer and Approve and Reject buttons',
  'The organizer’s side: each payment with its reference number and screenshot, ready to check against your own account and approve. Sample data.', False),
 ('google-forms-vs-ticket-page-small-events', '<li><b>Ready-made lists.</b> Attendee lists, sign-in sheets and exports without manual sorting.</li>\n</ul>', ('tx-event-page', 'tixward-event-page', (0, 0, 780, 1500)),
  'A Tixward event page on a phone with a cover image, date, organizer and ticket types with prices and limits',
  'A ticket page on a phone: cover, date, organizer and ticket levels, each with its own limit. Sample event.', True),
 ('class-reunion-planning-checklist', 'A simple timeline keeps the planning calm', ('d-reunion-timeline', 'reunion-timeline', None),
  'A reunion planning timeline from four to six months before, through the night itself, to after the reunion',
  'The whole plan on one line. The sections below go through each step.', False),
 ('class-reunion-planning-checklist', 'Reunions with up to 300 paid tickets are free on Tixward.', ('tx-reunion-attendees', 'tixward-reunion-attendees', (90, 590, 1560, 1140)),
  'Tixward attendee list for a reunion with counts per section, each guest’s section and meal choice, and payment status',
  'Guests counted by section, with each person’s meal choice and whether they have paid. Sample data.', False),
 ('smooth-event-check-in', 'and tickets for other sessions show a warning.', ('tx-door-valid', 'tixward-door-check', (0, 250, 780, 1250), 1440, ('tx-door-used', (0, 250, 780, 1250))),
  'Two phone screens from the Tixward door scanner: a green screen for a valid ticket and a red Already used screen with the time it was first scanned',
  'At the door: green for a valid ticket, red for one already used, with the name and the time it was first scanned.', False),
 ('fitness-classes-limited-slots', 'add the next few weeks at once.', ('tx-zumba-sessions', 'tixward-zumba-sessions', (0, 0, 780, 1150)),
  'Choosing a Zumba session on a phone: four sessions with seats left or sold out, and drop-in and student tickets',
  'Each class time has its own slots. A full session shows as sold out, and buyers pick another.', True),
 ('fitness-classes-limited-slots', 'First-timers who feel welcomed are far more likely to come back.', ('tx-zumba-attendees', 'tixward-zumba-first-timers', (90, 590, 1560, 1140)),
  'Tixward attendee list for a Zumba class showing 19 first-timers and 37 returning members',
  'The answer to “First time doing Zumba?” counted across all sessions, so you know who to welcome. Sample data.', False),
 ('price-tickets-community-event', 'and raises money for the choir’s next trip.', ('d-breakeven', 'breakeven-chart', None),
  'Chart of the break-even ticket price falling as guests increase, with a $7 price line and points at 150 and 180 guests',
  'The break-even price for the choir concert example. At $7, the concert still covers its costs if fewer people come than expected.', False),
 ('school-fundraiser-event-planning', '<li>at the end, you download a list of every order for your report.</li>\n</ul>', ('tx-fundraiser-levels', 'tixward-fundraiser-levels', (0, 0, 780, 1250)),
  'Fundraiser ticket levels on a phone: regular seat, supporter seat, table of 8 and a free volunteer ticket',
  'Ticket levels for a benefit dinner, including a higher supporter seat and free volunteer tickets. Sample event.', True),
]

for slug, anchor, args, alt, cap, phone in PLAN:
    src, out, crop = args[0], args[1], args[2]
    maxw = args[3] if len(args) > 3 else (780 if phone else 1440)
    pair = args[4] if len(args) > 4 else None
    size = save(src, out, crop, maxw, pair)
    f = G + slug + '.html'; s = open(f).read()
    if f'/guides/img/{out}.webp' in s: continue
    i = s.find(anchor)
    if i < 0: anchor = anchor.replace('’', "'"); i = s.find(anchor)
    assert i >= 0, (slug, anchor)
    if not anchor.endswith('>'):        # anchor is text inside a paragraph: insert after that paragraph
        j = s.find('</p>', i); assert j >= 0; i = j + 4
        # if the anchor is inside a figure we just added, insert after the figure instead
        if s.rfind('<figure', 0, i) > s.rfind('</figure>', 0, i): i = s.find('</figure>', i) + 9
    else: i += len(anchor)
    s = s[:i] + fig(out, size, alt, cap, phone) + s[i:]
    open(f, 'w').write(s)
    print('ok', slug, out, size)

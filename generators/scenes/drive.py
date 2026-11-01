"""Re-render illustrated scenes with character/tree/boat motion and rolling waves.
Usage: python3 drive.py 2|3 name [name ...]"""
import sys, os, importlib
sys.path[:0] = ['/home/claude/scenes', '/home/claude/scenes2', '/home/claude/scenes3']
import cv2, numpy as np
from warp import Warp, Swell, render_w
from animate import color_mask

K = 1920 / 1456
Wd, Hd = 1920, 1080

def head(cx, cy, r, px, py, deg=1.5, sp=1, ph=0.0, ry=None):
    return ('sway', cx, cy, r, ry or r, deg, px, py, sp, ph)

WARPS = {
 # ---- batch 2
 'alpine-christmas': [('sway', 1340, 250, 150, 240, 0.6, 1360, 640, 1, 0)],
 'harbour-fireworks': [('bob', 330, 690, 150, 70, 0, 3, 2, 0), ('bob', 870, 705, 140, 70, 0, 3, 2, .3),
                       ('bob', 1180, 712, 140, 70, 0, 3, 2, .6), ('bob', 445, 640, 70, 40, 0, 2, 2, .15)],
 'sakura-lanterns': [('sway', 400, 260, 110, 170, 1.6, 400, 90, 1, 0), ('sway', 735, 450, 100, 150, 1.6, 735, 290, 1, .3),
                     ('sway', 1100, 200, 100, 150, 1.6, 1100, 50, 1, .6), ('sway', 985, 410, 70, 100, 2.0, 985, 315, 1, .8),
                     ('sway', 245, 605, 60, 80, 2.0, 245, 535, 1, .45), ('sway', 1260, 400, 80, 110, 1.8, 1260, 300, 1, .2)],
 'ramadan-town': [('sway', 245, 195, 55, 85, 3.0, 245, 95, 1, 0), ('sway', 185, 310, 50, 80, 3.0, 190, 225, 1, .4),
                  ('sway', 1390, 330, 130, 150, 0.8, 1400, 700, 1, 0)],
 'irish-cottage': [('sway', 950, 380, 240, 130, 0.5, 950, 560, 1, 0), ('bob', 900, 170, 500, 200, 9, 0, 1, 0)],
 'sakura-river': [('sway', 250, 250, 320, 260, 0.5, 230, 600, 1, 0), ('sway', 1250, 300, 300, 290, -0.5, 1300, 650, 1, .4)],
 'xmas-girl': [head(480, 280, 300, 480, 470, 1.5, 1, 0, 260), ('breathe', 470, 640, 330, 220, 0.012, 816, 2, 0)],
 'sparkler-boy': [head(1150, 400, 300, 1150, 640, 1.5), ('breathe', 1150, 700, 260, 160, 0.012, 816, 2, 0),
                  ('bob', 840, 520, 120, 130, 0, 4, 2, .25)],
 'qipao-girl': [head(680, 330, 300, 680, 520, 2.0, 1, 0, 260), ('breathe', 650, 640, 230, 190, 0.015, 816, 2, 0),
                ('sway', 545, 600, 95, 145, 3.0, 590, 480, 1, .25)],
 'umbrella-kids': [head(840, 380, 115, 840, 470, 2.0, 1, 0, 125), head(980, 320, 125, 975, 430, -1.5, 1, .5, 135),
                   ('sway', 930, 160, 240, 120, 1.0, 980, 450, 1, .2), ('sway', 400, 560, 260, 120, 1.2, 400, 750, 2, 0),
                   ('sway', 1300, 700, 190, 150, 1.5, 1300, 816, 2, .3)],
 'shamrock-boy': [head(310, 180, 190, 300, 330, 1.5, 1, 0, 170), ('breathe', 300, 450, 230, 210, 0.012, 700, 2, 0),
                  ('bob', 1100, 180, 420, 160, 10, 0, 1, 0)],
 # ---- batch 3
 'diwali-temple': [('bob', 1100, 150, 420, 160, 10, 0, 1, 0)],
 'sunset-cove': [('sway', 1300, 180, 210, 230, 0.7, 1350, 420, 1, 0), ('bob', 965, 612, 390, 130, 0, 3, 2, 0),
                 ('bob', 500, 250, 460, 160, 8, 0, 1, 0)],
 'rainy-alley': [('sway', 1300, 90, 190, 130, 1.0, 1300, 0, 1, 0), ('sway', 1100, 180, 130, 90, 1.2, 1100, 100, 1, .4)],
 'autumn-park': [('sway', 300, 120, 420, 210, 0.5, 300, 500, 1, 0), ('sway', 1250, 150, 320, 210, -0.5, 1250, 500, 1, .4)],
 'med-steps': [('sway', 880, 230, 180, 170, 1.0, 900, 400, 1, 0), ('sway', 1300, 280, 170, 190, 1.0, 1320, 450, 1, .4),
               ('bob', 190, 560, 55, 70, 0, 3, 2, 0)],
 'starry-lake': [],
 'sakura-girl': [head(1120, 500, 115, 1125, 590, 2.0), ('breathe', 1135, 650, 95, 95, 0.02, 730, 2, 0),
                 ('sway', 1185, 560, 75, 95, 2.5, 1170, 480, 2, .2), ('sway', 800, 200, 720, 270, 0.3, 400, 700, 1, 0)],
 'school-boy': [('bob', 390, 440, 240, 400, 0, 6, 4, 0), head(390, 230, 175, 390, 350, 1.5, 2, 0, 155),
                ('sway', 250, 100, 360, 160, 0.4, 250, 400, 1, 0)],
 'church-kids': [head(150, 230, 100, 150, 330, 1.8, 2, 0), head(290, 260, 100, 290, 350, 1.8, 2, .25),
                 head(445, 245, 100, 445, 340, 1.8, 2, .5), head(600, 270, 100, 600, 360, 1.8, 2, .75)],
 'birthday-twins': [head(420, 360, 300, 420, 660, 1.2, 1, 0), head(1050, 350, 310, 1050, 660, -1.2, 1, .5),
                    ('bob', 870, 140, 170, 150, 0, 6, 1, 0), ('bob', 1370, 330, 120, 160, 0, 5, 1, .3)],
 'beach-boy': [head(950, 440, 210, 950, 560, 1.5, 2, 0, 175), ('breathe', 930, 600, 160, 110, 0.015, 700, 2, 0),
               ('sway', 1280, 150, 270, 210, 1.0, 1400, 400, 1, 0)],
 'reading-girl': [head(1000, 400, 210, 1000, 560, 1.0, 1, 0, 195), ('breathe', 1000, 620, 230, 160, 0.012, 800, 2, 0),
                  ('breathe', 700, 690, 115, 65, 0.03, 740, 2, .3)],
}
SWELL = {
 'beach-boy': ((0, 380, 1000, 650), dict(amp=4.5, wl=60, speed=2, foam=0.15), [(170, 330, 440, 410)]),
 'sunset-cove': ((0, 400, 1456, 816), dict(amp=3.5, wl=55, speed=2, foam=0.12, slant=-0.15), [(610, 505, 1330, 715)]),
}
# lantern-girl was cropped and rescaled (1.486) from the source, so its coordinates are given in output pixels
LANTERN_GIRL = [('sway', 431, 364, 250, 230, 1.5, 431, 557, 1, 0), ('breathe', 431, 765, 200, 230, 0.012, 1077, 2, 0),
                ('sway', 684, 825, 125, 165, 3.0, 669, 587, 1, .25)]

batch = sys.argv[1]
mod = importlib.import_module('scenes2' if batch == '2' else 'scenes3')
os.chdir(f'/home/claude/scenes{batch}')
for n in sys.argv[2:]:
    img = cv2.imread(f'clean/{n}.png')
    focus, zoom, fx, ly = mod.S(n, img)
    if n in SWELL:
        (x0, y0, x1, y1), kw, ex = SWELL[n]
        sc = lambda bx: tuple(int(v * K) for v in bx)
        m = color_mask(img, [sc((x0, y0, x1, y1))], lambda R, G, B: R >= 0, exclude=[sc(e) for e in ex], feather=8)
        fx = [Swell(img, m, **kw)] + fx
    warp = Warp(Wd, Hd, LANTERN_GIRL, 1.0) if n == 'lantern-girl' else (Warp(Wd, Hd, WARPS.get(n, []), K) if WARPS.get(n) else None)
    render_w(n, f'clean/{n}.png', (Wd, Hd), focus, zoom, fx, ly, warp=warp)

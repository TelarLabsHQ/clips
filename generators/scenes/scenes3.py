import sys, os
sys.path.insert(0, '/home/claude/scenes')
import cv2, numpy as np
from animate import *

W, H = 1920, 1080
K = 1920 / 1456

def b(x0, y0, x1, y1):
    return tuple(int(round(v * K)) for v in (x0, y0, x1, y1))

PINK = [(205, 190, 255), (220, 210, 255), (190, 175, 248), (230, 225, 255)]
BOUG = [(120, 40, 230), (150, 70, 245), (100, 30, 210)]
AUTUMN = [(20, 110, 230), (30, 150, 245), (20, 70, 200), (40, 180, 250)]
LEAF_G = [(60, 150, 110), (50, 170, 140), (40, 130, 100)]
CONF = [(60, 60, 235), (40, 200, 255), (200, 160, 30), (90, 200, 60), (210, 90, 200), (40, 140, 255)]
WARM = [(150, 225, 255), (120, 210, 255), (170, 235, 255)]
EMBER = [(80, 170, 255), (60, 140, 255), (120, 200, 255)]
STAR = [(255, 250, 240)]

class MaskedRain:
    """Rain drawn only inside a mask (e.g. a window)."""
    def __init__(self, mask, **kw):
        self.r = Rain(W, H, **kw); self.m = mask
    def draw(self, frame, t):
        layer = np.zeros_like(frame); self.r.draw(layer, t)
        frame += layer * self.m

def all_mask(img, fn, feather=1.5, boxes=None):
    return color_mask(img, boxes or [(0, 0, W, H)], fn, feather=feather)

def S(n, img):
    fx, ly = [], []
    if n == 'diwali-temple':
        fl = all_mask(img, lambda R, G, B: (R > 230) & (G > 170) & (R - B > 60))
        fx = [Twinkle(img, fl, strength=0.45, sigma=2.5, bloom=0.18, color=(90, 170, 255))]
        ly = [Fall(W, H, 22, 'glow', EMBER, size=(2, 4), speed=(1, 1), sway=25, slant=0.05, alpha=0.8, seed=3, rise=True),
              Float(W, H, 30, 'sparkle', STAR, size=(1.2, 2.4), region=b(500, 0, 1456, 300), drift=2, alpha=0.7)]
        return (900, 560), 0.025, fx, ly
    if n == 'sunset-cove':
        wm = color_mask(img, [b(0, 395, 1456, 816)], lambda R, G, B: (G > R) | (B > R),
                        exclude=[b(610, 505, 1330, 715)])
        fx = [Water(img, wm, amp=2.2, wl=22, glint=28, glint_color=(170, 210, 255))]
        ly = [Birds(W, H, 5, (120, 300), color=(80, 70, 90), size=(9, 14), seed=4)]
        return (700, 520), 0.025, fx, ly
    if n == 'rainy-alley':
        lm = all_mask(img, lambda R, G, B: (R > 200) & (R - B > 80), feather=3)
        st = color_mask(img, [b(380, 480, 1050, 816)], lambda R, G, B: R >= 0)
        fx = [Glow(img, lm, color=(60, 120, 255), strength=0.08, bloom=0.2), Water(img, st, amp=1.6, wl=16, glint=18, glint_color=(120, 180, 255))]
        ly = [Rain(W, H, n=280, slant=0.08, alpha=(0.12, 0.3))]
        return (960, 520), 0.025, fx, ly
    if n == 'autumn-park':
        g = all_mask(img, lambda R, G, B: (R + G + B) > 450, feather=6)
        fx = [Dapple(img, g, strength=0.10, seed=8)]
        ly = [Fall(W, H, 34, 'leaf', AUTUMN, size=(8, 14), speed=(1, 1), sway=45, slant=0.25, alpha=0.95, seed=9),
              Float(W, H, 30, 'glow', WARM, size=(1.6, 3), region=b(500, 100, 1300, 650), drift=30, alpha=0.5)]
        return (900, 540), 0.025, fx, ly
    if n == 'med-steps':
        sea = color_mask(img, [b(0, 512, 640, 770)], lambda R, G, B: B > R + 40)
        fx = [Water(img, sea, amp=1.6, wl=16, glint=35)]
        ly = [Fall(W, H, 22, 'petal', BOUG, size=(6, 10), speed=(1, 1), sway=35, slant=-0.2, region=b(600, 0, 1456, 816), alpha=0.95, seed=12),
              Birds(W, H, 4, (100, 320), color=(90, 90, 100), size=(9, 13), seed=13, direction=-1)]
        return (700, 500), 0.025, fx, ly
    if n == 'starry-lake':
        wm = color_mask(img, [b(0, 650, 1456, 816)], lambda R, G, B: R >= 0, exclude=[b(0, 720, 640, 816)])
        win = color_mask(img, [b(1020, 570, 1160, 625), b(1020, 670, 1160, 720)], lambda R, G, B: R > 170, feather=3)
        fx = [Water(img, wm, amp=1.8, wl=20, glint=20, glint_color=(255, 220, 230)), Glow(img, win, color=(90, 130, 255), strength=0.12, bloom=0.35)]
        ly = [Float(W, H, 70, 'sparkle', STAR, size=(1.3, 2.8), region=b(0, 0, 1456, 450), drift=2, alpha=0.9),
              Float(W, H, 14, 'glow', [(150, 255, 230)], size=(2, 3.5), region=b(0, 560, 1000, 700), drift=30, alpha=0.7)]
        return (900, 500), 0.025, fx, ly
    if n == 'sakura-girl':
        ly = [Fall(W, H, 60, 'petal', PINK, size=(6, 11), speed=(1, 2), sway=30, slant=0.18, alpha=0.92, seed=21)]
        return (1200, 600), 0.025, fx, ly
    if n == 'school-boy':
        g = all_mask(img, lambda R, G, B: (G > R) & (G > B), feather=6)
        fx = [Dapple(img, g, strength=0.07, seed=22)]
        ly = [Birds(W, H, 4, (60, 240), color=(80, 80, 85), size=(9, 13), seed=23),
              Fall(W, H, 8, 'leaf', LEAF_G, size=(8, 12), speed=(1, 1), sway=40, slant=0.3, alpha=0.9, seed=24)]
        return (500, 500), 0.025, fx, ly
    if n == 'church-kids':
        g = all_mask(img, lambda R, G, B: (G > R) & (G > B), feather=6)
        fx = [Dapple(img, g, strength=0.07, seed=31)]
        ly = [Birds(W, H, 4, (60, 220), color=(80, 80, 85), size=(9, 13), seed=32),
              Float(W, H, 26, 'glow', WARM, size=(1.6, 3), region=b(0, 100, 1456, 700), drift=30, alpha=0.5)]
        return (800, 520), 0.025, fx, ly
    if n == 'birthday-twins':
        cd = color_mask(img, [b(640, 580, 960, 720)], lambda R, G, B: (R > 230) & (G > 180), feather=2)
        fx = [Glow(img, cd, color=(110, 200, 255), strength=0.15, bloom=0.5)]
        ly = [Fall(W, H, 45, 'confetti', CONF, size=(5, 8), speed=(1, 2), sway=30, slant=0.1, alpha=0.9, seed=41)]
        return (960, 600), 0.025, fx, ly
    if n == 'beach-boy':
        sea = color_mask(img, [b(0, 380, 1000, 650)], lambda R, G, B: (B > R + 20) | (R + G + B > 600), exclude=[b(170, 330, 440, 410)])
        fx = [Water(img, sea, amp=2.4, wl=24, glint=25)]
        ly = [Birds(W, H, 4, (80, 300), color=(90, 90, 100), size=(9, 13), seed=51)]
        return (900, 560), 0.025, fx, ly
    if n == 'reading-girl':
        win = cv2.GaussianBlur(box_mask(img.shape, [b(115, 0, 800, 380)]), (0, 0), 4)[..., None]
        lamp = color_mask(img, [b(300, 220, 560, 640)], lambda R, G, B: (R > 220) & (G > 150), feather=3)
        fx = [Glow(img, lamp, color=(90, 160, 255), strength=0.10, bloom=0.35)]
        ly = [MaskedRain(win, n=220, slant=0.05, alpha=(0.15, 0.35), color=(255, 230, 210))]
        return (1100, 560), 0.025, fx, ly

if __name__ == '__main__':
    os.chdir('/home/claude/scenes3')
    for n in sys.argv[1:]:
        img = cv2.imread(f'clean/{n}.png')
        focus, zoom, fx, ly = S(n, img)
        render(n, f'clean/{n}.png', (W, H), focus, zoom, fx, ly)

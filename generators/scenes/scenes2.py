import sys
sys.path.insert(0, '/home/claude/scenes')
import cv2, numpy as np
from animate import *

W, H = 1920, 1080
K = 1920 / 1456  # source-image coords -> video coords

def b(x0, y0, x1, y1, k=K):
    return tuple(int(round(v * k)) for v in (x0, y0, x1, y1))

SNOW = [(255, 255, 255), (250, 245, 240)]
PINK = [(220, 205, 255), (235, 225, 255), (205, 185, 250)]
SAKURA = [(205, 190, 255), (220, 210, 255), (190, 175, 248), (230, 225, 255)]
PLUM = [(60, 50, 220), (90, 80, 240), (120, 110, 250)]
WARM = [(150, 225, 255), (120, 210, 255), (170, 235, 255)]
FIRE = [(150, 225, 255), (255, 200, 150), (200, 150, 255), (120, 210, 255)]
STAR = [(255, 250, 240)]

def snow(n, size, seed, speed=(1, 1), alpha=0.85, sway=15):
    f = Fall(W, H, n, 'glow', SNOW, size=size, speed=speed, sway=sway, slant=0.08, alpha=alpha, seed=seed)
    f.add_glow = False
    return f

def S(n, img):
    L = img.astype(np.float32).mean(axis=2)
    fx, ly = [], []
    if n == 'alpine-christmas':
        m = color_mask(img, [(0, 0, W, H)], lambda R, G, B: (R > 200) & (G > 140) & (R - B > 60), feather=1.5)
        fx = [Twinkle(img, m, strength=0.45, sigma=3, bloom=0.12, color=(110, 190, 255))]
        ly = [snow(170, (1.2, 3.0), 1), snow(22, (3.2, 5.0), 2, speed=(1, 2), alpha=0.9, sway=30)]
        return (960, 560), 0.03, fx, ly
    if n == 'harbour-fireworks':
        wm = color_mask(img, [b(0, 600, 520, 816), b(520, 632, 1456, 816)], lambda R, G, B: R >= 0,
                        exclude=[b(185, 575, 435, 748), b(395, 600, 500, 668), b(740, 640, 1000, 765), b(1050, 595, 1305, 770),
                                 b(100, 470, 235, 645), b(0, 600, 85, 665)])
        fw = color_mask(img, [b(520, 0, 1300, 450)], lambda R, G, B: (R + G + B) > 420, feather=1.5)
        lm = color_mask(img, [b(325, 572, 362, 618), b(445, 602, 478, 642), b(1192, 592, 1232, 648)],
                        lambda R, G, B: (R > 200) & (G > 130), feather=2)
        fx = [Water(img, wm, amp=2.2, wl=20, glint=25, glint_color=(170, 220, 255)),
              Twinkle(img, fw, strength=0.55, sigma=3), Glow(img, lm, color=(90, 170, 255), strength=0.12, bloom=0.35)]
        ly = [Float(W, H, 34, 'sparkle', FIRE, size=(2, 4), region=b(540, 20, 1280, 420), drift=20, alpha=0.95)]
        return (1000, 420), 0.025, fx, ly
    if n == 'sakura-lanterns':
        lm = color_mask(img, [(0, 0, W, H)], lambda R, G, B: (R > 200) & (R - B > 100), feather=3)
        bk = color_mask(img, [(0, 0, W, H)], lambda R, G, B: (R + G + B) > 560, feather=1.5)
        fx = [Glow(img, lm, color=(60, 110, 255), strength=0.08, bloom=0.22), Twinkle(img, bk, strength=0.3, sigma=4)]
        ly = [Fall(W, H, 40, 'petal', PINK, size=(6, 10), speed=(1, 2), sway=30, slant=0.12, alpha=0.9, seed=3)]
        return (960, 480), 0.03, fx, ly
    if n == 'ramadan-town':
        wl = color_mask(img, [b(0, 380, 1456, 816)], lambda R, G, B: (R > 180) & (R - B > 80), feather=1.5)
        hl = color_mask(img, [b(150, 100, 300, 390)], lambda R, G, B: (R > 140) & (R - B > 50), feather=2)
        fx = [Twinkle(img, wl, strength=0.45, sigma=3, bloom=0.1, color=(90, 160, 255)),
              Glow(img, hl, color=(80, 160, 255), strength=0.12, bloom=0.3)]
        ly = [Float(W, H, 45, 'sparkle', STAR, size=(1.3, 2.6), region=b(330, 20, 1456, 320), drift=2, alpha=0.85)]
        return (960, 560), 0.025, fx, ly
    if n == 'irish-cottage':
        g = color_mask(img, [b(0, 380, 1456, 816)], lambda R, G, B: (G > R) & (G > B), feather=6)
        fx = [Dapple(img, g, strength=0.10, seed=21)]
        ly = [Birds(W, H, 4, (90, 260), color=(70, 70, 75), size=(9, 14), seed=5),
              Float(W, H, 26, 'glow', WARM, size=(1.6, 3), region=b(0, 420, 1456, 816), drift=30, alpha=0.5)]
        return (900, 560), 0.025, fx, ly
    if n == 'sakura-river':
        wm = color_mask(img, [b(0, 645, 1456, 816)], lambda R, G, B: R >= 0)
        fx = [Water(img, wm, amp=2.0, wl=22, glint=22, glint_color=(255, 240, 250))]
        ly = [Fall(W, H, 55, 'petal', SAKURA, size=(6, 11), speed=(1, 2), sway=30, slant=0.15, alpha=0.9, seed=7)]
        return (960, 520), 0.03, fx, ly
    if n == 'xmas-girl':
        tl = color_mask(img, [b(690, 100, 1040, 780), b(700, 0, 1456, 600)], lambda R, G, B: (R + G + B > 600) | ((R > 200) & (R - B > 90)), feather=1.5)
        wg = color_mask(img, [b(0, 0, 340, 350)], lambda R, G, B: (R > 230) & (G > 180), feather=4)
        fx = [Twinkle(img, tl, strength=0.35, sigma=3), Glow(img, wg, color=(110, 200, 255), strength=0.04, bloom=0.08)]
        ly = [snow(120, (1.2, 3.0), 9), snow(16, (3.0, 4.6), 10, speed=(1, 2), alpha=0.9, sway=25)]
        return (520, 460), 0.025, fx, ly
    if n == 'sparkler-boy':
        sp = color_mask(img, [b(790, 395, 880, 470)], lambda R, G, B: (R + G + B) > 600, feather=2)
        cl = color_mask(img, [b(0, 420, 1100, 816)], lambda R, G, B: (R > 200) & (G > 110) & (R - B > 70), feather=1.5)
        fx = [Glow(img, sp, color=(150, 220, 255), strength=0.15, bloom=0.6), Twinkle(img, cl, strength=0.4, sigma=3)]
        ly = [Float(W, H, 28, 'sparkle', WARM + [(255, 255, 255)], size=(2, 4.5), region=b(760, 360, 910, 500), drift=35, alpha=1.0),
              Float(W, H, 16, 'glow', WARM, size=(4, 8), region=b(0, 0, 1000, 420), drift=40, alpha=0.45)]
        return (1100, 520), 0.025, fx, ly
    if n == 'qipao-girl':
        lm = color_mask(img, [(0, 0, W, H)], lambda R, G, B: (R > 220) & (R - B > 90), feather=3)
        fx = [Glow(img, lm, color=(60, 120, 255), strength=0.07, bloom=0.18)]
        ly = [Fall(W, H, 26, 'petal', PLUM, size=(6, 10), speed=(1, 2), sway=30, slant=-0.1, alpha=0.95, seed=11),
              Float(W, H, 20, 'glow', WARM, size=(2, 4), region=(0, 0, W, H), drift=30, alpha=0.5)]
        return (740, 430), 0.025, fx, ly
    if n == 'umbrella-kids':
        hb = color_mask(img, [b(0, 0, 1456, 470)], lambda R, G, B: (R + G + B) > 470, feather=4)
        wm = color_mask(img, [b(0, 650, 640, 816)], lambda R, G, B: (B > 90) & (G < R + 40) & ~((R > 180) & (B < 150)))
        fx = [Twinkle(img, hb, strength=0.18, sigma=12), Water(img, wm, amp=1.5, wl=18, glint=15)]
        ly = [Rain(W, H, n=240, slant=-0.05, alpha=(0.15, 0.35))]
        return (1000, 460), 0.025, fx, ly
    if n == 'lantern-girl':
        lm = color_mask(img, [(600, 540, 820, 930)], lambda R, G, B: (R > 200) & (G > 140), feather=3)
        fx = [Glow(img, lm, color=(110, 190, 255), strength=0.14, bloom=0.45)]
        ly = [Float(W, H, 18, 'glow', WARM, size=(1.6, 3.2), region=(560, 480, 880, 950), drift=40, alpha=0.8),
              Float(W, H, 45, 'sparkle', STAR, size=(1.3, 2.6), region=(1000, 60, 1900, 640), drift=2, alpha=0.85)]
        return (720, 560), 0.025, fx, ly
    if n == 'shamrock-boy':
        g = color_mask(img, [b(0, 380, 1456, 816)], lambda R, G, B: (G > R) & (G > B), feather=6)
        fx = [Dapple(img, g, strength=0.08, seed=31)]
        ly = [Birds(W, H, 4, (120, 330), color=(80, 80, 85), size=(9, 14), seed=6, direction=-1),
              Float(W, H, 22, 'glow', WARM, size=(1.6, 3), region=b(300, 300, 1456, 816), drift=30, alpha=0.5)]
        return (420, 520), 0.025, fx, ly

if __name__ == '__main__':
    import os
    os.chdir('/home/claude/scenes2')
    for n in sys.argv[1:]:
        img = cv2.imread(f'clean/{n}.png')
        focus, zoom, fx, ly = S(n, img)
        render(n, f'clean/{n}.png', (W, H), focus, zoom, fx, ly)

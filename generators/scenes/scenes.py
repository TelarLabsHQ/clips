import sys, cv2
from animate import *

SAKURA = [(205, 190, 255), (220, 210, 255), (190, 175, 248), (230, 225, 255)]
BOUGAIN = [(200, 60, 190), (225, 95, 215), (175, 40, 160), (235, 130, 230)]
MARIGOLD = [(20, 150, 250), (30, 190, 255), (10, 120, 240), (40, 210, 255)]
CONFETTI = [(60, 60, 235), (40, 200, 255), (200, 160, 30), (90, 200, 60), (210, 90, 200), (40, 140, 255), (230, 200, 60)]
LEAVES = [(60, 150, 110), (50, 170, 140), (40, 120, 90), (70, 190, 200)]
WARM = [(150, 225, 255), (120, 210, 255)]
FIREFLY = [(150, 255, 230), (120, 240, 255)]
GOLD = [(80, 210, 255), (120, 230, 255)]

def load(n):
    return cv2.imread(f'clean/{n}.png')

def S(n):
    W, H = (1080, 1350) if n in ('bamboo-torii', 'santorini-sunset') else (1080, 1080)
    img = load(n)
    fx, ly = [], []
    if n == 'bamboo-torii':
        m = color_mask(img, [(220, 560, 480, 800), (780, 360, 980, 600), (960, 640, 1080, 920), (560, 600, 800, 800)],
                       lambda R, G, B: (R > 190) & (G > 80) & (R - B > 60), feather=3)
        fx = [Glow(img, m, color=(70, 110, 255), strength=0.12, bloom=0.35)]
        ly = [Float(W, H, 26, 'glow', FIREFLY, size=(2.5, 4.5), region=(0, 480, 1080, 1350), drift=30, alpha=0.8),
              Fall(W, H, 45, 'petal', SAKURA, size=(6, 11), speed=(1, 2), sway=25, slant=0.12, alpha=0.9)]
        return W, H, (540, 620), 0.035, fx, ly
    if n == 'santorini-sunset':
        m = color_mask(img, [(600, 380, 920, 660)], lambda R, G, B: (R > 200) & (B < 170) & (G > 90), feather=3)
        fx = [Water(img, m, amp=1.4, wl=16, glint=45, glint_color=(170, 225, 255))]
        ly = [Fall(W, H, 30, 'petal', BOUGAIN, size=(6, 11), speed=(1, 1), sway=35, slant=-0.15, alpha=0.92, seed=21)]
        return W, H, (720, 520), 0.03, fx, ly
    if n == 'courtyard':
        L = img.mean(axis=2)
        m = cv2.GaussianBlur(((L > 150).astype(np.float32)), (0, 0), 6)[..., None]
        g = color_mask(img, [(820, 230, 1080, 460)], lambda R, G, B: (R > 170) & (R - G > 60), feather=3)
        fx = [Dapple(img, m, strength=0.09), Glow(img, g, color=(60, 120, 255), strength=0.05, bloom=0.2)]
        ly = [Float(W, H, 30, 'glow', WARM, size=(2, 3.5), region=(0, 0, 1080, 900), drift=35, alpha=0.55),
              Fall(W, H, 10, 'leaf', LEAVES, size=(8, 13), speed=(1, 1), sway=45, slant=0.3, alpha=0.95, seed=31)]
        return W, H, (560, 700), 0.03, fx, ly
    if n == 'palawan':
        m = color_mask(img, [(560, 560, 1030, 930)], lambda R, G, B: (B > R + 15) & (G > R + 5) & (R + G + B > 380) & (R + G + B < 680),
                       exclude=[(560, 600, 950, 805), (750, 565, 935, 650)])
        fx = [Water(img, m, amp=2.0, wl=22, glint=35)]
        ly = [Birds(W, H, 5, (240, 380), color=(95, 95, 100), size=(8, 13))]
        return W, H, (560, 560), 0.03, fx, ly
    if n == 'japan':
        ly = [Fall(W, H, 34, 'petal', SAKURA, size=(6, 11), speed=(1, 2), sway=25, slant=0.32, region=(60, 120, 700, 1000), alpha=0.9, seed=41)]
        return W, H, (560, 560), 0.025, fx, ly
    if n == 'ireland':
        m = color_mask(img, [(150, 555, 1030, 930)], lambda R, G, B: (B > R + 8) & (R + G + B > 300) & (R + G + B < 690),
                       exclude=[(360, 200, 720, 1020)])
        fx = [Water(img, m, amp=2.4, wl=30, glint=30)]
        ly = [Float(W, H, 9, 'sparkle', GOLD, size=(3, 5.5), region=(420, 560, 570, 660), drift=12, alpha=0.95)]
        return W, H, (540, 600), 0.025, fx, ly
    if n == 'mexico':
        m = color_mask(img, [(700, 410, 1030, 945), (560, 410, 700, 520)], lambda R, G, B: (B > R + 25) & (G > R))
        fx = [Water(img, m, amp=2.0, wl=22, glint=30)]
        ly = [Fall(W, H, 26, 'marigold', MARIGOLD, size=(5, 9), speed=(1, 2), sway=30, slant=0.1, alpha=0.95, seed=51)]
        return W, H, (560, 520), 0.025, fx, ly
    if n == 'korea':
        ly = [Fall(W, H, 28, 'petal', SAKURA, size=(6, 11), speed=(1, 2), sway=25, slant=0.2, alpha=0.9, seed=61)]
        return W, H, (420, 560), 0.025, fx, ly
    if n == 'greece':
        m = color_mask(img, [(0, 150, 380, 600)], lambda R, G, B: (B > R + 40) & (R + G + B < 470))
        fx = [Water(img, m, amp=1.6, wl=16, glint=30)]
        ly = [Birds(W, H, 4, (60, 190), color=(85, 85, 90), size=(8, 12), direction=-1, seed=71)]
        return W, H, (620, 560), 0.03, fx, ly
    if n == 'vietnam':
        m = color_mask(img, [(40, 575, 1040, 905)], lambda R, G, B: (B > R + 5) & (G > R + 5) & (R + G + B > 330) & (R + G + B < 690),
                       exclude=[(420, 250, 760, 1010), (690, 560, 880, 680)])
        fx = [Water(img, m, amp=2.0, wl=24, glint=30)]
        ly = [Float(W, H, 10, 'sparkle', [(255, 255, 255)], size=(2.5, 4.5), region=(60, 620, 1020, 860), drift=10, alpha=0.8)]
        return W, H, (540, 600), 0.025, fx, ly
    if n == 'brazil':
        ly = [Float(W, H, 14, 'sparkle', GOLD, size=(4, 7), region=(220, 150, 880, 880), drift=15, alpha=0.9),
              Fall(W, H, 60, 'confetti', CONFETTI, size=(5, 8), speed=(1, 2), sway=30, slant=0.1, alpha=0.95, seed=81)]
        return W, H, (540, 540), 0.03, fx, ly
    if n == 'portugal':
        m = color_mask(img, [(40, 600, 240, 712), (480, 620, 620, 705)], lambda R, G, B: (B > R + 20) & (R + G + B < 720))
        fx = [Water(img, m, amp=1.5, wl=14, glint=25)]
        ly = [Birds(W, H, 4, (130, 300), color=(85, 85, 90), size=(8, 12), seed=91)]
        return W, H, (560, 560), 0.025, fx, ly

if __name__ == '__main__':
    for n in sys.argv[1:]:
        W, H, focus, zoom, fx, ly = S(n)
        render(n, f'clean/{n}.png', (W, H), focus, zoom, fx, ly)

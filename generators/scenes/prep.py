"""Clean masters: crop, remove baked-in words, export square/portrait PNGs."""
import numpy as np, cv2
from PIL import Image

F = 2500 / 1932  # display coords -> original coords for 2500px images

def load(n):
    return cv2.cvtColor(np.array(Image.open(f'src/{n}.png').convert('RGB')), cv2.COLOR_RGB2BGR)

def box(img, x0, y0, x1, y1, scale=F):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = [int(round(v * scale)) for v in (x0, y0, x1, y1)]
    return max(0, x0), max(0, y0), min(w, x1), min(h, y1)

def white_fill(img, b, thr=40):
    """Text on white paper: everything non-white in the box becomes white (soft edges)."""
    x0, y0, x1, y1 = b
    reg = img[y0:y1, x0:x1].astype(np.float32)
    # distance from white
    d = 255 - reg.min(axis=2)
    m = (d > 6).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((9, 9), np.uint8))
    m = cv2.GaussianBlur(m, (0, 0), 2).astype(np.float32)[..., None] / 255
    paper = np.full_like(reg, 255)
    out = (reg * (1 - m) + paper * m)
    out[(255 - out.min(axis=2)) < 14] = 255
    img[y0:y1, x0:x1] = out.astype(np.uint8)

def inpaint_mask(img, mask, r=9):
    mask = cv2.dilate(mask, np.ones((7, 7), np.uint8))
    return cv2.inpaint(img, mask, r, cv2.INPAINT_TELEA)

def color_mask(img, b, fn):
    x0, y0, x1, y1 = b
    m = np.zeros(img.shape[:2], np.uint8)
    reg = img[y0:y1, x0:x1].astype(int)
    B, G, R = reg[..., 0], reg[..., 1], reg[..., 2]
    m[y0:y1, x0:x1] = fn(R, G, B).astype(np.uint8) * 255
    return m

def save(n, img, size):
    out = cv2.resize(img, size, interpolation=cv2.INTER_AREA if img.shape[1] > size[0] else cv2.INTER_LANCZOS4)
    if img.shape[1] < size[0]:  # upscaled: gentle sharpen
        bl = cv2.GaussianBlur(out, (0, 0), 1.2)
        out = cv2.addWeighted(out, 1.35, bl, -0.35, 0)
    cv2.imwrite(f'clean/{n}.png', out)

SQ = (1080, 1080)
PT = (1080, 1350)

# --- white-paper illustrations: words on white ---
jobs = {
    'palawan': [(700, 1610, 1220, 1720)],
    'japan': [(1370, 630, 1680, 745), (1560, 420, 1640, 540)],
    'ireland': [(1225, 610, 1660, 800), (1170, 660, 1240, 800)],
    'mexico': [(1310, 190, 1650, 300), (1310, 300, 1500, 335)],
    'korea': [(1110, 280, 1650, 556)],
    'brazil': [(770, 1600, 1160, 1730)],
    'portugal': [(345, 660, 780, 840)],
}
for n, boxes in jobs.items():
    img = load(n)
    for bx in boxes:
        white_fill(img, box(img, *bx))
    if n == 'ireland':
        b = box(img, 1140, 600, 1250, 810)
        m = color_mask(img, b, lambda R, G, B: (G > R + 15) & (G > B))
        m = cv2.dilate(m, np.ones((9, 9), np.uint8))
        img[m > 0] = 255
    if n == 'japan':  # scribbled "signature" on the lantern base
        b = box(img, 470, 1580, 660, 1650)
        m = color_mask(img, b, lambda R, G, B: (R + G + B) < 330)
        img = inpaint_mask(img, m)
    if n == 'portugal':  # tiny mark on the wall, and the thin frame line
        b = box(img, 1360, 1360, 1410, 1410)
        m = color_mask(img, b, lambda R, G, B: (R + G + B) < 600)
        img = inpaint_mask(img, m)
        x0, y0, x1, y1 = box(img, 175, 175, 1758, 1758)
        img = img[y0:y1, x0:x1]
    cv2.imwrite(f'chk/{n}-clean-full.png', img)
    save(n, img, SQ)

# Vietnam: gold signature partly touching the rock edge -> inpaint
img = load('vietnam')
b = box(img, 1330, 1620, 1660, 1760)
m = color_mask(img, b, lambda R, G, B: (R - B > 35) & (R > G) & (G > B))
m = cv2.dilate(m, np.ones((11, 11), np.uint8))
img[m > 0] = 255
white_fill(img, box(img, 1330, 1695, 1660, 1760))
cv2.imwrite('chk/vietnam-clean-full.png', img); save('vietnam', img, SQ)

# Courtyard: crop the painted square (drop white border); fake shop-sign characters -> plain board
img = load('courtyard')
m = np.zeros(img.shape[:2], np.uint8)
for bx in [(1355, 600, 1440, 668), (1492, 600, 1600, 668)]:
    m |= color_mask(img, box(img, *bx), lambda R, G, B: (R > 120) & (G > 0.55 * R) & (R - B > 40))
img = inpaint_mask(img, m, 6)
x0, y0, x1, y1 = box(img, 140, 142, 1795, 1795)
img = img[y0:y1, x0:x1]
cv2.imwrite('chk/courtyard-clean-full.png', img); save('courtyard', img, SQ)

# Greece (phone screenshot, 1:1 coords): remove GREECE from the sky, crop square
img = load('greece')
b = (70, 395, 395, 480)
m = color_mask(img, b, lambda R, G, B: (B - R > 30) & (R < 120))
img = inpaint_mask(img, m, 12)
img = img[445:1119, 45:719]
cv2.imwrite('chk/greece-clean-full.png', img); save('greece', img, SQ)

# Bamboo torii (screenshot) -> 4:5 portrait
img = load('bamboo-torii')[300:1125, 30:690]
save('bamboo-torii', img, PT)

# Santorini (screenshot-ish, dark bar on top) -> 4:5 portrait
img = load('santorini-sunset')[150:987, 0:670]
save('santorini-sunset', img, PT)
print('ok')

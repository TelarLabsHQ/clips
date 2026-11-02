"""Green-screen cutout v2: chroma key with hue test (removes darker green shadows), colour unmixing on soft edges
(no green fringe on glows), despill, largest-subject cleanup."""
import sys, numpy as np, cv2
from PIL import Image
def cut(src, dst, keep_frac=0.02):
    im = cv2.imread(src).astype(np.float32); h, w = im.shape[:2]
    b, g, r = im[..., 0], im[..., 1], im[..., 2]
    border = np.concatenate([im[:6].reshape(-1, 3), im[-6:].reshape(-1, 3), im[:, :6].reshape(-1, 3), im[:, -6:].reshape(-1, 3)])
    bg = np.median(border, 0)                      # BGR of the screen
    # greenness: how much green exceeds the other channels, relative to the screen's own greenness
    gx = g - np.maximum(r, b); gbg = bg[1] - max(bg[0], bg[2])
    k = np.clip(gx / max(gbg, 1), 0, 1.2)          # ~1 on the screen (also on darker green shadows), ~0 on the subject
    a = np.clip((0.62 - k) / 0.45, 0, 1)           # opaque below ~0.17, clear above ~0.62
    m = (a > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.isin(lab, [i for i in range(1, n) if st[i, 4] > keep_frac * h * w])
    a = a * cv2.dilate(keep.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    a = cv2.GaussianBlur(a, (0, 0), 0.7)
    # unmix: C = a*F + (1-a)*BG  ->  F = (C - (1-a)*BG)/a  on soft pixels
    A = np.clip(a, 1e-3, 1)[..., None]
    F = np.where(a[..., None] < 0.995, (im - (1 - A) * bg) / A, im)
    F = np.clip(F, 0, 255)
    fb, fg, fr = F[..., 0], F[..., 1], F[..., 2]
    fg = np.minimum(fg, np.maximum(fr, fb) * 1.03 + 4)   # despill
    rgba = np.dstack([fr, fg, fb, a * 255]).clip(0, 255).astype(np.uint8)
    ys, xs = np.where(a > 0.05); pad = 8
    rgba = rgba[max(0, ys.min() - pad):ys.max() + pad, max(0, xs.min() - pad):xs.max() + pad]
    Image.fromarray(rgba, 'RGBA').save(dst)
if __name__ == '__main__':
    cut(sys.argv[1], sys.argv[2])

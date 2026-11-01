"""Single-stroke handwriting paths (Hershey fonts) for scripted board writing."""
import json, sys, random
from HersheyFonts import HersheyFonts
def strokes(text, x, y, h, font='futural', jitter=0.6, seed=1):
    f = HersheyFonts(); f.load_default_font(font); f.normalize_rendering(h)
    rnd = random.Random(seed); out = []
    for st in f.strokes_for_text(text):
        out.append([[round(x + px + rnd.uniform(-jitter, jitter), 1), round(y - py + rnd.uniform(-jitter, jitter), 1)] for px, py in st])
    return out
if __name__ == '__main__':
    spec = json.loads(sys.argv[1])
    print(json.dumps({k: strokes(**v) for k, v in spec.items()}))

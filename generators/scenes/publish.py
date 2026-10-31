"""Copy finished scene clips into the Telar Clips repo: named full files (for R2), previews and posters."""
import json, os, subprocess, shutil
REPO = '/home/claude/telar-clips'
FULL = '/home/claude/scenes/upload'
os.makedirs(FULL, exist_ok=True)
clips = [c for c in json.load(open(f'{REPO}/data/clips.json')) if c.get('illustrated')]
for c in clips:
    src = f'/home/claude/scenes/out/{c["src"]}.mp4'
    dst = f'{FULL}/{c["file"]}'
    shutil.copy(src, dst)
    w, h = c['width'], c['height']
    sc = '480:480' if w == h else '432:540'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', f'scale={sc}', '-an', '-c:v', 'libx264', '-preset', 'veryfast',
                    '-crf', '28', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{REPO}/public/media/preview/{c["id"]}.mp4'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '4', '-i', src, '-frames:v', '1', '-vf', f'scale={sc}', '-q:v', '82',
                    f'{REPO}/public/media/poster/{c["id"]}.webp'], check=True)
    print('ok', c['id'])

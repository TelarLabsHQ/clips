"""Pre-made AI narration for built-in Telar Stories (Kokoro af_heart, speed 0.95 = the app's default)."""
import json, re, subprocess, sys, soundfile as sf
from kokoro_onnx import Kokoro
K = Kokoro('/tmp/kok/kokoro-v1.0.onnx', '/tmp/kok/voices-v1.0.bin')
OUT = '/home/claude/telarlabs-home/public/stories-demo/assets/voice/'
PRON = {'Mochi': 'Mowchee'}
def spoken(title, text):
    t = '. '.join(x for x in [title, text] if x)
    for a, b in PRON.items(): t = re.sub(r'\b' + a + r'\b', b, t)
    return re.sub('["“”]', '', t).strip()
def make(story, scenes):
    for i, (title, text) in enumerate(scenes, 1):
        s = spoken(title, text)
        if not s: continue
        a, sr = K.create(s, voice='af_heart', speed=0.95, lang='en-us')
        sf.write('/tmp/v.wav', a, sr)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/v.wav', '-ac', '1', '-c:a', 'aac', '-b:a', '64k', f'{OUT}{story}/s{i}.m4a'], check=True)
        print(story, i, round(len(a) / sr, 1), 's', flush=True)
XMAS = [
 ('The First Christmas', 'A story from the Bible.'),
 ('', 'Long ago, in a little town called Nazareth, lived a young woman named Mary. One day, an angel named Gabriel came to visit her.'),
 ('', '"Do not be afraid, Mary," said the angel. "God is with you. You will have a baby boy, and you will name him Jesus."'),
 ('', 'Mary married a kind carpenter named Joseph. The king ordered everyone to be counted in their hometown, so they made the long trip to Bethlehem.'),
 ('', 'When they arrived, Bethlehem was crowded with people. There was no room for them anywhere.'),
 ('', 'A kind innkeeper let them stay in his stable. It was quiet and warm, with the animals all around.'),
 ('', 'That night, baby Jesus was born. Mary wrapped him in soft cloths and laid him in a manger.'),
 ('', 'Out in the fields, shepherds were watching their sheep. Suddenly, an angel appeared! "I bring you good news of great joy. Today a Savior is born!"'),
 ('', 'Then the sky filled with angels, singing, "Glory to God in the highest, and peace on earth!" The shepherds hurried off to Bethlehem.'),
 ('', "They found baby Jesus, just as the angel said. He was God's greatest gift to the world. And that is why we celebrate Christmas. The End."),
]
MIRA = [
 ('Mira and the Rainy Day', ''),
 ('', 'It was a rainy afternoon. Mira wanted to play outside, but the rain would not stop.'),
 ('', '"There is nothing to do," Mira sighed. Her little cat, Mochi, was fast asleep.'),
 ('', 'Then Mochi woke up, stretched, and wandered over to the bookshelf.'),
 ('', 'Bump! Mochi pushed an old red book onto the floor.'),
 ('', '"What is this?" Mira wondered. She picked up the book and opened it.'),
 ('', 'The book was full of stories about faraway places, brave animals and wonderful friends.'),
 ('', 'When she looked up, the rain was stopping, and a rainbow filled the sky!'),
 ('', 'Mira jumped for joy. "Come on, Mochi! Let\'s go outside!"'),
 ('The End', 'A rainy day can become a great adventure when you open a book.'),
]
if __name__ == '__main__':
    make('first-christmas', XMAS); make('mira', MIRA)

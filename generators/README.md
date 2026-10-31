# Clip generators

The Python scripts that render the Telar Clips motion graphics (1920x1080, 30 fps, 8-second seamless loops).
They are kept here so any clip can be re-rendered or a new version made (for example, a 2028 New Year title).

Needs Python 3 with numpy, scipy and Pillow, plus ffmpeg. Run from an output folder, for example:

    PYTHONPATH=path/to/generators python3 path/to/generators/pack4.py happy-new-year-2027-gold-loop

- `pack.py` – first set (bokeh, snow, sparkles, gradients, rays, confetti, lanterns, fireflies)
- `pack2.py` – bokeh/gradient variants, green screens, overlays, tech, countdown, banderitas
- `pack3.py` – world celebrations (Chinese lanterns, moon, sakura, Halloween, autumn, stars)
- `pack4.py` – upcoming holidays (Lantern Festival, St. Patrick's, Ramadan/Eid, Hanukkah, Diwali, Holi, Easter, New Year 2027 …)
- `xmas.py` – parol, string lights, light frame, fireworks
- `greenframe.py` – Christmas lights frame on green (16:9 and 9:16)
- `listings.py` – titles, descriptions and tags; writes clip-listings.csv and clips.json
- `reel.py` – the 9:16 TikTok preview reel

Full-size MP4s are not stored in this repo; they live in the Cloudflare R2 bucket.

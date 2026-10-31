# Telar Clips

Free motion backgrounds, overlays and green screen clips by Telar Labs.
A fast static website: no database, no server, hosted free on Cloudflare Pages.

## What's in this folder

| Path | What it is |
|---|---|
| `site.config.json` | **The only file you normally edit**: site name, domain, media link, contact email, AdSense IDs |
| `data/clips.json` | The list of clips: titles, descriptions, tags, categories |
| `tools/build.py` | Builds every page into `public/` from the two files above |
| `tools/make_previews.sh` | Makes the small preview video and poster for new clips |
| `public/` | The finished website (this is what Cloudflare serves) |
| `public/media/preview/`, `public/media/poster/` | Small previews (about 150 KB each). The full-size MP4s are **not** here; they go in Cloudflare R2 |

## 1. Put the full clips in Cloudflare R2

1. Cloudflare dashboard → **R2** → **Create bucket**. Name it `telar-clips-media`.
2. Open the bucket → **Upload**. Upload all the full-size `.mp4` files from the clip pack (not the posters).
3. Bucket → **Settings → Custom Domains → Connect domain**. Enter `media.yourdomain.com`.
   This needs your domain's nameservers on Cloudflare.
4. Bucket → **Settings → CORS policy → Edit**, and paste the following, using your real domain:

```json
[{"AllowedOrigins":["https://yourdomain.com","https://www.yourdomain.com"],"AllowedMethods":["GET","HEAD"],"AllowedHeaders":["*"],"MaxAgeSeconds":86400}]
```

The CORS policy lets the Download button save the file directly. Without it, the button still works, but it opens the video in a new tab.

## 2. Set your details

Edit `site.config.json`:

- `site_url`: your domain, for example `https://telarclips.com`.
- `media_base`: your R2 domain with a slash at the end, for example `https://media.telarclips.com/`.
- `contact_email`: an email address you check.
- Leave `adsense_client` empty for now.

## 3. Publish on Cloudflare Pages

1. Cloudflare dashboard → **Workers & Pages → Create → Pages → Connect to Git**, then pick this repo.
2. Use these build settings:
   - Framework preset: **None**
   - Build command: `python3 tools/build.py`
   - Build output directory: `public`
3. Click **Save and Deploy**. Your site appears at `<project>.pages.dev`.
4. Project → **Custom domains → Set up a domain**, then add `yourdomain.com` and `www.yourdomain.com`.

From now on, every change you push to GitHub rebuilds the site automatically.

## 4. AdSense

1. Apply at adsense.google.com with your domain.
2. When Google gives you your publisher ID (`ca-pub-1234567890123456`), put it in `adsense_client` and push.
   - The verification code appears on every page.
   - `ads.txt` is created automatically.
3. In AdSense → **Privacy & messaging**, turn on the **European regulations** consent message. The privacy page already mentions it.
4. After approval, keep **Auto ads OFF**. Create **Display ad units** and paste each unit's `data-ad-slot` number into `ad_slots`:
   - `home_grid`: one ad between the Pasko row and the full list on the homepage.
   - `list_grid`: ads after every 12 clips in long lists.
   - `clip_below_download`: under the download box on each clip page.

   Ads only appear once both the client ID and a slot number are set.
5. Also add the site to **Google Search Console** and submit `https://yourdomain.com/sitemap.xml`.

## 5. Adding new clips

1. Copy the new full-size `name.mp4` and `name-poster.jpg` into a folder, then run:
   `bash tools/make_previews.sh /path/to/that/folder`
   This makes the preview and poster in `public/media/`.
2. Add an entry to `data/clips.json`. Copy an existing one and change the id, title, category, description, uses and tags.
   Categories: Christmas & New Year, Filipino, Green Screen, Bokeh Lights, Gradients, Overlays, Celebrations & Events, Nature & Calm, Tech & Abstract.
3. Upload the full `name.mp4` to the R2 bucket.
4. Commit and push. The site rebuilds itself, and `sitemap.xml` updates too.

## Preview the site on your computer

```
python3 tools/build.py
cd public && python3 -m http.server 8000
```

Then open http://localhost:8000.

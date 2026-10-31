#!/usr/bin/env bash
# Make small website previews (MP4) and posters (WebP) for every full-size clip in a folder.
# Usage: bash tools/make_previews.sh /path/to/folder-with-mp4s
# Needs ffmpeg. Each clip's poster is taken from name-poster.jpg if present, otherwise from the video.
set -e
SRC="${1:?give the folder with the full-size .mp4 files}"
OUT="$(cd "$(dirname "$0")/.." && pwd)/public/media"
mkdir -p "$OUT/preview" "$OUT/poster"
for f in "$SRC"/*.mp4; do
  n=$(basename "$f" .mp4)
  w=$(ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 "$f")
  W=${w%,*}; H=${w#*,}
  if [ "$H" -gt "$W" ]; then sc="360:640"; else sc="640:360"; fi
  ffmpeg -y -loglevel error -i "$f" -vf scale=$sc -an -c:v libx264 -preset veryfast -crf 30 -pix_fmt yuv420p -movflags +faststart "$OUT/preview/$n.mp4"
  if [ -f "$SRC/$n-poster.jpg" ]; then
    ffmpeg -y -loglevel error -i "$SRC/$n-poster.jpg" -vf scale=$sc -q:v 80 "$OUT/poster/$n.webp"
  else
    ffmpeg -y -loglevel error -ss 4 -i "$f" -frames:v 1 -vf scale=$sc -q:v 80 "$OUT/poster/$n.webp"
  fi
  echo "done $n"
done

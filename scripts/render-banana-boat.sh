#!/usr/bin/env bash
set -euo pipefail
mkdir -p output .render/banana-boat
shopt -s nullglob
images=(assets/banana-boat/*.jpg)
if [ "${#images[@]}" -ne 4 ]; then
  echo "Expected exactly four JPG files in assets/banana-boat/ (currently ${#images[@]})." >&2
  exit 1
fi
: > .render/banana-boat/clips.txt
for i in 0 1 2 3; do
  n=$((i+1))
  ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 24 -i "${images[$i]}" \
    -vf "crop=iw:ih-148:0:148,scale=820:1430,crop=720:1280:x='(iw-ow)/2+25*sin(n/65)':y='(ih-oh)/2+24*cos(n/73)',fade=t=in:st=0:d=0.25,fade=t=out:st=3.65:d=0.35,format=yuv420p" \
    -t 4 -r 24 -an -c:v libx264 -preset veryfast -crf 22 ".render/banana-boat/clip_${n}.mp4"
  echo "file 'clip_${n}.mp4'" >> .render/banana-boat/clips.txt
done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i .render/banana-boat/clips.txt -c copy output/banana-boat-motion.mp4
python3 - <<'PY'
import json,subprocess
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,avg_frame_rate:format=duration','-of','json','output/banana-boat-motion.mp4']))
s=p['streams'][0]
assert (s['width'],s['height'])==(720,1280)
assert abs(float(p['format']['duration'])-16)<.1
print('PASS: 720x1280 16s MP4')
PY

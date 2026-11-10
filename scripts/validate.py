#!/usr/bin/env python3
import json, subprocess, sys
path, expected=sys.argv[1],int(sys.argv[2])
data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_frames:format=duration','-of','json',path],text=True))
v=data['streams'][0];a,b=map(int,v['avg_frame_rate'].split('/'));fps=a/b
duration=float(data['format']['duration'])
assert (v['width'],v['height'])==(1920,1080),str(v)
assert abs(fps-30)<.01,f'Wrong FPS: {fps}'
assert abs(duration-expected)<.1,f'Wrong duration: {duration}'
assert int(v.get('nb_frames') or 0)==expected*30,f'Wrong frame count: {v}'
print(f'PASS: 1920x1080, 30fps, {duration:.2f}s')

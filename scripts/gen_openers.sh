#!/usr/bin/env bash
# Generate keyframe + Seedance clip for each work dir's s01a opener. Usage: scripts/gen_openers.sh work/a work/b ...
set -e
for wd in "$@"; do
  P=$(python -c "import yaml,sys;s=[x for x in yaml.safe_load(open('$wd/shots.yaml')) if x['id']=='s01a'][0];print(s['prompt'])")
  V=$(python -c "import yaml,sys;s=[x for x in yaml.safe_load(open('$wd/shots.yaml')) if x['id']=='s01a'][0];print(s.get('video_prompt','slow cinematic push in'))")
  python scripts/openrouter.py image --prompt "$P Photorealistic, 16:9 widescreen." --out $wd/keyframes/s01a.png --workdir $wd | tail -1
  python scripts/openrouter.py video --model-key video_motion --image $wd/keyframes/s01a.png --prompt "$V" --seconds 8 --out $wd/shots/s01a.mp4 --workdir $wd | grep -v '^status'
done

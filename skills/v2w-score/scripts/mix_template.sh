#!/usr/bin/env bash
# v2w mix for a piece with an external music track. Copy to <piece>/mix.sh and edit the block below.
#
# Why: animate's export mixes an external track with one-pass (dynamic) loudnorm, which rides the gain
# over time and flattens any volume automation. This redoes renders/audio.wav with ONE static gain to the
# target loudness plus a limiter, then remuxes final.mp4 / share.mp4 (video stream untouched).
#
# Order: node <animate>/tools/export.mjs <piece> --only-audio --share   (writes renders/stem-sfx.wav)
#        ./mix.sh
#        node <animate>/tools/review.mjs <piece>
# Re-run after EVERY export: export overwrites share.mp4 with its own mix.
set -euo pipefail

# ---- edit -------------------------------------------------------------------------------------------
TRACK="audio/take1_raw.mp3"   # raw track
DUR=45                         # piece length, s
FADE_OUT=0.5                   # final fade, s
TARGET_LUFS=-14
LIMIT=0.84                     # alimiter linear limit (~ -1.5 dBFS)
# Volume automation as an ffmpeg expression in t (seconds); 1 = unchanged. Example:
#   0-8 s full, 8-22.7 s -6 dB, 0.05 s ramp to a hole until 23.0 s, payoff +2 dB to 25 s, ease back by 26.5 s.
VOL_EXPR="if(lt(t,8),1, if(lt(t,22.7),0.5, if(lt(t,22.75),0.5*(22.75-t)/0.05, if(lt(t,23.0),0, if(lt(t,25),1.26, if(lt(t,26.5),1.26-0.26*(t-25)/1.5,1))))))"
# -----------------------------------------------------------------------------------------------------

cd "$(dirname "$0")"
q() { ffmpeg -y -hide_banner -loglevel error "$@"; }

# 1. automated track
q -i "$TRACK" -af "volume='${VOL_EXPR}':eval=frame" -ar 48000 audio/track.wav
cp audio/track.wav renders/stem-music.wav

# 2. track + sfx stem, summed without normalisation
q -t "$DUR" -i audio/track.wav -i renders/stem-sfx.wav -filter_complex \
  "[0:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=out:st=$(echo "$DUR - $FADE_OUT" | bc -l):d=${FADE_OUT}[m];[1:a]aresample=48000,aformat=channel_layouts=stereo[s];[m][s]amix=inputs=2:normalize=0:duration=first[o]" \
  -map "[o]" -t "$DUR" renders/mix-raw.wav

# 3. one static gain to target, then limiter
I=$(ffmpeg -hide_banner -nostats -i renders/mix-raw.wav -af ebur128 -f null - 2>&1 | grep -A2 "Integrated loudness" | awk '/I:/{print $2}')
G=$(echo "$TARGET_LUFS - ($I)" | bc -l)
echo "mix-raw: $I LUFS -> gain $G dB"
q -i renders/mix-raw.wav -af "volume=${G}dB,alimiter=limit=${LIMIT}:attack=1:release=50:level=disabled" -ar 48000 -c:a pcm_s16le renders/audio.wav
rm renders/mix-raw.wav

# 4. remux
for f in final share; do
  [ -f "renders/$f.mp4" ] || continue
  q -i "renders/$f.mp4" -i renders/audio.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "renders/$f-remux.mp4"
  mv "renders/$f-remux.mp4" "renders/$f.mp4"
done
echo "remuxed renders/final.mp4 and renders/share.mp4"

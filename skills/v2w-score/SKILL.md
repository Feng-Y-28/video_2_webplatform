---
name: v2w-score
description: Stage 5 of the v2w pipeline. Give a piece its sound — a synthesized score in animate's score.js, an AI-generated track (ACE-Step), or a library track — shape it to the story arc with volume automation, and mix it to −14 LUFS without losing that automation. TRIGGER when the v2w-orchestra reaches stage 5, or the user asks to "add / change / fix the music", "generate a background track", "make the hit louder", "the music sounds bad", "mix to −14 LUFS" for a v2w piece.
---

# v2w-score

You cannot hear, and nobody listens before the sample review. Everything here is
**measured**. Gate: **music checks passed** — all of:
- `../v2w-review/scripts/band_energy.py renders/audio.wav` prints no WARN;
- animate review SOUND: −14 ± 1 LUFS, TP ≤ −1 dBTP, loudest 100 ms inside the payoff act;
- no pattern in `score.js` repeating unchanged for more than ~8 s.

Read `references/music-principles.md` first.

## Choose a source (record the choice in brief.md → Sound plan)

| Source | When | Notes |
|---|---|---|
| Synthesized (`src/score.js`) | Exact sync matters; no licence questions | Sounds thin by default. Follow the timbre rules in music-principles §5 |
| AI track (ACE-Step) | `allow_hosted_music_api` is true | See `references/ace-step.md`. It will not hit time targets |
| Supplied track | The input came with one | Check the licence; no trending-platform audio reused elsewhere |

## Track-first workflow (external track)

1. Generate or collect 2–4 takes in `<piece>/audio/` as `takeN_raw.*`.
2. For each, measure the shape: `node <animate>/tools/beats.mjs <take> <piece> --dur <len>`
   plus segment loudness (`../v2w-review/scripts/band_energy.py <take> --segments …`).
   Choose automatically: the take whose build / peak / fall times are closest to
   the piece's acts (least automation needed). Log every take's numbers and the
   choice in LOG.md. A take whose natural shape fits beats any fix.
3. In `piece.json` set `"music": {"file": "audio/track.wav", …}`; move hits,
   risers and the closing chord in `src/score.js` to the sfx bus (`to = 's'`).
4. Copy `scripts/mix_template.sh` to `<piece>/mix.sh`, set the variables at
   the top (track, length, automation), then:
   `export.mjs <piece> --only-audio --share` → `./mix.sh` → v2w-review.
   **Re-run `mix.sh` after every export**, because export overwrites `share.mp4`
   with its dynamically normalised mix.
5. Shape: duck the build −3…−6 dB, leave a 0.2–0.3 s hole before the payoff
   hit (or a riser cut into silence), lift the payoff +2 dB, ease back.

## Synthesized workflow

Edit `src/score.js`; iterate with `export.mjs --only-audio --share` until the
music checks pass. Follow `references/music-principles.md` §5. Run `band_energy.py` and fix what it flags
(low-mid mud, a thin top end). It cannot hear loops: re-read `score.js` for any pattern repeating unchanged for more than ~8 s.

## Hand-off

`LOG.md`: source, take chosen and why, automation numbers, LUFS / TP / LRA,
where the loudest 100 ms lands, band_energy summary. Tick `music checks passed`.
Then go to v2w-review. If the checks still fail after 2 retries, log it as an open issue and continue.

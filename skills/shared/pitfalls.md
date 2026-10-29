# Pitfalls

Things that broke at least once and cost time. Each item lists the
symptom, the cause, and the fix. Keep entries short; add new ones at the
bottom with the version that added them.

### ffmpeg has no `drawtext` (macOS / Homebrew) — v0.1.0
- **Symptom:** animate `review.mjs` fails with `No such filter: 'drawtext'`
  while building the first contact sheet.
- **Cause:** the default Homebrew `ffmpeg` bottle is built without libfreetype.
- **Fix:** `brew install ffmpeg-full` (keg-only), and prepend it only for review:
  `PATH="$(brew --prefix)/opt/ffmpeg-full/bin:$PATH" node tools/review.mjs <piece>`.

### animate tools cannot find Playwright — v0.1.0
- **Symptom:** `still.mjs` / `export.mjs` fail with `Cannot find module 'playwright'`.
- **Cause:** Playwright is installed outside the skill directory.
- **Fix:** `export NODE_PATH=<dir containing node_modules with playwright>`
  before running animate tools.

### External music loses its volume automation — v0.1.0
- **Symptom:** you automate a track (duck before the hit, lift the payoff),
  but review still finds the loudest moment in the wrong act, and the
  numbers do not change monotonically with the automation.
- **Cause:** animate's export mixes an external track with a **one-pass**
  `loudnorm` (ffmpeg's dynamic mode), which rides gain over time.
- **Fix:** use `v2w-score/scripts/mix_template.sh`: static gain to −14 LUFS
  + limiter, run after every `export.mjs --only-audio --share`.

### Review passes but the music is unbearable — v0.1.0
- **Symptom:** story arc / loudness all PASS, the listener hates it.
- **Cause:** animate's review measures structure and loudness, not spectrum,
  timbre or repetition.
- **Fix:** run `v2w-review/scripts/band_energy.py` and read its warnings;
  the sample review is the only listening, so fix every band_energy WARN first.

### AI music ignores time targets — v0.1.0
- **Symptom:** asked for a break at 36 s and a climax at 37.5 s, every take
  resolves on its own around 40 s.
- **Fix:** pick a take whose *natural* shape matches the piece (or re-cut the
  piece to the take), then automate. Do not expect the model to hit seconds.

### Audio node scheduled at negative time — v0.1.0
- **Symptom:** export throws on `setValueAtTime` with a time like −0.05.
- **Fix:** clamp pre-roll starts: `Math.max(0, t0 - lead)`.

# Review checklist

| # | Check | Tool | Pass | Typical fix |
|---|---|---|---|---|
| 1 | Cuts on the beat grid | review.mjs CUTS | all on grid | move cut to nearest 8th |
| 2 | Story arc | review.mjs STORY ARC | ≥ 4/5 | lift payoff, duck build, add silence before hit |
| 3 | Loudest 100 ms in payoff act | review.mjs SOUND | yes | automation (v2w-score) — not loudnorm |
| 4 | Loudness | review.mjs SOUND | −14 ± 1 LUFS, TP ≤ −1 dBTP | mix.sh static gain + limiter |
| 5 | Text inside frame / not overlapping / out of phone UI | review.mjs TEXT | 0 issues | shorten label, move into safe area |
| 6 | Dead beats | review.mjs DEAD BEATS | none > 3 s (except agreed ending) | split shot, add a small result pop |
| 7 | Spectral balance | band_energy.py | no WARN | high-pass pads, add hats, cut low-mid |
| 8 | Repetition | read score.js | no pattern unchanged > ~8 s | vary arpeggio / voicing per chord |
| 9 | Hook works on mute | your eye on frames 0–3 s | conflict readable | bigger text, fewer words |
| 10 | Every on-screen number sourced | brief.md | all present | add source or remove claim |
| 11 | Critique D | v2w-critique | critique_gate.py PASS | apply fixes, ≤ 2 retries |
| 12 | Sample review | user (only human step) | approve | route notes back to the earliest stage |

## Notes

- Translated pieces fail on text length most often: abbreviate units
  (`8 B/cyc`), shorten verdict lines, re-run (5).
- A piece can pass 1–6 and still sound bad. Nobody listens before the sample
  review, so 7 and 8 are not optional.

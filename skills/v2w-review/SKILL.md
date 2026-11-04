---
name: v2w-review
description: Stage 6 of the v2w pipeline. Prove a rendered piece works — run animate's measured review (cuts, story arc, text in safe zones, loudness, dead beats), add the checks it does not cover (spectral balance, phone preview, fact re-check), write a per-shot PASS table to LOG.md, run critique D, and prepare the sample review — the pipeline's only human step. TRIGGER when the v2w-orchestra reaches stage 6, after any re-export, or when the user asks to "review / check / QA piece X", "is it ready", "why does review fail".
---

# v2w-review

Run after **every** change to picture or sound. A failed check sends you back
to v2w-production or v2w-score; a structural failure (story arc + dead beats
in the same act) sends you back to v2w-script.

## Checks

1. **animate review** — `node <animate>/tools/review.mjs <piece>`
   (ffmpeg with `drawtext` on PATH; see `../shared/pitfalls.md`). Needs:
   cuts on grid, story arc ≥ 4/5 (5/5 preferred), TEXT pass, no dead beat
   > 3 s outside an intentional ending, −14 ± 1 LUFS, TP ≤ −1 dBTP, loudest
   100 ms inside the payoff act.
2. **Spectrum** — `python3 scripts/band_energy.py <piece>/renders/audio.wav`.
   Warns on low-mid mud and a thin top end. It cannot detect a loop that runs
   too long; check `score.js` for patterns repeating unchanged > ~8 s.
   This catches what (1) cannot.
3. **Look at the sheets** — open `review/shot*-sheet.jpg` and `phone.jpg`
   yourself. The text check is more reliable than your eye for cropping, but
   only your eye notices weak contrast or a confusing frame.
4. **Facts** — every number on screen appears in `brief.md` → Claims + sources,
   with the same value. Translated pieces: check that units and abbreviations
   still read correctly.
5. Tick `review checks passed` only when all of these exist: `review/shot*-sheet.jpg`,
   `review/phone.jpg`, a non-empty `renders/share.mp4`, and a `## vN review`
   block in `LOG.md` with `Checks:` and `Weakest shot:` lines — and checks 1–4
   pass. Write `publish.md` (v2w-publish steps 1–2) **before** critique D, then
   run **v2w-critique gate D**. The order is fixed: publish.md → D → sample
   review.

## Sample review (the only human step)

Run this after a D round exists. If the latest `critique/D-r<n>.json` passes
`critique_gate.py` (exit 0), proceed normally. If D failed, or any earlier gate
is open, present every open issue and require explicit user approval; record one
line per open gate under `STATUS.md` → `User waivers`:
`- <gate> accepted with open issues by user (YYYY-MM-DD): <one line>`.
Present, in one message: the path to `renders/share.mp4` (and `exports/` copy),
`publish.md`, a 5-line summary of LOG.md (critique scores, music numbers,
weakest shot), and every open issue from `STATUS.md`. Ask for **approve** or
**revise + notes**. Do not say how it sounds.
- approve → tick `sample approved (user)`; if a gate is open, the waiver line
  above is required first. Then go to v2w-publish step 3.
- revise → route each note to the earliest stage it touches (content → distill,
  order → script, picture → production, sound → score); re-run every gate after it.

Full checklist with thresholds: `references/review-checklist.md`.

## Output

Append to `LOG.md`:

```
## vN review (YYYY-MM-DD)
| shot | t | result | note |
Checks: cuts · story arc x/5 · text · LUFS / TP / LRA · loudest @ t · dead beats
Spectrum: <band_energy summary>
Weakest shot: <one line>
```

Every remaining WARN needs a written reason in LOG.md (e.g. a quiet ending on
purpose). This is the only exception D1 and D3 allow: D3 accepts a
`band_energy` WARN only when LOG.md gives the written reason, matching D1 and
this review hand-off. Without that written reason, `band_energy` has no
exception — fix it before D. Critique D checks those reasons.

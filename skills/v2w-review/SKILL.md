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
5. Tick `review checks passed` when 1–4 pass. Write `publish.md` (v2w-publish
   steps 1–2) so critique D can check it, then run **v2w-critique gate D**.

## Sample review (the only human step)

Present, in one message: the path to `renders/share.mp4` (and `exports/` copy),
`publish.md`, a 5-line summary of LOG.md (critique scores, music numbers,
weakest shot), and every open issue from `STATUS.md`. Ask for **approve** or
**revise + notes**. Do not say how it sounds.
- approve → tick `sample approved (user)`, go to v2w-publish step 3.
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
purpose). Critique D checks those reasons.

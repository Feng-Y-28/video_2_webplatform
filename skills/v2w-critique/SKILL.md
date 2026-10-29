---
name: v2w-critique
description: Independent rubric critique for the v2w pipeline. Spawns a fresh subagent that sees only an artefact and a fixed rubric (gate A content, B script, C visual, D final), scores every item 1–5 with evidence, and returns JSON; a deterministic script then decides PASS / FAIL and how many retries are left. Used by v2w-distill, v2w-script, v2w-production and v2w-review in place of human check-ins. TRIGGER when a v2w stage says "run critique <gate>", or the user asks to "critique / score / review the principle / script / storyboard / final cut against the rubric".
---

# v2w-critique

The critic must be **independent**. Your reasoning would anchor it, so it never
sees that reasoning: it gets the rubric, the listed files, and the schema.

## Gates

| Gate | Rubric | Artefacts given to the critic |
|---|---|---|
| A content | `references/rubric-A-content.md` | `principle.md`, `source/` |
| B script | `references/rubric-B-script.md` | `brief.md`, `principle.md`, `refs/refcard.md` |
| C visual | `references/rubric-C-visual.md` | `review/look.png`, `review/board.png`, `brief.md`, `refs/refcard.md` (synthesis only) |
| D final | `references/rubric-D-final.md` | `review/shot*-sheet.jpg`, `review/phone.jpg`, the latest review output in `LOG.md`, `band_energy.py` output, `brief.md`, `principle.md`, `publish.md` |

## Procedure

1. Round number `n` = number of existing `critique/<gate>-r*.json` + 1.
2. Spawn **one fresh subagent** (general-purpose; read-only work) with
   exactly this prompt, filled in:

   ```
   You are an independent reviewer for a short explainer video. Judge only
   what is in the files below; do not assume intent. Be strict: a 5 means a
   seasoned editor would change nothing.

   Rubric: <absolute path to rubric file>
   Files: <absolute paths, one per line>
   [Round n > 1 only] Previous must-fix items to verify: <list from round n-1>

   For every rubric item give: id, score 1-5, evidence (quote or file+location),
   fix (one concrete action, or "" if score 5). List blocking problems in
   must_fix. Write ONLY this JSON to <piece>/critique/<gate>-r<n>.json:
   {"gate": "<gate>", "round": n, "items": [{"id": "", "score": 0, "evidence": "", "fix": ""}],
    "takeaway": "<the one idea a viewer would leave with, in one sentence>",
    "must_fix": [], "summary": ""}
   ```

   Do not add your opinion, the history of the piece, or hints about
   what you expect.
3. `python3 scripts/critique_gate.py <piece> <gate>` → PASS / FAIL, retries left.
4. **PASS** → tick the gate in `STATUS.md`, append the summary to `LOG.md`.
   **FAIL** with retries left → apply every `fix` of items below threshold and
   every `must_fix`, log the changes, go to 1. **FAIL** with no retries → stop
   the pipeline; the sample review gets the open issues.

## Pass rule (enforced by the script)

- every item marked **blocking** in the rubric scores ≥ 3;
- mean score ≥ 4.0;
- `must_fix` is empty;
- for gates B and D, `takeaway` must be non-empty. The orchestrator compares
  it with the mechanism in `principle.md`. If they differ, treat it as a FAIL even if
  the scores pass.

## Changing rubrics

Rubrics are versioned with the repo. Add an item only when a real failure
got past the current rubric, and note that in CHANGELOG. Topic-specific checks
come from `refs/refcard.md`; they extend a critique and never replace items.

# Architecture

```
                         v2w-orchestra  (directories, gates, order, config)
                                │
 distill ─A─ reference ── script ─B─ production ─C─ score ─M─ review ─D─ [sample: user] ─ publish
    │            │                       │            │          │                          │
 nature-reader  browser +             animate      animate    animate review            browser
 deep-research  transcript skill      anatomy      ACE-Step   band_energy.py
                                │
                         v2w-critique  (fresh subagent + rubric + critique_gate.py)
                         shared/  claims-and-sources · pitfalls
```

`A`–`D` are fresh-subagent rubric critiques (`v2w-critique`). `M` is machine
checks — animate review and `band_energy.py` — **plus a manual or agent read of
`score.js`**, because `band_energy.py` cannot detect a repeated pattern; a
repeating phrase has to be seen in the score.

Critique `C` runs on the **look and the storyboard, before the full build**;
the finished cut is not the first time the visuals are judged.

## Design choices

- **Autonomous until the sample.** Every place a human used to approve
  (content, script, look, storyboard, music) is a rubric critique or a machine
  check. The user's single review then deals with taste, not basic errors.
- **Independent critics.** A critique runs in a fresh subagent that receives
  only the artefact, the rubric and an output schema, never the author's
  reasoning or the piece's history. A deterministic script turns its JSON
  into PASS/FAIL so that the bar cannot drift.
- **Bounded retries.** `max_retries` (default 2) counts automatic retries
  *after* the first round, so each gate gets `1 + max_retries` automated rounds.
  When that budget is spent, one repair plus a single **verification round** is
  allowed; only a PASS in the verification round ticks the gate. If it still
  fails, the open issues go to the sample review instead of looping.
- **No stale passes.** A critique round records a hash of its inputs. If an
  artefact changes afterwards, the gate is STALE and cannot be ticked until a
  new round is run.
- **Thin wrappers over existing skills.** Paper reading, fact checking,
  transcripts, rendering, review metrics and music generation belong to other
  skills and tools. v2w adds the order, the rubrics and the glue that a
  technical explainer needs.
- **Standing consent.** Outward actions (browsing, hosted APIs, uploading,
  publishing) are decided once in `v2w.config.json`; publishing additionally
  waits for the approved sample.
- **Deterministic scripts only.** Scripts never call an LLM or the network.
